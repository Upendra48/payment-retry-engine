# Payment Retry Engine

## Overview

The Payment Retry Engine is a production-inspired backend system designed to process payments reliably while handling transient gateway failures automatically.

Instead of immediately marking every failed payment as permanently failed, the engine intelligently determines whether the failure is temporary (for example, a timeout or network issue). If the failure is retryable, the payment is scheduled for another attempt after a configurable delay.

The retry process is fully asynchronous and is powered by Celery, RabbitMQ, and Celery Beat, allowing retries to occur without blocking API requests.

The system also implements idempotency to prevent duplicate payments and exposes Prometheus metrics for monitoring and Grafana dashboards for visualization.

---

# Goals

The primary goals of the project are:

* Prevent duplicate payments.
* Automatically retry temporary failures.
* Separate business logic from infrastructure.
* Support asynchronous processing.
* Provide observability through metrics.
* Follow production-oriented backend architecture.

---

# Technologies Used

| Component             | Purpose                   |
| --------------------- | ------------------------- |
| Django REST Framework | REST API                  |
| PostgreSQL            | Primary database          |
| Celery                | Background task execution |
| RabbitMQ              | Message broker            |
| Celery Beat           | Scheduled retries         |
| Docker Compose        | Local orchestration       |
| Prometheus            | Metrics collection        |
| Grafana               | Monitoring dashboards     |

---

# System Architecture

```text
                    Client

                      │

                      ▼

              Django REST API

                      │

          PaymentService.create_payment()

                      │

                      ▼

                 PostgreSQL

                      │

                      ▼

             Mock Payment Gateway

              ┌──────────────┐
              │              │
              │ Success      │ Failure
              │              │
              ▼              ▼

         SUCCESS        Retry Policy

                              │

                   Retryable Failure?

                    ┌─────────┴─────────┐

                   Yes                 No

                    │                  │

                    ▼                  ▼

               RETRYING             FAILED

                    │

           next_retry_at assigned

                    │

                    ▼

              Celery Beat

                    │

                    ▼

               RabbitMQ

                    │

                    ▼

             Celery Worker

                    │

                    ▼

      PaymentService.retry_payment()

                    │

                    ▼

             Payment Updated
```

---

# Payment Lifecycle

Every payment moves through a series of states.

## 1. Payment Created

The client submits a payment request.

```text
POST /api/payments/
```

The payment is stored in PostgreSQL with an initial status.

---

## 2. Idempotency Check

Before creating a payment, the system checks whether the supplied idempotency key already exists.

If it exists:

* The existing payment is returned.

If it does not exist:

* A new payment is created.

This guarantees that duplicate API requests never create duplicate payments.

---

## 3. Gateway Processing

The payment is sent to the payment gateway.

Possible outcomes:

### Success

```text
SUCCESS
```

The payment is complete.

---

### Temporary Failure

Examples:

* Timeout
* Connection error
* Service unavailable

These failures may succeed later.

The payment becomes:

```text
RETRYING
```

---

### Permanent Failure

Examples:

* Invalid card
* Invalid request
* Fraud detection

These failures should never be retried.

The payment becomes:

```text
FAILED
```

---

# Retry Policy

The retry policy decides whether another attempt should be made.

Example logic:

```text
Gateway Timeout

↓

Retry

Network Error

↓

Retry

Invalid Card

↓

Do Not Retry
```

The policy also determines:

* Maximum retry attempts.
* Delay before the next retry.
* Final failure conditions.

---

# Retry Lifecycle

When a retryable failure occurs:

```text
FAILED

↓

Retry Policy

↓

status = RETRYING

↓

next_retry_at calculated

↓

Database Updated
```

Nothing happens immediately.

The payment simply waits until its retry time arrives.

---

# Automatic Retry Flow

Every minute:

Celery Beat executes:

```text
retry_due_payments()
```

This task:

* Finds payments whose retry time has arrived.
* Sends retry tasks to RabbitMQ.

RabbitMQ forwards those tasks to Celery Workers.

Workers execute:

```text
PaymentService.retry_payment()
```

The payment is processed again.

---

# Payment States

## PENDING

Payment has been created but not processed.

---

## SUCCESS

Payment completed successfully.

No more retries occur.

---

## RETRYING

The previous attempt failed due to a temporary issue.

The payment is waiting for its scheduled retry.

---

## FAILED

The payment has permanently failed.

No additional retries occur.

---

# Idempotency

Every payment request includes an idempotency key.

Example:

```text
payment-001
```

If the client accidentally sends the same request multiple times:

```text
POST

↓

POST

↓

POST
```

Only one payment is created.

All subsequent requests return the existing payment.

This prevents duplicate charges.

---

# Payment Attempts

Every communication with the gateway creates a PaymentAttempt record.

Example:

| Attempt | Result  |
| ------- | ------- |
| 1       | TIMEOUT |
| 2       | SUCCESS |

This provides a complete audit trail for every payment.

---

# Service Layer

Business logic is isolated inside the service layer.

Responsibilities include:

* Creating payments.
* Calling the gateway.
* Recording attempts.
* Updating payment status.
* Applying retry policy.
* Managing idempotency.

Views remain thin and primarily handle HTTP requests and responses.

---

# Asynchronous Processing

Instead of retrying immediately:

```text
API

↓

RabbitMQ

↓

Worker

↓

Retry
```

This keeps API responses fast and allows retries to happen independently.

---

# Scheduling

Celery Beat checks every minute:

```text
next_retry_at <= current_time
```

If true:

The payment is queued for retry.

---

# Monitoring

The engine exposes Prometheus metrics.

Examples include:

* Payments created
* Successful payments
* Failed payments
* Retry count
* Gateway latency
* Payment processing time

Grafana visualizes these metrics through dashboards.

---

# Database Models

## Payment

Stores:

* Amount
* Currency
* Customer email
* Status
* Retry count
* Retry schedule
* Gateway reference

---

## PaymentAttempt

Stores:

* Attempt number
* Response code
* Response message
* Gateway transaction ID
* Processing duration

---

## IdempotencyKey

Maps an idempotency key to a payment.

Prevents duplicate payment creation.

---

# API Endpoints

Create payment:

```text
POST /api/payments/
```

List payments:

```text
GET /api/payments/
```

Retrieve payment:

```text
GET /api/payments/{id}/
```

Payment attempts:

```text
GET /api/payments/{id}/attempts/
```

---

# Production Features

This project includes:

* Service Layer Architecture
* Retry Policy
* Idempotent Requests
* UUID Primary Keys
* PostgreSQL
* Docker
* Celery
* RabbitMQ
* Celery Beat
* Prometheus Metrics
* Grafana Dashboards
* Filtering
* Searching
* Ordering
* Pagination
* API Documentation
* Background Processing

---

# Common Failure Scenarios

## Gateway Timeout

The payment enters the `RETRYING` state and is scheduled for another attempt.

---

## Duplicate API Request

The idempotency key prevents duplicate payment creation.

---

## Worker Stops

Retry tasks remain in RabbitMQ until a worker becomes available again.

---

## RabbitMQ Stops

New retry tasks cannot be queued until RabbitMQ is restored.

---

## PostgreSQL Stops

Payment processing cannot continue because the application's persistent state is unavailable.

---

# Why This Architecture?

This architecture follows the principle of **separation of concerns**:

* Django handles HTTP requests.
* The Service Layer contains business logic.
* PostgreSQL stores persistent data.
* RabbitMQ transports background tasks.
* Celery executes background work.
* Celery Beat schedules retries.
* Prometheus collects metrics.
* Grafana visualizes system health.

Each component has a single responsibility, making the system easier to understand, test, maintain, and scale.

---

# Interview Questions

## Why build a payment retry engine?

Real payment gateways occasionally fail due to temporary issues such as network outages or timeouts. Automatically retrying those failures improves the likelihood of successful payment processing while reducing manual intervention.

---

## Why not retry every failure?

Some failures are permanent, such as invalid payment details or fraud detection. Retrying these requests wastes resources and may produce unintended side effects. The retry policy distinguishes between transient and permanent failures.

---

## Why use asynchronous retries?

Retrying payments synchronously would increase API response times and reduce scalability. Asynchronous processing allows the API to remain responsive while background workers handle retries independently.

---

## Why use idempotency?

Clients may resend the same request because of network interruptions or timeouts. Idempotency ensures that repeated requests do not create duplicate payments or duplicate charges.

---

## Revision Notes

* Prevent duplicate payments using idempotency keys.
* Separate business logic into a dedicated service layer.
* Retry only transient failures.
* Execute retries asynchronously with Celery and RabbitMQ.
* Schedule retries using Celery Beat.
* Record every gateway interaction with `PaymentAttempt`.
* Monitor the system using Prometheus and Grafana.
* Design components with clear responsibilities to improve maintainability and scalability.

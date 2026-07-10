# Payment Retry Engine

A production-inspired backend system built with Django REST Framework that simulates how modern payment platforms process transactions, prevent duplicate payments, automatically retry failed payments, expose operational metrics, and provide API observability.

This project demonstrates backend engineering concepts commonly used in fintech systems, including idempotency, asynchronous task processing, retry strategies, monitoring, scheduling, REST API design, and containerized deployment.

---

## Features

### Payment Processing

* Create payment requests through REST APIs
* Simulated payment gateway integration
* Automatic payment status management
* Payment attempt history
* UUID-based payment identifiers

---

### Idempotency Support

Duplicate payment requests are prevented using idempotency keys.

If the same request is submitted multiple times with the same key, the existing payment is returned instead of creating a duplicate transaction.

---

### Automatic Retry Engine

Failed payments are retried automatically using an exponential backoff strategy.

Features include:

* Retry policy service
* Configurable retry limits
* Scheduled retry execution
* Automatic retry queue
* Retry history tracking
* Celery workers for asynchronous execution
* Celery Beat for scheduled retries

---

### Payment Gateway Simulation

A mock payment gateway simulates real-world payment responses.

It randomly generates:

* Successful payments
* Temporary failures
* Permanent failures
* Gateway latency
* Transaction IDs

This allows testing retry logic without requiring an actual payment provider.

---

### Payment Attempt Tracking

Every gateway interaction is stored.

Each attempt records:

* Attempt number
* Status
* Response code
* Response message
* Gateway transaction ID
* Processing duration

This provides complete payment auditability.

---

### REST API

Implemented endpoints include:

```
POST   /api/payments/
GET    /api/payments/
GET    /api/payments/{id}/
GET    /api/payments/{id}/attempts/
```

---

### Payment Listing

Supports production-style querying.

Features:

* Pagination
* Filtering
* Ordering
* Searching

Examples:

```
GET /api/payments/

GET /api/payments/?status=SUCCESS

GET /api/payments/?status=FAILED

GET /api/payments/?customer_email=user@example.com

GET /api/payments/?ordering=-created_at

GET /api/payments/?search=user@example.com
```

---

### API Documentation

Interactive OpenAPI documentation generated using DRF Spectacular.

Available through:

```
/api/schema/swagger/
```

---

### Monitoring

Application metrics are exposed using Prometheus.

Custom metrics include:

* Total payments created
* Successful payments
* Failed payments
* Retry count
* Payments waiting for retry
* Gateway latency
* Payment processing duration

Metrics endpoint:

```
/metrics
```

---

### Grafana Dashboard

Prometheus metrics can be visualized through Grafana.

Typical dashboards include:

* Total payments
* Successful payments
* Failed payments
* Retry statistics
* Gateway latency
* Payment processing duration
* Requests per second

---

### Background Processing

Asynchronous tasks are handled using Celery.

Tasks include:

* Retrying failed payments
* Scheduling retry jobs
* Queue processing

---

### Containerized Development

Entire application stack runs inside Docker.

Services:

* Django
* PostgreSQL
* RabbitMQ
* Celery Worker
* Celery Beat
* Prometheus
* Grafana

---

## Architecture

```
                Client
                   │
                   ▼
          Django REST Framework
                   │
                   ▼
            Payment Service
                   │
      ┌────────────┴────────────┐
      ▼                         ▼
 PostgreSQL             Mock Gateway
      │                         │
      ▼                         ▼
Payment Records          Gateway Response
      │
      ▼
 Retry Policy
      │
      ▼
 Celery Queue
      │
      ▼
 Celery Worker
      │
      ▼
 Scheduled Retry
      │
      ▼
 Payment Updated

Prometheus <──── Metrics ─── Django

Grafana <────── Prometheus
```

---

## Tech Stack

### Backend

* Python 3.12
* Django
* Django REST Framework

### Database

* PostgreSQL

### Task Queue

* Celery
* RabbitMQ
* Celery Beat

### Monitoring

* Prometheus
* Grafana

### API Documentation

* DRF Spectacular

### Filtering

* django-filter

### Containerization

* Docker
* Docker Compose

---

## Project Structure

```
apps/
│
├── common/
├── payments/
│   ├── models/
│   ├── serializers/
│   ├── services/
│   ├── tasks.py
│   ├── metrics.py
│   ├── filters.py
│   ├── views.py
│   └── urls.py
│
└── users/

config/
```

---

## Core Design Patterns

The project is organized using a service-oriented architecture.

Key components include:

* Service Layer
* DTO (Data Transfer Objects)
* Retry Policy abstraction
* Payment Gateway abstraction
* Background task processing
* Repository usage through Django ORM
* Idempotency pattern
* Exponential Backoff algorithm

---

## Development Setup

Clone the repository.

```
git clone <repository-url>
```

Build the containers.

```
docker compose up --build
```

Run database migrations.

```
docker compose exec web python manage.py migrate
```

Application URLs:

```
Application
http://localhost:8000

Swagger
http://localhost:8000/api/schema/swagger/

Prometheus
http://localhost:9090

Grafana
http://localhost:3000

RabbitMQ Management
http://localhost:15672
```

---

## Observability

The project includes production-inspired observability.

Metrics collected include:

* Payment creation count
* Successful transactions
* Failed transactions
* Retry count
* Processing duration
* Gateway latency

These metrics are scraped by Prometheus and visualized using Grafana dashboards.

---

## Future Improvements

Potential production enhancements include:

* Multiple payment gateway providers
* Webhook processing
* Circuit breaker implementation
* Distributed locking for retries
* Redis caching
* Dead Letter Queue (DLQ)
* API rate limiting
* Email notifications
* Kubernetes deployment
* CI/CD pipeline
* Structured logging
* OpenTelemetry tracing
* Multi-currency support
* Role-based access control
* Payment analytics dashboard

---

## What This Project Demonstrates

This project demonstrates practical backend engineering concepts including:

* REST API development
* Clean architecture principles
* Service-oriented design
* Idempotent payment processing
* Background job execution
* Scheduling with Celery Beat
* Retry mechanisms with exponential backoff
* API documentation
* Monitoring and observability
* Containerized development
* Production-style backend design

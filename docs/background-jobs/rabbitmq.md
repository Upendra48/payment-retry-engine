# RabbitMQ

## Overview

RabbitMQ is an open-source message broker that enables different parts of an application to communicate asynchronously. Instead of one component directly calling another, messages are placed into a queue. Consumers then retrieve and process those messages independently.

In this project, RabbitMQ acts as the communication bridge between Django, Celery Beat, and Celery Workers. Whenever Django or Celery Beat wants a background task to be executed, it sends a message to RabbitMQ. Celery Workers continuously listen to RabbitMQ and execute those tasks.

---

# Why Do We Need RabbitMQ?

Imagine a payment fails and needs to be retried.

Without RabbitMQ:

```text
Django

↓

Directly execute retry

↓

User waits
```

The application becomes slow because Django has to perform all the work itself.

With RabbitMQ:

```text
Django

↓

Queue Task

↓

RabbitMQ

↓

Worker

↓

Retry Payment
```

The API returns immediately while the worker performs the retry in the background.

---

# What Problem Does RabbitMQ Solve?

RabbitMQ decouples task producers from task consumers.

Instead of:

```text
Producer

↓

Consumer
```

we get:

```text
Producer

↓

RabbitMQ Queue

↓

Consumer
```

The producer doesn't need to know:

* Which worker will execute the task.
* When the task will execute.
* How many workers exist.
* Whether workers are currently busy.

RabbitMQ handles all of that automatically.

---

# What Is a Message Broker?

A message broker is software that receives, stores, and forwards messages between applications.

In this project:

```text
Django

↓

RabbitMQ

↓

Celery Worker
```

RabbitMQ guarantees that queued tasks remain available until a worker processes them.

---

# Core Components

## Producer

A producer creates messages.

Examples in this project:

* Django API
* Celery Beat

Both send tasks to RabbitMQ.

---

## Queue

A queue temporarily stores messages.

Example:

```text
retry_payment_task

retry_payment_task

retry_payment_task

retry_payment_task
```

Messages remain in the queue until a worker consumes them.

---

## Consumer

Consumers retrieve messages from the queue.

In this project:

```text
Celery Worker
```

is the consumer.

---

## Message

A message contains information about the task.

Example:

```text
Task:
apps.payments.tasks.retry_payment_task

Arguments:
payment_id
```

RabbitMQ doesn't execute the task.

It only transports this message.

---

# How RabbitMQ Works

```text
Django API

↓

retry_payment_task.delay(payment_id)

↓

RabbitMQ Queue

↓

Celery Worker

↓

retry_payment_task()

↓

PaymentService.retry_payment()
```

The worker polls RabbitMQ continuously and executes tasks as soon as they become available.

---

# RabbitMQ in This Project

This project contains three task producers.

## Django API

Queues retry tasks manually.

Example:

```python
retry_payment_task.delay(payment.id)
```

---

## Celery Beat

Every minute:

```python
retry_due_payments()
```

queues retry tasks for payments whose retry time has arrived.

---

## Celery Worker

Consumes queued tasks and executes them.

---

# Complete Architecture

```text
                HTTP Request

                      │

                      ▼

               Django REST API

                      │

        retry_payment_task.delay()

                      │

                      ▼

                 RabbitMQ Queue

          ┌───────────┴───────────┐

          ▼                       ▼

    Worker 1                 Worker 2

          │                       │

          └───────────┬───────────┘

                      ▼

             PaymentService

                      ▼

                PostgreSQL
```

Notice that Django never communicates directly with the worker.

Everything goes through RabbitMQ.

---

# Why RabbitMQ Instead of Direct Function Calls?

Suppose 500 payment retries are needed simultaneously.

Without RabbitMQ:

```text
Django

↓

500 retry calls

↓

Very slow API
```

With RabbitMQ:

```text
Django

↓

500 queued messages

↓

RabbitMQ

↓

Workers process gradually
```

The API remains responsive regardless of queue size.

---

# Why RabbitMQ Instead of Redis?

Both RabbitMQ and Redis can act as Celery brokers.

| RabbitMQ                        | Redis                         |
| ------------------------------- | ----------------------------- |
| Purpose-built message broker    | In-memory data store          |
| Strong delivery guarantees      | Simpler configuration         |
| Advanced routing                | Faster for lightweight queues |
| Durable queues                  | Often used for caching        |
| Better for enterprise messaging | Better for simple workloads   |

RabbitMQ was chosen because this project focuses on reliable background task processing, which closely resembles production payment systems.

---

# Docker Configuration

RabbitMQ is started using Docker Compose.

```yaml
rabbitmq:
  image: rabbitmq:3-management

  ports:
    - "5672:5672"
    - "15672:15672"

  environment:
    RABBITMQ_DEFAULT_USER: guest
    RABBITMQ_DEFAULT_PASS: guest
```

---

# Ports

## 5672

AMQP protocol.

Celery communicates with RabbitMQ through this port.

---

## 15672

RabbitMQ Management Dashboard.

Open:

```text
http://localhost:15672
```

Default credentials:

```text
Username: guest

Password: guest
```

The dashboard allows you to:

* View queues
* Monitor connections
* Inspect exchanges
* Observe consumers
* Check message rates

---

# Django Configuration

In Django settings:

```python
CELERY_BROKER_URL = "amqp://guest:guest@rabbitmq:5672//"
```

This tells Celery where RabbitMQ is running.

---

# Task Flow in This Project

## Step 1

Payment fails.

```text
Gateway Timeout
```

---

## Step 2

Payment becomes:

```text
RETRYING
```

---

## Step 3

Celery Beat runs.

---

## Step 4

Beat queues:

```python
retry_payment_task.delay(payment.id)
```

---

## Step 5

RabbitMQ stores the task.

---

## Step 6

Celery Worker receives the task.

---

## Step 7

Worker executes:

```python
PaymentService.retry_payment()
```

---

## Step 8

Database is updated.

---

# Advantages

* Asynchronous processing
* Reliable message delivery
* Decouples components
* Highly scalable
* Multiple workers supported
* Fault tolerant
* Production ready

---

# Best Practices

* Keep RabbitMQ dedicated to messaging.
* Store business data in PostgreSQL.
* Make background tasks idempotent.
* Monitor queue size.
* Use health checks in Docker.
* Restart workers after major code changes.

---

# Common Errors

## Connection Refused

RabbitMQ is not running.

Verify:

```bash
docker compose ps
```

---

## Worker Doesn't Receive Tasks

Check worker logs.

```bash
docker compose logs worker
```

---

## Broker URL Incorrect

Verify:

```python
CELERY_BROKER_URL
```

points to:

```text
rabbitmq:5672
```

inside Docker.

---

## Queue Never Empties

Possible causes:

* Worker crashed.
* Worker unavailable.
* Task failure loop.

Inspect the RabbitMQ Management Dashboard.

---

# Monitoring RabbitMQ

Useful commands:

View containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs rabbitmq
```

Open management dashboard:

```text
http://localhost:15672
```

---

# Interview Questions

## What is RabbitMQ?

RabbitMQ is a message broker that stores and forwards messages between producers and consumers.

---

## Why use RabbitMQ?

It enables asynchronous communication, improves scalability, and decouples application components.

---

## Does RabbitMQ execute tasks?

No.

RabbitMQ only stores and forwards messages.

Workers execute the actual business logic.

---

## How does RabbitMQ work with Celery?

1. Django creates a task.
2. Celery serializes it.
3. RabbitMQ stores it.
4. Workers consume it.
5. The worker executes the task.

---

## Why use RabbitMQ in a payment retry engine?

Payment retries should not block API requests.

RabbitMQ allows retry tasks to execute asynchronously while ensuring reliable message delivery.

---

## What happens if the worker stops?

Tasks remain in RabbitMQ until a worker becomes available again.

This prevents tasks from being lost.

---

## What happens if RabbitMQ stops?

New tasks cannot be queued until RabbitMQ is available again.

Existing queued tasks remain unavailable until the broker is restored.

---

# Revision Notes

* RabbitMQ is a message broker.
* Django and Celery Beat produce tasks.
* Celery Workers consume tasks.
* RabbitMQ stores messages until workers process them.
* The payment retry engine uses RabbitMQ to queue retry tasks.
* RabbitMQ improves scalability, reliability, and responsiveness.
* Port **5672** is used for messaging.
* Port **15672** provides the management dashboard.
* RabbitMQ does not execute tasks; it only transports them.

# Celery

## Overview

Celery is a distributed task queue for Python that allows applications to execute time-consuming or background tasks asynchronously. Instead of making users wait for a task to complete, Celery moves that work into a separate worker process, allowing the application to respond immediately.

Celery is widely used in production systems for handling tasks such as sending emails, processing payments, generating reports, resizing images, and executing scheduled jobs.

In this project, Celery is responsible for executing payment retries in the background without blocking the API.

---

# Why Do We Need Celery?

Imagine a payment request takes 30 seconds because the payment gateway is slow.

Without Celery:

```text
Client
   │
   ▼
Django API
   │
   ▼
Payment Gateway (30 seconds)
   │
   ▼
Response
```

The user must wait until the gateway responds.

With Celery:

```text
Client
   │
   ▼
Django API
   │
   ├────────────► Celery Queue
   │                  │
   │                  ▼
Immediate Response   Worker
                         │
                         ▼
                  Payment Gateway
```

The API responds quickly while the worker processes the payment independently.

---

# What Problems Does Celery Solve?

Celery helps when tasks:

* Take a long time to complete.
* Can be processed later.
* Should not block API responses.
* Need retries after failure.
* Need scheduled execution.
* Must run independently of user requests.

Examples:

* Sending emails
* Processing payments
* Image processing
* Video encoding
* Report generation
* Notifications
* Scheduled cleanup jobs

---

# Core Components

## Django Application

Creates tasks.

Example:

```text
Payment API

↓

Create Payment

↓

Queue Task
```

---

## Message Broker

Stores queued tasks until workers process them.

In this project:

```text
RabbitMQ
```

acts as the message broker.

---

## Celery Worker

A separate process that continuously waits for new tasks.

```text
Queue

↓

Worker

↓

Execute Task
```

Multiple workers can run simultaneously to process many tasks concurrently.

---

## Result Backend (Optional)

Stores task results.

Common options include:

* Redis
* Database
* RabbitMQ
* RPC

This project does not rely on task results because payment status is persisted in PostgreSQL.

---

# Celery Architecture

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
                    │
                    ▼
             Celery Worker
                    │
                    ▼
          PaymentService.retry_payment()
                    │
                    ▼
               PostgreSQL
```

---

# Installing Celery

Install Celery.

```bash
pip install celery
```

For RabbitMQ support:

```bash
pip install amqp
```

---

# Django Configuration

Create a Celery application.

```python
config/celery.py
```

```python
import os

from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

app = Celery("config")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY",
)

app.autodiscover_tasks()
```

---

Import Celery when Django starts.

```python
config/__init__.py
```

```python
from .celery import app as celery_app

__all__ = ("celery_app",)
```

---

Configure Django settings.

```python
CELERY_BROKER_URL = ...

CELERY_RESULT_BACKEND = ...

CELERY_ACCEPT_CONTENT = ["json"]

CELERY_TASK_SERIALIZER = "json"

CELERY_RESULT_SERIALIZER = "json"
```

---

# Creating a Task

Celery tasks are regular Python functions decorated with `@shared_task`.

Example:

```python
from celery import shared_task

@shared_task
def send_email():
    ...
```

Tasks are executed by workers rather than Django itself.

---

# Running Workers

Start a worker.

```bash
celery -A config worker -l info
```

Inside Docker:

```bash
docker compose up worker
```

---

# Calling Tasks

Instead of calling a function directly:

```python
retry_payment(payment)
```

queue the task:

```python
retry_payment_task.delay(payment.id)
```

`.delay()` sends a message to RabbitMQ.

The worker executes the function later.

---

# Task Lifecycle

```text
Task Created

↓

RabbitMQ Queue

↓

Worker Receives Task

↓

Task Executes

↓

Database Updated
```

---

# How Celery Is Used In This Project

## Payment Retry

When a payment gateway fails with a retryable error:

```text
TIMEOUT

↓

Payment Status

↓

RETRYING
```

The payment is not retried immediately.

Instead:

* retry_count increases
* next_retry_at is calculated
* payment status becomes RETRYING

Later:

Celery Beat schedules the retry.

Celery Worker executes:

```python
retry_payment_task(payment_id)
```

The worker:

* Loads the payment.
* Calls `PaymentService.retry_payment()`.
* Processes the gateway again.
* Updates payment status.

---

## Scheduled Retries

Celery does not check retry times itself.

Another component (Celery Beat) periodically executes:

```python
retry_due_payments()
```

This function:

* Finds payments waiting for retry.
* Queues a retry task for each payment.

Workers then process those queued tasks.

---

# Advantages

* Non-blocking API
* Scalable
* Reliable
* Supports retries
* Supports scheduling
* Multiple workers
* Fault tolerant
* Production ready

---

# Best Practices

* Keep tasks small and focused.
* Store important state in the database.
* Make tasks idempotent whenever possible.
* Avoid long-running database transactions.
* Log task failures.
* Use retries only for transient errors.
* Monitor workers in production.

---

# Common Errors

## Worker Not Receiving Tasks

Verify:

```bash
docker compose logs worker
```

---

## Task Not Registered

Check:

```bash
celery -A config inspect registered
```

Expected:

```text
apps.payments.tasks.retry_payment_task
```

---

## Broker Connection Error

Verify RabbitMQ is running.

```bash
docker compose ps
```

---

## Circular Imports

Avoid importing tasks inside modules that already import those modules.

Instead:

* Keep tasks lightweight.
* Delegate business logic to service classes.

---

## Worker Doesn't Pick Up Code Changes

Restart the worker.

```bash
docker compose restart worker
```

---

# Interview Questions

## What is Celery?

Celery is a distributed task queue that enables asynchronous and scheduled execution of background jobs.

---

## Why use Celery?

To execute time-consuming tasks without blocking the application's request-response cycle.

---

## Why not use Python threads?

Threads run inside the web process and are lost if the server restarts. Celery workers are separate processes that communicate through a message broker, making them more reliable and scalable.

---

## What is a Message Broker?

A message broker temporarily stores tasks until workers are available to process them.

Examples:

* RabbitMQ
* Redis

---

## What does `.delay()` do?

`.delay()` serializes the task and sends it to the message broker for asynchronous execution.

---

## Does Celery execute tasks immediately?

No.

Celery places tasks into the broker queue.

Workers execute them independently.

---

## Why did this project use Celery?

The payment retry engine must retry failed payments asynchronously without blocking user requests.

Celery allows retries to happen automatically in the background while keeping the API responsive.

---

# Revision Notes

* Celery executes asynchronous background tasks.
* Django creates tasks.
* RabbitMQ stores queued tasks.
* Workers consume and execute tasks.
* Tasks are created using `@shared_task`.
* `.delay()` sends a task to the broker.
* Workers process payment retries.
* Business logic remains inside `PaymentService`, while Celery is responsible only for task execution.

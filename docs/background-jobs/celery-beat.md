# Celery Beat

## Overview

Celery Beat is a scheduler for Celery that periodically sends tasks to the message broker based on a predefined schedule.

Unlike a Celery Worker, which executes tasks, Celery Beat only schedules them. Once a scheduled task is due, Beat places it into the message broker (RabbitMQ in this project), and one of the Celery workers executes it.

In this project, Celery Beat is responsible for periodically checking whether any payments are ready to be retried.

---

# Why Do We Need Celery Beat?

Imagine a payment fails at **10:00 AM**, and according to the retry policy it should be retried after **5 minutes**.

Without Celery Beat:

* Someone would have to manually trigger the retry.
* Django would need an infinite background loop.
* The API would become responsible for scheduling background work.

These approaches are unreliable and difficult to maintain.

Celery Beat solves this by checking for scheduled work automatically.

---

# What Problem Does It Solve?

Celery Workers execute tasks.

Celery Beat decides **when** those tasks should be executed.

Examples of scheduled jobs:

* Retry failed payments
* Send daily reports
* Clear expired sessions
* Generate invoices
* Database cleanup
* Weekly backups
* Send reminder emails

---

# Celery vs Celery Beat

| Celery Worker            | Celery Beat                        |
| ------------------------ | ---------------------------------- |
| Executes tasks           | Schedules tasks                    |
| Listens to RabbitMQ      | Periodically checks schedules      |
| Processes jobs           | Creates jobs                       |
| Multiple workers can run | Usually only one Beat process runs |

Think of it like this:

```text
Celery Beat = Alarm Clock

Celery Worker = Employee

RabbitMQ = Task Inbox
```

The alarm clock tells the employee it's time to work.

---

# How Celery Beat Works

```text
Every Minute

        │
        ▼

Celery Beat

        │

Checks Schedule

        │

Task Due?

        │

      Yes

        │

        ▼

RabbitMQ Queue

        │

        ▼

Celery Worker

        │

        ▼

Execute Task
```

Beat never executes the task itself.

Its only responsibility is placing scheduled tasks into RabbitMQ.

---

# Architecture in This Project

```text
                    Payment

                        │

                        ▼

              status = RETRYING

                        │

         next_retry_at = 10:05 AM

                        │

                        ▼

                Celery Beat

         Runs Every Minute

                        │

                        ▼

         retry_due_payments()

                        │

Find all payments whose

next_retry_at <= current time

                        │

                        ▼

retry_payment_task.delay()

                        │

                        ▼

RabbitMQ

                        │

                        ▼

Celery Worker

                        │

                        ▼

PaymentService.retry_payment()
```

---

# Installation

Celery Beat is included with Celery.

No additional package is required.

---

# Configuration

Configure scheduled tasks inside Django settings.

Example:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "retry-due-payments": {
        "task": "apps.payments.tasks.retry_due_payments",
        "schedule": crontab(minute="*"),
    },
}
```

This means:

Every minute, Celery Beat will enqueue the `retry_due_payments` task.

---

# Scheduling Options

## Every Minute

```python
crontab(minute="*")
```

---

## Every Five Minutes

```python
crontab(minute="*/5")
```

---

## Every Hour

```python
crontab(hour="*")
```

---

## Every Day at Midnight

```python
crontab(hour=0, minute=0)
```

---

## Every Monday

```python
crontab(day_of_week=1)
```

---

# Running Celery Beat

Start Beat manually:

```bash
celery -A config beat -l info
```

Inside Docker:

```bash
docker compose up beat
```

The Beat container continuously monitors the configured schedule.

---

# How We Used Celery Beat

Our payment retry engine supports automatic retries.

When a payment fails with a retryable error:

```text
Gateway Timeout

↓

Retry Policy

↓

Payment Status = RETRYING

↓

next_retry_at = Future Time
```

Instead of retrying immediately, the payment waits until the scheduled retry time.

Every minute, Celery Beat executes:

```python
retry_due_payments()
```

That task:

* Queries PostgreSQL for payments whose retry time has arrived.
* Sends each payment to RabbitMQ.
* Workers process those retry tasks.

This makes retries fully automatic.

---

# The Retry Pipeline

```text
Payment Created

        │

        ▼

Gateway Failure

        │

        ▼

Retry Policy

        │

        ▼

status = RETRYING

next_retry_at = Future Time

        │

        ▼

Celery Beat

        │

        ▼

retry_due_payments()

        │

        ▼

RabbitMQ

        │

        ▼

Celery Worker

        │

        ▼

retry_payment_task()

        │

        ▼

PaymentService

        │

        ▼

Update Payment Status
```

---

# Why Use Celery Beat Instead of a While Loop?

A background loop inside Django would:

* Waste CPU resources.
* Be difficult to scale.
* Stop when Django restarts.
* Be hard to monitor.

Celery Beat provides:

* Reliable scheduling.
* Production-grade implementation.
* Easy configuration.
* Better scalability.
* Integration with Celery workers.

---

# Best Practices

* Run only one Beat instance unless using distributed scheduling.
* Keep scheduled tasks lightweight.
* Move business logic into service classes.
* Schedule tasks frequently enough without overloading the system.
* Store application state in the database instead of memory.

---

# Common Errors

## Beat Running but Nothing Happens

Possible causes:

* Worker is not running.
* RabbitMQ is unavailable.
* Scheduled task name is incorrect.

Verify:

```bash
docker compose logs beat
```

---

## Task Never Executes

Check:

```python
CELERY_BEAT_SCHEDULE
```

Ensure the task path matches the actual task.

Example:

```python
apps.payments.tasks.retry_due_payments
```

---

## Worker Doesn't Receive Tasks

Inspect registered tasks:

```bash
celery -A config inspect registered
```

---

## RabbitMQ Connection Error

Verify:

```bash
docker compose ps
```

RabbitMQ should be running and healthy.

---

# Docker Setup in This Project

A dedicated Beat container is used.

```yaml
beat:
  build: .

  command: celery -A config beat -l info

  depends_on:
    rabbitmq:
      condition: service_healthy

  env_file:
    - .env.example

  volumes:
    - ./src:/app/src
```

Keeping Beat separate from workers follows production best practices.

---

# Interview Questions

## What is Celery Beat?

Celery Beat is a scheduler that periodically sends tasks to the message broker according to a configured schedule.

---

## Does Celery Beat execute tasks?

No.

It only schedules tasks.

Workers execute them.

---

## Why is Celery Beat needed?

Some tasks must execute at specific times or intervals, such as payment retries or daily reports.

Beat automates that scheduling.

---

## Can multiple Beat instances run?

Typically only one Beat instance should run.

Running multiple Beat schedulers without coordination can cause duplicate scheduled tasks.

---

## How did you use Celery Beat in your project?

Celery Beat runs every minute and queues retry tasks for payments whose `next_retry_at` timestamp has been reached. Celery Workers then execute those retries asynchronously.

---

## What happens if Beat stops?

New scheduled tasks will no longer be added to RabbitMQ.

Existing queued tasks will still be processed by workers.

---

# Revision Notes

* Celery Beat schedules tasks.
* Celery Workers execute tasks.
* RabbitMQ stores scheduled tasks.
* Beat never performs business logic.
* The retry engine uses Beat to automatically retry payments.
* `retry_due_payments()` runs every minute.
* Payments are retried only when `next_retry_at` has been reached.
* Beat and Workers run as separate Docker containers.

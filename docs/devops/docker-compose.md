# Docker Compose

## Overview

Docker Compose is a tool for defining and running multi-container Docker applications.

Instead of starting each container manually, Docker Compose allows you to describe the entire application stack in a single `docker-compose.yml` file.

With one command, Docker Compose can:

* Build images
* Create containers
* Connect containers through a shared network
* Mount volumes
* Configure environment variables
* Manage dependencies
* Start and stop the entire application stack

In this project, Docker Compose orchestrates the complete Payment Retry Engine infrastructure, including the web application, PostgreSQL, RabbitMQ, Celery workers, Celery Beat, Prometheus, and Grafana.

---

# Why Do We Need Docker Compose?

Modern backend applications rarely consist of a single service.

Our project requires:

* Django
* PostgreSQL
* RabbitMQ
* Celery Worker
* Celery Beat
* Prometheus
* Grafana

Without Docker Compose, each service would need to be started manually.

Example:

```text
Start PostgreSQL

↓

Start RabbitMQ

↓

Start Django

↓

Start Celery Worker

↓

Start Celery Beat

↓

Start Prometheus

↓

Start Grafana
```

Managing all of these manually quickly becomes difficult.

Docker Compose automates the process.

---

# What Problem Does Docker Compose Solve?

Without Docker Compose:

* Multiple terminal windows
* Manual networking
* Manual environment configuration
* Manual startup order
* Difficult onboarding

With Docker Compose:

```text
docker compose up
```

Everything starts automatically.

---

# Architecture

```text
                     Docker Compose

                           │

        ┌──────────────────┼──────────────────┐

        ▼                  ▼                  ▼

     PostgreSQL        RabbitMQ         Prometheus

        ▲                  ▲                  ▲

        │                  │                  │

        │             Celery Worker           │

        │                  ▲                  │

        │                  │                  │

        │             Celery Beat             │

        │                  ▲                  │

        └────────────── Django API ───────────┘

                           │

                           ▼

                       Grafana
```

Every service runs inside its own isolated container.

---

# Services Used in This Project

| Service    | Purpose               |
| ---------- | --------------------- |
| web        | Django REST API       |
| db         | PostgreSQL database   |
| rabbitmq   | Message broker        |
| worker     | Executes Celery tasks |
| beat       | Schedules retry tasks |
| prometheus | Collects metrics      |
| grafana    | Visualizes metrics    |

Each service has a single responsibility.

---

# Docker Network

Docker Compose automatically creates a private network.

Every container can communicate using the service name.

Example:

```text
web

↓

db:5432
```

instead of

```text
localhost:5432
```

Another example:

```text
worker

↓

rabbitmq:5672
```

Prometheus:

```text
prometheus

↓

web:8000/metrics
```

This built-in DNS resolution is one of Docker Compose's most useful features.

---

# Project Structure

```text
project/

├── docker-compose.yml

├── Dockerfile

├── prometheus.yml

├── src/

└── .env.example
```

The `docker-compose.yml` file defines the entire infrastructure.

---

# Web Service

The web service runs Django.

Example:

```yaml
web:
  build: .

  ports:
    - "8000:8000"

  volumes:
    - ./src:/app/src

  env_file:
    - .env.example
```

Responsibilities:

* Run migrations
* Start Django
* Expose the REST API
* Expose `/metrics`

---

# Database Service

The PostgreSQL service stores application data.

```yaml
db:
  image: postgres:16-alpine
```

Responsibilities:

* Store payments
* Store payment attempts
* Store idempotency keys

Persistent storage is achieved using Docker volumes.

---

# RabbitMQ Service

RabbitMQ transports asynchronous tasks.

```yaml
rabbitmq:
  image: rabbitmq:3-management
```

Responsibilities:

* Queue retry tasks
* Deliver tasks to Celery workers

---

# Celery Worker

The worker executes background jobs.

```yaml
worker:
  command: celery -A config worker -l info
```

Responsibilities:

* Retry failed payments
* Execute asynchronous tasks

---

# Celery Beat

Beat schedules recurring jobs.

```yaml
beat:
  command: celery -A config beat -l info
```

Responsibilities:

* Run `retry_due_payments`
* Queue retry jobs every minute

---

# Prometheus

Prometheus collects metrics.

```yaml
prometheus:
  image: prom/prometheus:latest
```

Responsibilities:

* Scrape `/metrics`
* Store time-series data

---

# Grafana

Grafana visualizes metrics.

```yaml
grafana:
  image: grafana/grafana:latest
```

Responsibilities:

* Query Prometheus
* Display dashboards

---

# Volumes

Docker volumes persist data even when containers are recreated.

Example:

```yaml
volumes:

  postgres_data:

  grafana_data:
```

Benefits:

* Database survives container recreation
* Grafana dashboards persist
* No data loss during development

---

# Environment Variables

Sensitive configuration is stored in:

```text
.env.example
```

Examples:

* Database credentials
* Secret key
* RabbitMQ URL
* Celery configuration

This keeps configuration separate from source code.

---

# Service Dependencies

Some services depend on others.

Example:

```yaml
depends_on:

  db:

    condition: service_healthy
```

This ensures:

* PostgreSQL starts first.
* Django waits until PostgreSQL is ready.

Similarly:

* Worker waits for RabbitMQ.
* Beat waits for RabbitMQ.
* Prometheus waits for the web service.
* Grafana waits for Prometheus.

---

# Useful Commands

Start all services:

```bash
docker compose up
```

Run in background:

```bash
docker compose up -d
```

Stop services:

```bash
docker compose down
```

Rebuild images:

```bash
docker compose up --build
```

View logs:

```bash
docker compose logs
```

View logs for one service:

```bash
docker compose logs worker
```

List running containers:

```bash
docker compose ps
```

Execute a shell inside a container:

```bash
docker compose exec web bash
```

Restart a service:

```bash
docker compose restart worker
```

---

# Container Communication

One advantage of Docker Compose is automatic networking.

Example:

Django connects to PostgreSQL using:

```text
db
```

instead of

```text
localhost
```

RabbitMQ:

```text
rabbitmq
```

Prometheus:

```text
web:8000
```

No manual IP management is required.

---

# How We Used Docker Compose

The entire Payment Retry Engine is started with a single command.

```bash
docker compose up
```

This launches:

* Django
* PostgreSQL
* RabbitMQ
* Celery Worker
* Celery Beat
* Prometheus
* Grafana

All services automatically connect through Docker's internal network.

---

# Advantages

* One command to start the system
* Consistent development environment
* Automatic networking
* Easy onboarding
* Service isolation
* Persistent storage
* Easy scaling
* Production-like local environment

---

# Common Issues

## Container Cannot Connect

Verify:

* Service name
* Docker network
* Container status

Never use `localhost` when one container needs to reach another. Use the service name instead (for example, `db`, `rabbitmq`, or `web`).

---

## Volume Problems

If data behaves unexpectedly:

```bash
docker compose down -v
```

removes containers **and** named volumes. Use this carefully because it deletes persisted data.

---

## Image Not Updating

Rebuild:

```bash
docker compose up --build
```

---

## Service Starts Too Early

Use:

```yaml
depends_on
```

combined with health checks where appropriate.

---

# Interview Questions

## What is Docker Compose?

Docker Compose is a tool for defining and running multi-container Docker applications using a single YAML configuration file.

---

## Why use Docker Compose instead of individual Docker commands?

It simplifies container orchestration by managing networking, volumes, environment variables, dependencies, and startup order in one place.

---

## How do containers communicate in Docker Compose?

Containers communicate over an automatically created network using **service names** as hostnames.

For example:

* `db`
* `rabbitmq`
* `web`

---

## What is the difference between a Docker image and a Docker Compose service?

An image is a packaged application template.

A service is a running container (or set of containers) created from an image with specific configuration.

---

## What services does this project run?

* Django
* PostgreSQL
* RabbitMQ
* Celery Worker
* Celery Beat
* Prometheus
* Grafana

---

## Why use named volumes?

Named volumes persist important data independently of container lifecycles, allowing databases and dashboards to survive container recreation.

---

# Revision Notes

* Docker Compose orchestrates multi-container applications.
* This project runs seven coordinated services using a single `docker-compose.yml` file.
* Containers communicate through Docker's internal network using service names.
* Named volumes persist PostgreSQL and Grafana data.
* `depends_on` and health checks help coordinate startup order.
* One command (`docker compose up`) launches the complete Payment Retry Engine environment.

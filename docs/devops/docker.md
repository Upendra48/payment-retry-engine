# Docker

## Overview

Docker is an open-source containerization platform that allows applications and their dependencies to be packaged into lightweight, portable, and isolated environments called **containers**.

A Docker container contains everything required to run an application:

* Source code
* Runtime
* Libraries
* Dependencies
* System tools
* Configuration

This ensures the application behaves the same regardless of where it is deployed.

In this project, Docker is used to package the Django Payment Retry Engine into a reproducible environment that can run consistently on any machine.

---

# Why Do We Need Docker?

One of the biggest problems in software development is environment inconsistency.

Example:

```text
Developer A

Python 3.12

PostgreSQL 16

Works Perfectly

────────────

Developer B

Python 3.10

PostgreSQL 15

Application Fails
```

Different operating systems, Python versions, and installed packages often lead to unexpected bugs.

Docker solves this by packaging the entire runtime environment together with the application.

---

# What Problem Does Docker Solve?

Without Docker:

* Manual dependency installation
* Different operating systems
* Different Python versions
* Different package versions
* "Works on my machine" problems

With Docker:

```text
Application

↓

Docker Image

↓

Docker Container

↓

Runs Anywhere
```

Every developer runs the same environment.

---

# Virtual Machines vs Docker

Traditional deployment uses virtual machines.

```text
Hardware

↓

Host Operating System

↓

Hypervisor

↓

Virtual Machine

↓

Guest Operating System

↓

Application
```

Each VM includes an entire operating system.

This consumes significant memory and storage.

Docker is different.

```text
Hardware

↓

Host Operating System

↓

Docker Engine

↓

Containers

↓

Application
```

Containers share the host operating system kernel, making them much lighter and faster than virtual machines.

---

# Docker Architecture

Docker consists of several core components.

```text
Docker CLI

↓

Docker Engine

↓

Images

↓

Containers
```

Each plays a different role.

---

# Docker Image

A Docker image is a read-only blueprint for creating containers.

Think of it like a class in object-oriented programming.

Example:

```text
Image

↓

Python 3.12

Django

Application Code

Dependencies
```

Images are immutable.

Whenever the application changes, a new image is built.

---

# Docker Container

A container is a running instance of an image.

Think of it like an object created from a class.

```text
Docker Image

↓

docker run

↓

Running Container
```

Containers are isolated from one another.

Each has its own:

* Filesystem
* Processes
* Network interfaces
* Environment variables

---

# Dockerfile

A Dockerfile contains the instructions used to build a Docker image.

Typical structure:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver"]
```

Each instruction creates a new image layer.

---

# Image Layers

Docker images are built in layers.

Example:

```text
Base Python Image

↓

Install Dependencies

↓

Copy Source Code

↓

Configure Startup

↓

Final Image
```

Docker caches unchanged layers, making rebuilds much faster.

---

# Build Process

The build process converts a Dockerfile into an image.

```bash
docker build -t payment-retry-engine .
```

Result:

```text
Dockerfile

↓

Docker Image

↓

Ready to Run
```

---

# Running a Container

Run the image:

```bash
docker run payment-retry-engine
```

Docker creates a new container from the image.

---

# Docker Volumes

Containers are temporary.

If a container is deleted, its internal filesystem is also deleted.

Volumes solve this problem.

```text
Container

↓

Volume

↓

Persistent Data
```

In this project, Docker volumes store:

* PostgreSQL database files
* Grafana dashboards

This ensures data survives container recreation.

---

# Docker Networking

Docker automatically creates isolated networks.

Containers communicate using hostnames.

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

The same applies to:

* RabbitMQ
* Prometheus
* Grafana

---

# Environment Variables

Sensitive values should never be hardcoded.

Instead, Docker loads configuration from environment variables.

Example:

```text
SECRET_KEY

DB_HOST

DB_NAME

CELERY_BROKER_URL
```

This project stores them in:

```text
.env.example
```

---

# Docker Commands

Build an image:

```bash
docker build -t payment-retry-engine .
```

Run a container:

```bash
docker run payment-retry-engine
```

List images:

```bash
docker images
```

List running containers:

```bash
docker ps
```

List all containers:

```bash
docker ps -a
```

Stop a container:

```bash
docker stop <container_id>
```

Remove a container:

```bash
docker rm <container_id>
```

Remove an image:

```bash
docker rmi <image_id>
```

View logs:

```bash
docker logs <container_id>
```

Execute a shell:

```bash
docker exec -it <container_id> bash
```

---

# Docker in This Project

Docker packages the Django backend together with all required dependencies.

The Docker image includes:

* Python 3.12
* Django
* Django REST Framework
* Celery
* RabbitMQ client libraries
* PostgreSQL driver
* Prometheus client
* Application source code

This guarantees a consistent execution environment across development and deployment.

---

# Relationship with Docker Compose

Docker and Docker Compose are related but serve different purposes.

| Docker                                | Docker Compose                          |
| ------------------------------------- | --------------------------------------- |
| Builds and runs individual containers | Orchestrates multiple containers        |
| Uses a Dockerfile                     | Uses `docker-compose.yml`               |
| Focuses on a single application       | Focuses on the entire application stack |

In this project:

* Docker creates the application image.
* Docker Compose starts and connects all required services.

---

# Advantages

* Consistent environments
* Fast startup
* Lightweight containers
* Easy deployment
* Dependency isolation
* Portable across operating systems
* Excellent cloud support
* Simplified onboarding

---

# Common Issues

## Build Fails

Possible causes:

* Incorrect Dockerfile
* Missing dependencies
* Invalid file paths

Rebuild after fixing:

```bash
docker build -t payment-retry-engine .
```

---

## Container Exits Immediately

Check the logs:

```bash
docker logs <container_id>
```

---

## Cannot Connect to Another Service

Inside Docker, use service names instead of `localhost`.

Example:

```text
db
```

instead of

```text
localhost
```

---

## Changes Not Reflected

If source code is copied during image build, rebuild the image.

If volumes are mounted, verify the mount path is correct.

---

# Best Practices

* Use official base images.
* Keep images as small as possible.
* Store secrets in environment variables.
* Use multi-stage builds for production.
* Cache dependency installation layers.
* Never store persistent data inside containers.
* Rebuild images after dependency changes.

---

# Interview Questions

## What is Docker?

Docker is a containerization platform that packages applications and their dependencies into portable containers.

---

## What is the difference between an image and a container?

An image is a blueprint.

A container is a running instance of that image.

---

## Why use Docker?

Docker eliminates environment inconsistencies, simplifies deployment, and ensures applications run the same everywhere.

---

## What is a Dockerfile?

A Dockerfile contains the instructions used to build a Docker image.

---

## Why use Docker volumes?

Volumes persist data independently of the container lifecycle, preventing data loss when containers are recreated.

---

## How does Docker differ from virtual machines?

Containers share the host operating system kernel, making them significantly lighter and faster than virtual machines, which each include a full guest operating system.

---

## How is Docker used in this project?

Docker packages the Django Payment Retry Engine and its dependencies into a portable image. Docker Compose then uses that image to run the web service alongside PostgreSQL, RabbitMQ, Celery, Prometheus, and Grafana.

---

# Revision Notes

* Docker is a containerization platform.
* Images are blueprints; containers are running instances.
* Dockerfile defines how images are built.
* Volumes provide persistent storage.
* Docker networking enables container-to-container communication using service names.
* Environment variables separate configuration from application code.
* This project uses Docker to package the Django backend into a reproducible, portable environment that works consistently across development and deployment.

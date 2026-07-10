# PostgreSQL

## Overview

PostgreSQL is a powerful, open-source Relational Database Management System (RDBMS) known for its reliability, extensibility, ACID compliance, and rich SQL support. It is widely used in production systems ranging from small web applications to enterprise-scale platforms.

Unlike lightweight databases such as SQLite, PostgreSQL is designed to handle concurrent users, complex queries, large datasets, and production workloads efficiently.

In this project, PostgreSQL serves as the primary database for storing payment information, retry history, idempotency records, and payment attempts.

---

# Why PostgreSQL?

A payment processing system requires a database that guarantees data consistency and reliability.

For example:

* A payment should never be created twice.
* A retry attempt should never overwrite another retry.
* Multiple users should be able to perform transactions simultaneously.
* Database operations should remain consistent even if the application crashes.

PostgreSQL provides these guarantees through transactions, constraints, indexing, and ACID compliance.

---

# Why PostgreSQL Instead of SQLite?

| SQLite                    | PostgreSQL                                  |
| ------------------------- | ------------------------------------------- |
| File-based database       | Client-server database                      |
| Best for development      | Production ready                            |
| Limited concurrent writes | Handles thousands of concurrent connections |
| Minimal configuration     | Highly configurable                         |
| Limited scalability       | Highly scalable                             |

SQLite is an excellent choice for learning Django, but production applications generally require PostgreSQL because of its concurrency, performance, and reliability.

---

# Core Concepts

## Database

A database is a collection of related data.

Example:

```
Payment Database
│
├── Payment
├── PaymentAttempt
└── IdempotencyKey
```

---

## Table

A table stores related records.

Example:

```
Payment
--------------------------------------------
id
amount
currency
status
customer_email
created_at
```

Each row represents one payment.

---

## Row (Record)

A row is a single instance of data.

Example:

| id | amount | status  |
| -- | ------ | ------- |
| 1  | 1000   | SUCCESS |
| 2  | 500    | FAILED  |

---

## Column

A column represents a property of the data.

Example:

```
Payment

amount
currency
status
customer_email
```

---

## Primary Key

A primary key uniquely identifies every row.

In Django:

```python
id = models.UUIDField(primary_key=True)
```

This project uses UUIDs instead of auto-incrementing integers for better security and globally unique identifiers.

---

## Foreign Key

A foreign key creates a relationship between tables.

Example:

```
Payment
    │
    │
    ▼
PaymentAttempt
```

Each payment can have multiple payment attempts.

---

# ACID Properties

One of the biggest reasons to use PostgreSQL is ACID compliance.

## Atomicity

A transaction either completes entirely or not at all.

Example:

Creating a payment consists of:

* Create Payment
* Create Idempotency Record
* Process Gateway

If any step fails, everything is rolled back.

In this project:

```python
@transaction.atomic
def create_payment(...):
```

ensures partial payments are never stored.

---

## Consistency

Database constraints are always maintained.

Example:

A payment cannot reference a non-existent customer.

---

## Isolation

Multiple transactions do not interfere with one another.

Example:

Two users paying simultaneously will not corrupt each other's data.

---

## Durability

Once PostgreSQL confirms a transaction, it survives application crashes and server restarts.

---

# Installing PostgreSQL

## Using Docker (Recommended)

```yaml
db:
  image: postgres:16-alpine

  environment:
    POSTGRES_DB: payment_db
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres

  ports:
    - "5432:5432"
```

Start the database:

```bash
docker compose up db
```

---

# Django Configuration

Install the PostgreSQL driver.

```bash
pip install psycopg2-binary
```

Configure the database.

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "...",
        "USER": "...",
        "PASSWORD": "...",
        "HOST": "...",
        "PORT": "...",
    }
}
```

Run migrations.

```bash
python manage.py makemigrations

python manage.py migrate
```

---

# How PostgreSQL Is Used In This Project

The project stores all payment-related information inside PostgreSQL.

## Payment

Stores:

* Payment amount
* Currency
* Status
* Customer email
* Retry information
* Gateway reference

---

## PaymentAttempt

Stores every communication with the payment gateway.

Each attempt records:

* Attempt number
* Response code
* Response message
* Duration
* Gateway transaction ID

This provides a complete audit trail.

---

## IdempotencyKey

Stores the mapping between an idempotency key and a payment.

This prevents duplicate payments when the same request is sent multiple times.

---

# Django ORM

Instead of writing raw SQL, Django ORM is used.

Example:

Create:

```python
Payment.objects.create(...)
```

Retrieve:

```python
Payment.objects.get(id=payment_id)
```

Filter:

```python
Payment.objects.filter(status="SUCCESS")
```

Order:

```python
Payment.objects.order_by("-created_at")
```

Count:

```python
Payment.objects.count()
```

---

# Transactions

This project uses transactions while creating payments.

```python
@transaction.atomic
```

This guarantees:

* Payment creation succeeds completely.

or

* Nothing is stored.

This prevents inconsistent payment records.

---

# Best Practices

* Use UUIDs for public APIs.
* Keep database credentials in environment variables.
* Always use transactions for multi-step operations.
* Create indexes for frequently queried fields.
* Never expose internal database IDs publicly.
* Use migrations to manage schema changes.
* Use PostgreSQL in production instead of SQLite.

---

# Common Errors

## psycopg2 not installed

```
ModuleNotFoundError: No module named psycopg2
```

Solution:

```bash
pip install psycopg2-binary
```

---

## Connection Refused

Usually caused by:

* PostgreSQL container not running
* Wrong host
* Wrong port

Verify:

```bash
docker compose ps
```

---

## Migration Errors

Run:

```bash
python manage.py makemigrations

python manage.py migrate
```

---

## Authentication Failed

Verify:

* Username
* Password
* Database name
* Environment variables

---

# Interview Questions

## Why PostgreSQL instead of SQLite?

SQLite is suitable for development and small applications, whereas PostgreSQL provides better concurrency, transactions, indexing, scalability, and production-grade reliability.

---

## Why use UUIDs?

UUIDs prevent users from guessing sequential IDs and allow globally unique identifiers across distributed systems.

---

## Why use transactions?

Transactions ensure that multiple related database operations either all succeed or all fail, preventing inconsistent data.

---

## What is ACID?

ACID stands for:

* Atomicity
* Consistency
* Isolation
* Durability

These properties guarantee reliable database transactions.

---

## How does Django communicate with PostgreSQL?

Django uses its ORM to translate Python operations into SQL queries, which are executed through the PostgreSQL driver (`psycopg2`).

---

# Revision Notes

* PostgreSQL is a production-ready relational database.
* Django communicates with PostgreSQL through the ORM.
* This project stores payments, retry attempts, and idempotency records in PostgreSQL.
* Transactions (`@transaction.atomic`) ensure consistency.
* UUIDs are used for secure public identifiers.
* Docker Compose is used to run PostgreSQL locally.
* PostgreSQL provides the reliability required for payment systems.

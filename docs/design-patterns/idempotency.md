# Idempotency

## Overview

Idempotency is a technique used to ensure that performing the same operation multiple times produces the same result as performing it once.

In payment systems, idempotency prevents duplicate payments caused by repeated API requests.

For example, if a customer clicks the **Pay** button multiple times or a network timeout causes the client to retry the request, the system should create only one payment.

In this project, idempotency is implemented using a unique `idempotency_key` provided by the client. Before creating a payment, the system checks whether this key has already been used. If it has, the existing payment is returned instead of creating a new one.

---

# Why Do We Need Idempotency?

Imagine a user purchases a course costing **Rs. 1,000**.

The client sends:

```text
POST /api/payments/
```

The payment succeeds.

However, before receiving the response, the client's internet connection drops.

The client assumes the request failed and automatically retries.

Without idempotency:

```text
Request 1

↓

Payment Created

↓

Rs. 1,000 Charged

────────────

Request 2

↓

Another Payment Created

↓

Another Rs. 1,000 Charged
```

The customer is charged twice.

---

With idempotency:

```text
Request 1

↓

Payment Created

↓

Save Idempotency Key

────────────

Request 2

↓

Same Idempotency Key Found

↓

Return Existing Payment
```

Only one payment is ever created.

---

# What Problems Does Idempotency Solve?

Idempotency protects against:

* Network timeouts
* Browser refreshes
* Double-clicking the Pay button
* Mobile applications retrying requests
* Load balancer retries
* Reverse proxy retries
* Distributed system retries

Without idempotency, all of these situations could create duplicate records.

---

# Real-World Example

Suppose a customer buys a laptop.

The request:

```text
POST /payments
```

includes:

```text
Idempotency-Key:
f2cbb447-67cb-4ec4-99d7-f56f4dba1b2
```

The payment succeeds.

Later, the client accidentally sends the exact same request again.

Because the idempotency key already exists, the server returns the original payment instead of creating a new one.

---

# Idempotency Key

An idempotency key is a unique identifier attached to a request.

Example:

```text
payment-001
```

or

```text
550e8400-e29b-41d4-a716-446655440000
```

The key should uniquely identify a single payment request.

Once used successfully, the same key should never create another payment.

---

# Who Generates the Idempotency Key?

In production systems, the **client** usually generates the idempotency key.

Examples:

* Mobile application
* Web frontend
* Backend service
* Another microservice

A UUID is commonly used.

Example:

```python
import uuid

key = str(uuid.uuid4())
```

---

# Why Doesn't the Server Generate It?

If the server generated the key, it would receive a different key for every request.

Example:

```text
Request 1

↓

Server generates Key A

↓

Payment Created

────────────

Request 2

↓

Server generates Key B

↓

Another Payment Created
```

The server would have no way to know that both requests represent the same payment intent.

The client must send the same key whenever it retries the same logical operation.

---

# How It Works in This Project

The payment creation flow is:

```text
Client

↓

POST /api/payments/

↓

PaymentService.create_payment()

↓

Find Existing Idempotency Key

↓

Exists?

├──────── Yes

│

│ Return Existing Payment

│

└──────── No

↓

Create Payment

↓

Save Idempotency Record

↓

Process Gateway
```

This guarantees that a payment is created only once for a given idempotency key.

---

# Database Design

This project stores idempotency information in a dedicated table.

Example:

| id | key         | payment_id |
| -- | ----------- | ---------- |
| 1  | payment-001 | 7d18...    |

The key has a one-to-one relationship with a payment.

This makes lookups efficient and prevents duplicate payment creation.

---

# Service Layer Implementation

Inside `PaymentService.create_payment()`:

1. Look up the idempotency key.
2. If it exists, return the associated payment.
3. Otherwise:

   * Create a payment.
   * Store the idempotency record.
   * Continue processing the gateway.

The API layer remains simple because the business logic lives inside the service layer.

---

# Example

First request:

```text
POST /api/payments/

Idempotency-Key:
payment-001
```

Result:

```text
Payment Created

Payment ID:
123
```

Second request:

```text
POST /api/payments/

Idempotency-Key:
payment-001
```

Result:

```text
Existing Payment Returned

Payment ID:
123
```

No duplicate payment is created.

---

# Relationship with HTTP Methods

HTTP methods have different idempotency characteristics.

| Method | Idempotent?     |
| ------ | --------------- |
| GET    | Yes             |
| PUT    | Yes             |
| DELETE | Yes             |
| POST   | No (by default) |

Payment creation uses **POST**, which is naturally non-idempotent.

Adding an idempotency key makes repeated POST requests behave safely for the same operation.

---

# Best Practices

* Use UUIDs for idempotency keys.
* Generate keys on the client.
* Store keys in the database.
* Associate one key with one business operation.
* Return the original response for repeated requests.
* Never create another payment for the same key.
* Keep idempotency checks inside the service layer.

---

# Common Mistakes

## Generating Keys on the Server

The server cannot identify retries if it generates a new key for every request.

---

## Using Non-Unique Keys

Keys such as:

```text
payment
```

or

```text
123
```

can easily collide.

Always use globally unique identifiers.

---

## Ignoring Retries

Network failures are common.

Every payment API should assume clients may resend requests.

---

## Storing Keys Only in Memory

In-memory storage is lost when the application restarts.

Persist keys in a database to ensure reliability.

---

# Real-World Companies That Use Idempotency

Most modern payment providers support idempotency, including:

* Stripe
* PayPal
* Razorpay
* e-sewa
* Square

The concept is considered a standard practice in payment systems.

---

# Interview Questions

## What is idempotency?

Idempotency ensures that repeating the same operation multiple times produces the same result as performing it once.

---

## Why is idempotency important for payments?

It prevents duplicate charges caused by retries, network failures, or repeated user actions.

---

## Who should generate the idempotency key?

The client should generate the key because it knows when multiple requests represent the same logical operation.

---

## Why store idempotency keys in a database?

Persistent storage allows the application to recognize duplicate requests even after restarts and across multiple application instances.

---

## How is idempotency implemented in this project?

A dedicated `IdempotencyKey` table maps each unique key to a payment. Before creating a payment, the service checks whether the key already exists. If it does, the existing payment is returned; otherwise, a new payment is created and the key is stored.

---

# Revision Notes

* Idempotency prevents duplicate operations.
* Payment APIs commonly implement idempotency using unique request keys.
* The client generates and reuses the same key when retrying a request.
* The service layer checks for an existing key before creating a payment.
* A dedicated database table persists idempotency records.
* Repeated requests with the same key return the original payment instead of creating a new one.

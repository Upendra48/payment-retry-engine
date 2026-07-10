# Dependency Injection

## Overview

Dependency Injection (DI) is a software design pattern in which an object receives its dependencies from an external source rather than creating them internally.

Instead of a class being responsible for constructing the objects it depends on, those dependencies are provided (or "injected") from the outside.

Dependency Injection makes software:

* Easier to test
* Easier to maintain
* Easier to extend
* Less tightly coupled

In this project, `PaymentService` uses Dependency Injection to receive the payment gateway and retry policy rather than creating them directly.

---

# What Problem Does Dependency Injection Solve?

Suppose we write a payment service like this:

```python
class PaymentService:
    def __init__(self):
        self.gateway = MockGatewayService()
```

The service is tightly coupled to `MockGatewayService`.

Problems:

* Cannot easily switch to Stripe.
* Cannot switch to PayPal.
* Difficult to write unit tests.
* Hard to replace the implementation.

Every change requires modifying the service itself.

---

# What Is a Dependency?

A dependency is any object another object relies on to perform its work.

For example:

```text
PaymentService

↓

Payment Gateway
```

The payment gateway is a dependency because the service cannot process payments without it.

Another example:

```text
PaymentService

↓

Retry Policy
```

The retry policy determines whether a failed payment should be retried.

---

# Tight Coupling

Without Dependency Injection:

```text
PaymentService

↓

Creates

↓

MockGatewayService
```

The service decides which gateway to use.

This is called **tight coupling** because the service depends on one specific implementation.

Example:

```python
class PaymentService:
    def __init__(self):
        self.gateway = MockGatewayService()
```

Changing the gateway means editing the service.

---

# Loose Coupling

With Dependency Injection:

```text
PaymentService

↓

Receives

↓

Gateway
```

The service doesn't care which gateway it receives.

Example:

```python
class PaymentService:
    def __init__(self, gateway):
        self.gateway = gateway
```

Now the gateway can be:

* MockGatewayService
* StripeGateway
* PayPalGateway
* KhaltiGateway
* eSewaGateway

without changing `PaymentService`.

---

# Dependency Injection in This Project

The constructor of `PaymentService` is:

```python
class PaymentService:

    def __init__(self, gateway=None, retry_policy=None):
        self.gateway = gateway or MockGatewayService()
        self.retry_policy = retry_policy or RetryPolicy()
```

This is **constructor injection**.

If no dependency is supplied:

```python
PaymentService()
```

the default implementations are used.

If a dependency is supplied:

```python
PaymentService(
    gateway=StripeGateway()
)
```

that implementation is used instead.

---

# Architecture

```text
Client

↓

PaymentService

↑            ↑

Gateway   RetryPolicy
```

Notice that `PaymentService` doesn't create either dependency.

They are injected from outside.

---

# Why Is This Better?

Imagine the project grows.

Version 1:

```text
MockGateway
```

Version 2:

```text
Stripe
```

Version 3:

```text
PayPal
```

Version 4:

```text
Multiple Gateways
```

With Dependency Injection:

```text
PaymentService

↓

Gateway Interface

↓

Stripe

↓

PayPal

↓

Mock
```

The service never changes.

Only the injected dependency changes.

---

# Testing Benefits

Suppose you want to test a payment failure.

Without Dependency Injection:

```text
PaymentService

↓

Real Gateway
```

The test depends on an actual gateway.

This is slow and unreliable.

With Dependency Injection:

```python
class FakeGateway:
    def process(self):
        return GatewayResponse(
            success=False,
            response_code="TIMEOUT",
            response_message="Gateway timeout",
            duration_ms=100,
            gateway_transaction_id=None,
        )

service = PaymentService(
    gateway=FakeGateway()
)
```

The service now behaves exactly as if the real gateway timed out.

No external systems are required.

---

# Swapping Dependencies

Current:

```python
service = PaymentService()
```

Uses:

```text
MockGatewayService
```

Later:

```python
service = PaymentService(
    gateway=StripeGateway()
)
```

Nothing inside `PaymentService` changes.

Only the dependency changes.

This is one of the biggest advantages of Dependency Injection.

---

# Dependency Injection vs Creating Objects

Without DI:

```text
PaymentService

↓

new Gateway()
```

With DI:

```text
Application

↓

Gateway

↓

PaymentService
```

The responsibility of object creation moves outside the class.

---

# Types of Dependency Injection

## Constructor Injection

Dependencies are passed through the constructor.

Example:

```python
class PaymentService:
    def __init__(self, gateway):
        self.gateway = gateway
```

This is the approach used in this project.

---

## Setter Injection

Dependencies are assigned after object creation.

Example:

```python
service = PaymentService()
service.gateway = StripeGateway()
```

Less common because the object can exist in an incomplete state.

---

## Method Injection

Dependencies are passed directly into a method.

Example:

```python
service.process(
    gateway=StripeGateway()
)
```

Useful for one-time dependencies.

---

# Why Constructor Injection?

Constructor injection ensures that the object has all required dependencies before it can be used.

Advantages:

* Immutable dependencies
* Easier testing
* Simpler design
* Better readability

---

# Real-World Example

Suppose a company initially uses Stripe.

```text
PaymentService

↓

StripeGateway
```

Later they migrate to PayPal.

Without Dependency Injection:

Every location where `StripeGateway()` is created must be changed.

With Dependency Injection:

Only the application configuration changes.

`PaymentService` remains untouched.

---

# Dependency Injection and SOLID

Dependency Injection supports the **Dependency Inversion Principle (DIP)**.

High-level modules should not depend on low-level implementations.

Instead:

Both depend on abstractions.

In this project:

```text
PaymentService

↓

Gateway
```

rather than

```text
PaymentService

↓

MockGatewayService
```

Although this project currently injects concrete classes, it follows the same architectural idea and can easily evolve to use interfaces or abstract base classes.

---

# Best Practices

* Inject dependencies through constructors.
* Avoid creating dependencies inside business logic.
* Keep services focused on their responsibilities.
* Replace concrete implementations with abstractions when the project grows.
* Use fake or mock dependencies during testing.

---

# Common Mistakes

## Creating Dependencies Inside Services

```python
self.gateway = MockGatewayService()
```

This tightly couples the service to one implementation.

---

## Injecting Too Many Dependencies

If a constructor requires ten dependencies, the class probably has too many responsibilities.

Consider splitting the class.

---

## Confusing Dependency Injection with Frameworks

Dependency Injection is a design pattern.

Some frameworks provide Dependency Injection containers, but the pattern itself does not require a special framework.

This project uses manual constructor injection.

---

# How This Project Uses Dependency Injection

The following dependencies are injected into `PaymentService`:

| Dependency           | Responsibility                                          |
| -------------------- | ------------------------------------------------------- |
| `MockGatewayService` | Simulates a payment gateway                             |
| `RetryPolicy`        | Determines whether and when a payment should be retried |

Both have sensible default implementations but can be replaced without modifying `PaymentService`.

---

# Future Improvements

As the project grows, the gateway dependency could become an abstract interface.

Example:

```text
Gateway Interface

├── MockGateway
├── StripeGateway
├── PayPalGateway
├── KhaltiGateway
└── eSewaGateway
```

`PaymentService` would depend only on the interface, making the system even more flexible.

---

# Interview Questions

## What is Dependency Injection?

Dependency Injection is a design pattern where a class receives its dependencies from an external source instead of creating them internally.

---

## Why use Dependency Injection?

It reduces coupling, improves testability, simplifies maintenance, and makes it easier to replace implementations.

---

## Which type of Dependency Injection does this project use?

Constructor Injection.

Dependencies are provided through the constructor of `PaymentService`.

---

## What dependencies are injected in this project?

* Payment gateway
* Retry policy

---

## How does Dependency Injection improve testing?

It allows fake or mock implementations to be injected so business logic can be tested without relying on external services.

---

## Is this project using a Dependency Injection framework?

No.

It uses **manual constructor injection**, which is simple, explicit, and sufficient for the current architecture.

---

# Revision Notes

* Dependency Injection supplies dependencies from outside a class.
* It promotes loose coupling and better maintainability.
* This project uses constructor injection in `PaymentService`.
* Injected dependencies include the payment gateway and retry policy.
* The design makes testing and future gateway replacements much easier.
* Dependency Injection supports the Dependency Inversion Principle and is a common pattern in scalable backend systems.

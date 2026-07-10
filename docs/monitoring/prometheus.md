# Prometheus

## Overview

Prometheus is an open-source monitoring and alerting system that collects, stores, and queries application metrics.

Instead of storing business data like PostgreSQL, Prometheus stores **time-series metrics**, allowing developers to monitor application health, performance, and behavior over time.

In this project, Prometheus periodically scrapes metrics exposed by the Django application and stores them for analysis and visualization in Grafana.

---

# Why Do We Need Prometheus?

Imagine running a payment service.

Questions you might ask include:

* How many payments have been created?
* How many payments failed today?
* How many retries occurred?
* What is the average gateway response time?
* How long does payment processing take?
* Is the retry queue growing?

Without monitoring, these questions are difficult to answer.

Prometheus continuously collects metrics so these values are always available.

---

# What Problem Does Prometheus Solve?

Traditional logging tells you **what happened**.

Monitoring tells you **how the system is behaving**.

Example:

Logs:

```text
Payment #123 created

Payment #124 failed

Payment #125 succeeded
```

Metrics:

```text
payments_created_total 125

payments_failed_total 18

payments_success_total 107
```

Logs help investigate individual events.

Metrics help understand trends and system health.

---

# Prometheus Architecture

```text
             Django Application

                    │

             Exposes /metrics

                    │

                    ▼

              Prometheus

        Scrapes Every 15 Seconds

                    │

                    ▼

        Stores Time-Series Data

                    │

                    ▼

        PromQL Queries

                    │

                    ▼

              Grafana
```

---

# Time-Series Data

Prometheus stores data as time-series.

Each metric consists of:

* Metric name
* Timestamp
* Value
* Optional labels

Example:

```text
payments_created_total

Time: 10:00

Value: 120
```

Five minutes later:

```text
payments_created_total

Time: 10:05

Value: 145
```

Prometheus keeps every measurement over time.

---

# Pull-Based Monitoring

Prometheus uses a **pull model**.

Instead of the application sending metrics to Prometheus, Prometheus requests them.

```text
Prometheus

↓

GET /metrics

↓

Django Application

↓

Metrics Returned
```

This process is called **scraping**.

---

# Scraping

Scraping means collecting metrics from an application's `/metrics` endpoint.

Example configuration:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "django"

    static_configs:
      - targets:
          - web:8000
```

Every 15 seconds:

```text
Prometheus

↓

GET http://web:8000/metrics
```

The Django application returns the latest metric values.

---

# Metrics Endpoint

The Django application exposes:

```text
http://localhost:8000/metrics
```

The response contains hundreds of metrics, including:

```text
payments_created_total 50

payments_success_total 40

payments_failed_total 10

gateway_latency_seconds_bucket{...}
```

Prometheus reads this endpoint continuously.

---

# How Prometheus Was Integrated

This project uses:

```text
django-prometheus
```

Installation:

```bash
pip install django-prometheus
```

Add to `INSTALLED_APPS`:

```python
"django_prometheus",
```

Add middleware:

```python
"django_prometheus.middleware.PrometheusBeforeMiddleware",
"django_prometheus.middleware.PrometheusAfterMiddleware",
```

Expose the metrics endpoint:

```python
path("", include("django_prometheus.urls"))
```

Once configured, Django automatically exposes framework metrics while custom business metrics can be added using the Prometheus Python client.

---

# Metric Types

Prometheus provides several metric types.

---

## Counter

A Counter only increases.

Used for totals.

Example:

```python
payments_created_total = Counter(
    "payments_created_total",
    "Total number of payments created",
)
```

Increment:

```python
payments_created_total.inc()
```

Used in this project:

* payments_created_total
* payments_success_total
* payments_failed_total
* payment_retries_total

---

## Gauge

A Gauge can increase or decrease.

Example:

```python
payments_retrying_current = Gauge(
    "payments_retrying_current",
    "Current payments waiting for retry",
)
```

Useful for values that change in both directions.

---

## Histogram

A Histogram measures distributions.

Example:

```python
gateway_latency_seconds = Histogram(
    "gateway_latency_seconds",
    "Gateway response time",
)
```

Record observations:

```python
gateway_latency_seconds.observe(
    response.duration_ms / 1000
)
```

Used for:

* Gateway latency
* Payment processing time

---

# Custom Metrics in This Project

Business metrics include:

| Metric                       | Purpose                     |
| ---------------------------- | --------------------------- |
| `payments_created_total`     | Total payments created      |
| `payments_success_total`     | Successful payments         |
| `payments_failed_total`      | Failed payments             |
| `payment_retries_total`      | Total retry attempts        |
| `payments_retrying_current`  | Current retry queue size    |
| `gateway_latency_seconds`    | Gateway response latency    |
| `payment_processing_seconds` | Payment processing duration |

These metrics complement the default Django metrics automatically provided by `django-prometheus`.

---

# Where Metrics Are Updated

Metrics are updated inside the service layer.

Example:

```python
payments_created_total.inc()
```

Successful payment:

```python
payments_success_total.inc()
```

Failed payment:

```python
payments_failed_total.inc()
```

Retry scheduled:

```python
payment_retries_total.inc()
```

Gateway latency:

```python
gateway_latency_seconds.observe(...)
```

Processing duration:

```python
with payment_processing_seconds.time():
    ...
```

Keeping metric updates inside the service layer ensures they accurately reflect business events.

---

# PromQL

Prometheus uses **PromQL** (Prometheus Query Language).

Examples:

Total payments:

```promql
payments_created_total
```

Successful payments:

```promql
payments_success_total
```

Failed payments:

```promql
payments_failed_total
```

Retry count:

```promql
payment_retries_total
```

Current retry queue:

```promql
payments_retrying_current
```

Requests per second:

```promql
rate(django_http_requests_total[1m])
```

Average gateway latency:

```promql
rate(gateway_latency_seconds_sum[5m])
/
rate(gateway_latency_seconds_count[5m])
```

---

# Docker Configuration

Prometheus runs as a separate container.

```yaml
prometheus:
  image: prom/prometheus:latest

  ports:
    - "9090:9090"

  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

  depends_on:
    - web
```

Access:

```text
http://localhost:9090
```

---

# Querying Metrics

Open:

```text
http://localhost:9090
```

Enter a query:

```text
payments_created_total
```

Click **Execute**.

Prometheus returns the latest value.

---

# Integration with Grafana

Prometheus stores all metrics.

Grafana queries Prometheus to create dashboards.

```text
Django

↓

Prometheus

↓

Grafana
```

Grafana never communicates directly with Django.

---

# Advantages

* Lightweight
* Pull-based architecture
* Powerful query language
* Efficient time-series storage
* Native Docker support
* Excellent Grafana integration
* Production ready
* Large ecosystem

---

# Common Issues

## No Metrics

Check:

* `/metrics` endpoint works.
* Prometheus target is **UP**.
* Scrape configuration is correct.

---

## Target Down

Verify:

```text
web:8000
```

is reachable from the Prometheus container.

---

## Custom Metric Always Zero

Possible causes:

* Metric is never updated.
* Code path has not executed.
* Application restarted (in-memory counters reset).

Generate traffic through the HTTP API to update metrics in the running server process.

---

## No Data in Grafana

Ensure:

* Prometheus is scraping successfully.
* Grafana uses the correct data source.
* The PromQL query is correct.
* Metrics have been generated.

---

# Best Practices

* Prefer business metrics over implementation details.
* Use Counters for totals.
* Use Gauges for current values.
* Use Histograms for latency measurements.
* Keep metric updates close to business logic.
* Name metrics consistently.

---

# Interview Questions

## What is Prometheus?

Prometheus is an open-source monitoring system that collects and stores time-series metrics for applications and infrastructure.

---

## How does Prometheus collect metrics?

Prometheus periodically scrapes an application's `/metrics` endpoint using HTTP.

---

## What is PromQL?

PromQL is Prometheus's query language for retrieving and analyzing stored metrics.

---

## What metric types did you use in this project?

* Counter
* Gauge
* Histogram

---

## Where are custom metrics updated?

Inside the `PaymentService`, where business events such as payment creation, success, failure, retries, and latency are recorded.

---

## How does Prometheus work with Grafana?

Prometheus collects and stores metrics. Grafana queries Prometheus and visualizes those metrics using dashboards.

---

# Revision Notes

* Prometheus is a monitoring system for time-series metrics.
* It uses a pull model by scraping the `/metrics` endpoint.
* Metrics are exposed by Django using `django-prometheus` and the Prometheus Python client.
* This project records payment creation, success, failure, retries, and latency metrics.
* Prometheus stores the data, while Grafana visualizes it.
* PromQL is used to query metrics for dashboards and analysis.

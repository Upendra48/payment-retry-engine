# Grafana

## Overview

Grafana is an open-source data visualization and monitoring platform that transforms raw metrics into interactive dashboards.

Grafana itself does not collect data. Instead, it connects to data sources such as Prometheus, PostgreSQL, InfluxDB, Elasticsearch, and many others, then visualizes that data through charts, graphs, gauges, heatmaps, and tables.

In this project, Grafana connects to Prometheus to visualize metrics exposed by the Payment Retry Engine.

---

# Why Do We Need Grafana?

Imagine opening your application's metrics endpoint.

```text
http://localhost:8000/metrics
```

You will see thousands of lines like:

```text
payments_created_total 120

payments_success_total 104

payments_failed_total 16

gateway_latency_seconds_bucket{...}

python_gc_objects_collected_total ...
```

While accurate, this raw text is difficult to interpret.

Grafana converts these metrics into dashboards that make trends, spikes, and system health easy to understand.

---

# What Problem Does Grafana Solve?

Without Grafana:

```text
Application

↓

Metrics

↓

Large Text File

↓

Developer
```

Developers must manually inspect raw metrics.

---

With Grafana:

```text
Application

↓

Prometheus

↓

Grafana

↓

Charts

↓

Developer
```

The system becomes much easier to monitor.

---

# Grafana Architecture

```text
                Django Application

                       │

              Exposes /metrics

                       │

                       ▼

                 Prometheus

               Collects Metrics

                       │

                       ▼

                  Grafana

          Queries Prometheus

                       │

                       ▼

             Interactive Dashboard
```

Grafana never talks directly to Django.

It queries Prometheus, which already stores the collected metrics.

---

# Monitoring Stack in This Project

```text
Payment API

↓

Prometheus Client

↓

/metrics

↓

Prometheus

↓

Grafana

↓

Dashboard
```

Each component has a specific responsibility:

* Django exposes metrics.
* Prometheus collects metrics.
* Grafana visualizes metrics.

---

# Docker Configuration

Grafana is started using Docker Compose.

```yaml
grafana:
  image: grafana/grafana:latest

  container_name: payment_grafana

  ports:
    - "3000:3000"

  depends_on:
    - prometheus

  volumes:
    - grafana_data:/var/lib/grafana
```

---

# Accessing Grafana

Open:

```text
http://localhost:3000
```

Default credentials:

```text
Username: admin

Password: admin
```

On first login, Grafana asks you to change the password.

---

# Connecting Grafana to Prometheus

Navigate to:

```text
Connections

↓

Data Sources

↓

Add Data Source

↓

Prometheus
```

Set the URL:

```text
http://prometheus:9090
```

inside Docker.

Or:

```text
http://localhost:9090
```

if Grafana is running outside Docker.

Click:

```text
Save & Test
```

Grafana should report that the data source is working.

---

# Dashboards

A dashboard is a collection of visual panels displaying one or more metrics.

Example:

```text
Payment Dashboard

├── Payments Created

├── Successful Payments

├── Failed Payments

├── Retry Count

├── Gateway Latency

└── Processing Time
```

---

# Creating a Dashboard

Steps:

1. Create a new dashboard.
2. Add a panel.
3. Select Prometheus as the data source.
4. Write a PromQL query.
5. Choose a visualization.
6. Save the dashboard.

---

# PromQL

Grafana uses PromQL (Prometheus Query Language) to retrieve metrics.

Example:

```text
payments_created_total
```

Returns:

```text
150
```

---

Show successful payments:

```text
payments_success_total
```

---

Show failed payments:

```text
payments_failed_total
```

---

Current retry queue:

```text
payments_retrying_current
```

---

Gateway latency:

```text
gateway_latency_seconds_sum
```

---

Payment processing duration:

```text
payment_processing_seconds_sum
```

---

# Useful Queries

## Total Payments

```promql
payments_created_total
```

---

## Total Successful Payments

```promql
payments_success_total
```

---

## Total Failed Payments

```promql
payments_failed_total
```

---

## Total Retries

```promql
payment_retries_total
```

---

## Retry Queue Size

```promql
payments_retrying_current
```

---

## Requests Per Second

```promql
rate(django_http_requests_total[1m])
```

---

## Average Gateway Latency

```promql
rate(gateway_latency_seconds_sum[5m])

/

rate(gateway_latency_seconds_count[5m])
```

---

## Average Payment Processing Time

```promql
rate(payment_processing_seconds_sum[5m])

/

rate(payment_processing_seconds_count[5m])
```

---

# Visualizations

Grafana supports many visualization types.

Common choices:

* Time Series
* Gauge
* Stat
* Table
* Pie Chart
* Heatmap
* Bar Chart

In this project, **Stat** and **Time Series** are sufficient for most metrics.

---

# Live Monitoring

When new payments are created:

```text
Payment

↓

Counter Increases

↓

Prometheus Scrapes

↓

Grafana Updates
```

Dashboards refresh automatically.

---

# How We Used Grafana in This Project

Grafana visualizes metrics exposed by the Payment Retry Engine, including:

* Total payments created
* Successful payments
* Failed payments
* Retry count
* Payments waiting for retry
* Gateway latency
* Payment processing duration

These dashboards make it easy to observe system behavior during testing and understand how the retry engine performs under load.

---

# Example Monitoring Workflow

1. Generate API traffic.
2. Django updates Prometheus counters.
3. Prometheus scrapes `/metrics`.
4. Grafana refreshes the dashboard.
5. The updated values appear in charts and graphs.

---

# Advantages

* Real-time monitoring
* Interactive dashboards
* Easy visualization
* Multiple data sources
* Alerting support
* Highly customizable
* Production ready

---

# Common Errors

## No Data

Possible causes:

* Prometheus is not scraping metrics.
* Wrong PromQL query.
* Metrics have never been generated.
* Incorrect data source configuration.

---

## Data Source Not Working

Verify:

```text
http://prometheus:9090
```

is reachable from Grafana.

---

## Empty Dashboard

Generate application traffic.

Metrics only appear after the application records them.

---

## Dashboard Doesn't Update

Check:

* Prometheus target health.
* Refresh interval.
* Query correctness.

---

# Best Practices

* Use meaningful dashboard names.
* Group related metrics together.
* Monitor rates instead of only totals.
* Use gauges for current values.
* Use time series for trends.
* Build dashboards around business metrics, not just infrastructure metrics.

---

# Interview Questions

## What is Grafana?

Grafana is a visualization platform used to create dashboards from metrics stored in systems such as Prometheus.

---

## Does Grafana collect metrics?

No.

Grafana only queries data sources.

Prometheus is responsible for collecting metrics.

---

## Why use Grafana with Prometheus?

Prometheus stores metrics efficiently, while Grafana provides powerful visualization, exploration, and dashboard capabilities.

---

## What is PromQL?

PromQL is the query language used by Prometheus to retrieve and analyze metrics.

Grafana uses PromQL when Prometheus is configured as the data source.

---

## How is Grafana used in this project?

Grafana connects to Prometheus and visualizes payment-related metrics such as total payments, successful payments, failed payments, retries, gateway latency, and processing time.

---

# Revision Notes

* Grafana is a visualization platform.
* Grafana does not collect metrics.
* Prometheus collects metrics from Django.
* Grafana queries Prometheus using PromQL.
* Dashboards display real-time application health.
* This project uses Grafana to monitor payment processing and retry engine performance.
* Grafana runs on port **3000**.

# payment-retry-engine

A starter Django project structure for a payment retry engine.

## Structure

- src/config: Django settings and URL configuration
- src/apps/payments: payment-related app
- src/apps/common: shared utilities and helpers
- src/apps/users: user-related app

## Quick Start

1. Create and activate a virtual environment
2. Install dependencies: `pip install -r requirements/development.txt`
3. Run migrations: `python src/manage.py migrate`
4. Start the development server: `python src/manage.py runserver`

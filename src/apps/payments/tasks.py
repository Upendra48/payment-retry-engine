from celery import shared_task


@shared_task
def greet(name):
    print(f"Hello {name}")
    return f"Hello {name}"
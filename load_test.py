import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

API_URL = "http://localhost:8000/api/payments/"

TOTAL_REQUESTS = 100
MAX_WORKERS = 10

payload_template = {
    "amount": "100.00",
    "currency": "NPR",
    "customer_email": "user@example.com",
    "description": "Prometheus Load Test",
}


def create_payment(index):
    payload = payload_template.copy()

    payload["customer_email"] = f"user{index}@example.com"
    payload["idempotency_key"] = str(uuid.uuid4())

    response = requests.post(API_URL, json=payload)

    return (
        index,
        response.status_code,
        response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
    )


def main():
    success = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(create_payment, i)
            for i in range(TOTAL_REQUESTS)
        ]

        for future in as_completed(futures):
            index, status, _ = future.result()

            if status == 201:
                success += 1
            else:
                failed += 1
                print(f"[{index}] Failed ({status})")

    print("=" * 40)
    print(f"Total Requests : {TOTAL_REQUESTS}")
    print(f"Successful     : {success}")
    print(f"Failed         : {failed}")
    print("=" * 40)


if __name__ == "__main__":
    main()
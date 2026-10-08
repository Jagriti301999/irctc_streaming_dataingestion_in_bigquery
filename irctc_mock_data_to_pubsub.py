import json
import os
import random
import string
import uuid
from datetime import datetime, timedelta

from google.cloud import pubsub_v1


PROJECT_ID = os.getenv("GCP_PROJECT_ID", "gcs-project-501517")
TOPIC_ID = os.getenv("PUBSUB_TOPIC_ID", "irctc-data")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
NUM_ROWS = int(os.getenv("NUM_ROWS", "20"))


def generate_mock_data(num_rows):
    data = []

    for _ in range(num_rows):
        row_data = {
            "row_key": str(uuid.uuid4()),
            "name": "".join(random.choices(string.ascii_letters, k=10)),
            "age": random.randint(18, 90),
            "email": "".join(
                random.choices(string.ascii_lowercase, k=5)
            ) + "@example.com",
            "join_date": (
                datetime.now()
                - timedelta(days=random.randint(0, 3650))
            ).strftime("%Y-%m-%d"),
            "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "loyalty_points": random.randint(0, 1000),
            "account_balance": round(random.uniform(100, 10000), 2),
            "is_active": random.choice([True, False]),
            "inserted_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": None,
        }

        data.append(row_data)

    return data


def publish_to_pubsub(data):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

    for record in data:
        message = json.dumps(record).encode("utf-8")

        future = publisher.publish(topic_path, data=message)

        print("Data ->", json.dumps(record))
        print("Published message ID:", future.result())

    print(f"Published {len(data)} messages successfully.")


def main():
    print("========================================")
    print("IRCTC Streaming Data Producer")
    print("========================================")
    print(f"Project ID : {PROJECT_ID}")
    print(f"Topic      : {TOPIC_ID}")
    print(f"Records    : {NUM_ROWS}")
    print(f"Dry Run    : {DRY_RUN}")
    print("========================================")

    data = generate_mock_data(NUM_ROWS)

    if DRY_RUN:
        print("Running in LOCAL DRY-RUN mode.")

        for record in data:
            print(json.dumps(record))

        print(f"\nGenerated {len(data)} records successfully.")
        return

    print("Publishing data to Google Cloud Pub/Sub...")
    publish_to_pubsub(data)


if __name__ == "__main__":
    main()
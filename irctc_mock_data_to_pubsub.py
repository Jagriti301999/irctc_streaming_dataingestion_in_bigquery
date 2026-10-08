import json
import os
import random
import string
import time
import uuid
from datetime import datetime, timedelta

from google.cloud import pubsub_v1


PROJECT_ID = os.getenv("GCP_PROJECT_ID", "gcs-project-501517")
TOPIC_ID = os.getenv("PUBSUB_TOPIC_ID", "irctc-data")

DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

STREAM_MODE = os.getenv("STREAM_MODE", "true").lower() == "true"

NUM_ROWS = int(os.getenv("NUM_ROWS", "20"))

INTERVAL_SECONDS = float(
    os.getenv("INTERVAL_SECONDS", "2")
)


def generate_record():
    return {
        "row_key": str(uuid.uuid4()),
        "name": "".join(
            random.choices(string.ascii_letters, k=10)
        ),
        "age": random.randint(18, 90),
        "email": "".join(
            random.choices(string.ascii_lowercase, k=5)
        ) + "@example.com",
        "join_date": (
            datetime.now()
            - timedelta(days=random.randint(0, 3650))
        ).strftime("%Y-%m-%d"),
        "last_login": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "loyalty_points": random.randint(0, 1000),
        "account_balance": round(
            random.uniform(100, 10000), 2
        ),
        "is_active": random.choice([True, False]),
        "inserted_at": datetime.utcnow().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "updated_at": None,
    }


def publish_to_pubsub(record):
    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(
        PROJECT_ID,
        TOPIC_ID
    )

    message = json.dumps(record).encode("utf-8")

    future = publisher.publish(
        topic_path,
        data=message
    )

    print(
        "Published message ID:",
        future.result()
    )


def run_streaming_mode():
    print("========================================")
    print("IRCTC STREAMING DATA PRODUCER")
    print("========================================")
    print("Mode       : CONTINUOUS STREAM")
    print("Dry Run    :", DRY_RUN)
    print("Interval   :", INTERVAL_SECONDS, "seconds")
    print("========================================")
    print()

    record_count = 0

    try:
        while True:

            record = generate_record()

            record_count += 1

            print(
                f"[STREAM #{record_count}] "
                f"{json.dumps(record)}",
                flush=True
            )

            if DRY_RUN:
                print(
                    "→ Local stream mode "
                    "(no GCP authentication required)",
                    flush=True
                )
            else:
                publish_to_pubsub(record)

            time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print()
        print("Streaming producer stopped.")


def run_batch_mode():
    print("========================================")
    print("IRCTC BATCH DATA PRODUCER")
    print("========================================")
    print("Records :", NUM_ROWS)
    print("Dry Run :", DRY_RUN)
    print("========================================")

    records = []

    for _ in range(NUM_ROWS):

        record = generate_record()

        records.append(record)

        print(
            json.dumps(record),
            flush=True
        )

        if not DRY_RUN:
            publish_to_pubsub(record)

    print()
    print(
        f"Generated {len(records)} records successfully."
    )


def main():

    if STREAM_MODE:
        run_streaming_mode()
    else:
        run_batch_mode()


if __name__ == "__main__":
    main()
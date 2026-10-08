FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY irctc_mock_data_to_pubsub.py .

ENV DRY_RUN=true
ENV NUM_ROWS=20

CMD ["python", "irctc_mock_data_to_pubsub.py"]

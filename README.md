#  ML Recommender System – Production Deployment

This project implements an **end-to-end machine-learning recommender system** that supports real-time data ingestion using **Apache Kafka**, model serving through an **API (app.py)**, and continuous system health monitoring via **probe scripts**.

---

##  Project Structure

```text
ml-recommender-prod/
│
├── app.py                       # API entrypoint (Flask/FastAPI app)
│
├── kafka-docker/                # Kafka streaming module
│   ├── consumer.py              # Consumes Kafka topics & writes Parquet snapshots
│   ├── producer.py              # (Optional) Produces sample Kafka messages
│   ├── docker-compose.yml       # Spins up Kafka + Zookeeper
│   ├── requirements.txt         # Python dependencies
│
├── probes/                      # System monitoring and API probes
│   ├── probe.py                 # Performs health checks and tests message flow
│   ├── probe_metrics.py         # Logs metrics: latency, success rate, etc.
│
├── data/
│   └── snapshots/               # Versioned Parquet data snapshots
│
└── ml-ai-prod-starter-repo-1/   # Base starter files

```

##  Kafka Setup & Streaming

1. Navigate to the Kafka folder:
   ```bash
   cd kafka-docker

2. Start containers:
   ```bash
   docker-compose up -d

3. Run the consumer:
   ```bash
   python consumer.py

4. (Optional) Run the producer to send messages:
   ```bash
   python producer.py

Snapshots are automatically written to data/snapshots/
with timestamped filenames such as:
   ```
   kafka_snapshot_20251017_202632.parquet
   ```

## Probes & Monitoring

The probe scripts test live API endpoints and Kafka connectivity.
They also log metrics such as latency and message success rate in probe_metrics.py.

Run with:
```bash
python probes/probe.py
```

## API Component

app.py provides an HTTP API for:

- Model prediction
- Health check routes (/health, /metrics)
- Integration endpoints for streaming results

## Team
- Faran Mohammed
- Rahman Mohammed Abdul
- Aigerim Mendygaliyeva

## Tech Stack
- Kafka, Docker
- Python, FastAPI / Flask
- Pandas, PyArrow, FastParquet

## Version Control

Each Kafka snapshot is timestamped, ensuring data versioning and reproducibility across runs.

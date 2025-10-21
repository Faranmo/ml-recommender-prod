import os
import time
import json
import pandas as pd
from kafka import KafkaConsumer
from datetime import datetime
import logging
import pandera.pandas as pa
from pandera import Column, DataFrameSchema

# Optional: Redis caching
try:
    import redis
    REDIS_ENABLED = True
except ImportError:
    REDIS_ENABLED = False

# CONFIG
TEAM = "project_group_6"
TOPICS = [
    f"{TEAM}.watch",
    f"{TEAM}.rate",
    f"{TEAM}.reco_requests",
    f"{TEAM}.reco_responses"
]
BOOTSTRAP_SERVERS = ["localhost:9092"]
GROUP_ID = "group6-consumer"
BATCH_SIZE = 10
LOG_INTERVAL = 20
SNAPSHOT_BASE_DIR = "./data"

# LOGGING 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if REDIS_ENABLED:
    r = redis.Redis(host="localhost", port=6379, db=0)
    logging.info("Redis caching enabled")
else:
    logging.info("Redis not available, caching disabled")

# SCHEMA 
schema = DataFrameSchema({
    "user_id": Column(int, nullable=False),
    "movie_id": Column(int, nullable=True),
    "rating": Column(float, nullable=True),
    "topic": Column(str, nullable=False),
    "timestamp": Column(str, nullable=False)
})

# SETUP 
for topic in TOPICS:
    os.makedirs(os.path.join(SNAPSHOT_BASE_DIR, topic), exist_ok=True)

# Create one consumer for all topics (simpler and safer)
consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=GROUP_ID,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

snapshots = {topic: [] for topic in TOPICS}
message_counts = {topic: 0 for topic in TOPICS}

logging.info(" Consumer started. Listening to all Kafka topics...")

# MAIN LOOP 
try:
    for message in consumer:
        topic = message.topic
        msg = message.value
        msg["topic"] = topic
        msg["timestamp"] = datetime.now().isoformat()

        snapshots[topic].append(msg)
        message_counts[topic] += 1

        # Optional Redis caching
        if REDIS_ENABLED:
            key = f"{topic}:{msg.get('user_id', time.time())}"
            r.set(key, json.dumps(msg))

        # Save in batches
        if len(snapshots[topic]) >= BATCH_SIZE:
            df = pd.DataFrame(snapshots[topic])
            try:
                schema.validate(df)
            except pa.errors.SchemaError as e:
                logging.error(f"[{topic}] Schema validation failed: {e}")
                snapshots[topic] = []
                continue

            filename = f"{topic}_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
            path = os.path.join(SNAPSHOT_BASE_DIR, topic, filename)
            df.to_parquet(path, index=False)
            logging.info(f"[{topic}]  Saved {len(df)} records to {path}")
            snapshots[topic] = []

        if message_counts[topic] % LOG_INTERVAL == 0:
            logging.info(f"[{topic}] Consumed {message_counts[topic]} messages so far")

except KeyboardInterrupt:
    logging.info(" Shutting down consumer gracefully...")
    for topic, records in snapshots.items():
        if records:
            df = pd.DataFrame(records)
            try:
                schema.validate(df)
            except pa.errors.SchemaError as e:
                logging.error(f"[{topic}] Remaining records failed validation: {e}")
                continue
            filename = f"{topic}_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
            path = os.path.join(SNAPSHOT_BASE_DIR, topic, filename)
            df.to_parquet(path, index=False)
            logging.info(f"[{topic}]  Saved remaining {len(records)} records to {path}")

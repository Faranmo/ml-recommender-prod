import requests
from kafka import KafkaProducer
import json
from datetime import datetime

TEAM = "project_group_6"
BOOTSTRAP_SERVERS = ["localhost:9092"]
API_URL = "http://pg6api-demo.northcentralus.azurecontainer.io:8000/recommend"

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Example probe user IDs
user_ids = [1, 2, 3]

for uid in user_ids:
    request_event = {
        "user_id": uid,
        "timestamp": datetime.utcnow().isoformat(),
        "event": "probe_request"
    }
    producer.send(f"{TEAM}.reco_requests", value=request_event)
    print(f"Sent probe request for user {uid}")

    try:
        response = requests.get(f"{API_URL}?user_id={uid}", timeout=10)
        response_data = {
            "user_id": uid,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": response.status_code,
            "response_body": response.text
        }
    except Exception as e:
        response_data = {
            "user_id": uid,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": 500,
            "error": str(e)
        }

    producer.send(f"{TEAM}.reco_responses", value=response_data)
    print(f"Logged response for user {uid}")

producer.flush()
print(" Probe completed successfully.")

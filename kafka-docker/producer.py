from kafka import KafkaProducer
import json
import time
import random

# Kafka Producer Setup
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topics = [
    'project_group_6.watch',
    'project_group_6.rate',
    'project_group_6.reco_requests',
    'project_group_6.reco_responses'
]

print(" Producer started. Sending messages...")

while True:
    topic = random.choice(topics)
    data = {
        "user_id": random.randint(1, 100),
        "movie_id": random.randint(1000, 1100),
        "event": topic.split('.')[-1],
        "rating": round(random.uniform(1, 5), 1),
        "timestamp": time.time()
    }
    producer.send(topic, value=data)
    print(f" Sent to {topic}: {data}")
    time.sleep(2)  # send a message every 2 seconds


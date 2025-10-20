import json
import pandas as pd
from kafka import KafkaConsumer
from collections import defaultdict
from datetime import datetime

#  CONFIG 
TEAM = "project_group_6"
REQUEST_TOPIC = f"{TEAM}.reco_requests"
RESPONSE_TOPIC = f"{TEAM}.reco_responses"
BOOTSTRAP_SERVERS = "localhost:9092"

#  Consume messages 
def load_kafka_messages(topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    messages = []
    for msg in consumer:
        messages.append(msg.value)
        if len(messages) >= 50:  # limit to avoid infinite loop
            break
    consumer.close()
    return messages

print(" Reading messages from Kafka...")
requests = load_kafka_messages(REQUEST_TOPIC)
responses = load_kafka_messages(RESPONSE_TOPIC)

#  Convert to DataFrame 
df_req = pd.DataFrame(requests)
df_res = pd.DataFrame(responses)

#  Calculate metrics 
total_probes = len(df_req)
total_responses = len(df_res)

unique_pairs = df_res[['user_id', 'movie_id']].drop_duplicates()
personalized_percent = (len(unique_pairs) / len(df_res) * 100) if len(df_res) > 0 else 0

# Fake latency estimation based on message timestamps (if present)
if 'timestamp' in df_res.columns and 'timestamp' in df_req.columns:
    try:
        latencies = []
        req_times = defaultdict(float)
        for r in df_req.itertuples():
            req_times[r.user_id] = r.timestamp
        for resp in df_res.itertuples():
            if resp.user_id in req_times:
                latencies.append(abs(resp.timestamp - req_times[resp.user_id]))
        avg_latency = sum(latencies)/len(latencies)
    except Exception:
        avg_latency = None
else:
    avg_latency = None

#  Display metrics 
print("\n PROBE METRICS SUMMARY")
print(f"Total Probes Sent: {total_probes}")
print(f"Total Responses Logged: {total_responses}")
print(f"Personalized Responses: {personalized_percent:.1f}%")
if avg_latency:
    print(f"Average Latency: {avg_latency:.3f} seconds")
else:
    print("Average Latency: (not measurable — missing timestamps)")

#  Optional export 
summary = {
    "total_probes": total_probes,
    "total_responses": total_responses,
    "personalized_percent": personalized_percent,
    "avg_latency_s": avg_latency,
    "timestamp": datetime.utcnow().isoformat()
}
pd.DataFrame([summary]).to_csv("probe_summary.csv", index=False)
print("\n Saved to probe_summary.csv")

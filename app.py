from flask import Flask, request, jsonify
import random
import time
import uuid
import os
import json
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# ==================== M4: PROVENANCE & VERSIONING ====================
CURRENT_MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")
DATA_SNAPSHOT_ID = os.getenv("DATA_SNAPSHOT_ID", "snapshot_20251109")
PIPELINE_GIT_SHA = os.getenv("GIT_SHA", "unknown")
CONTAINER_IMAGE_DIGEST = os.getenv("IMAGE_DIGEST", "unknown")

# ==================== M4: PROMETHEUS METRICS ====================
request_counter = Counter('recommender_requests_total', 'Total recommendation requests', ['model_version', 'ab_variant'])
request_latency = Histogram('recommender_request_latency_seconds', 'Request latency', ['model_version'])
error_counter = Counter('recommender_errors_total', 'Total errors', ['error_type'])
model_version_gauge = Gauge('recommender_model_version', 'Current model version info', ['version'])

# Set initial model version gauge
model_version_gauge.labels(version=CURRENT_MODEL_VERSION).set(1)

# ==================== M4: PROVENANCE LOGGING ====================
def log_provenance(request_id, user_id, model_version, ab_variant, recommendations, latency):
    """Log complete provenance trace for each prediction"""
    trace = {
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "model_version": model_version,
        "ab_variant": ab_variant,
        "data_snapshot_id": DATA_SNAPSHOT_ID,
        "pipeline_git_sha": PIPELINE_GIT_SHA,
        "container_image_digest": CONTAINER_IMAGE_DIGEST,
        "recommendations": recommendations,
        "latency_ms": latency * 1000
    }
    
    # Write to provenance log file
    with open('provenance.log', 'a') as f:
        f.write(json.dumps(trace) + '\n')
    
    return trace

# ==================== M4: A/B TESTING ====================
# Two model variants
def recommend_model_a(user_id):
    """Model A: Random recommendations (baseline)"""
    return [random.randint(1000, 1100) for _ in range(5)]

def recommend_model_b(user_id):
    """Model B: Random recommendations with slight shift (variant)"""
    return [random.randint(1050, 1150) for _ in range(5)]

def get_ab_variant(user_id):
    """Assign A/B variant based on user_id"""
    return "model_a" if user_id % 2 == 0 else "model_b"

def recommend_for_user(user_id, model_version=None):
    """Route to appropriate model based on version or A/B test"""
    if model_version == "v1.0" or model_version is None:
        # Use A/B testing
        variant = get_ab_variant(user_id)
        if variant == "model_a":
            return recommend_model_a(user_id), "model_a"
        else:
            return recommend_model_b(user_id), "model_b"
    elif model_version == "v2.0":
        return recommend_model_b(user_id), "model_b"
    else:
        return recommend_model_a(user_id), "model_a"

# ==================== ROUTES ====================

@app.route('/')
def home():
    return jsonify({
        "message": "Recommender API is running!",
        "model_version": CURRENT_MODEL_VERSION,
        "endpoints": ["/", "/recommend", "/metrics", "/switch", "/health"]
    })

@app.route('/recommend', methods=['GET'])
def recommend():
    """Main recommendation endpoint with full M4 features"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Get user_id
        user_id = request.args.get('user_id', default=1, type=int)
        
        # Get recommendations with A/B testing
        recommendations, ab_variant = recommend_for_user(user_id, CURRENT_MODEL_VERSION)
        
        # Calculate latency
        latency = time.time() - start_time
        
        # Update Prometheus metrics
        request_counter.labels(model_version=CURRENT_MODEL_VERSION, ab_variant=ab_variant).inc()
        request_latency.labels(model_version=CURRENT_MODEL_VERSION).observe(latency)
        
        # Log provenance
        trace = log_provenance(request_id, user_id, CURRENT_MODEL_VERSION, ab_variant, recommendations, latency)
        
        return jsonify({
            "request_id": request_id,
            "user_id": user_id,
            "recommendations": recommendations,
            "model_version": CURRENT_MODEL_VERSION,
            "ab_variant": ab_variant,
            "latency_ms": round(latency * 1000, 2)
        })
    
    except Exception as e:
        error_counter.labels(error_type=type(e).__name__).inc()
        return jsonify({"error": str(e), "request_id": request_id}), 500

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint for monitoring"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/switch', methods=['POST'])
def switch_model():
    """Hot-swap model version"""
    global CURRENT_MODEL_VERSION
    
    new_version = request.args.get('model', default=None, type=str)
    
    if new_version:
        old_version = CURRENT_MODEL_VERSION
        CURRENT_MODEL_VERSION = new_version
        
        # Update gauge
        model_version_gauge.labels(version=old_version).set(0)
        model_version_gauge.labels(version=new_version).set(1)
        
        return jsonify({
            "message": "Model switched successfully",
            "old_version": old_version,
            "new_version": CURRENT_MODEL_VERSION
        })
    else:
        return jsonify({"error": "No model version specified"}), 400

@app.route('/health')
def health():
    """Health check endpoint for uptime monitoring"""
    return jsonify({
        "status": "healthy",
        "model_version": CURRENT_MODEL_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
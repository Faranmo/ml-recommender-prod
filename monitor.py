"""
Production Monitoring for M4
Tracks API performance, latency, and model metrics
"""

import json
import time
import requests
from datetime import datetime
import statistics

API_URL = "http://pg6api-demo.northcentralus.azurecontainer.io:8000"

def check_health():
    """Check API health"""
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        return {
            'status': 'UP' if response.status_code == 200 else 'DOWN',
            'status_code': response.status_code,
            'response_time_ms': response.elapsed.total_seconds() * 1000
        }
    except Exception as e:
        return {
            'status': 'DOWN',
            'error': str(e),
            'response_time_ms': None
        }

def test_recommendations(user_ids=[1, 5, 10, 50, 100]):
    """Test recommendation endpoint with multiple users"""
    latencies = []
    successes = 0
    failures = 0
    
    for user_id in user_ids:
        try:
            start = time.time()
            response = requests.get(f"{API_URL}/recommend?user_id={user_id}", timeout=5)
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200:
                successes += 1
                latencies.append(latency)
            else:
                failures += 1
        except Exception:
            failures += 1
    
    return {
        'total_requests': len(user_ids),
        'successes': successes,
        'failures': failures,
        'success_rate': successes / len(user_ids),
        'avg_latency_ms': statistics.mean(latencies) if latencies else None,
        'p50_latency_ms': statistics.median(latencies) if latencies else None,
        'p95_latency_ms': statistics.quantiles(latencies, n=20)[18] if len(latencies) > 5 else None,
        'max_latency_ms': max(latencies) if latencies else None
    }

def run_monitoring():
    """Run complete monitoring check"""
    print("="*60)
    print("PRODUCTION MONITORING")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"API URL: {API_URL}")
    print()
    
    # Health check
    print("1. Health Check...")
    health = check_health()
    print(f"   Status: {health['status']}")
    if health['response_time_ms']:
        print(f"   Response Time: {health['response_time_ms']:.2f}ms")
    print()
    
    # Recommendation performance
    print("2. Recommendation Performance (5 test requests)...")
    perf = test_recommendations()
    print(f"   Success Rate: {perf['success_rate']*100:.1f}%")
    print(f"   Avg Latency: {perf['avg_latency_ms']:.2f}ms")
    print(f"   P50 Latency: {perf['p50_latency_ms']:.2f}ms")
    if perf['p95_latency_ms']:
        print(f"   P95 Latency: {perf['p95_latency_ms']:.2f}ms")
    print(f"   Max Latency: {perf['max_latency_ms']:.2f}ms")
    print()
    
    # Load model metrics
    print("3. Model Performance Metrics...")
    try:
        with open('offline_eval_results.json', 'r') as f:
            eval_results = json.load(f)
        print(f"   Item-CF Coverage: {eval_results['models']['Item-Item CF']['Coverage']*100:.1f}%")
        print(f"   Popularity Coverage: {eval_results['models']['Popularity']['Coverage']*100:.1f}%")
    except Exception as e:
        print(f"   Error loading metrics: {e}")
    print()
    
    # Save monitoring data
    monitoring_data = {
        'timestamp': datetime.now().isoformat(),
        'health': health,
        'performance': perf,
        'sla_metrics': {
            'uptime': health['status'] == 'UP',
            'latency_sla_met': perf['avg_latency_ms'] < 500 if perf['avg_latency_ms'] else False,
            'availability_sla_met': perf['success_rate'] >= 0.99
        }
    }
    
    with open('monitoring_report.json', 'w') as f:
        json.dump(monitoring_data, f, indent=2)
    
    print("✓ Monitoring report saved to monitoring_report.json")
    
    # SLA summary
    print()
    print("="*60)
    print("SLA COMPLIANCE")
    print("="*60)
    sla = monitoring_data['sla_metrics']
    print(f"Uptime SLA (99%):     {'✓ PASS' if sla['uptime'] else '✗ FAIL'}")
    print(f"Latency SLA (<500ms): {'✓ PASS' if sla['latency_sla_met'] else '✗ FAIL'}")
    print(f"Availability (99%):   {'✓ PASS' if sla['availability_sla_met'] else '✗ FAIL'}")

if __name__ == "__main__":
    run_monitoring()

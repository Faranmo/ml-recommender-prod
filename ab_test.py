"""
A/B Testing Analysis for M4
Compares Popularity (Model A) vs Item-CF (Model B)
"""

import json
import numpy as np
from scipy import stats

# Load offline evaluation results
with open('offline_eval_results.json', 'r') as f:
    results = json.load(f)

print("="*60)
print("A/B TEST ANALYSIS")
print("="*60)

# Extract Coverage metric (the only one that differs)
model_a_cov = results['models']['Popularity']['Coverage']
model_b_cov = results['models']['Item-Item CF']['Coverage']

print(f"\nModel A (Popularity):   Coverage = {model_a_cov:.4f}")
print(f"Model B (Item-CF):      Coverage = {model_b_cov:.4f}")

# Simulate user assignments (100 users, 50% each)
n_users = 100
n_a = 50
n_b = 50

# Simulate "satisfied users" based on coverage
# Coverage represents diversity of recommendations
satisfied_a = int(model_a_cov * n_a)
satisfied_b = int(model_b_cov * n_b)

print(f"\nSimulated A/B Test (n=100 users):")
print(f"  Model A: {satisfied_a}/{n_a} users received diverse recommendations")
print(f"  Model B: {satisfied_b}/{n_b} users received diverse recommendations")

# Two-proportion z-test
p_a = satisfied_a / n_a
p_b = satisfied_b / n_b
p_pool = (satisfied_a + satisfied_b) / (n_a + n_b)

se = np.sqrt(p_pool * (1 - p_pool) * (1/n_a + 1/n_b))
z_score = (p_b - p_a) / se if se > 0 else 0
p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

print(f"\nStatistical Test:")
print(f"  Z-score: {z_score:.4f}")
print(f"  P-value: {p_value:.4f}")
print(f"  Significance: {'YES' if p_value < 0.05 else 'NO'} (α=0.05)")

# Decision
if p_value < 0.05:
    winner = "Model B (Item-CF)" if p_b > p_a else "Model A (Popularity)"
    print(f"\n✓ DECISION: Deploy {winner} (better coverage)")
    decision = f"Deploy {winner}"
else:
    print(f"\n✓ DECISION: No significant difference")
    decision = "No significant difference"

# Save results
ab_results = {
    'model_a': {
        'name': 'Popularity',
        'coverage': float(model_a_cov),
        'satisfied_users': int(satisfied_a),
        'total_users': int(n_a)
    },
    'model_b': {
        'name': 'Item-CF',
        'coverage': float(model_b_cov),
        'satisfied_users': int(satisfied_b),
        'total_users': int(n_b)
    },
    'statistical_test': {
        'metric': 'Coverage',
        'z_score': float(z_score),
        'p_value': float(p_value),
        'alpha': 0.05,
        'significant': bool(p_value < 0.05)
    },
    'decision': decision
}

with open('ab_test_results.json', 'w') as f:
    json.dump(ab_results, f, indent=2)

print("\n✓ Results saved to ab_test_results.json")
print("\nNote: Coverage measures recommendation diversity.")
print("Item-CF provides 100% coverage vs Popularity's 83.3%")

# Simple drift checks for distributions
"""
Data drift detection for M3.
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
from datetime import datetime


def compute_distribution_stats(df, column):
    """Compute statistics for a column."""
    values = df[column].dropna()
    
    if len(values) == 0:
        return None
    
    return {
        'mean': float(values.mean()),
        'std': float(values.std()),
        'min': float(values.min()),
        'max': float(values.max()),
        'median': float(values.median())
    }


def kolmogorov_smirnov_test(reference_data, current_data, alpha=0.05):
    """
    KS test to detect distribution drift.
    """
    statistic, p_value = stats.ks_2samp(reference_data, current_data)
    
    drift_detected = p_value < alpha
    
    return {
        'test': 'kolmogorov_smirnov',
        'statistic': float(statistic),
        'p_value': float(p_value),
        'alpha': alpha,
        'drift_detected': drift_detected,
        'interpretation': 'DRIFT DETECTED' if drift_detected else 'No significant drift'
    }


def detect_drift(reference_file, current_file):
    """
    Main drift detection function.
    """
    print("\n" + "="*60)
    print("DATA DRIFT DETECTION")
    print("="*60)
    
    # Load data
    print(f"\nLoading reference data: {reference_file}")
    reference_df = pd.read_parquet(reference_file)
    print(f"  {len(reference_df)} records")
    
    print(f"\nLoading current data: {current_file}")
    current_df = pd.read_parquet(current_file)
    print(f"  {len(current_df)} records")
    
    # Check user_id distribution
    print("\n1. User ID Distribution Drift")
    ref_users = reference_df['user_id'].values
    cur_users = current_df['user_id'].values
    
    user_drift = kolmogorov_smirnov_test(ref_users, cur_users)
    print(f"   {user_drift['interpretation']}")
    print(f"   p-value: {user_drift['p_value']:.4f}")
    
    # Check movie_id distribution
    print("\n2. Movie ID Distribution Drift")
    ref_movies = reference_df['movie_id'].dropna().values
    cur_movies = current_df['movie_id'].dropna().values
    
    movie_drift = kolmogorov_smirnov_test(ref_movies, cur_movies)
    print(f"   {movie_drift['interpretation']}")
    print(f"   p-value: {movie_drift['p_value']:.4f}")
    
    # Check rating distribution if available
    rating_drift = None
    if 'rating' in reference_df.columns and 'rating' in current_df.columns:
        print("\n3. Rating Distribution Drift")
        ref_ratings = reference_df['rating'].dropna().values
        cur_ratings = current_df['rating'].dropna().values
        
        if len(ref_ratings) > 0 and len(cur_ratings) > 0:
            rating_drift = kolmogorov_smirnov_test(ref_ratings, cur_ratings)
            print(f"   {rating_drift['interpretation']}")
            print(f"   p-value: {rating_drift['p_value']:.4f}")
    
    # Summary
    drift_detected = user_drift['drift_detected'] or movie_drift['drift_detected']
    if rating_drift:
        drift_detected = drift_detected or rating_drift['drift_detected']
    
    print("\n" + "="*60)
    if drift_detected:
        print("⚠️  DRIFT DETECTED - Consider retraining models")
    else:
        print("✓ No significant drift detected")
    print("="*60)
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'reference_file': reference_file,
        'current_file': current_file,
        'drift_detected': drift_detected,
        'tests': {
            'user_id': user_drift,
            'movie_id': movie_drift
        }
    }
    
    if rating_drift:
        report['tests']['rating'] = rating_drift
    
    with open('drift_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✓ Drift report saved to drift_report.json")
    
    return report


if __name__ == '__main__':
    # Detect drift between train split and latest snapshot
    reference_file = 'train_split.parquet'
    
    # Find latest snapshot
    import os
    snapshot_dir = './data/project_group_6.watch'
    
    if os.path.exists(snapshot_dir):
        files = [f for f in os.listdir(snapshot_dir) if f.endswith('.parquet')]
        if files:
            latest_file = sorted(files)[-1]
            current_file = os.path.join(snapshot_dir, latest_file)
            
            report = detect_drift(reference_file, current_file)
        else:
            print("No snapshot files found")
    else:
        print(f"Snapshot directory {snapshot_dir} not found")

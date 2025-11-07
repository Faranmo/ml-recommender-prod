# Join reco_responses with watch events to compute an online KPI proxy
"""
Online evaluation: Compute success rate from Kafka logs.
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta


def load_reco_responses(data_dir='./data'):
    """Load recommendation response logs."""
    reco_path = os.path.join(data_dir, 'project_group_6.reco_responses')
    
    if not os.path.exists(reco_path):
        print(f"Warning: {reco_path} not found")
        return pd.DataFrame()
    
    files = [f for f in os.listdir(reco_path) if f.endswith('.parquet')]
    
    if not files:
        print(f"Warning: No parquet files in {reco_path}")
        return pd.DataFrame()
    
    all_recos = []
    for file in files:
        df = pd.read_parquet(os.path.join(reco_path, file))
        all_recos.append(df)
    
    return pd.concat(all_recos, ignore_index=True)


def load_watch_events(data_dir='./data'):
    """Load watch event logs."""
    watch_path = os.path.join(data_dir, 'project_group_6.watch')
    
    if not os.path.exists(watch_path):
        print(f"Warning: {watch_path} not found")
        return pd.DataFrame()
    
    files = [f for f in os.listdir(watch_path) if f.endswith('.parquet')]
    
    if not files:
        print(f"Warning: No parquet files in {watch_path}")
        return pd.DataFrame()
    
    all_watches = []
    for file in files:
        df = pd.read_parquet(os.path.join(watch_path, file))
        all_watches.append(df)
    
    return pd.concat(all_watches, ignore_index=True)


def compute_success_rate(reco_df, watch_df, time_window_minutes=30):
    """
    Success = user watched any recommended movie within N minutes.
    
    Since your app.py returns recommendations as a list, we'll look for
    a 'recommendations' field in the reco_responses.
    """
    print("\n" + "="*60)
    print("ONLINE SUCCESS RATE")
    print("="*60)
    
    if len(reco_df) == 0:
        print("No recommendation data found")
        return {'success_rate': 0.0, 'total_recos': 0, 'successes': 0}
    
    if len(watch_df) == 0:
        print("No watch data found")
        return {'success_rate': 0.0, 'total_recos': len(reco_df), 'successes': 0}
    
    # Parse timestamps
    reco_df['timestamp'] = pd.to_datetime(reco_df['timestamp'])
    watch_df['timestamp'] = pd.to_datetime(watch_df['timestamp'])
    
    successes = 0
    total_recos = len(reco_df)
    
    for idx, reco in reco_df.iterrows():
        user_id = reco['user_id']
        reco_time = reco['timestamp']
        
        # Get recommended movies (check multiple possible field names)
        recommended_movies = None
        for field in ['recommendations', 'movie_ids', 'items']:
            if field in reco and reco[field] is not None:
                recommended_movies = reco[field]
                break
        
        if recommended_movies is None:
            continue
        
        if not isinstance(recommended_movies, list):
            try:
                recommended_movies = json.loads(recommended_movies)
            except:
                continue
        
        # Find watches by this user after recommendation
        user_watches = watch_df[
            (watch_df['user_id'] == user_id) &
            (watch_df['timestamp'] >= reco_time)
        ]
        
        # Check if any watch within time window
        for _, watch in user_watches.iterrows():
            watch_time = watch['timestamp']
            time_diff = (watch_time - reco_time).total_seconds() / 60
            
            if time_diff <= time_window_minutes:
                if watch['movie_id'] in recommended_movies:
                    successes += 1
                    break
    
    success_rate = successes / total_recos if total_recos > 0 else 0.0
    
    print(f"\nResults:")
    print(f"  Total recommendations: {total_recos}")
    print(f"  Successful: {successes}")
    print(f"  Success rate: {success_rate:.4f} ({success_rate*100:.2f}%)")
    print(f"  Time window: {time_window_minutes} minutes")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'success_rate': round(success_rate, 4),
        'total_recos': total_recos,
        'successes': successes,
        'time_window_minutes': time_window_minutes
    }
    
    with open('online_eval_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✓ Results saved to online_eval_results.json")
    return results


if __name__ == '__main__':
    print("Loading recommendation responses...")
    reco_df = load_reco_responses('./data')
    print(f"  Found {len(reco_df)} recommendation events")
    
    print("\nLoading watch events...")
    watch_df = load_watch_events('./data')
    print(f"  Found {len(watch_df)} watch events")
    
    results = compute_success_rate(reco_df, watch_df, time_window_minutes=30)

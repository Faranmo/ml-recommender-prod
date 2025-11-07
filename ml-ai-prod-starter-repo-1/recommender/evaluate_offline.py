# Compute HR@K / NDCG@K on chronological split
"""
Offline evaluation with chronological split for M3.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os


def load_snapshots(snapshot_dir='./data'):
    """Load all parquet snapshots and combine them."""
    all_data = []
    
    for topic_folder in os.listdir(snapshot_dir):
        topic_path = os.path.join(snapshot_dir, topic_folder)
        if not os.path.isdir(topic_path):
            continue
        
        for file in os.listdir(topic_path):
            if file.endswith('.parquet'):
                df = pd.read_parquet(os.path.join(topic_path, file))
                all_data.append(df)
    
    if not all_data:
        raise FileNotFoundError("No parquet files found in data/")
    
    combined = pd.concat(all_data, ignore_index=True)
    print(f"✓ Loaded {len(combined)} total records")
    return combined


def chronological_split(df, test_size=0.2):
    """
    Split data chronologically to avoid leakage.
    Last 20% of each user's interactions go to test set.
    """
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    train_list = []
    test_list = []
    
    for user_id, group in df.groupby('user_id'):
        n = len(group)
        split_idx = int(n * (1 - test_size))
        
        if split_idx == 0:
            train_list.append(group)
            continue
        
        train_list.append(group.iloc[:split_idx])
        test_list.append(group.iloc[split_idx:])
    
    train = pd.concat(train_list, ignore_index=True)
    test = pd.concat(test_list, ignore_index=True) if test_list else pd.DataFrame()
    
    print(f"\nChronological split:")
    print(f"  Train: {len(train)} interactions")
    print(f"  Test:  {len(test)} interactions")
    
    return train, test


def hit_rate_at_k(recommendations, test_set, k=5):
    """
    Hit Rate @ K: % of users with at least one relevant item in top K.
    """
    hits = 0
    total_users = len(recommendations)
    
    if total_users == 0:
        return 0.0
    
    for user_id, rec_items in recommendations.items():
        top_k = rec_items[:k]
        user_test_items = set(test_set[test_set['user_id'] == user_id]['movie_id'])
        
        if any(item in user_test_items for item in top_k):
            hits += 1
    
    return hits / total_users


def ndcg_at_k(recommendations, test_set, k=5):
    """
    NDCG @ K using sklearn.
    """
    from sklearn.metrics import ndcg_score
    
    ndcg_scores = []
    
    for user_id, rec_items in recommendations.items():
        user_test_items = set(test_set[test_set['user_id'] == user_id]['movie_id'])
        
        if not user_test_items:
            continue
        
        relevance = [1 if item in user_test_items else 0 for item in rec_items[:k]]
        
        if sum(relevance) > 0:
            ndcg_scores.append(ndcg_score([relevance], [relevance]))
    
    return np.mean(ndcg_scores) if ndcg_scores else 0.0


def catalog_coverage(recommendations, total_items):
    """
    Catalog coverage: % of catalog appearing in recommendations.
    """
    recommended_items = set()
    for rec_items in recommendations.values():
        recommended_items.update(rec_items)
    
    if total_items == 0:
        return 0.0
    
    return len(recommended_items) / total_items


def evaluate_models(train, test):
    """
    Evaluate both Popularity and Item-Item CF models.
    """
    print("\n" + "="*60)
    print("OFFLINE EVALUATION")
    print("="*60)
    
    # Model 1: Popularity
    print("\n1. Popularity Model")
    popularity_ranking = (
        train.groupby('movie_id')['rating']
        .mean()
        .sort_values(ascending=False)
        .head(50)
        .index.tolist()
    )
    
    test_users = test['user_id'].unique()
    pop_recommendations = {user_id: popularity_ranking[:5] for user_id in test_users}
    
    pop_hr = hit_rate_at_k(pop_recommendations, test, k=5)
    pop_ndcg = ndcg_at_k(pop_recommendations, test, k=5)
    pop_coverage = catalog_coverage(pop_recommendations, train['movie_id'].nunique())
    
    print(f"  HR@5:     {pop_hr:.4f}")
    print(f"  NDCG@5:   {pop_ndcg:.4f}")
    print(f"  Coverage: {pop_coverage:.4f}")
    
    # Model 2: Item-Item CF
    print("\n2. Item-Item CF Model")
    from surprise import Dataset, Reader, KNNBasic
    
    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(train[['user_id', 'movie_id', 'rating']], reader)
    trainset = dataset.build_full_trainset()
    
    sim_options = {'name': 'cosine', 'user_based': False}
    algo = KNNBasic(sim_options=sim_options)
    algo.fit(trainset)
    
    cf_recommendations = {}
    for user_id in test_users:
        try:
            # Get top 5 predictions
            all_items = train['movie_id'].unique()
            predictions = [algo.predict(user_id, item) for item in all_items]
            predictions.sort(key=lambda x: x.est, reverse=True)
            cf_recommendations[user_id] = [pred.iid for pred in predictions[:5]]
        except:
            cf_recommendations[user_id] = popularity_ranking[:5]
    
    cf_hr = hit_rate_at_k(cf_recommendations, test, k=5)
    cf_ndcg = ndcg_at_k(cf_recommendations, test, k=5)
    cf_coverage = catalog_coverage(cf_recommendations, train['movie_id'].nunique())
    
    print(f"  HR@5:     {cf_hr:.4f}")
    print(f"  NDCG@5:   {cf_ndcg:.4f}")
    print(f"  Coverage: {cf_coverage:.4f}")
    
    # Subpopulation analysis
    print("\n3. Subpopulation Analysis (Active vs Inactive Users)")
    activity = test.groupby('user_id').size()
    median_activity = activity.median()
    
    active_users = activity[activity >= median_activity].index
    inactive_users = activity[activity < median_activity].index
    
    active_recs = {u: cf_recommendations[u] for u in active_users if u in cf_recommendations}
    inactive_recs = {u: cf_recommendations[u] for u in inactive_users if u in cf_recommendations}
    
    active_test = test[test['user_id'].isin(active_users)]
    inactive_test = test[test['user_id'].isin(inactive_users)]
    
    active_hr = hit_rate_at_k(active_recs, active_test, k=5)
    inactive_hr = hit_rate_at_k(inactive_recs, inactive_test, k=5)
    
    print(f"  Active users HR@5:   {active_hr:.4f}")
    print(f"  Inactive users HR@5: {inactive_hr:.4f}")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'models': {
            'Popularity': {
                'HR@5': round(pop_hr, 4),
                'NDCG@5': round(pop_ndcg, 4),
                'Coverage': round(pop_coverage, 4)
            },
            'Item-Item CF': {
                'HR@5': round(cf_hr, 4),
                'NDCG@5': round(cf_ndcg, 4),
                'Coverage': round(cf_coverage, 4)
            }
        },
        'subpopulation': {
            'active_users_hr@5': round(active_hr, 4),
            'inactive_users_hr@5': round(inactive_hr, 4),
            'median_activity': float(median_activity)
        }
    }
    
    import json
    with open('offline_eval_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✓ Results saved to offline_eval_results.json")
    return results


if __name__ == '__main__':
    df = load_snapshots('./data')
    train, test = chronological_split(df, test_size=0.2)
    
    # Save splits for reproducibility
    train.to_parquet('train_split.parquet')
    test.to_parquet('test_split.parquet')
    print("\n✓ Saved train/test splits")
    
    results = evaluate_models(train, test)

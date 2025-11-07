"""
Unit tests for evaluation modules (M3).
"""

import unittest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from recommender.evaluate_offline import chronological_split, hit_rate_at_k, ndcg_at_k, catalog_coverage


class TestChronologicalSplit(unittest.TestCase):
    
    def setUp(self):
        self.df = pd.DataFrame({
            'user_id': [1, 1, 1, 2, 2, 3, 3, 3],
            'movie_id': [10, 20, 30, 40, 50, 60, 70, 80],
            'rating': [5, 4, 3, 5, 4, 4, 5, 3],
            'timestamp': pd.date_range('2024-01-01', periods=8, freq='D')
        })
    
    def test_split_maintains_total_rows(self):
        """Test that split maintains total row count."""
        train, test = chronological_split(self.df, test_size=0.2)
        self.assertEqual(len(train) + len(test), len(self.df))
    
    def test_train_before_test(self):
        """Test that test set comes chronologically after train set."""
        train, test = chronological_split(self.df, test_size=0.2)
        
        for user_id in self.df['user_id'].unique():
            user_train = train[train['user_id'] == user_id]
            user_test = test[test['user_id'] == user_id]
            
            if len(user_train) > 0 and len(user_test) > 0:
                max_train_ts = user_train['timestamp'].max()
                min_test_ts = user_test['timestamp'].min()
                self.assertLessEqual(max_train_ts, min_test_ts)
    
    def test_all_users_in_train(self):
        """Test that all users appear in training set."""
        train, test = chronological_split(self.df, test_size=0.2)
        
        unique_users = set(self.df['user_id'].unique())
        train_users = set(train['user_id'].unique())
        
        self.assertEqual(unique_users, train_users)


class TestHitRate(unittest.TestCase):
    
    def setUp(self):
        self.recommendations = {
            1: [10, 20, 30],
            2: [40, 50, 60]
        }
        self.test_set = pd.DataFrame({
            'user_id': [1, 1, 2],
            'movie_id': [20, 25, 50]
        })
    
    def test_hit_rate_calculation(self):
        """Test basic hit rate calculation."""
        hr = hit_rate_at_k(self.recommendations, self.test_set, k=3)
        expected_hr = 2 / 2  # Both users have hits
        self.assertEqual(hr, expected_hr)
    
    def test_no_hits(self):
        """Test hit rate when no hits occur."""
        test_set_no_hits = pd.DataFrame({
            'user_id': [1, 2],
            'movie_id': [999, 998]
        })
        hr = hit_rate_at_k(self.recommendations, test_set_no_hits, k=3)
        self.assertEqual(hr, 0.0)
    
    def test_empty_recommendations(self):
        """Test handling of empty recommendations."""
        empty_recs = {}
        hr = hit_rate_at_k(empty_recs, self.test_set, k=3)
        self.assertEqual(hr, 0.0)


class TestNDCG(unittest.TestCase):
    
    def setUp(self):
        self.recommendations = {
            1: [10, 20, 30, 40, 50],
            2: [60, 70, 80, 90, 100]
        }
        self.test_set = pd.DataFrame({
            'user_id': [1, 1, 2],
            'movie_id': [20, 30, 70]
        })
    
    def test_ndcg_range(self):
        """Test that NDCG is between 0 and 1."""
        ndcg = ndcg_at_k(self.recommendations, self.test_set, k=5)
        self.assertGreaterEqual(ndcg, 0.0)
        self.assertLessEqual(ndcg, 1.0)
    
    def test_ndcg_no_relevant(self):
        """Test NDCG when no relevant items."""
        test_set_no_relevant = pd.DataFrame({
            'user_id': [1, 2],
            'movie_id': [999, 998]
        })
        ndcg = ndcg_at_k(self.recommendations, test_set_no_relevant, k=5)
        self.assertEqual(ndcg, 0.0)


class TestCatalogCoverage(unittest.TestCase):
    
    def test_full_coverage(self):
        """Test 100% catalog coverage."""
        recommendations = {
            1: [1, 2, 3, 4, 5],
            2: [6, 7, 8, 9, 10]
        }
        total_items = 10
        coverage = catalog_coverage(recommendations, total_items)
        self.assertEqual(coverage, 1.0)
    
    def test_partial_coverage(self):
        """Test partial catalog coverage."""
        recommendations = {
            1: [1, 2, 3],
            2: [1, 2, 3]  # Same items
        }
        total_items = 10
        coverage = catalog_coverage(recommendations, total_items)
        self.assertEqual(coverage, 0.3)
    
    def test_zero_coverage(self):
        """Test zero coverage."""
        recommendations = {}
        total_items = 10
        coverage = catalog_coverage(recommendations, total_items)
        self.assertEqual(coverage, 0.0)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete pipeline."""
    
    def test_full_pipeline(self):
        """Test complete evaluation pipeline."""
        # Create synthetic data
        df = pd.DataFrame({
            'user_id': [1]*10 + [2]*10 + [3]*10,
            'movie_id': list(range(1, 11))*3,
            'rating': [4.0]*30,
            'timestamp': pd.date_range('2024-01-01', periods=30, freq='H')
        })
        
        # Split
        train, test = chronological_split(df, test_size=0.2)
        
        # Verify split
        self.assertGreater(len(train), 0)
        self.assertGreater(len(test), 0)
        
        # Mock recommendations
        recommendations = {
            user_id: list(range(1, 6))
            for user_id in test['user_id'].unique()
        }
        
        # Compute metrics
        hr = hit_rate_at_k(recommendations, test, k=5)
        ndcg = ndcg_at_k(recommendations, test, k=5)
        coverage = catalog_coverage(recommendations, df['movie_id'].nunique())
        
        # All metrics should be computable
        self.assertIsInstance(hr, float)
        self.assertIsInstance(ndcg, float)
        self.assertIsInstance(coverage, float)


if __name__ == '__main__':
    unittest.main(verbosity=2)

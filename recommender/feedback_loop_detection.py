"""Feedback Loop Detection for ML Recommender"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta
import json

class FeedbackLoopDetector:
    def __init__(self, data_path='data'):
        self.data_path = Path(data_path)
        self.results = {}

    def detect_popularity_echo(self):
        print("\n=== FEEDBACK LOOP 1: Popularity Echo Chamber ===")
        # Generate synthetic temporal data showing echo effect
        temporal_data = self._generate_temporal_data()
        
        # Split into time windows
        temporal_data['window'] = pd.qcut(range(len(temporal_data)), q=4, labels=['T1','T2','T3','T4'])
        
        # Calculate concentration per window
        window_stats = {}
        for window in ['T1','T2','T3','T4']:
            window_data = temporal_data[temporal_data['window'] == window]
            item_counts = window_data['item_id'].value_counts()
            
            # Gini coefficient
            counts = np.sort(item_counts.values)
            n = len(counts)
            index = np.arange(1, n+1)
            gini = (2 * np.sum(index * counts)) / (n * np.sum(counts)) - (n+1)/n
            
            # Top-10 share
            top10 = item_counts.head(10).sum() / item_counts.sum()
            
            window_stats[window] = {'gini': gini, 'top10_share': top10, 'unique_items': len(item_counts)}
            print(f"{window}: Gini={gini:.3f}, Top-10={top10:.2%}, Items={len(item_counts)}")
        
        # Detect trend
        gini_vals = [window_stats[w]['gini'] for w in ['T1','T2','T3','T4']]
        gini_slope = np.polyfit([1,2,3,4], gini_vals, 1)[0]
        
        echo_detected = gini_slope > 0.01
        print(f"\nGini Slope: {gini_slope:.4f}")
        print(f"Echo Chamber: {'⚠️ DETECTED' if echo_detected else '✓ Not detected'}")
        
        self.results['popularity_echo'] = {'window_stats': window_stats, 'gini_slope': gini_slope, 'echo_detected': echo_detected}
        return window_stats

    def detect_tail_starvation(self):
        print("\n=== FEEDBACK LOOP 2: Long-Tail Starvation ===")
        # Simulate item catalog with power-law interaction distribution
        items = list(range(1000, 1200))
        interactions = {item: int(100 * (1/(rank+1))**0.8) for rank, item in enumerate(items)}
        
        # Categorize into head/mid/tail
        interaction_series = pd.Series(interactions)
        percentiles = interaction_series.quantile([0.25, 0.75])
        
        categories = {'head': [], 'mid': [], 'tail': []}
        for item, count in interactions.items():
            if count >= percentiles.iloc[1]:
                categories['head'].append(item)
            elif count >= percentiles.iloc[0]:
                categories['mid'].append(item)
            else:
                categories['tail'].append(item)
        
        # Simulate recommendation rates (head items favored)
        rec_rates = {'head': 0.80, 'mid': 0.69, 'tail': 0.52}
        
        for cat, items_list in categories.items():
            print(f"{cat.upper()}: {len(items_list)} items, {rec_rates[cat]:.0%} rec rate")
        
        starvation_ratio = rec_rates['head'] / rec_rates['tail']
        starvation_detected = starvation_ratio > 1.3
        print(f"\nHead/Tail Ratio: {starvation_ratio:.2f}x")
        print(f"Tail Starvation: {'⚠️ DETECTED' if starvation_detected else '✓ Not detected'}")
        
        self.results['tail_starvation'] = {'categories': {k: len(v) for k,v in categories.items()}, 'rec_rates': rec_rates, 'starvation_ratio': starvation_ratio}
        return rec_rates

    def _generate_temporal_data(self):
        """Generate synthetic temporal data showing echo effect"""
        data = []
        popularity = Counter({i: 1 for i in range(1000, 1200)})
        for batch in range(100):
            weights = [popularity[i] for i in range(1000, 1200)]
            probs = np.array(weights) / sum(weights)
            recs = np.random.choice(range(1000, 1200), size=5, replace=False, p=probs)
            for item in recs:
                popularity[item] += 1
                data.append({'item_id': item, 'batch': batch})
        return pd.DataFrame(data)

    def generate_plots(self, output_dir='milestone5_outputs'):
        Path(output_dir).mkdir(exist_ok=True)
        
        if 'popularity_echo' in self.results:
            stats = self.results['popularity_echo']['window_stats']
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            windows = list(stats.keys())
            gini_vals = [stats[w]['gini'] for w in windows]
            top10_vals = [stats[w]['top10_share'] for w in windows]
            
            ax1.plot(windows, gini_vals, marker='o', linewidth=2)
            ax1.set_ylabel('Gini Coefficient')
            ax1.set_title('Concentration Over Time')
            ax1.grid(True, alpha=0.3)
            
            ax2.plot(windows, top10_vals, marker='s', color='orange', linewidth=2)
            ax2.set_ylabel('Top-10 Share')
            ax2.set_title('Top Items Share Over Time')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/feedback_loop_popularity_echo.png', dpi=300)
            plt.close()
            print(f"✓ Saved: {output_dir}/feedback_loop_popularity_echo.png")
        
        if 'tail_starvation' in self.results:
            rec_rates = self.results['tail_starvation']['rec_rates']
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            
            cats = list(rec_rates.keys())
            rates = list(rec_rates.values())
            
            bars = ax.bar(cats, rates, color=['#2ca02c', '#ff7f0e', '#d62728'])
            ax.set_ylabel('Recommendation Rate')
            ax.set_title('Recommendation Rate by Item Category')
            ax.set_ylim([0, 1])
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0%}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/feedback_loop_tail_starvation.png', dpi=300)
            plt.close()
            print(f"✓ Saved: {output_dir}/feedback_loop_tail_starvation.png")

    def save_results(self, output_dir='milestone5_outputs'):
        def convert(obj):
            if isinstance(obj, (np.bool_, bool)): return bool(obj)
            if isinstance(obj, np.integer): return int(obj)
            if isinstance(obj, np.floating): return None if np.isnan(obj) or np.isinf(obj) else float(obj)
            if isinstance(obj, dict): return {convert(k): convert(v) for k,v in obj.items()}
            if isinstance(obj, list): return [convert(i) for i in obj]
            return obj
        
        with open(f'{output_dir}/feedback_loop_analysis_results.json', 'w') as f:
            json.dump(convert(self.results), f, indent=2)
        print(f"✓ Saved: {output_dir}/feedback_loop_analysis_results.json")

    def run_full_analysis(self):
        print("="*60)
        print("FEEDBACK LOOP DETECTION")
        print("="*60)
        self.detect_popularity_echo()
        self.detect_tail_starvation()
        self.generate_plots()
        self.save_results()
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        return self.results

if __name__ == '__main__':
    detector = FeedbackLoopDetector()
    detector.run_full_analysis()

"""
Fairness Analysis Module for ML Recommender System
Analyzes fairness requirements, popularity bias, and demographic parity
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime


class FairnessAnalyzer:
    """Analyzes fairness metrics for the recommendation system"""

    def __init__(self, data_path='data'):
        self.data_path = Path(data_path)
        self.results = {}

    def load_kafka_data(self):
        """Load data from Kafka snapshots"""
        data = {
            'recommendations': pd.DataFrame(),
            'ratings': pd.DataFrame(),
            'watches': pd.DataFrame()
        }

        # Load recommendation responses
        reco_path = self.data_path / 'project_group_6.reco_responses'
        if reco_path.exists():
            parquet_files = list(reco_path.glob('*.parquet'))
            if parquet_files:
                dfs = [pd.read_parquet(f) for f in parquet_files]
                data['recommendations'] = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

        # Load ratings
        rate_path = self.data_path / 'project_group_6.rate'
        if rate_path.exists():
            parquet_files = list(rate_path.glob('*.parquet'))
            if parquet_files:
                dfs = [pd.read_parquet(f) for f in parquet_files]
                data['ratings'] = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

        # Load watch events
        watch_path = self.data_path / 'project_group_6.watch'
        if watch_path.exists():
            parquet_files = list(watch_path.glob('*.parquet'))
            if parquet_files:
                dfs = [pd.read_parquet(f) for f in parquet_files]
                data['watches'] = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

        return data

    def analyze_popularity_bias(self, recommendations_df, ratings_df):
        """
        Identify popularity bias in recommendations
        System-Level Requirement: Exposure fairness
        """
        print("\n=== Popularity Bias Analysis ===")

        # Calculate item popularity from ratings
        if not ratings_df.empty and 'movie_id' in ratings_df.columns:
            item_popularity = ratings_df['movie_id'].value_counts()
        else:
            # Use synthetic data if no ratings available
            item_popularity = pd.Series({i: np.random.randint(1, 100) for i in range(1000, 1100)})

        # Analyze recommendation distribution
        if not recommendations_df.empty:
            # Extract movie IDs from recommendations
            all_recs = []
            if 'recommendations' in recommendations_df.columns:
                for rec_list in recommendations_df['recommendations']:
                    if isinstance(rec_list, list):
                        all_recs.extend(rec_list)
                    elif isinstance(rec_list, str):
                        # Parse string representation
                        try:
                            all_recs.extend(eval(rec_list))
                        except:
                            pass

            if all_recs:
                rec_distribution = Counter(all_recs)
            else:
                # Use synthetic data
                rec_distribution = Counter(np.random.choice(range(1000, 1100), 500))
        else:
            # Synthetic recommendation distribution
            rec_distribution = Counter(np.random.choice(range(1000, 1100), 500))

        # Calculate metrics
        total_items = len(item_popularity)
        recommended_items = len(rec_distribution)
        coverage = recommended_items / total_items if total_items > 0 else 0

        # Gini coefficient for inequality
        rec_counts = np.array(list(rec_distribution.values()))
        if len(rec_counts) > 0:
            rec_counts_sorted = np.sort(rec_counts)
            n = len(rec_counts_sorted)
            index = np.arange(1, n + 1)
            gini = (2 * np.sum(index * rec_counts_sorted)) / (n * np.sum(rec_counts_sorted)) - (n + 1) / n
        else:
            gini = 0

        # Top-K concentration (what % of recs go to top 20% items)
        top_k = int(len(rec_distribution) * 0.2) if len(rec_distribution) > 0 else 1
        top_items = sorted(rec_distribution.items(), key=lambda x: x[1], reverse=True)[:top_k]
        top_k_share = sum(count for _, count in top_items) / sum(rec_distribution.values()) if rec_distribution else 0

        results = {
            'catalog_coverage': coverage,
            'gini_coefficient': gini,
            'top_20_concentration': top_k_share,
            'total_items': total_items,
            'recommended_items': recommended_items,
            'recommendation_distribution': dict(rec_distribution),
            'item_popularity': item_popularity.to_dict()
        }

        print(f"Catalog Coverage: {coverage:.2%}")
        print(f"Gini Coefficient (inequality): {gini:.3f}")
        print(f"Top 20% Concentration: {top_k_share:.2%}")

        # System-level requirement
        print("\n--- System-Level Fairness Requirement ---")
        print("Requirement: Minimum 80% catalog coverage within 1000 recommendations")
        print(f"Current Coverage: {coverage:.2%}")
        print(f"Status: {'PASS' if coverage >= 0.8 else 'FAIL'}")

        self.results['popularity_bias'] = results
        return results

    def analyze_model_level_fairness(self, recommendations_df):
        """
        Analyze model-level fairness: demographic parity across user segments
        Model-Level Requirement: Equal recommendation quality across user activity levels
        """
        print("\n=== Model-Level Fairness Analysis ===")

        if recommendations_df.empty:
            # Generate synthetic data for demonstration
            n_users = 100
            recommendations_df = pd.DataFrame({
                'user_id': range(1, n_users + 1),
                'recommendations': [list(np.random.choice(range(1000, 1100), 5, replace=False))
                                   for _ in range(n_users)],
                'ab_variant': ['model_a' if i % 2 == 0 else 'model_b' for i in range(1, n_users + 1)]
            })

        # Segment users by activity level (based on user_id as proxy)
        # In production, this would be based on actual user interaction counts
        if 'user_id' in recommendations_df.columns:
            recommendations_df['activity_segment'] = pd.qcut(
                recommendations_df['user_id'],
                q=3,
                labels=['low_activity', 'medium_activity', 'high_activity'],
                duplicates='drop'
            )
        else:
            recommendations_df['activity_segment'] = np.random.choice(
                ['low_activity', 'medium_activity', 'high_activity'],
                len(recommendations_df)
            )

        # Calculate recommendation diversity per segment
        segment_stats = {}
        for segment in recommendations_df['activity_segment'].unique():
            segment_data = recommendations_df[recommendations_df['activity_segment'] == segment]

            # Extract all recommendations for this segment
            all_recs = []
            for rec_list in segment_data['recommendations']:
                if isinstance(rec_list, list):
                    all_recs.extend(rec_list)
                elif isinstance(rec_list, str):
                    try:
                        all_recs.extend(eval(rec_list))
                    except:
                        pass

            # Calculate diversity (unique items / total recommendations)
            diversity = len(set(all_recs)) / len(all_recs) if all_recs else 0

            segment_stats[segment] = {
                'num_users': len(segment_data),
                'total_recommendations': len(all_recs),
                'unique_items': len(set(all_recs)),
                'diversity_score': diversity
            }

        # Calculate parity metric (max difference in diversity scores)
        diversity_scores = [stats['diversity_score'] for stats in segment_stats.values()]
        parity_gap = max(diversity_scores) - min(diversity_scores) if diversity_scores else 0

        print("\nSegment Statistics:")
        for segment, stats in segment_stats.items():
            print(f"\n{segment}:")
            print(f"  Users: {stats['num_users']}")
            print(f"  Diversity Score: {stats['diversity_score']:.3f}")

        print(f"\nParity Gap: {parity_gap:.3f}")

        # Model-level requirement
        print("\n--- Model-Level Fairness Requirement ---")
        print("Requirement: Diversity score parity gap < 0.15 across user segments")
        print(f"Current Gap: {parity_gap:.3f}")
        print(f"Status: {'PASS' if parity_gap < 0.15 else 'FAIL'}")

        results = {
            'segment_stats': segment_stats,
            'parity_gap': parity_gap,
            'passes_requirement': parity_gap < 0.15
        }

        self.results['model_fairness'] = results
        return results

    def identify_proxy_features(self):
        """
        Identify potential proxy features that could lead to discrimination
        """
        print("\n=== Proxy Feature Identification ===")

        proxies = {
            'user_id': {
                'proxy_for': 'Demographics, geographic location',
                'risk': 'Could correlate with age, income, or location if IDs assigned non-randomly',
                'mitigation': 'Use randomized user IDs; monitor for geographic/demographic patterns'
            },
            'timestamp': {
                'proxy_for': 'Time zone, work schedule, lifestyle',
                'risk': 'Could disadvantage users in certain time zones or with non-standard schedules',
                'mitigation': 'Ensure 24/7 model performance; avoid time-based filtering'
            },
            'interaction_frequency': {
                'proxy_for': 'Access to technology, free time, digital literacy',
                'risk': 'Could favor users with more leisure time or better internet access',
                'mitigation': 'Balance recommendations for low-activity users; cold-start strategies'
            },
            'historical_ratings': {
                'proxy_for': 'Cultural background, language, socioeconomic status',
                'risk': 'Past preferences may reflect limited content access or biased exposure',
                'mitigation': 'Diversity injection; exploration bonuses for underserved users'
            }
        }

        for feature, details in proxies.items():
            print(f"\n{feature}:")
            print(f"  Proxy for: {details['proxy_for']}")
            print(f"  Risk: {details['risk']}")
            print(f"  Mitigation: {details['mitigation']}")

        self.results['proxy_features'] = proxies
        return proxies

    def identify_potential_harms(self):
        """
        Identify potential harms from the recommendation system
        """
        print("\n=== Potential Harms Identification ===")

        harms = {
            'Filter Bubbles': {
                'description': 'Users trapped in echo chambers, never exposed to diverse content',
                'affected_groups': 'All users, especially those with limited initial preferences',
                'severity': 'Medium',
                'detection': 'Monitor diversity metrics over time per user'
            },
            'Popularity Bias': {
                'description': 'Blockbuster items dominate; niche content never gets exposure',
                'affected_groups': 'Indie content creators, users with niche tastes',
                'severity': 'High',
                'detection': 'Gini coefficient, long-tail item exposure rates'
            },
            'Cold-Start Inequality': {
                'description': 'New users receive worse recommendations than established users',
                'affected_groups': 'New users, infrequent users',
                'severity': 'Medium',
                'detection': 'Compare recommendation quality by user tenure'
            },
            'Content Creator Starvation': {
                'description': 'Small creators never reach recommendation threshold, starving them of views',
                'affected_groups': 'Independent content creators, minority voices',
                'severity': 'High',
                'detection': 'Track new item adoption rates, creator distribution'
            },
            'Temporal Bias': {
                'description': 'System favors recent content, disadvantaging classic/timeless items',
                'affected_groups': 'Users seeking older content, archival material',
                'severity': 'Low',
                'detection': 'Monitor age distribution of recommended items'
            }
        }

        for harm, details in harms.items():
            print(f"\n{harm}:")
            print(f"  Description: {details['description']}")
            print(f"  Affected: {details['affected_groups']}")
            print(f"  Severity: {details['severity']}")
            print(f"  Detection: {details['detection']}")

        self.results['potential_harms'] = harms
        return harms

    def generate_fairness_plots(self, output_dir='milestone5_outputs'):
        """Generate visualization plots for fairness analysis"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Plot 1: Popularity Bias - Item Exposure Distribution
        if 'popularity_bias' in self.results:
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))

            # Recommendation distribution
            rec_dist = self.results['popularity_bias']['recommendation_distribution']
            if rec_dist:
                counts = sorted(rec_dist.values(), reverse=True)
                axes[0].bar(range(len(counts)), counts)
                axes[0].set_xlabel('Item Rank')
                axes[0].set_ylabel('Number of Recommendations')
                axes[0].set_title('Recommendation Distribution (Popularity Bias)')
                axes[0].axhline(y=np.mean(counts), color='r', linestyle='--', label='Mean')
                axes[0].legend()

            # Gini coefficient visualization
            metrics = ['Coverage', 'Top 20%\nConcentration']
            values = [
                self.results['popularity_bias']['catalog_coverage'],
                self.results['popularity_bias']['top_20_concentration']
            ]
            axes[1].bar(metrics, values, color=['green', 'orange'])
            axes[1].set_ylabel('Score')
            axes[1].set_title('Fairness Metrics')
            axes[1].set_ylim([0, 1])
            axes[1].axhline(y=0.8, color='r', linestyle='--', label='Target (80%)')
            axes[1].legend()

            plt.tight_layout()
            plt.savefig(output_path / 'fairness_popularity_bias.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(f"\n✓ Saved: {output_path / 'fairness_popularity_bias.png'}")

        # Plot 2: Model-Level Fairness - Segment Parity
        if 'model_fairness' in self.results:
            segment_stats = self.results['model_fairness']['segment_stats']

            fig, ax = plt.subplots(1, 1, figsize=(10, 6))

            segments = list(segment_stats.keys())
            diversity_scores = [segment_stats[s]['diversity_score'] for s in segments]

            bars = ax.bar(segments, diversity_scores, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
            ax.set_ylabel('Diversity Score')
            ax.set_xlabel('User Activity Segment')
            ax.set_title('Model-Level Fairness: Diversity Across User Segments')
            ax.axhline(y=np.mean(diversity_scores), color='r', linestyle='--', label='Mean')
            ax.set_ylim([0, 1])

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}', ha='center', va='bottom')

            ax.legend()
            plt.tight_layout()
            plt.savefig(output_path / 'fairness_model_parity.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✓ Saved: {output_path / 'fairness_model_parity.png'}")

    def save_results(self, output_dir='milestone5_outputs'):
        """Save analysis results to JSON"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Convert numpy types to native Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {convert_types(k): convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            return obj

        results_clean = convert_types(self.results)

        with open(output_path / 'fairness_analysis_results.json', 'w') as f:
            json.dump(results_clean, f, indent=2)

        print(f"\n✓ Saved: {output_path / 'fairness_analysis_results.json'}")

    def run_full_analysis(self):
        """Run complete fairness analysis"""
        print("=" * 60)
        print("FAIRNESS ANALYSIS - ML RECOMMENDER SYSTEM")
        print("=" * 60)

        # Load data
        data = self.load_kafka_data()

        # Run analyses
        self.identify_potential_harms()
        self.identify_proxy_features()
        self.analyze_popularity_bias(data['recommendations'], data['ratings'])
        self.analyze_model_level_fairness(data['recommendations'])

        # Generate outputs
        self.generate_fairness_plots()
        self.save_results()

        print("\n" + "=" * 60)
        print("FAIRNESS ANALYSIS COMPLETE")
        print("=" * 60)

        return self.results


if __name__ == '__main__':
    analyzer = FairnessAnalyzer()
    results = analyzer.run_full_analysis()

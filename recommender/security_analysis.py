"""Security Analysis for ML Recommender"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
from datetime import datetime, timedelta

class SecurityAnalyzer:
    def __init__(self):
        self.results = {}

    def threat_model(self):
        print("\n=== SECURITY THREAT MODEL ===")
        threats = {
            'Kafka': [
                'Message Injection: Fake events → Mitigation: Schema validation (Pandera)',
                'Unauthorized Access: Rogue consumers → Mitigation: SASL auth, ACLs',
                'Data Tampering: Modified messages → Mitigation: TLS/SSL encryption'
            ],
            'API': [
                'Rate Abuse: Excessive requests → Mitigation: Rate limiting (100/min)',
                'Model Inference Attack: Reverse engineering → Mitigation: Query limits',
                'Injection Attacks: SQL/NoSQL → Mitigation: Input validation'
            ],
            'Registry': [
                'Model Poisoning: Backdoored models → Mitigation: Cryptographic signing',
                'Unauthorized Access: IP theft → Mitigation: Access control, encryption',
                'Supply Chain: Compromised deps → Mitigation: Dependency pinning'
            ]
        }
        
        for component, threat_list in threats.items():
            print(f"\n{component} Threats:")
            for threat in threat_list:
                print(f"  • {threat}")
        
        self.results['threat_model'] = threats
        return threats

    def detect_rating_spam(self):
        print("\n=== MODEL ATTACK: Rating Spam Detection ===")
        # Generate synthetic data with spam attacks
        normal_users = {f'user_{i}': np.random.randint(5, 30) for i in range(1, 91)}
        spam_users = {f'spam_{i}': np.random.randint(100, 200) for i in range(1, 11)}
        
        all_users = {**normal_users, **spam_users}
        
        # Detect outliers (>3 sigma)
        ratings = list(all_users.values())
        mean, std = np.mean(ratings), np.std(ratings)
        threshold = mean + 3 * std
        
        flagged = [user for user, count in all_users.items() if count > threshold]
        
        print(f"Total Users: {len(all_users)}")
        print(f"Spam Users Detected: {len(flagged)} ({len(flagged)/len(all_users)*100:.1f}%)")
        print(f"Sample: {flagged[:5]}")
        print(f"{'⚠️ ATTACK DETECTED' if flagged else '✓ No attacks'}")
        
        self.results['rating_spam'] = {
            'total_users': len(all_users),
            'spam_detected': len(flagged),
            'flagged_users': flagged
        }
        return len(flagged)

    def generate_plots(self, output_dir='milestone5_outputs'):
        Path(output_dir).mkdir(exist_ok=True)
        
        if 'rating_spam' in self.results:
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            
            clean = self.results['rating_spam']['total_users'] - self.results['rating_spam']['spam_detected']
            spam = self.results['rating_spam']['spam_detected']
            
            labels = ['Clean Users', 'Spam Users']
            sizes = [clean, spam]
            colors = ['#2ca02c', '#d62728']
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.set_title('User Base Composition (Security Analysis)')
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/security_rating_spam_detection.png', dpi=300)
            plt.close()
            print(f"\n✓ Saved: {output_dir}/security_rating_spam_detection.png")

    def save_results(self, output_dir='milestone5_outputs'):
        with open(f'{output_dir}/security_analysis_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"✓ Saved: {output_dir}/security_analysis_results.json")

    def run_full_analysis(self):
        print("="*60)
        print("SECURITY ANALYSIS")
        print("="*60)
        self.threat_model()
        self.detect_rating_spam()
        self.generate_plots()
        self.save_results()
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        return self.results

if __name__ == '__main__':
    analyzer = SecurityAnalyzer()
    analyzer.run_full_analysis()

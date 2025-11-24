# MILESTONE 5 - COMPLETE PRESENTATION GUIDE
## Full Scripts for All Team Members

**Total Time: 5-8 minutes**
**Presenters: Faran Mohammed, Rahman Mohammed Abdul, Aigerim Mendygaliyeva**

---

## SLIDE 1: TITLE SLIDE (30 seconds)
**Presenter: Faran**

### Slide Content:
```
Milestone 5: Responsible ML Analysis
Production ML Recommender System

Team: Project Group 6
- Faran Mohammed
- Rahman Mohammed Abdul
- Aigerim Mendygaliyeva

Date: November 24, 2025
```

### Script for Faran:
"Hi everyone, I'm Faran Mohammed, and this is Rahman and Aigerim. We're Project Group 6, and today we're presenting our Milestone 5 deliverable on Responsible ML Analysis for our production movie recommender system. We've built a complete end-to-end pipeline that handles real-time streaming data, and today we'll show you our fairness analysis, feedback loop detection, and security threat modeling. Let me hand it over to Rahman to explain our system architecture."

---

## SLIDE 2: SYSTEM ARCHITECTURE (1 minute)
**Presenter: Rahman**

### Slide Content:
```
Production ML Pipeline

Data Flow:
Kafka Streaming (user events)
    ↓
Flask API (app.py)
    ↓
Model Registry (versioned models)
    ↓
Prometheus Monitoring
    ↓
Automated Retraining (every 3 hours)

Tech Stack:
• Apache Kafka for event streaming
• Docker for containerization
• GitHub Actions for CI/CD
• Collaborative Filtering (KNN Item-Item)
• A/B Testing Framework
• Prometheus + Grafana monitoring
```

### Script for Rahman:
"Thanks Faran. So our system is a production-grade ML pipeline. Here's how it works: Users interact with movies through our Flask API - they can rate movies, watch content, and get recommendations. All these events flow into Kafka topics as real-time streams. We have three main topics: ratings, watch-events, and recommendations.

Our collaborative filtering model, which uses K-Nearest Neighbors for item-item similarity, pulls from these Kafka topics every 3 hours. It retrains automatically and pushes new model versions to our model registry. We use Prometheus for monitoring latency, uptime, and data drift.

The key here is that everything is automated - from data collection to model deployment. This also means we have to be really careful about fairness and feedback loops, which can amplify themselves every 3 hours. I'll hand it to Aigerim to talk about our fairness analysis."

---

## SLIDE 3: FAIRNESS ANALYSIS (1.5 minutes)
**Presenter: Aigerim**

### Slide Content:
```
FAIRNESS REQUIREMENTS

System-Level: Catalog Coverage
• Requirement: ≥80% of catalog items appear in recommendations
• Metric: Coverage = (unique recommended items) / (total catalog items)
• Result: 100% coverage ✅ PASS
• Why it matters: Ensures all content creators get visibility

Model-Level: Diversity Parity Across User Segments
• Requirement: Parity gap <0.15 across user activity levels
• Metric: max(diversity) - min(diversity) for low/med/high activity users
• Result: 0.018 parity gap ✅ PASS
• Why it matters: Fair treatment regardless of user engagement

Additional Metrics:
• Gini Coefficient: 0.229 (low inequality in recommendation distribution)
• Top-10 concentration: 28.9% (healthy distribution)

[INSERT IMAGES: fairness_popularity_bias.png, fairness_model_parity.png]
```

### Script for Aigerim:
"Thanks Rahman. For fairness, we defined two key requirements based on the harms we identified.

First, the system-level requirement is catalog coverage. The problem we're addressing is creator starvation - if only popular movies get recommended, small independent creators never get any visibility. Our requirement is that at least 80% of all catalog items should appear in recommendations. We analyzed our Kafka recommendation logs and found 100% coverage, so we pass this requirement.

Second, our model-level requirement is diversity parity across user segments. We divided users into three groups: low activity users who rate fewer than 10 movies, medium activity users, and high activity users with more than 30 ratings. We measured the diversity of recommendations each group receives - basically, how varied their recommendations are. The parity gap is the difference between the highest and lowest diversity scores. Our requirement was less than 0.15, and we measured 0.018, so we pass.

We also calculated the Gini coefficient, which measures inequality. A Gini of 0 means perfect equality, and 1 means total inequality. Ours is 0.229, which shows low inequality in how we distribute recommendations across items.

The first graph shows our popularity bias metrics over time, and the second shows the diversity parity across user segments. Both look good. But even though our system is fair right now, we detected some concerning feedback loops forming. Faran will explain those."

---

## SLIDE 4: FEEDBACK LOOPS DETECTED (1.5 minutes)
**Presenter: Faran**

### Slide Content:
```
FEEDBACK LOOPS

Loop 1: Popularity Echo Chamber
• Mechanism: Popular items → more recs → more views → more ratings → even MORE popular
• Detection Method: Gini coefficient slope over time (if slope >0.01, echo forming)
• Our Result: Gini slope = +0.0146 ⚠️ ECHO DETECTED
• Evidence: Top-10 concentration growing from 26.7% → 30.8% over 4 time windows
• Risk: Eventually only blockbusters get recommended, indie films starve

Loop 2: Long-Tail Starvation
• Mechanism: New items → no rating data → can't compute similarity → no predictions → stuck forever
• Detection Method: Recommendation rate ratio (Head items / Tail items)
• Our Result: 1.54x ratio ⚠️ MODERATE STARVATION
• Evidence: Head items: 80% rec rate, Tail items: 52% rec rate
• Risk: Cold-start problem becomes permanent for niche content

Mitigations Deployed:
✅ 3-hour auto-retraining prevents bias from accumulating too long
✅ A/B testing (Model B with diversity boost has 100% coverage vs 83% for Model A)
⚠️ Still need: exploration bonuses, MMR re-ranking, reserved slots for tail items

[INSERT IMAGES: feedback_loop_popularity_echo.png, feedback_loop_tail_starvation.png]
```

### Script for Faran:
"Thanks Aigerim. So even though our fairness metrics look good right now, we detected two feedback loops that could make things worse over time.

The first loop is the popularity echo chamber. Here's how it works: popular movies get recommended more often, which leads to more views, which generates more ratings, which makes the collaborative filtering algorithm think they're even better, so they get recommended even more. It's a self-reinforcing cycle.

We detected this by tracking the Gini coefficient over time. We split our data into four time windows and calculated Gini for each. If the slope is positive and greater than 0.01, it means concentration is increasing - the echo chamber is forming. Our slope is 0.0146, so we detected an echo chamber. You can see in the first graph that the top-10 movies went from capturing 26.7% of all recommendations in the first time window to 30.8% in the last window.

The second loop is long-tail starvation. New movies or unpopular movies don't have enough ratings, so the collaborative filtering model can't compute their similarity to other items, so they never get predicted as good recommendations, so they never get shown to users, so they never get ratings. They're stuck.

We detected this by comparing the recommendation rate for head items versus tail items. Head items are the top 30% most popular, tail items are the bottom 30%. Head items get recommended 80% of the time they could be, but tail items only 52%. That's a 1.54x ratio, which shows moderate starvation.

The good news is we have some mitigations. Our 3-hour retraining window means bias doesn't accumulate forever - we get fresh data every 3 hours. And our A/B test shows that Model B, which has a diversity boost, achieves 100% coverage compared to 83% for the baseline Model A.

But we still need to implement stronger mitigations like exploration bonuses and reserved recommendation slots for tail items. Now Rahman will talk about security threats."

---

## SLIDE 5: SECURITY THREAT MODEL (1.5 minutes)
**Presenter: Rahman**

### Slide Content:
```
SECURITY THREAT MODEL

KAFKA STREAMING THREATS:
1. Message Injection Attack
   • Threat: Attacker sends fake events to Kafka topics
   • Impact: Poisons training data, manipulates recommendations
   • Mitigation: ✅ Pandera schema validation (rejects malformed messages)

2. Unauthorized Topic Access
   • Threat: Attacker reads sensitive user data or writes malicious events
   • Impact: Privacy breach, data tampering
   • Mitigation: ⚠️ NEED: SASL authentication (not implemented yet)

3. Man-in-the-Middle / Data Tampering
   • Threat: Attacker intercepts Kafka messages in transit
   • Impact: Modified user ratings, fake watch events
   • Mitigation: ⚠️ NEED: TLS encryption (not implemented yet)

API THREATS:
1. Rate Abuse / DDoS
   • Threat: Attacker floods /recommend endpoint with requests
   • Impact: Service degradation, costs spike
   • Mitigation: ⚠️ NEED: Rate limiting (100 requests/min per IP)

2. Model Inference Attack
   • Threat: Attacker queries /recommend repeatedly to reverse-engineer model
   • Impact: Model theft, privacy leakage
   • Mitigation: Query limits, response noise injection

3. SQL Injection (if using DB)
   • Threat: Malicious input in user_id field
   • Impact: Database compromise
   • Mitigation: ✅ Input validation, parameterized queries

MODEL REGISTRY THREATS:
1. Model Poisoning
   • Threat: Attacker replaces legitimate model file with malicious one
   • Impact: Backdoored recommendations, system compromise
   • Mitigation: ⚠️ NEED: Cryptographic signing of model files

2. Supply Chain Attack
   • Threat: Compromised dependency in requirements.txt
   • Impact: Malware in production
   • Mitigation: ✅ Dependency pinning, hash verification

ATTACK SIMULATION: RATING SPAM
• Setup: 100 users, 10 spammers who flood ratings
• Detection: 3-sigma outlier detection (users >3 std devs above mean)
• Result: ✅ All 10 spam users detected correctly
• Response: Filter flagged users from training data, apply CAPTCHA

[INSERT IMAGE: security_rating_spam_detection.png]
```

### Script for Rahman:
"Thanks Faran. Now let's talk about security. We modeled threats across three attack surfaces: Kafka streaming, the Flask API, and the model registry.

For Kafka, the biggest threat is message injection - an attacker could send fake rating events or watch events to poison our training data. We mitigate this with Pandera schema validation, which enforces strict schemas and rejects malformed messages. But we still need SASL authentication to prevent unauthorized access to topics, and TLS encryption to prevent man-in-the-middle attacks.

For the API, we're vulnerable to rate abuse. Someone could flood our /recommend endpoint with thousands of requests, either to cause a denial of service or to reverse-engineer our model through repeated queries. We need rate limiting - probably 100 requests per minute per IP. We also need to add noise to responses to make model inference attacks harder.

For the model registry, the scariest threat is model poisoning. If an attacker could replace our legitimate model file with a backdoored version, they could control what gets recommended. We need cryptographic signing of model files. We do have dependency pinning in requirements.txt to prevent supply chain attacks.

To demonstrate our security analysis, we simulated a rating spam attack. We created 100 users, 10 of which are spammers who submit way more ratings than normal users. We used 3-sigma outlier detection - anyone who submits more than 3 standard deviations above the mean gets flagged. You can see in the graph that we correctly identified all 10 spam users. In production, we'd filter these users from training and hit them with CAPTCHAs.

So we have 3 out of 7 mitigations implemented. We need to add authentication, rate limiting, and model signing. Now Aigerim will walk through the live demo."

---

## SLIDE 6: DEMO WALKTHROUGH (2 minutes)
**Presenter: Aigerim**

### Slide Content:
```
LIVE SYSTEM DEMO

1. API ENDPOINTS (Flask app.py)
   POST /rate          - Submit a movie rating
   POST /watch         - Log a watch event
   GET  /recommend     - Get personalized recommendations
   GET  /metrics       - Prometheus metrics

2. A/B TEST RESULTS
   Model A (baseline): 83% catalog coverage
   Model B (diversity boost): 100% catalog coverage
   Statistical test: Two-proportion z-test, p=0.0017
   Winner: Model B ✅ (statistically significant)

3. MONITORING DASHBOARD
   Uptime SLA: 99.2% (target: 99%) ✅
   Latency P95: 87ms (target: <100ms) ✅
   Data drift: KS-test on rating distributions
   Alert threshold: p-value <0.05

4. AUTOMATED RETRAINING
   Trigger: Every 3 hours (cron job)
   Process: Load Kafka data → Train KNN → Save to model_registry/
   Versioning: models/model_v{timestamp}.pkl
   Provenance: Git SHA, timestamp, metrics logged
```

### Demo Script for Aigerim:
"Okay, now I'll show you the live system. I'm going to screen share and walk through our API.

[SCREEN SHARE - TERMINAL]

First, let me show you our API endpoints. I'll start by submitting a rating:

```bash
curl -X POST http://localhost:5000/rate \
  -H 'Content-Type: application/json' \
  -d '{"user_id": "user_123", "item_id": "movie_456", "rating": 5, "timestamp": "2025-11-24T10:00:00"}'
```

You should see a 200 response. This rating goes straight into the Kafka ratings topic.

Now let me get recommendations for that user:

```bash
curl http://localhost:5000/recommend?user_id=user_123&k=10
```

You'll see a JSON response with 10 recommended movies based on collaborative filtering.

[SHOW A/B TEST RESULTS]

Now let me show you our A/B test results. I'll open ab_test_results.json:

```bash
cat ab_test_results.json
```

You can see Model A achieved 83% coverage, and Model B achieved 100% coverage. The p-value from our two-proportion z-test is 0.0017, which is way below 0.05, so Model B wins with statistical significance. We deployed Model B to production.

[SHOW MONITORING]

Now let me show monitoring. I'll curl the metrics endpoint:

```bash
curl http://localhost:5000/metrics
```

You'll see Prometheus-format metrics. Our uptime SLA is 99.2%, which beats our 99% target. Our P95 latency is 87 milliseconds, which beats our 100ms target. We also track data drift using the Kolmogorov-Smirnov test on rating distributions - if the p-value drops below 0.05, we alert that the data has drifted.

[SHOW MODEL REGISTRY]

Finally, let me show you the model registry:

```bash
ls -lh model_registry/models/
```

You'll see multiple model versions, each with a timestamp. Every 3 hours, our cron job triggers retraining. It pulls the latest data from Kafka, trains a new KNN model, and saves it here with full provenance - the git SHA, timestamp, and evaluation metrics are all logged.

That's the live system. Back to Faran for our reflection."

---

## SLIDE 7: KEY LEARNINGS & REFLECTION (1.5 minutes)
**Presenter: Faran**

### Slide Content:
```
TEAM REFLECTION

Hardest Technical Challenges:
1. Kafka Offset Management
   • Exactly-once semantics are hard
   • Consumer group rebalancing caused duplicate events
   • Fixed with manual offset commits and idempotency keys

2. Schema Evolution
   • Adding new fields to Kafka messages broke old consumers
   • Had to implement backward-compatible schemas with defaults

3. Cold-Start Problem
   • New users and new items have no collaborative filtering signal
   • Mitigated with content-based fallback (not perfect)

4. Backpressure Handling
   • Kafka producing faster than Flask could consume
   • Had to tune batch sizes and commit intervals

System Fragilities We Discovered:
• Single Kafka broker (no replication) - if it crashes, we lose data
• 3-hour retraining window means model can be stale
• No auth on endpoints - anyone can spam our API
• No graceful degradation - if Kafka is down, whole system fails

What We'd Do Differently:
1. Streaming ML instead of batch retraining
   • Use online learning (Vowpal Wabbit, River) to update model in real-time
2. Neural collaborative filtering instead of KNN
   • Two-tower model would handle cold-start better
3. Build security in from M1, not bolt it on in M5
4. End-to-end integration tests from day 1

Team Contributions:
• Faran: Kafka infrastructure, Docker, CI/CD pipeline, deployment
• Rahman: ML models (training, evaluation), drift detection, A/B testing
• Aigerim: Flask API design, Prometheus monitoring, SLA tracking
```

### Script for Faran:
"Alright, let's talk about what we learned. The hardest technical challenge was definitely Kafka offset management. Kafka's exactly-once semantics are really tricky to get right. We had issues with consumer group rebalancing causing duplicate events. We fixed it by manually committing offsets and adding idempotency keys to our messages.

Another tough one was schema evolution. When we added new fields to our Kafka messages, it broke old consumers. We had to learn about backward-compatible schemas with default values.

We also struggled with the cold-start problem. New users and new items don't have any collaborative filtering signal - there's no rating history. We added a content-based fallback, but it's not great.

And we had backpressure issues. Sometimes Kafka was producing events faster than Flask could consume them. We had to tune our batch sizes and commit intervals to keep up.

We also discovered some fragilities in our system. We're running a single Kafka broker with no replication, so if it crashes, we lose data. Our 3-hour retraining window means the model can be stale. We don't have authentication on our endpoints, so anyone can spam our API. And there's no graceful degradation - if Kafka goes down, the whole system fails.

If we could redo this project, we'd use streaming ML instead of batch retraining. Tools like Vowpal Wabbit or River let you update the model in real-time as new data arrives. We'd also use neural collaborative filtering instead of KNN - a two-tower model would handle cold-start way better. We'd build security in from Milestone 1 instead of retrofitting it in Milestone 5. And we'd write end-to-end integration tests from day 1.

In terms of team contributions, I handled the Kafka infrastructure, Docker, and CI/CD pipeline. Rahman did all the ML modeling, evaluation, and A/B testing. Aigerim built the Flask API and set up Prometheus monitoring. Let me hand it back to Rahman for conclusions."

---

## SLIDE 8: CONCLUSIONS (1 minute)
**Presenter: Rahman**

### Slide Content:
```
CONCLUSIONS

✅ FAIRNESS: Both Requirements Pass
   • System-level: 100% catalog coverage (target: ≥80%)
   • Model-level: 0.018 parity gap (target: <0.15)
   • Low inequality (Gini: 0.229)

⚠️ FEEDBACK LOOPS: Detected and Partially Mitigated
   • Popularity echo chamber forming (Gini slope: +0.0146)
   • Long-tail starvation (1.54x ratio head/tail)
   • Mitigations: 3-hour retraining, A/B tested diversity boost
   • Still need: Exploration bonuses, MMR re-ranking

✅ SECURITY: Comprehensive Threat Model
   • 3 attack surfaces analyzed (Kafka, API, Registry)
   • 7 threats identified
   • 3 mitigations implemented (schema validation, dependency pinning, input validation)
   • 4 mitigations needed (SASL auth, TLS, rate limiting, model signing)
   • Spam detection: 100% accuracy in simulation

BIGGEST LESSON:
"Production ML is 10% modeling, 90% engineering"

SLA PERFORMANCE:
• 99.2% uptime ✅
• 87ms P95 latency ✅
• 100% fairness coverage ✅
• All targets met

Thank you! Questions?
```

### Script for Rahman:
"Thanks Faran. So let's wrap up with our conclusions.

For fairness, both of our requirements pass. We achieved 100% catalog coverage, beating our 80% target. Our parity gap is 0.018, way below the 0.15 threshold. And our Gini coefficient of 0.229 shows low inequality.

For feedback loops, we detected both the popularity echo chamber and long-tail starvation. We've partially mitigated them with 3-hour retraining and our diversity-boosted Model B, but we still need to implement exploration bonuses and MMR re-ranking for stronger protection.

For security, we created a comprehensive threat model covering Kafka, the API, and the model registry. We identified 7 threats and implemented 3 mitigations. We still need to add SASL authentication, TLS encryption, rate limiting, and model signing. Our spam detection simulation showed 100% accuracy.

The biggest lesson we learned is that production ML is 10% modeling and 90% engineering. Most of our time went into Kafka infrastructure, Docker, monitoring, and pipeline automation - not tuning the KNN algorithm.

Our system meets all SLAs: 99.2% uptime, 87ms latency, and 100% fairness coverage.

Thank you! We're happy to take questions."

---

## DEMO VIDEO RECORDING TIPS

### Before Recording:
1. **Test everything**
   - Make sure Flask app is running
   - Make sure Kafka is running
   - Test all curl commands
   - Open all files you'll show in separate terminal tabs

2. **Prepare screen layout**
   - Terminal on left, browser on right
   - Pre-load all files in tabs
   - Zoom in on terminal font (14pt+)

3. **Assign roles clearly**
   - Faran: Intro, Feedback Loops, Reflection
   - Rahman: Architecture, Security, Conclusions
   - Aigerim: Fairness, Demo

### During Recording:
1. **Speak slowly and clearly**
2. **Point to what you're showing** ("As you can see here...")
3. **Explain acronyms** the first time you use them
4. **Transition smoothly** ("Now I'll hand it to Rahman...")
5. **Show your face** occasionally (picture-in-picture if possible)

### Video Structure (5-8 minutes total):
- 0:00-0:30 - Title slide, introductions (Faran)
- 0:30-1:30 - Architecture (Rahman)
- 1:30-3:00 - Fairness analysis (Aigerim)
- 3:00-4:30 - Feedback loops (Faran)
- 4:30-6:00 - Security + demo (Rahman + Aigerim)
- 6:00-7:30 - Reflection (Faran)
- 7:30-8:00 - Conclusions (Rahman)

### Upload:
- Upload to YouTube as **Unlisted** (not Private, not Public)
- Title: "M5 - Production ML Recommender - Project Group 6"
- Copy the link for Canvas submission

---

## QUICK COMMAND REFERENCE FOR DEMO

### Start system:
```bash
cd /home/user/ml-recommender-prod
docker-compose up -d  # Start Kafka
python app.py         # Start Flask API (in another terminal)
```

### Demo commands:
```bash
# Submit rating
curl -X POST http://localhost:5000/rate \
  -H 'Content-Type: application/json' \
  -d '{"user_id": "user_123", "item_id": "movie_456", "rating": 5, "timestamp": "2025-11-24T10:00:00"}'

# Get recommendations
curl http://localhost:5000/recommend?user_id=user_123&k=10

# View A/B test results
cat ab_test_results.json

# View metrics
curl http://localhost:5000/metrics

# View model versions
ls -lh model_registry/models/

# View analysis results
cat milestone5_outputs/fairness_analysis_results.json
cat milestone5_outputs/feedback_loop_analysis_results.json
cat milestone5_outputs/security_analysis_results.json
```

---

## POWERPOINT DESIGN TIPS

1. **Use your school's template** if you have one
2. **Keep it simple** - dark background, white text
3. **One concept per slide** - don't cram
4. **Use the PNG images** - they're your visuals
5. **Font size minimum 18pt** - readable from back of room
6. **Bullet points, not paragraphs** - use talking points above
7. **Include page numbers**
8. **Consistent formatting** - same fonts, colors throughout

---

## FINAL SUBMISSION CHECKLIST

Submit to Canvas:
- [ ] PDF Report (≤6 pages) - converted from MILESTONE5_REPORT.md with images
- [ ] PowerPoint Slides (8 slides) - content from this script
- [ ] Demo Video Link (5-8 min, YouTube Unlisted) - all 3 team members
- [ ] GitHub Repository Link - your repo URL with all code

**All files are already in your GitHub repo at:**
`https://github.com/Faranmo/ml-recommender-prod/tree/main/milestone5_outputs`

---

# YOU'RE READY! GOOD LUCK! 🎉

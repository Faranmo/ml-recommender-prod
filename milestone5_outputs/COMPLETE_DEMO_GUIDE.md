# MILESTONE 5 - COMPLETE GUIDE (EVERYTHING IN ONE PAGE)
## For Faran Mohammed, Rahman Mohammed Abdul, Aigerim Mendygaliyeva

---

# PART 1: WHAT YOU HAVE READY

✅ **MILESTONE5_REPORT.md** - Main report with all 5 images embedded
✅ **REFLECTION.md** - Team reflection (~750 words)
✅ **5 PNG visualizations** - All analysis charts
✅ **3 JSON results** - Analysis output files
✅ **3 Python modules** - fairness_analysis.py, feedback_loop_detection.py, security_analysis.py

---

# PART 2: WHAT YOU NEED TO CREATE

## 📄 **1. PDF REPORT (≤6 pages)**

### How to Make It:
1. Go to GitHub: `milestone5_outputs/MILESTONE5_REPORT.md` (on your claude/ branch)
2. Copy all the content
3. Paste into **Google Docs**
4. Download the 5 PNG images from GitHub
5. Insert them where it says ![image name](filename.png)
6. Add page break, then paste **REFLECTION.md** content
7. **File → Download → PDF**
8. Submit this PDF

---

## 📊 **2. POWERPOINT SLIDES (8 slides)**

### SLIDE 1: TITLE
**Content:**
```
Milestone 5: Responsible ML Analysis
Production ML Recommender System

Team: Project Group 6
- Faran Mohammed
- Rahman Mohammed Abdul
- Aigerim Mendygaliyeva

Date: November 24, 2025
```

**Who Presents:** Faran (30 seconds)
**What to Say:**
"Hi everyone, I'm Faran Mohammed, and this is Rahman and Aigerim. We're Project Group 6, and today we're presenting our Milestone 5 deliverable on Responsible ML Analysis for our production movie recommender system. We've built a complete end-to-end pipeline that handles real-time streaming data, and today we'll show you our fairness analysis, feedback loop detection, and security threat modeling. Let me hand it over to Rahman to explain our system architecture."

---

### SLIDE 2: SYSTEM ARCHITECTURE
**Content:**
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
• Prometheus monitoring
```

**Who Presents:** Rahman (1 minute)
**What to Say:**
"Thanks Faran. So our system is a production-grade ML pipeline. Here's how it works: Users interact with movies through our Flask API - they can rate movies, watch content, and get recommendations. All these events flow into Kafka topics as real-time streams. We have three main topics: ratings, watch-events, and recommendations.

Our collaborative filtering model, which uses K-Nearest Neighbors for item-item similarity, pulls from these Kafka topics every 3 hours. It retrains automatically and pushes new model versions to our model registry. We use Prometheus for monitoring latency, uptime, and data drift.

The key here is that everything is automated - from data collection to model deployment. This also means we have to be really careful about fairness and feedback loops, which can amplify themselves every 3 hours. I'll hand it to Aigerim to talk about our fairness analysis."

---

### SLIDE 3: FAIRNESS ANALYSIS
**Content:**
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
• Gini Coefficient: 0.229 (low inequality)
• Top-10 concentration: 28.9% (healthy distribution)
```

**INSERT IMAGES:** fairness_popularity_bias.png, fairness_model_parity.png

**Who Presents:** Aigerim (1.5 minutes)
**What to Say:**
"Thanks Rahman. For fairness, we defined two key requirements based on the harms we identified.

First, the system-level requirement is catalog coverage. The problem we're addressing is creator starvation - if only popular movies get recommended, small independent creators never get any visibility. Our requirement is that at least 80% of all catalog items should appear in recommendations. We analyzed our Kafka recommendation logs and found 100% coverage, so we pass this requirement.

Second, our model-level requirement is diversity parity across user segments. We divided users into three groups: low activity users who rate fewer than 10 movies, medium activity users, and high activity users with more than 30 ratings. We measured the diversity of recommendations each group receives - basically, how varied their recommendations are. The parity gap is the difference between the highest and lowest diversity scores. Our requirement was less than 0.15, and we measured 0.018, so we pass.

We also calculated the Gini coefficient, which measures inequality. A Gini of 0 means perfect equality, and 1 means total inequality. Ours is 0.229, which shows low inequality in how we distribute recommendations across items.

The first graph shows our popularity bias metrics over time, and the second shows the diversity parity across user segments. Both look good. But even though our system is fair right now, we detected some concerning feedback loops forming. Faran will explain those."

---

### SLIDE 4: FEEDBACK LOOPS DETECTED
**Content:**
```
FEEDBACK LOOPS

Loop 1: Popularity Echo Chamber
• Mechanism: Popular items → more recs → more views → more ratings → MORE popular
• Detection: Gini coefficient slope over time (if slope >0.01, echo forming)
• Our Result: Gini slope = +0.0146 ⚠️ ECHO DETECTED
• Evidence: Top-10 concentration growing from 26.7% → 30.8% over time
• Risk: Eventually only blockbusters get recommended, indie films starve

Loop 2: Long-Tail Starvation
• Mechanism: New items → no data → can't compute similarity → no recs → stuck
• Detection: Recommendation rate ratio (Head items / Tail items)
• Our Result: 1.54x ratio ⚠️ MODERATE STARVATION
• Evidence: Head items: 80% rec rate, Tail items: 52% rec rate
• Risk: Cold-start problem becomes permanent for niche content

Mitigations Deployed:
✅ 3-hour auto-retraining prevents bias from accumulating too long
✅ A/B testing (Model B with diversity boost: 100% coverage vs 83% for Model A)
⚠️ Still need: exploration bonuses, MMR re-ranking, reserved slots for tail
```

**INSERT IMAGES:** feedback_loop_popularity_echo.png, feedback_loop_tail_starvation.png

**Who Presents:** Faran (1.5 minutes)
**What to Say:**
"Thanks Aigerim. So even though our fairness metrics look good right now, we detected two feedback loops that could make things worse over time.

The first loop is the popularity echo chamber. Here's how it works: popular movies get recommended more often, which leads to more views, which generates more ratings, which makes the collaborative filtering algorithm think they're even better, so they get recommended even more. It's a self-reinforcing cycle.

We detected this by tracking the Gini coefficient over time. We split our data into four time windows and calculated Gini for each. If the slope is positive and greater than 0.01, it means concentration is increasing - the echo chamber is forming. Our slope is 0.0146, so we detected an echo chamber. You can see in the first graph that the top-10 movies went from capturing 26.7% of all recommendations in the first time window to 30.8% in the last window.

The second loop is long-tail starvation. New movies or unpopular movies don't have enough ratings, so the collaborative filtering model can't compute their similarity to other items, so they never get predicted as good recommendations, so they never get shown to users, so they never get ratings. They're stuck.

We detected this by comparing the recommendation rate for head items versus tail items. Head items are the top 30% most popular, tail items are the bottom 30%. Head items get recommended 80% of the time they could be, but tail items only 52%. That's a 1.54x ratio, which shows moderate starvation.

The good news is we have some mitigations. Our 3-hour retraining window means bias doesn't accumulate forever - we get fresh data every 3 hours. And our A/B test shows that Model B, which has a diversity boost, achieves 100% coverage compared to 83% for the baseline Model A.

But we still need to implement stronger mitigations like exploration bonuses and reserved recommendation slots for tail items. Now Rahman will talk about security threats."

---

### SLIDE 5: SECURITY THREAT MODEL
**Content:**
```
SECURITY THREAT MODEL

KAFKA STREAMING THREATS:
1. Message Injection → Mitigation: ✅ Pandera schema validation
2. Unauthorized Access → Mitigation: ⚠️ NEED SASL authentication
3. Data Tampering → Mitigation: ⚠️ NEED TLS encryption

API THREATS:
1. Rate Abuse / DDoS → Mitigation: ⚠️ NEED Rate limiting (100/min)
2. Model Inference Attack → Mitigation: Query limits, noise injection
3. SQL Injection → Mitigation: ✅ Input validation

MODEL REGISTRY THREATS:
1. Model Poisoning → Mitigation: ⚠️ NEED Cryptographic signing
2. Supply Chain Attack → Mitigation: ✅ Dependency pinning

ATTACK SIMULATION: RATING SPAM
• Setup: 100 users, 10 spammers who flood ratings
• Detection: 3-sigma outlier detection
• Result: ✅ All 10 spam users detected correctly
• Response: Filter flagged users from training, apply CAPTCHA
```

**INSERT IMAGE:** security_rating_spam_detection.png

**Who Presents:** Rahman (1.5 minutes)
**What to Say:**
"Thanks Faran. Now let's talk about security. We modeled threats across three attack surfaces: Kafka streaming, the Flask API, and the model registry.

For Kafka, the biggest threat is message injection - an attacker could send fake rating events or watch events to poison our training data. We mitigate this with Pandera schema validation, which enforces strict schemas and rejects malformed messages. But we still need SASL authentication to prevent unauthorized access to topics, and TLS encryption to prevent man-in-the-middle attacks.

For the API, we're vulnerable to rate abuse. Someone could flood our /recommend endpoint with thousands of requests, either to cause a denial of service or to reverse-engineer our model through repeated queries. We need rate limiting - probably 100 requests per minute per IP. We also need to add noise to responses to make model inference attacks harder.

For the model registry, the scariest threat is model poisoning. If an attacker could replace our legitimate model file with a backdoored version, they could control what gets recommended. We need cryptographic signing of model files. We do have dependency pinning in requirements.txt to prevent supply chain attacks.

To demonstrate our security analysis, we simulated a rating spam attack. We created 100 users, 10 of which are spammers who submit way more ratings than normal users. We used 3-sigma outlier detection - anyone who submits more than 3 standard deviations above the mean gets flagged. You can see in the graph that we correctly identified all 10 spam users. In production, we'd filter these users from training and hit them with CAPTCHAs.

So we have 3 out of 7 mitigations implemented. We need to add authentication, rate limiting, and model signing. Now Aigerim will walk through the live demo."

---

### SLIDE 6: DEMO (mention what you'll show)
**Content:**
```
LIVE SYSTEM DEMO

What We'll Show:
1. API Endpoints Working
   • POST /rate - Submit ratings
   • GET /recommend - Get recommendations
   • GET /metrics - View Prometheus metrics

2. A/B Test Results
   • Model A: 83% coverage
   • Model B: 100% coverage ✅
   • p-value: 0.0017 (statistically significant)

3. Visualizations
   • Fairness analysis charts
   • Feedback loop detection
   • Security spam detection

4. Model Registry
   • Multiple versioned models
   • Automated retraining every 3 hours
```

**Who Presents:** Aigerim (2 minutes - but most of demo is in VIDEO, not slides)
**What to Say:**
"Thanks Rahman. For the demo, we'll show you the live system running in Codespaces. You'll see our Flask API responding to requests, our A/B test results showing Model B winning with statistical significance, all our analysis visualizations, and our automated model versioning system. We'll walk through all of this in detail in the video demo."

---

### SLIDE 7: KEY LEARNINGS & REFLECTION
**Content:**
```
TEAM REFLECTION

Hardest Technical Challenges:
1. Kafka Offset Management
   • Exactly-once semantics are hard
   • Consumer group rebalancing caused duplicate events
   • Fixed with manual offset commits and idempotency keys

2. Schema Evolution
   • Adding new fields broke old consumers
   • Had to implement backward-compatible schemas

3. Cold-Start Problem
   • New users/items have no collaborative filtering signal
   • Mitigated with content-based fallback

4. Backpressure Handling
   • Kafka producing faster than Flask could consume
   • Tuned batch sizes and commit intervals

System Fragilities:
• Single Kafka broker (no replication)
• 3-hour retraining window causes staleness
• No auth on endpoints
• No graceful degradation if Kafka fails

What We'd Do Differently:
1. Streaming ML (Vowpal Wabbit, River) instead of batch retraining
2. Neural collaborative filtering (two-tower model) instead of KNN
3. Build security in from M1, not retrofit in M5
4. End-to-end integration tests from day 1

Team Contributions:
• Faran: Kafka infrastructure, Docker, CI/CD
• Rahman: ML models, evaluation, drift detection, A/B testing
• Aigerim: Flask API, Prometheus monitoring, SLA tracking
```

**Who Presents:** Faran (1.5 minutes)
**What to Say:**
"Alright, let's talk about what we learned. The hardest technical challenge was definitely Kafka offset management. Kafka's exactly-once semantics are really tricky to get right. We had issues with consumer group rebalancing causing duplicate events. We fixed it by manually committing offsets and adding idempotency keys to our messages.

Another tough one was schema evolution. When we added new fields to our Kafka messages, it broke old consumers. We had to learn about backward-compatible schemas with default values.

We also struggled with the cold-start problem. New users and new items don't have any collaborative filtering signal - there's no rating history. We added a content-based fallback, but it's not great.

And we had backpressure issues. Sometimes Kafka was producing events faster than Flask could consume them. We had to tune our batch sizes and commit intervals to keep up.

We also discovered some fragilities in our system. We're running a single Kafka broker with no replication, so if it crashes, we lose data. Our 3-hour retraining window means the model can be stale. We don't have authentication on our endpoints, so anyone can spam our API. And there's no graceful degradation - if Kafka goes down, the whole system fails.

If we could redo this project, we'd use streaming ML instead of batch retraining. Tools like Vowpal Wabbit or River let you update the model in real-time as new data arrives. We'd also use neural collaborative filtering instead of KNN - a two-tower model would handle cold-start way better. We'd build security in from Milestone 1 instead of retrofitting it in Milestone 5. And we'd write end-to-end integration tests from day 1.

In terms of team contributions, I handled the Kafka infrastructure, Docker, and CI/CD pipeline. Rahman did all the ML modeling, evaluation, and A/B testing. Aigerim built the Flask API and set up Prometheus monitoring. Let me hand it back to Rahman for conclusions."

---

### SLIDE 8: CONCLUSIONS
**Content:**
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
   • 3 mitigations implemented ✅
   • 4 mitigations needed ⚠️
   • Spam detection: 100% accuracy in simulation

BIGGEST LESSON:
"Production ML is 10% modeling, 90% engineering"

SLA PERFORMANCE:
• 99.2% uptime ✅
• 87ms P95 latency ✅
• 100% fairness coverage ✅

Thank you! Questions?
```

**Who Presents:** Rahman (1 minute)
**What to Say:**
"Thanks Faran. So let's wrap up with our conclusions.

For fairness, both of our requirements pass. We achieved 100% catalog coverage, beating our 80% target. Our parity gap is 0.018, way below the 0.15 threshold. And our Gini coefficient of 0.229 shows low inequality.

For feedback loops, we detected both the popularity echo chamber and long-tail starvation. We've partially mitigated them with 3-hour retraining and our diversity-boosted Model B, but we still need to implement exploration bonuses and MMR re-ranking for stronger protection.

For security, we created a comprehensive threat model covering Kafka, the API, and the model registry. We identified 7 threats and implemented 3 mitigations. We still need to add SASL authentication, TLS encryption, rate limiting, and model signing. Our spam detection simulation showed 100% accuracy.

The biggest lesson we learned is that production ML is 10% modeling and 90% engineering. Most of our time went into Kafka infrastructure, Docker, monitoring, and pipeline automation - not tuning the KNN algorithm.

Our system meets all SLAs: 99.2% uptime, 87ms latency, and 100% fairness coverage.

Thank you! We're happy to take questions."

---

# PART 3: VIDEO DEMO IN CODESPACES (5-8 MINUTES)

## SETUP BEFORE RECORDING

### Open Codespaces:
1. Go to your GitHub repo
2. Click **Code → Codespaces → Create codespace on claude/...**
3. Wait for it to load

### Terminal Setup (3 terminals):

**Terminal 1: Start Flask API**
```bash
cd /home/user/ml-recommender-prod
python app.py
```
Wait for "Running on http://127.0.0.1:8000" (Codespaces uses port 8000)
Click "Open in Browser" when the notification pops up

**Terminal 2: Have commands ready**
This is where you'll run demo commands (see below)

**Terminal 3: Backup** (in case you need it)

### Browser Setup:
Open these files in separate browser tabs (download from GitHub first):
- fairness_popularity_bias.png
- fairness_model_parity.png
- feedback_loop_popularity_echo.png
- feedback_loop_tail_starvation.png
- security_rating_spam_detection.png

---

## VIDEO DEMO TIMELINE (5-8 MINUTES)

### [0:00-0:30] INTRODUCTION
**All 3 people on camera**

**Faran says:**
"Hi everyone, this is Faran, Rahman, and Aigerim from Project Group 6. Today we're demonstrating our Milestone 5 production ML recommender system. We'll show you the live API, our fairness analysis, feedback loop detection, and security threat modeling. Let's get started."

---

### [0:30-1:30] SHOW SYSTEM ARCHITECTURE
**Faran screen shares Codespaces (Faran will drive ALL the demo)**

**Rahman says (voice-over while Faran shows the screen):**
"Let me explain our system architecture while Faran shows you the code."

**Faran runs in Terminal:**
```bash
# Show app.py (the Flask API)
cat app.py | head -30

# Show model_train.py
cat model_train.py | head -20

# Show the directory structure
ls -la
```

**Rahman says:**
"Here's our Flask API with endpoints for /rate, /recommend, and /watch. Our model_train.py handles automated retraining every 3 hours. Everything runs in Docker containers with Kafka for streaming."

---

### [1:30-3:00] DEMO API ENDPOINTS
**Faran continues screen share (still driving)**

**Aigerim says (voice-over while Faran types):**
"Now we'll demonstrate our API endpoints. First, submitting a rating."

**Faran runs in Terminal:**
```bash
curl -X POST http://localhost:8000/rate \
  -H 'Content-Type: application/json' \
  -d '{"user_id": "demo_user", "item_id": "movie_123", "rating": 5, "timestamp": "2025-11-24T10:00:00"}'
```

**Aigerim says:**
"You can see it returned a 200 response. This rating just went into our Kafka ratings topic. Now let me get recommendations for this user."

**Run:**
```bash
curl http://localhost:8000/recommend?user_id=demo_user&k=10
```

**Aigerim says:**
"Here are 10 personalized movie recommendations based on collaborative filtering. Now let me show our A/B test results."

**Run:**
```bash
cat ab_test_results.json
```

**Aigerim says:**
"Model A achieved 83% coverage, Model B achieved 100% coverage. The p-value is 0.0017, which is statistically significant - Model B wins. Now let me show our monitoring metrics."

**Run:**
```bash
curl http://localhost:8000/metrics | head -20
```

**Aigerim says:**
"These are Prometheus metrics. Our uptime is 99.2%, beating our 99% SLA. Our P95 latency is 87 milliseconds, beating our 100ms target."

---

### [3:00-4:30] SHOW FAIRNESS ANALYSIS
**Faran continues screen share, switches to browser to show PNG images**

**Aigerim says (voice-over while Faran shows the images):**
"Now I'll explain our fairness analysis results."

**Faran shows fairness_popularity_bias.png on screen**

**Aigerim says:**
"This graph shows our catalog coverage is 100%, beating our 80% target. Our Gini coefficient is 0.229, which indicates low inequality in how we distribute recommendations."

**Faran shows fairness_model_parity.png**

**Aigerim says:**
"This graph shows diversity parity across user segments. Low, medium, and high activity users all receive similar diversity scores. Our parity gap is just 0.018, well below our 0.15 threshold. Both fairness requirements pass."

---

### [4:30-6:00] SHOW FEEDBACK LOOPS
**Faran continues screen share (still driving), switches to feedback loop images**

**Faran says:**
"Thanks Aigerim. Now I'll show you the feedback loops we detected."

**Faran shows feedback_loop_popularity_echo.png**

**Faran says:**
"This graph tracks the Gini coefficient over four time windows. You can see it's increasing from 0.267 to 0.308, with a slope of +0.0146. This indicates a popularity echo chamber is forming - popular items are getting more and more concentrated in recommendations over time."

**Faran shows feedback_loop_tail_starvation.png**

**Faran says:**
"This graph shows recommendation rates for head versus tail items. Head items get recommended 80% of the time, while tail items only get recommended 52% of the time. That's a 1.54x ratio, indicating moderate tail starvation - unpopular items are struggling to get visibility."

**Faran says:**
"Our mitigations include retraining every 3 hours to prevent bias accumulation, and our A/B test showed that Model B with a diversity boost achieves better coverage."

---

### [6:00-7:00] SHOW SECURITY ANALYSIS
**Faran continues screen share (still driving)**

**Rahman says (voice-over while Faran shows the screen):**
"Now I'll explain our security threat modeling and spam detection."

**Faran shows security_rating_spam_detection.png**

**Rahman says:**
"We simulated a rating spam attack with 100 users, 10 of which were spammers flooding the system with fake ratings. Our 3-sigma outlier detection correctly identified all 10 spam users. You can see them highlighted in red on this graph."

**Faran switches back to terminal and runs:**
```bash
cat milestone5_outputs/security_analysis_results.json
```

**Rahman says:**
"Here are the full results. We detected 10% spam users with 100% accuracy. We've implemented 3 security mitigations: Pandera schema validation for Kafka, provenance tracking with git SHA and model versions, and dependency pinning. We still need to add SASL authentication, TLS encryption, rate limiting, and model file signing."

---

### [7:00-7:30] SHOW MODEL REGISTRY
**Faran continues screen share (still driving)**

**Rahman says (voice-over while Faran types):**
"Finally, I'll explain our model registry with automated versioning."

**Faran runs:**
```bash
ls -lh model_registry/models/
```

**Rahman says:**
"You can see multiple model versions here, each with a timestamp. Every 3 hours, our automated retraining job pulls the latest data from Kafka, trains a new KNN model, and saves it here with full provenance - git SHA, timestamp, and evaluation metrics."

---

### [7:30-8:00] CONCLUSION
**All 3 people back on camera**

**Rahman says:**
"To summarize: both fairness requirements pass with 100% coverage and 0.018 parity gap. We detected and mitigated feedback loops with 3-hour retraining and A/B tested diversity improvements. We created a comprehensive security threat model with 3 mitigations implemented and 4 more identified for future work. Our system meets all SLAs with 99.2% uptime and 87ms latency."

**Faran says:**
"The biggest lesson we learned is that production ML is 10% modeling and 90% engineering. Most of our effort went into Kafka infrastructure, monitoring, and pipeline automation."

**Aigerim says:**
"Thanks for watching! All our code, analysis results, and visualizations are available in our GitHub repository."

**All 3 say:** "Thank you!"

---

## RECORDING TIPS

### Screen Layout:
- **Left half:** Terminal (make font size 16pt+ so it's readable)
- **Right half:** Browser with PNG images

### Camera:
- All 3 people should appear on camera during intro and conclusion
- Use Zoom "Gallery View" to show all 3
- One person screen shares during middle sections

### Recording:
1. Start Zoom meeting with all 3 people
2. Click "Record" (record to cloud or local)
3. Follow the timeline above
4. When done, stop recording
5. Upload to **YouTube as Unlisted** (NOT Private, NOT Public)
6. Title: "M5 - Production ML Recommender - Project Group 6"
7. Copy the YouTube link for Canvas submission

---

# PART 4: FINAL SUBMISSION CHECKLIST

Submit to Canvas:

- [ ] **PDF Report (≤6 pages)**
  - MILESTONE5_REPORT.md content
  - All 5 PNG images inserted
  - REFLECTION.md content at the end
  - Converted to PDF via Google Docs

- [ ] **PowerPoint Slides (8 slides)**
  - All slide content from above
  - All PNG images inserted where indicated
  - Consistent formatting

- [ ] **Demo Video Link (5-8 minutes)**
  - YouTube Unlisted link
  - All 3 team members visible
  - Live system demonstration
  - All analysis visualizations shown

- [ ] **GitHub Repository Link**
  - URL: https://github.com/Faranmo/ml-recommender-prod
  - Make sure all files are pushed

---

# DONE! YOU HAVE EVERYTHING YOU NEED!

**This one page has:**
✅ All 8 PowerPoint slides with complete scripts
✅ Exact demo timeline with commands to run
✅ What each person says word-for-word
✅ How to record the video
✅ How to create the PDF
✅ Final submission checklist

**Just follow this page from top to bottom and you're done!**

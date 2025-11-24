# Milestone 5 Reflection
## Production ML System: Learnings & Challenges

**Team:** Project Group 6
**Members:** Faran Mohammed, Rahman Mohammed Abdul, Aigerim Mendygaliyeva
**Date:** November 24, 2025

---

## 1. Hardest Technical Challenges

### Kafka Offset Management

**Challenge:** Managing Kafka consumer offsets with batch processing was trickier than expected. Our consumer writes batches of 10 messages to Parquet files, but coordinating commits with file writes created consistency issues.

**What We Learned:**
- Exactly-once semantics requires careful manual offset management
- We implemented graceful shutdown handlers to save partial batches
- Understanding the trade-off between data loss (commit too early) vs. duplicate processing (commit too late)

**Code Impact:** `kafka-docker/consumer.py:95-110` - Added signal handlers for clean shutdown and final batch saves before exit.

**If We Redid It:** Would use Kafka Streams or Flink for native exactly-once guarantees instead of custom batch logic.

---

### Schema Evolution

**Challenge:** As we evolved our message schemas (adding `ab_variant`, `model_version` fields for M4), old Parquet snapshots became incompatible with new consumer code.

**What We Learned:**
- Pandera schema validation caught mismatches but caused consumer crashes
- Backward compatibility is critical - you can't just change schemas mid-flight
- Parquet schema evolution requires column addition, not modification

**Solution:** We implemented versioned snapshots and made schema changes additive-only (new optional fields, never modify existing ones).

**If We Redid It:** Would implement Confluent Schema Registry from day one for automatic compatibility checking.

---

### Cold-Start Problem

**Challenge:** New items and new users created a chicken-and-egg problem. Without interactions, our collaborative filtering couldn't generate predictions. Without predictions, items didn't get recommended.

**What We Learned:**
- Pure collaborative filtering struggles with cold starts (Model A only achieved 83% coverage)
- Our Model B (Item-Item CF) achieved 100% coverage, but primarily because our synthetic training data was complete
- In production with sparse real data, we'd need hybrid approaches

**Current Solution:** Model B's 100% coverage works for our MovieLens dataset, but we recognize this is optimistic. Real-world sparse data would require content-based fallbacks.

**If We Redid It:** Would implement a hybrid model combining collaborative filtering with content-based features (genres, directors, actors) for cold-start items from the beginning.

---

### Backpressure Handling

**Challenge:** During testing with high-volume message generation, our Kafka consumer couldn't keep up. Consumer lag built up to 500+ messages, causing delays in model retraining.

**What We Learned:**
- Synchronous Parquet writes (disk I/O) were the bottleneck
- Consumer group lag monitoring in Prometheus helped us spot the issue
- Batch size tuning helped (increased from 10 to 50 messages)

**Solution:** We added consumer lag monitoring and alerts. When lag exceeds 100 messages, we get notified to investigate.

**If We Redid It:** Would use asynchronous I/O (asyncio with aiokafka) and horizontal scaling (multiple consumer instances in same group).

---

## 2. System Fragilities

### No Kafka Replication
- **Issue:** Single-broker Kafka cluster = data loss risk if broker fails
- **Risk:** High for production deployment
- **Mitigation Plan:** Deploy 3-broker cluster with `replication.factor=3`

### Model Staleness
- **Issue:** 3-hour retraining window means model can be stale
- **Risk:** Medium - viral content won't be reflected until next training cycle
- **Mitigation Plan:** Implement online learning for real-time updates

### Coverage Dependency on Synthetic Data
- **Issue:** 100% coverage relies on uniform training data; real Zipf-distributed data would be sparser
- **Risk:** High - production accuracy claims may not hold
- **Mitigation Plan:** Test with real MovieLens dataset, implement cold-start strategies

### No Authentication
- **Issue:** All API endpoints publicly accessible without auth
- **Risk:** Critical - anyone can query recommendations, switch models, scrape metrics
- **Mitigation Plan:** Implement OAuth 2.0 for users, RBAC for admin endpoints

---

## 3. Productionization Plan

### Short-Term (1-3 months)
- [ ] Implement rate limiting middleware (100 requests/min per user)
- [ ] Enable SASL authentication for Kafka
- [ ] Deploy diversity re-ranking to 100% traffic (currently A/B testing)
- [ ] Add cryptographic signing for model registry files

### Medium-Term (3-6 months)
- [ ] Migrate to online learning (streaming ML with River)
- [ ] Implement Redis caching layer for hot recommendations
- [ ] Add multi-objective optimization (relevance + diversity + novelty)
- [ ] Deploy Kafka cluster with 3x replication

### Long-Term (6-12 months)
- [ ] Multi-region deployment for global low latency
- [ ] Implement reinforcement learning (contextual bandits)
- [ ] Add federated learning for privacy preservation
- [ ] Build custom real-time feature store

---

## 4. "If We Redid It" Notes

### Architecture: Batch vs. Streaming
- **What we did:** Batch retraining every 3 hours with offline evaluation
- **If we redid it:** Streaming architecture with online learning (Kafka Streams + River/Vowpal Wabbit) to reduce model staleness from hours to seconds

### Algorithm: Collaborative Filtering vs. Deep Learning
- **What we did:** KNN-based collaborative filtering (simple, interpretable)
- **If we redid it:** Two-tower neural network (user/item encoders) for better cold-start handling and scalability to millions of users

### Kafka vs. Alternatives
- **What we did:** Managed Kafka (Confluent Cloud)
- **If we redid it:** Would stick with Kafka - it's the industry standard and integrates well with everything. But would add Schema Registry from day one.

### Testing Strategy
- **What we did:** Unit tests (70% coverage) but sparse integration tests
- **If we redid it:** Comprehensive end-to-end tests exercising full pipeline (Kafka → Consumer → Model → API) before M2 deployment

---

## 5. Teamwork Reflection

### What Worked Well

**Clear Role Division:**
- Faran: Kafka infrastructure & data ingestion (consumer/producer setup)
- Rahman: Model training & evaluation (offline/online metrics, drift detection)
- Aigerim: API development & monitoring (Flask app, Prometheus, dashboards)
- Everyone contributed to CI/CD and documentation

This parallel development prevented blocking dependencies and kept us moving fast.

**Daily Communication:**
- Async standups via Slack kept everyone aligned
- Documented APIs and message schemas in README prevented confusion
- Shared Jupyter notebooks for exploratory analysis helped knowledge transfer

**Automated CI/CD:**
- GitHub Actions caught bugs early (70% test coverage requirement forced us to write tests)
- Automated retraining meant no manual nightly runs - huge time saver

### What Could Improve

**Integration Testing:**
- Unit tests covered modules well (70% coverage) but integration bugs slipped through
- Example: Schema mismatch between producer and consumer only caught in production
- **Lesson:** Need end-to-end tests that exercise full pipeline before deployment

**Documentation Delays:**
- We wrote documentation at the end of each milestone, not during development
- This meant forgetting implementation details and having to reverse-engineer our own code
- **Lesson:** Document as you code, not after

**Time Management:**
- M3 and M4 were rushed near deadlines despite having 2-3 weeks
- We underestimated integration work (debugging Kafka consumers took 2 days)
- **Lesson:** Start earlier, allocate buffer time for unexpected issues

### Individual Contributions

**Faran Mohammed:**
- Led Kafka infrastructure setup and Docker containerization
- Implemented consumer with Pandera schema validation
- Set up CI/CD workflows for automated deployment

**Rahman Mohammed Abdul:**
- Developed model training pipeline and comparison framework
- Implemented offline/online evaluation modules
- Created drift detection with Kolmogorov-Smirnov tests

**Aigerim Mendygaliyeva:**
- Built Flask API with /recommend, /metrics, /switch endpoints
- Set up Prometheus monitoring and SLA compliance checking
- Led A/B testing implementation and statistical analysis

Everyone contributed roughly equally (~33% each). Peer ratings: 5/5 for all members.

---

## 6. Key Takeaways

### Technical Lessons

1. **Production ML is 10% modeling, 90% engineering** - The KNN algorithm is textbook. The hard part was making it reliable, fast, fair, and secure.

2. **Monitoring is not optional** - Without Prometheus metrics and SLA tracking, we'd be flying blind. Monitoring saved us multiple times by catching issues early.

3. **Exactly-once semantics are hard** - Even with Kafka's guarantees, we needed careful offset management and idempotent processing.

4. **Schema evolution requires upfront design** - Changing message formats mid-flight broke everything. Additive-only changes are the way.

5. **Synthetic data hides real problems** - Our 100% coverage looks great, but we know real sparse data would expose cold-start issues.

### Process Lessons

1. **Automate toil early** - Automated retraining (every 3 hours) saved us countless manual runs and human errors.

2. **Test end-to-end, not just units** - 70% unit test coverage gave false confidence. Integration bugs still happened.

3. **Document everything immediately** - Future you (and your team) will thank you. We learned this the hard way.

4. **Start with security** - Retrofitting authentication and rate limiting in M5 was harder than building it in from M1.

### Responsible ML Lessons

1. **Fairness requires continuous monitoring** - We can't just check coverage once and call it done. Distributions drift, biases emerge. Our 3-hour retraining helps, but we need real-time fairness dashboards.

2. **Feedback loops are real** - We detected popularity echo chamber forming (Gini slope +0.0146). Without intervention, this would compound over weeks into severe inequality.

3. **Security threats are diverse** - We identified 12 distinct threats across Kafka, API, and Registry. Defense in depth is essential - no single mitigation is enough.

4. **Metrics are social constructs** - "100% catalog coverage" sounds great, but if users don't want those tail items, it's meaningless. Need to balance algorithmic fairness with user satisfaction.

---

## 7. Final Thoughts

Building this production ML system was the most technically challenging project any of us have worked on. We initially thought the hard part would be choosing the right algorithm or tuning hyperparameters. We were wrong.

The real challenges were in the "boring" parts: getting Kafka offsets right, handling schema evolution without breaking consumers, debugging why Docker containers couldn't connect to Kafka, figuring out why CI/CD was failing on Azure but working locally. We spent more time reading Kafka documentation than machine learning papers.

But that's exactly what made this valuable. We learned that production ML is fundamentally about integration - connecting Kafka to Docker to GitHub Actions to Azure to Prometheus to Flask. Each component works fine in isolation, but making them all work together reliably is the real engineering challenge.

We're proud of what we shipped: a system that passes all SLAs (99% uptime, <100ms latency), meets fairness requirements (100% coverage, 0.018 parity gap), detects real security threats (spam users, echo chambers), and automatically retrains every 3 hours without human intervention. It's not perfect - we have a long list of improvements for productionization - but it's a solid foundation.

The biggest lesson? Production ML is a marathon, not a sprint. You're never "done" - there's always drift to detect, loops to break, threats to defend against. But that continuous improvement cycle is what makes it interesting.

If we had to do it again, we'd start with better integration tests, implement Schema Registry from day one, and document as we code instead of at the end. But overall, we're happy with our choices and proud of the system we built together.

---

**Document:** Milestone 5 Reflection
**Word Count:** ~1,850 words
**Authors:** Faran Mohammed, Rahman Mohammed Abdul, Aigerim Mendygaliyeva
**Last Updated:** November 24, 2025

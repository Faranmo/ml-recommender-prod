# Milestone 5 Reflection

**Team:** Project Group 6
**Members:** Faran Mohammed, Rahman Mohammed Abdul, Aigerim Mendygaliyeva

---

## Hardest Parts

### Kafka Offsets

Managing Kafka offsets was harder than we thought. Our consumer writes batches of 10 messages to Parquet files, but if it crashes mid-batch we'd either lose data (if we commit too early) or process duplicates (if we commit too late). We ended up adding signal handlers to save partial batches on shutdown. If we did this again we'd probably just use Kafka Streams instead of rolling our own batch logic.

### Schema Evolution

When we added new fields like `ab_variant` and `model_version` for M4, our old Parquet files broke the consumer. We learned you can't just change schemas mid-flight - you need backward compatibility. We fixed it by making all schema changes additive (new optional fields only, never modify existing ones). Should have used Schema Registry from the start.

### Cold-Start Problem

New items and users are hard for collaborative filtering. Without interactions, we can't make predictions. Without predictions, items don't get recommended. Without recommendations, no interactions. We're stuck in a loop. Our Model B gets 100% coverage but that's mostly because our training data is complete. Real sparse data would be way harder. Next time we'd build a hybrid model with content-based features from day 1.

### Backpressure

During testing with high message volumes, our consumer couldn't keep up. Lag built up to 500+ messages. The problem was synchronous Parquet writes blocking everything. We added monitoring and increased batch size from 10 to 50 messages which helped. Better solution would be async I/O or horizontal scaling with multiple consumers.

---

## System Fragilities

- **No Kafka replication:** Single broker = data loss if it fails
- **3-hour retraining window:** Model can be stale, misses viral content
- **100% coverage is optimistic:** Relies on complete training data, real sparse data would be lower
- **No authentication:** Anyone can access all endpoints, switch models, scrape metrics

---

## If We Redid It

**Architecture:** We did batch retraining every 3 hours. If we redid it we'd do streaming ML with online learning to reduce staleness from hours to seconds.

**Algorithm:** We used KNN collaborative filtering because it's simple. If we redid it we'd probably use a neural network (two-tower model) for better cold-start handling.

**Testing:** We had 70% unit test coverage but sparse integration tests. Next time we'd add end-to-end tests that exercise the full pipeline before deploying anything.

**Security:** We retrofitted security stuff in M5. Should have built it in from M1.

---

## Teamwork

**What worked:**
- Clear roles (Faran: Kafka/Docker, Rahman: ML/eval, Aigerim: API/monitoring)
- Daily Slack standups kept us aligned
- GitHub Actions automated testing/deployment - huge time saver

**What could improve:**
- Integration bugs slipped through because we only had unit tests
- We documented at the end instead of during development
- Time management - M3 and M4 got rushed despite having weeks

**Team contributions:**
- Faran: Kafka infrastructure, consumer, Docker, CI/CD
- Rahman: Model training, offline/online eval, drift detection
- Aigerim: Flask API, Prometheus monitoring, A/B testing
Everyone did about 33% each.

---

## Key Learnings

**Technical:**
- Production ML is 10% modeling, 90% engineering
- Exactly-once semantics are hard even with Kafka
- Schema evolution needs upfront planning
- Synthetic data hides real problems

**Process:**
- Automate everything - manual is error-prone
- End-to-end tests > unit tests alone
- Document as you code, not after
- Security should be built in, not added later

**Responsible ML:**
- Fairness needs continuous monitoring, not one-time checks
- Feedback loops are real (we detected echo chamber forming)
- Security threats are diverse, need defense in depth

---

## Final Thoughts

This was the hardest project we've done. We thought the hard part would be choosing algorithms or tuning hyperparameters. We were completely wrong.

The real challenges were the boring integration stuff: getting Kafka offsets right, handling schema changes, debugging Docker networking, figuring out why CI worked locally but failed on Azure. We spent way more time reading Kafka docs than ML papers.

But that's what made it valuable. We learned that production ML is about integration - connecting Kafka to Docker to GitHub Actions to Azure to Prometheus to Flask. Each part works alone but making them work together reliably is the real challenge.

We're proud we built a system that passes all SLAs (99% uptime, <100ms latency), meets fairness requirements (100% coverage, low parity gap), and detects real security threats. It's not perfect - we have a long list of improvements - but it's a solid foundation.

Biggest lesson: Production ML is a marathon not a sprint. You're never done - always drift to detect, loops to break, threats to defend against.

If we had to do it again: better integration tests, Schema Registry from day 1, document as we code not after. But overall happy with what we built.

---

**Word count:** ~750 words

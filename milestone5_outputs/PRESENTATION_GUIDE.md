# Milestone 5 Demo Presentation Guide
## 5-8 Minute Video Presentation

**Team:** [YOUR TEAM NAME]
**All Members Must Appear in Video**

---

## Slide Structure (10-12 slides recommended)

### SLIDE 1: Title (15 sec)
- Team name + member names
- "Milestone 5: Responsible ML Production System"
- Date

### SLIDE 2: System Overview (30 sec)
- Quick architecture diagram
- Key stats: 100% coverage, <100ms latency, 99% uptime
- Mention M1-M4 foundations (Kafka, CI/CD, monitoring, A/B testing)

### SLIDE 3: A/B Testing Results (45 sec)
- Show table: Model A (83% coverage) vs Model B (100% coverage)
- Z-score: 3.14, p-value: 0.0017 → statistically significant
- **LIVE DEMO:** `curl /recommend?user_id=42` showing A/B variant routing

### SLIDE 4: Fairness Requirements (45 sec)
- System-level: Coverage ≥80% → **100% PASS**
- Model-level: Parity gap <0.15 → **0.018 PASS**
- Show fairness_popularity_bias.png plot

### SLIDE 5: Fairness Harms & Mitigations (30 sec)
- List 5 harms (popularity bias, filter bubbles, cold-start, creator starvation, temporal)
- Quick mention of mitigations (diversity re-ranking, exploration bonuses)

### SLIDE 6: Feedback Loop Detection (45 sec)
- Loop 1: Popularity echo (Gini slope +0.0146 → DETECTED)
- Loop 2: Tail starvation (Head/Tail ratio 1.54x → RISK)
- Show feedback_loop_popularity_echo.png

### SLIDE 7: Security Threat Model (45 sec)
- Kafka threats: Message injection, unauthorized access
- API threats: Rate abuse, model inference attacks
- Registry threats: Model poisoning, supply chain
- Mention implemented mitigations (Pandera schema validation, provenance tracking)

### SLIDE 8: Security Analysis (30 sec)
- Rating spam detection: 10 spam users detected (10%)
- Show security_rating_spam_detection.png
- Explain detection method (>3σ outlier detection)

### SLIDE 9: LIVE SYSTEM DEMO (90 sec) ⭐ MOST IMPORTANT
**[Prepare screen recording or live demo]**
1. Show GitHub Actions → automated retraining runs
2. Show `/recommend` endpoint response with provenance
3. Show `/metrics` Prometheus output
4. Show monitoring_report.json (all SLAs passing)
5. Show model_registry/ versions (v1.0 → v1.4)

### SLIDE 10: Key Achievements (30 sec)
- ✓ Fairness: Both requirements PASS
- ✓ Feedback loops: Detected + mitigations deployed
- ✓ Security: Threat model + working detection
- ✓ Production: All SLAs passing, automated retraining

### SLIDE 11: Challenges & Learnings (30 sec)
**[Personalize from your reflection]**
- Hardest: [Pick 2 from your reflection]
- Learned: [Key takeaway]
- Would redo: [One thing]

### SLIDE 12: Q&A / Thank You (15 sec)
- GitHub repo link
- Live system URL
- Contact info

---

## Timing Breakdown (Total: 6-7 minutes)

| Section | Time | Slides |
|---------|------|--------|
| Intro + Overview | 45s | 1-2 |
| Fairness | 2min | 3-5 |
| Feedback Loops | 45s | 6 |
| Security | 75s | 7-8 |
| **Live Demo** | **90s** | 9 |
| Wrap-up | 45s | 10-12 |

---

## Demo Script for Slide 9

**[Practice this - it's the most important part]**

**Narrator:** "Let me show our live production system..."

**Screen 1: GitHub Actions**
```
"Our automated retraining runs every 3 hours. You can see the last 5 commits
are all 'Auto-retrain model', showing the CI/CD pipeline working."
```

**Screen 2: API Call**
```bash
curl https://flixstream-api.azurewebsites.net/recommend?user_id=42
```
"Here's a live recommendation request. Notice the response includes provenance:
model version, git SHA, and A/B variant - full traceability."

**Screen 3: Metrics**
```bash
curl https://flixstream-api.azurewebsites.net/metrics
```
"Our Prometheus metrics show request counts, latency histograms, and error rates.
All feeding into our monitoring dashboards."

**Screen 4: Monitoring Report**
```
cat monitoring_report.json
```
"All our SLAs are passing: 99% uptime, latency under 500ms, 100% availability."

**Screen 5: Analysis Outputs**
```
ls milestone5_outputs/
```
"These are our fairness, feedback loop, and security analysis outputs -
plots and data backing every claim in our report."

---

## Presentation Tips

### Delivery
- **All members speak** - divide slides among team
- **Practice transitions** between speakers
- **Time yourself** - aim for 6-7 min to leave buffer
- **Show enthusiasm** - this is cool stuff!

### Slides
- **Minimal text** - bullet points only
- **Big fonts** - readable on small screens
- **Visuals** - use the PNG plots you generated
- **Live links** - make URLs clickable

### Common Mistakes to Avoid
- ❌ Going over 8 minutes (will be cut off)
- ❌ Reading slides word-for-word
- ❌ Not showing the live system
- ❌ Only one person speaking
- ❌ Technical jargon without explanation

---

## Recording Checklist

- [ ] Test screen recording software
- [ ] Check audio quality (all members)
- [ ] Test live demo beforehand (API must be up!)
- [ ] Have backup screenshots if live demo fails
- [ ] All team members' names on title slide
- [ ] Clear intro (who you are)
- [ ] Smooth transitions between speakers
- [ ] Ending with Q&A slide

---

## PowerPoint Creation

**Use these layouts:**
1. Title slide - team name/members
2. Content slides - title + 3-4 bullets + image
3. Demo slide - screenshot/screencast
4. Conclusion - summary bullets

**Insert your PNG visualizations:**
- fairness_popularity_bias.png
- fairness_model_parity.png
- feedback_loop_popularity_echo.png
- feedback_loop_tail_starvation.png
- security_rating_spam_detection.png

---

## Video Upload

**Where to upload:**
- YouTube (unlisted)
- Google Drive (link sharing on)
- Vimeo

**Include in submission:**
- Video link in report PDF
- Video link in README.md

---

**Total Prep Time:** 2-3 hours (slides + practice + recording)
**Recommended:** Do a practice run before recording final version

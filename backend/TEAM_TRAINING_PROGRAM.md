# Team Training Program

**Phase 13.2: Comprehensive Team Onboarding & Certification**

## Executive Summary

Complete training program for team members to become proficient with BOB AI v7 system. Includes instructor materials, labs, and certification.

**Training Duration:** 5 half-day sessions (12 hours total)
**Target Audience:** Developers, QA, Operations, Business Analysts
**Certification:** BOB AI v7 Practitioner Certificate
**Success Metric:** 90%+ pass rate on final assessment

---

## 1. Training Program Overview

### 1.1 Curriculum Map

```
Module 1: Fundamentals (Day 1 - 3 hours)
├── System architecture overview
├── Core concepts (nodes, metadata, relationships)
└── Quality system basics

Module 2: API & Integration (Day 2 - 3 hours)
├── 8 REST endpoints deep-dive
├── Request/response examples
└── Error handling

Module 3: Advanced Features (Day 3 - 3 hours)
├── LLM integration
├── Cross-domain analysis
├── Custom relationship types

Module 4: Operations & Monitoring (Day 4 - 2 hours)
├── Deployment procedures
├── Monitoring dashboards
└── Alert management

Module 5: Hands-On Lab & Certification (Day 5 - 1 hour)
├── Complete workflow exercise
└── Certification exam
```

### 1.2 Training Schedule

```
Week 1:
├── Mon 10:00-12:30: Module 1 (Fundamentals)
├── Tue 10:00-12:30: Module 2 (API & Integration)
└── Wed 10:00-12:30: Module 3 (Advanced Features)

Week 2:
├── Thu 10:00-11:30: Module 4 (Operations)
└── Fri 14:00-15:30: Module 5 (Lab & Certification)

Plus: 2 weeks office hours for Q&A
```

---

## 2. Module 1: Fundamentals (3 hours)

### 2.1 Learning Objectives

After this module, participants will:

- ✓ Understand system architecture (8 layers)
- ✓ Create knowledge nodes and metadata
- ✓ Build relationships between items
- ✓ Understand quality scoring formula

### 2.2 Content Outline

#### Part 1: System Architecture (60 minutes)

**Topics:**

1. Overview: What is BOB AI v7?
   - Enterprise knowledge management
   - AI-powered semantic search
   - Real-time analytics

2. 8-Layer Architecture
   - Layer 1: Core (KnowledgeNode)
   - Layer 2: Quality (Scoring)
   - Layer 3: Semantics (15 types)
   - Layer 4: API (REST endpoints)
   - Layer 5: Performance (Indexing)
   - Layer 6: Enrichment (Wikipedia)
   - Layer 7: Domains (7 disciplines)
   - Layer 8: Integration (LLM)

3. Data Flow
   - Input → Processing → Storage → Query → Output

**Activity:** Architecture diagram walkthrough (15 min)

#### Part 2: Core Concepts (60 minutes)

**Topics:**

1. KnowledgeNode Structure

   ```python
   node = {
       'label': 'Machine Learning',
       'category': 'AI',
       'quality': 0.93,
       'metadata': {
           'confidence': 0.95,
           'precision': 0.90
       }
   }
   ```

2. Metadata System
   - Quality metrics (7 factors)
   - Confidence scores
   - Source attribution

3. Relationship Types (15 types)
   - is_a, part_of, depends_on
   - related_to, similar_to, enables
   - requires, produces, contradicts
   - refines, specializes, generalizes
   - aliases, precedes, competes_with

**Activity:** Create 5 example nodes (15 min)

#### Part 3: Quality System (60 minutes)

**Topics:**

1. Quality Formula
   - Score = 0.25×Confidence + 0.20×Precision + ...
   - Range: 0.0 to 1.0
   - Levels: CRITICAL, POOR, FAIR, GOOD, EXCELLENT

2. Quality Levels
   - CRITICAL: 0.0-0.3 (needs rework)
   - POOR: 0.3-0.5 (low confidence)
   - FAIR: 0.5-0.7 (acceptable)
   - GOOD: 0.7-0.85 (production quality)
   - EXCELLENT: 0.85-1.0 (trusted source)

3. Quality Validation
   - Automated scoring
   - Manual review process
   - Retrofit for batch items

**Activity:** Score 3 sample items (15 min)

### 2.3 Module 1 Assessment

**Quiz (10 questions, 80% pass):**

1. Name 3 of the 8 layers
2. What are the 5 quality levels?
3. List 5 relationship types
4. Calculate quality score for sample data
5. What is the purpose of metadata?

**Hands-on:** Create node with relationships (15 min)

---

## 3. Module 2: API & Integration (3 hours)

### 3.1 Learning Objectives

After this module, participants will:

- ✓ Call all 8 REST endpoints
- ✓ Handle errors and responses
- ✓ Implement error handling
- ✓ Integrate with external systems

### 3.2 Content Outline

#### Part 1: REST API Fundamentals (60 minutes)

**8 Endpoints:**

1. POST /add - Create item
2. PUT /update/{id} - Modify item
3. DELETE /remove/{id} - Delete item
4. GET /search - Find items
5. GET /domain/{domain} - Get domain items
6. GET /{id} - Item details
7. POST /relationships - Create links
8. GET /quality/report - Quality metrics

**For Each Endpoint:**

- Purpose & use case
- Request format
- Response format
- Example calls
- Common errors

**Activity:** Make 5 API calls using curl (15 min)

#### Part 2: Request/Response Handling (60 minutes)

**Topics:**

1. Request Format

   ```json
   {
     "label": "AI",
     "category": "Technology",
     "quality": 0.92,
     "metadata": {...}
   }
   ```

2. Response Format

   ```json
   {
     "success": true,
     "data": {...},
     "status_code": 201,
     "timestamp": "2025-10-27T..."
   }
   ```

3. Error Responses
   - 400: Bad Request (validation error)
   - 401: Unauthorized (auth failure)
   - 404: Not Found (item missing)
   - 500: Server Error (internal issue)

4. Rate Limiting
   - 100 requests/minute
   - Headers: X-RateLimit-Remaining
   - Backoff strategy

**Activity:** Handle 3 error scenarios (15 min)

#### Part 3: Integration Patterns (60 minutes)

**Topics:**

1. Batch Operations
   - Add multiple items
   - Bulk updates
   - Batch queries

2. Pagination
   - limit parameter (default: 10, max: 100)
   - offset parameter
   - total_count in response

3. Filtering
   - By domain
   - By quality level
   - By relationship type

4. Sorting
   - By quality (DESC)
   - By created_at (ASC)
   - By relevance (search)

**Activity:** Complex query with pagination (15 min)

### 3.3 Module 2 Assessment

**Quiz (10 questions, 80% pass):**

1. Write API call to search for "machine learning"
2. How do you handle a 429 rate limit error?
3. What response code means "item not found"?
4. Explain pagination with limit=50, offset=100
5. How many items can you retrieve per request (max)?

**Hands-on Lab:** Implement 3-endpoint workflow (30 min)

---

## 4. Module 3: Advanced Features (3 hours)

### 4.1 Learning Objectives

After this module, participants will:

- ✓ Use LLM enhancement context
- ✓ Understand cross-domain analysis
- ✓ Create custom relationships
- ✓ Leverage enrichment data

### 4.2 Content Outline

#### Part 1: LLM Integration (60 minutes)

**Topics:**

1. Context Retrieval Pipeline
   - Stage 1: Direct search
   - Stage 2: Semantic expansion
   - Stage 3: Cross-domain links
   - Stage 4: Quality ranking

2. Result Ranking
   - Quality score (40% weight)
   - Relevance score (30% weight)
   - Diversity score (15% weight)
   - Recency score (10% weight)
   - Relationship score (5% weight)

3. Use Cases
   - Enhanced search results
   - Decision support
   - Content generation
   - Relationship discovery

**Example:**

```
User Query: "Tell me about ML applications in healthcare"
├─ Stage 1: Find "Machine Learning" items
├─ Stage 2: Expand via "enables" relationships
├─ Stage 3: Bridge medicine↔technology
└─ Stage 4: Rank by quality → LLM context
```

**Activity:** Trace context retrieval for 2 queries (15 min)

#### Part 2: Cross-Domain Analysis (60 minutes)

**Topics:**

1. Domain Bridges (6 types)
   - Ethical considerations
   - Economic impacts
   - Regulatory frameworks
   - Medical/Health applications
   - Environmental effects
   - Historical context

2. 10 Domains Mapped
   - Business (57 items)
   - Medicine (63 items)
   - Law (60 items)
   - Environment (65 items)
   - History (70 items)
   - Philosophy (55 items)
   - Arts (60 items)
   - Plus 3 supporting domains

3. Bridge Query Example

   ```
   Business → Law:
   ├─ Regulatory compliance
   ├─ Contract law
   ├─ IP protection
   └─ Employment law
   ```

4. Finding Connections
   - Search across domains
   - Relationship traversal
   - 71 total connections

**Activity:** Find 5 cross-domain connections (15 min)

#### Part 3: Custom Relationships & Enrichment (60 minutes)

**Topics:**

1. Custom Relationships
   - Define domain-specific types
   - Set strength (0.0-1.0)
   - Bidirectional linking
   - Validate no cycles

2. Enrichment Sources
   - Wikipedia: Summaries, URLs
   - Wikidata: Entity IDs, properties
   - DBpedia: Resource mapping
   - Auto-linking via external IDs

3. Enrichment Workflow

   ```
   Add item → Validate → Search externally → Link → Store
   ```

**Activity:** Create custom relationship type (15 min)

### 4.3 Module 3 Assessment

**Quiz (10 questions, 80% pass):**

1. Explain the 4-stage context retrieval pipeline
2. What are the 6 cross-domain bridge types?
3. What's the highest-weight factor in result ranking?
4. Name 3 of the 10 domains
5. How many total cross-domain connections exist?

**Hands-on Lab:** Build context for LLM query (30 min)

---

## 5. Module 4: Operations & Monitoring (2 hours)

### 5.1 Learning Objectives

After this module, participants will:

- ✓ Deploy to staging/production
- ✓ Monitor system health
- ✓ Respond to alerts
- ✓ Troubleshoot issues

### 5.2 Content Outline

#### Part 1: Deployment (40 minutes)

**Topics:**

1. Staging Deployment
   - 12-item validation checklist
   - Pre-deployment backups
   - Health checks
   - Smoke tests

2. Production Deployment (Blue-Green)
   - Provision Green environment
   - Run validation tests
   - Switch load balancer
   - Monitor for 10 minutes
   - Keep Blue as backup

3. Rollback Procedure
   - Immediate: Switch back to Blue
   - Recovery time: <5 minutes
   - Data loss: <5 minutes

**Activity:** Practice deployment checklist (10 min)

#### Part 2: Monitoring & Alerts (80 minutes)

**Topics:**

1. KPIs & Dashboards
   - System health (CPU, memory, disk)
   - Application metrics (response time, errors)
   - Business metrics (items, quality)
   - Real-time dashboard access

2. Alert Rules
   - CPU >85%
   - Memory >90%
   - Error rate >1%
   - Response time >2s
   - Availability <99%

3. Alert Channels
   - Slack notifications
   - Email alerts
   - PagerDuty integration
   - Custom webhooks

4. Incident Response
   - Alert → Investigate → Fix → Verify
   - Escalation path
   - War room procedures
   - Post-incident review

5. Performance Analysis
   - Daily reports
   - Weekly trends
   - Monthly analysis
   - Optimization recommendations

**Activity:** Simulate alert response (15 min)

### 5.3 Module 4 Assessment

**Quiz (8 questions, 80% pass):**

1. What are the steps for production deployment?
2. How long does rollback take?
3. What's the critical memory usage threshold?
4. Name 3 alert channels
5. What does a daily report include?

**Hands-on:** Review monitoring dashboard (10 min)

---

## 6. Module 5: Hands-On Lab & Certification (1 hour)

### 6.1 Capstone Lab Exercise

**Objective:** Complete full workflow from knowledge input to LLM enhancement

**Scenario:**
You're a knowledge manager for a tech company. Add new AI concepts to the system and integrate with decision-support tools.

**Tasks (30 minutes):**

1. Create 3 new knowledge items with quality scoring
2. Create 5 relationships between items
3. Create cross-domain link (tech ↔ business)
4. Query using advanced search
5. Generate LLM context for decision support

**Success Criteria:**

- All items created with quality ≥0.85
- All relationships bidirectional
- No cycles in relationships
- LLM context properly ranked

### 6.2 Certification Exam

**Exam (15 minutes, 80% required to pass):**

**Part A: Knowledge (5 questions)**

1. Architecture: Describe the 8 layers in one sentence each
2. Quality: Write the quality formula
3. API: List all 8 endpoints
4. Semantics: Name 8 of 15 relationship types
5. Performance: What's the target response time?

**Part B: Practical (2 scenarios)**

1. Create this item with correct quality score
2. Troubleshoot this error response

**Part C: Advanced (2 questions)**

1. Design a cross-domain relationship solution
2. Explain how LLM context retrieval works

### 6.3 Certification Award

Upon passing:

- ✓ BOB AI v7 Practitioner Certificate
- ✓ Digital badge
- ✓ Access to advanced features
- ✓ Eligible for train-the-trainer role

---

## 7. Supplementary Materials

### 7.1 Quick Reference Cards

**API Quick Reference:**

```
POST   /add       → Create item
PUT    /update    → Modify item
DELETE /remove    → Delete item
GET    /search    → Find items
GET    /domain    → Domain items
GET    /{id}      → Get details
POST   /relationships → Link items
GET    /quality   → Quality report

All endpoints at: http://localhost:5000/api/v7
Rate: 100 req/min
```

**Quality Levels Reference:**

```
CRITICAL: 0.0-0.3  (❌ Unacceptable)
POOR:     0.3-0.5  (⚠️  Low confidence)
FAIR:     0.5-0.7  (✓  Acceptable)
GOOD:     0.7-0.85 (✓✓ Production)
EXCELLENT: 0.85-1.0 (✓✓✓ Trusted)
```

**Relationship Types:**

```
is_a, part_of, depends_on, related_to
similar_to, enables, requires, produces
contradicts, refines, specializes
generalizes, aliases, precedes, competes_with
```

### 7.2 Troubleshooting Guide

**Problem: Can't connect to API**

- Solution: Check if backend is running (python main.py)
- Check port 5000 is available (netstat -an | grep 5000)

**Problem: Quality score invalid (not 0-1)**

- Solution: Ensure all component metrics are 0-1
- Use Quality Dashboard to validate

**Problem: Relationship creation fails**

- Solution: Verify both items exist
- Check for cycles using path detection

**Problem: Search is slow**

- Solution: Verify cache is warmed
- Check indexing status in dashboard

---

## 8. Ongoing Support

### 8.1 Office Hours

**Schedule:**

- Monday 2-3 PM: General Q&A
- Wednesday 2-3 PM: Advanced topics
- Friday 10-11 AM: Troubleshooting

**Access:** Zoom link in calendar invite

### 8.2 Slack Channel

**#bob-ai-v7-support**

- General questions
- Quick troubleshooting
- Announcement channel
- 24-hour response SLA

### 8.3 Documentation

- API Reference: `/docs/API_REFERENCE.md`
- Developer Guide: `/docs/DEVELOPER_GUIDE.md`
- Architecture: `/docs/ARCHITECTURE_DIAGRAMS.md`
- Operations: `/docs/OPERATIONS_GUIDE.md`

---

## 9. Training Feedback & Iteration

### 9.1 Feedback Survey

After each module, participants complete:

```
1. Clarity of content (1-5 scale)
2. Pace of delivery (too fast/just right/too slow)
3. Quality of examples (1-5)
4. Most valuable topic
5. Topic needing more time
6. Overall satisfaction (1-5)
```

### 9.2 Continuous Improvement

- Collect all feedback
- Identify common gaps
- Update materials quarterly
- Track certification pass rate
- Monitor support ticket volume

---

## 10. Certification Tracking

### 10.1 Certification Database

```
Name | Date | Score | Level | Expiry
John | Oct 27 | 92% | Practitioner | Oct 28
Jane | Oct 27 | 87% | Practitioner | Oct 28
...
```

### 10.2 Advanced Certifications (Future)

- Advanced Practitioner (6 months experience)
- Instructor Certification (train others)
- Specialist: Architecture, Integration, Operations

---

## 11. Training Completion Checklist

- [ ] Module 1 completed by participant
- [ ] Module 1 quiz passed (80%+)
- [ ] Module 2 completed by participant
- [ ] Module 2 quiz passed (80%+)
- [ ] Module 3 completed by participant
- [ ] Module 3 quiz passed (80%+)
- [ ] Module 4 completed by participant
- [ ] Module 4 quiz passed (80%+)
- [ ] Module 5 capstone lab completed
- [ ] Certification exam passed (80%+)
- [ ] Certificate issued and dated
- [ ] Feedback survey completed
- [ ] Added to support channels

---

## 12. Training Success Metrics

**Target Metrics:**

- 90%+ certification pass rate
- Average satisfaction: 4.3/5.0
- Support ticket reduction: 50%+ (vs pre-training)
- Average resolution time: <4 hours
- Feature adoption: 85%+ within 3 months

---

*Last Updated: October 27, 2025*
*BOB AI v7 - Comprehensive Team Training Program*
*Status: Ready for Deployment*

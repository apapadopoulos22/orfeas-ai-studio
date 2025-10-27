# Staging Deployment Checklist

**Phase 11.1: Pre-Production Validation**

## Executive Summary

This checklist ensures BOB AI v7 is production-ready before deploying to live environment. All items must be validated in staging environment first.

**Deployment Timeline:** ~4-6 hours
**Risk Level:** LOW (all components tested)
**Success Criteria:** All 12 checklist items passing ✓

---

## Pre-Deployment Validation

### 1. Environment Setup Validation

- [ ] **Staging Server Provisioned**
  - [ ] Hardware: Dedicated VM or container (RTX 3090 GPU preferred)
  - [ ] OS: Ubuntu 20.04 LTS or Windows Server 2019+
  - [ ] Python: 3.10+ installed and verified
  - [ ] Ports: 5000 (backend), 3000 (frontend) available
  - [ ] Disk: 50GB+ free space
  - [ ] Memory: 32GB+ RAM

- [ ] **Dependencies Installed**

  ```bash
  cd backend
  pip install -r requirements.txt
  ```

  - [ ] torch: Verified GPU available
  - [ ] flask: Web server operational
  - [ ] requests: HTTP client working
  - [ ] All imports successful

- [ ] **Environment Variables Set**

  ```powershell
  # Core settings
  $env:DEVICE = "cuda"
  $env:ORT_TENSORRT_UNAVAILABLE = "1"
  $env:XFORMERS_DISABLED = "1"
  $env:GPU_MEMORY_LIMIT = "0.8"
  $env:HOME = $env:USERPROFILE

  # Knowledge base
  $env:KNOWLEDGE_BASE_PATH = "C:\data\knowledge_base"
  $env:HY3DGEN_MODELS = "C:\models"

  # API settings
  $env:FLASK_ENV = "staging"
  $env:CORS_ORIGINS = "*"
  $env:LOG_LEVEL = "INFO"
  ```

  - [ ] All variables populated
  - [ ] No undefined variables
  - [ ] Paths verified to exist

### 2. Backend Service Validation

- [ ] **Backend Starts Successfully**

  ```bash
  python main.py
  ```

  - [ ] No startup errors (wait 30 seconds)
  - [ ] Output shows "Running on <http://127.0.0.1:5000>" ✓
  - [ ] No TensorRT warnings (expected)
  - [ ] No XFORMERS warnings (expected)

- [ ] **Health Endpoint Responds**

  ```bash
  curl http://localhost:5000/health
  ```

  - [ ] Status: 200 OK
  - [ ] Response includes timestamp
  - [ ] All components "healthy"

- [ ] **Startup Performance**
  - [ ] Cold start time: <150ms
  - [ ] Warm start time: <50ms
  - [ ] Memory usage: <300MB
  - [ ] CPU usage: <10% at idle

### 3. Database & Knowledge Base Validation

- [ ] **Knowledge Base Loaded**
  - [ ] All 1,330+ items present
  - [ ] Total items verified
  - [ ] Average quality: 0.89+
  - [ ] Domains: 10 distinct

- [ ] **Data Integrity Checks**

  ```bash
  python validate_knowledge_base.py
  ```

  - [ ] No orphaned relationships
  - [ ] All cross-domain links valid (71 total)
  - [ ] Quality scores in range [0, 1]
  - [ ] No duplicate items
  - [ ] Referential integrity: 100%

- [ ] **Indexing Operational**
  - [ ] Label index: <1ms search time
  - [ ] Domain index: <5ms search time
  - [ ] Tag index: <2ms search time
  - [ ] All indexes pre-built and warm

### 4. API Endpoint Validation

- [ ] **All 8 Endpoints Functional**

  **Test 1: POST /api/v7/add**

  ```bash
  curl -X POST http://localhost:5000/api/v7/add \
    -H "Content-Type: application/json" \
    -d '{"label":"Test Item","category":"test","quality":0.92}'
  ```

  - [ ] Status: 201 Created
  - [ ] Response includes item_id
  - [ ] Quality verified

  **Test 2: GET /api/v7/search**

  ```bash
  curl "http://localhost:5000/api/v7/search?q=machine+learning&limit=5"
  ```

  - [ ] Status: 200 OK
  - [ ] Results returned: 5 items
  - [ ] Sorted by quality
  - [ ] Search time: <1ms

  **Test 3: GET /api/v7/domain/medicine**

  ```bash
  curl http://localhost:5000/api/v7/domain/medicine
  ```

  - [ ] Status: 200 OK
  - [ ] Returns 63+ items
  - [ ] Average quality: 0.92

  **Test 4: PUT /api/v7/update/{id}**
  - [ ] Status: 200 OK
  - [ ] Item updated
  - [ ] Relationships preserved

  **Test 5: POST /api/v7/relationships**
  - [ ] Status: 201 Created
  - [ ] Bidirectional link verified
  - [ ] No cycles detected

  **Test 6: GET /api/v7/{id}**
  - [ ] Status: 200 OK
  - [ ] Full item details returned
  - [ ] Relationships included

  **Test 7: DELETE /api/v7/remove/{id}**
  - [ ] Status: 200 OK
  - [ ] Item deleted
  - [ ] Related items updated

  **Test 8: GET /api/v7/quality/report**
  - [ ] Status: 200 OK
  - [ ] All metrics present
  - [ ] No calculation errors

- [ ] **Rate Limiting Functional**
  - [ ] Limit: 100 requests/minute
  - [ ] Headers returned correctly
  - [ ] 101st request rejected (429)

### 5. Performance Testing

- [ ] **Load Test (100 concurrent users)**

  ```bash
  locust -f load_test.py --host http://localhost:5000 -u 100 -r 10
  ```

  - [ ] Response time: <500ms (95th percentile)
  - [ ] Error rate: <0.1%
  - [ ] No memory leaks (stable)
  - [ ] No connection timeouts

- [ ] **Stress Test (burst to 500 requests)**
  - [ ] System recovers after burst
  - [ ] No data corruption
  - [ ] Graceful degradation

- [ ] **Memory Stability Test (1 hour)**
  - [ ] Memory usage stable
  - [ ] No growth >10MB/hour
  - [ ] Cache hit rate: 98%+

### 6. Security Validation

- [ ] **Input Validation**
  - [ ] SQL injection: Blocked ✓
  - [ ] XSS attempts: Blocked ✓
  - [ ] Invalid JSON: Rejected ✓
  - [ ] Oversized payloads: Rejected ✓

- [ ] **CORS Configuration**
  - [ ] Staging origin: Allowed
  - [ ] Production origin: Blocked
  - [ ] Credentials: Secure

- [ ] **Error Messages Safe**
  - [ ] No sensitive info leaked
  - [ ] Stack traces hidden (staging only)
  - [ ] User-friendly messages

### 7. Logging & Monitoring

- [ ] **Logging Operational**

  ```bash
  tail -f logs/app.log
  ```

  - [ ] INFO level: Active
  - [ ] ERROR level: Active
  - [ ] DEBUG level: Available (toggle)
  - [ ] Log rotation: Configured
  - [ ] Log file size: <100MB

- [ ] **Monitoring Dashboards**
  - [ ] System metrics: CPU, Memory, Disk
  - [ ] API metrics: Requests/sec, Error rate
  - [ ] Business metrics: Quality, Coverage
  - [ ] Alerts: Configured for thresholds

- [ ] **Error Tracking**
  - [ ] Error logger: Operational
  - [ ] Alerts for CRITICAL: Active
  - [ ] Alert for ERROR (>10/min): Active

### 8. External Integration Testing

- [ ] **Wikipedia Enrichment**
  - [ ] Test item enriched successfully
  - [ ] URL resolved correctly
  - [ ] Summary extracted properly

- [ ] **Wikidata Linking**
  - [ ] Entity ID found and linked
  - [ ] Properties available
  - [ ] Fallback works (DBpedia)

- [ ] **Cache Warming**
  - [ ] Frequent items pre-loaded
  - [ ] Cache hit rate: 100% for warm items
  - [ ] TTL expiration working

### 9. Backup & Recovery

- [ ] **Backup Procedure Tested**

  ```bash
  python backup_knowledge_base.py
  ```

  - [ ] Backup file created
  - [ ] Size: Expected range
  - [ ] Includes all 1,330+ items
  - [ ] Timestamp recorded

- [ ] **Recovery Procedure Tested**

  ```bash
  python restore_knowledge_base.py --from backup_20251027_120000.db
  ```

  - [ ] Knowledge base restored
  - [ ] Item count: 1,330+
  - [ ] Quality scores verified
  - [ ] No data loss

- [ ] **Disaster Recovery Plan**
  - [ ] Plan documented
  - [ ] Recovery time: <30 minutes
  - [ ] Data loss: <5 minutes

### 10. Documentation Review

- [ ] **API Reference Updated**
  - [ ] All 8 endpoints documented
  - [ ] Examples provided
  - [ ] Error codes listed
  - [ ] Performance metrics included

- [ ] **Developer Guide Current**
  - [ ] All code examples tested
  - [ ] Troubleshooting section complete
  - [ ] Best practices updated

- [ ] **Architecture Documentation Clear**
  - [ ] Diagrams accurate
  - [ ] Data flows documented
  - [ ] Component relationships correct

### 11. Compliance & Standards

- [ ] **Code Quality Standards**
  - [ ] All code: Type-hinted
  - [ ] All code: Error handling
  - [ ] All code: Logging
  - [ ] All tests: 99%+ pass rate

- [ ] **Performance Targets Met**
  - [ ] Label search: <1ms ✓
  - [ ] Domain search: <5ms ✓
  - [ ] Cache hit: >95% ✓
  - [ ] Startup: <150ms ✓

- [ ] **Security Standards**
  - [ ] No hardcoded secrets
  - [ ] All inputs validated
  - [ ] Error messages safe
  - [ ] Rate limiting active

### 12. Smoke Test (Pre-Production Ready)

- [ ] **Complete Workflow Test**

  ```bash
  python staging_smoke_test.py
  ```

  1. Add new item to knowledge base
     - [ ] Success: item created
     - [ ] Quality computed: 0.89+

  2. Create relationship between items
     - [ ] Success: link created
     - [ ] Bidirectional: verified

  3. Search and retrieve items
     - [ ] Results: correct ranking
     - [ ] Performance: <1ms

  4. Generate LLM context
     - [ ] Context: properly ranked
     - [ ] Items: semantically relevant

  5. Quality report generated
     - [ ] All metrics: present
     - [ ] Calculations: correct

  6. Cache performance verified
     - [ ] Hit rate: 100%
     - [ ] Memory: stable

---

## Sign-Off

### Deployment Approval Checklist

- [ ] **All 12 sections: PASSING** ✓
- [ ] **No blockers identified**
- [ ] **No performance issues**
- [ ] **No security concerns**
- [ ] **Documentation complete**
- [ ] **Team reviewed and approved**

### Stakeholder Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Backend Lead | | | |
| DevOps Lead | | | |
| Security Lead | | | |
| Product Owner | | | |

---

## Deployment Procedure

### Step 1: Pre-Deployment (1 hour)

```bash
# 1. Run final validation
cd backend
python main.py &  # Start backend

# 2. Run full test suite
pytest tests/unit/ -v
pytest tests/integration/ -v

# 3. Run performance validation
python bob_ai_v7_performance_validation.py

# 4. Verify backups
ls -lh backups/
```

### Step 2: Create Staging Snapshot

```bash
# Create pre-deployment backup
cp -r knowledge_base knowledge_base.backup.$(date +%s)

# Create database checkpoint
python backup_knowledge_base.py
```

### Step 3: Deploy to Staging

```bash
# Deploy application
docker build -t bob-ai-v7:staging .
docker run -d -p 5000:5000 --name bob-ai-staging bob-ai-v7:staging

# Verify deployment
curl http://localhost:5000/health
```

### Step 4: Validation (30 minutes)

```bash
# Run smoke tests
python staging_smoke_test.py

# Monitor logs
tail -f logs/app.log

# Run load test
locust -f load_test.py --host http://localhost:5000 -u 50 -r 5
```

### Step 5: Production Readiness Sign-Off

- [ ] All tests passing
- [ ] Performance acceptable
- [ ] No errors in logs
- [ ] Team sign-off obtained

---

## Rollback Procedure (If Needed)

### Immediate Rollback

```bash
# Stop staging deployment
docker stop bob-ai-staging
docker rm bob-ai-staging

# Restore from backup
python restore_knowledge_base.py --from backups/knowledge_base.backup.*

# Restart previous version
docker run -d -p 5000:5000 --name bob-ai-staging bob-ai-v7:stable
```

### Recovery Time Objective (RTO)

- **Estimated:** 5-10 minutes
- **Data Loss Objective (RPO):** <5 minutes

---

## Escalation Contacts

| Issue | Contact | Phone | Email |
|-------|---------|-------|-------|
| Backend issues | Backend Lead | | |
| DevOps issues | DevOps Lead | | |
| Security issues | Security Lead | | |
| Urgent escalation | CTO | | |

---

## Post-Deployment Actions

After successful staging validation:

1. **Schedule Production Deployment**
   - [ ] Date/time confirmed
   - [ ] Maintenance window scheduled
   - [ ] Stakeholders notified

2. **Brief Team on Changes**
   - [ ] Demo: New features
   - [ ] Training: New procedures
   - [ ] Q&A: Address concerns

3. **Prepare Monitoring**
   - [ ] Dashboards set up
   - [ ] Alerts configured
   - [ ] On-call schedule established

4. **Update Documentation**
   - [ ] Deployment history recorded
   - [ ] Runbooks updated
   - [ ] Change log updated

---

*Last Updated: October 27, 2025*
*BOB AI v7 - Staging Deployment Checklist*
*Status: Ready for Review*

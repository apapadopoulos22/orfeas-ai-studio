# Production Deployment Guide

**Phase 11.2: Live Environment Deployment**

## Executive Summary

This guide covers deploying BOB AI v7 to production using a blue-green deployment strategy to minimize downtime and enable rollback.

**Deployment Window:** 2-3 hours
**Estimated Downtime:** 0-2 minutes (health check transition)
**Risk Level:** LOW (blue-green strategy)
**Success Criteria:** Zero data loss, 99.9% uptime, all tests passing

---

## Pre-Deployment Checklist (Run Before Deployment)

All items from STAGING_DEPLOYMENT_CHECKLIST.md must be passing:

- [ ] Staging validation complete (all 12 sections passing)
- [ ] All smoke tests passing
- [ ] No performance issues detected
- [ ] No security concerns
- [ ] Team sign-off obtained
- [ ] Maintenance window scheduled
- [ ] Stakeholders notified
- [ ] Backup procedure verified
- [ ] Rollback procedure tested
- [ ] On-call team briefed

---

## Blue-Green Deployment Strategy

### Overview

```
CURRENT STATE (Blue)
├── Production instance running stable
├── Receiving 100% of traffic
├── Version: Previous release
└── Status: Operational

DEPLOYMENT PROCESS
├── Step 1: Deploy to Green (new instance)
├── Step 2: Run validation tests on Green
├── Step 3: Switch load balancer (traffic switch)
├── Step 4: Monitor Green for errors
├── Step 5: Keep Blue as instant rollback point

NEW STATE (Green)
├── Production instance running new version
├── Receiving 100% of traffic
├── Version: New release
├── Status: Operational (Blue remains as backup)
```

### Benefits

1. **Zero Downtime:** Traffic switches instantly
2. **Instant Rollback:** Blue environment remains live (can revert)
3. **Testing in Production:** Full validation before traffic switch
4. **Reduced Risk:** Easy to identify issues immediately

---

## Deployment Architecture

```
┌────────────────────────────────────────────────────────┐
│                  PRODUCTION ENVIRONMENT                │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │         Load Balancer (Health Check)            │  │
│  │  Routes traffic to Blue or Green (switchable)   │  │
│  └─────────────────────────────────────────────────┘  │
│                 │                                      │
│     ┌───────────┼───────────┐                         │
│     │           │           │                         │
│     ▼           ▼           ▼                         │
│  ┌──────┐   ┌──────┐   ┌──────────┐                  │
│  │ BLUE │   │GREEN │   │ Shared   │                  │
│  │(Old) │   │(New) │   │Storage   │                  │
│  │      │   │      │   │          │                  │
│  │ v7.0 │   │ v7.1 │   │Data      │                  │
│  │      │   │      │   │Backup    │                  │
│  │Ready │   │Ready │   │Logs      │                  │
│  │      │   │      │   │          │                  │
│  └──────┘   └──────┘   └──────────┘                  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │          Monitoring & Alerting                  │  │
│  │  Real-time metrics, error tracking, dashboards  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
└────────────────────────────────────────────────────────┘

Live Traffic → Load Balancer → Active Environment (Blue or Green)
```

---

## Step-by-Step Deployment Procedure

### Phase 1: Pre-Deployment (30 minutes before start)

#### 1.1 Notify All Stakeholders

```bash
# Send deployment notification
python send_deployment_notification.py --environment production --action start
```

- [ ] Notify team leads
- [ ] Notify operations
- [ ] Notify support team
- [ ] Post in Slack/Teams

#### 1.2 Verify Current State (Blue Environment)

```bash
# Check current production health
curl https://api.example.com/health

# Expected output:
# {
#   "status": "healthy",
#   "version": "7.0.0",
#   "uptime": "45 days",
#   "items": 1330,
#   "avg_quality": 0.89
# }
```

- [ ] Current version running
- [ ] All endpoints responding
- [ ] No active errors
- [ ] Recent backups verified

#### 1.3 Create Final Backup

```bash
# Create pre-deployment backup
python backup_knowledge_base.py --label pre-v7.1-deployment
python backup_database.py --label pre-v7.1-deployment
python backup_cache.py --label pre-v7.1-deployment

# Verify backups exist
ls -lh backups/pre-v7.1-deployment.*
```

- [ ] Knowledge base backed up
- [ ] Database backed up
- [ ] Cache backed up
- [ ] Backups verified (no corruption)

#### 1.4 Provision Green Environment

```bash
# Create new instance (Green)
docker run -d \
  -p 5001:5000 \
  --name bob-ai-green \
  --env-file .env.production \
  -v /data/knowledge_base:/app/data \
  -v /data/backups:/app/backups \
  bob-ai-v7:1.0.0

# Wait for startup
sleep 10

# Check Green status
curl http://localhost:5001/health
```

- [ ] Green environment created
- [ ] Startup completed without errors
- [ ] Health endpoint responds
- [ ] All services running

### Phase 2: Green Environment Validation (45 minutes)

#### 2.1 Basic Connectivity Tests

```bash
# Test all 8 API endpoints on Green
python validate_endpoints.py --target http://localhost:5001

# Expected: 8/8 endpoints responding
```

- [ ] POST /add: Working
- [ ] GET /search: Working
- [ ] PUT /update: Working
- [ ] DELETE /remove: Working
- [ ] GET /domain: Working
- [ ] GET /{id}: Working
- [ ] POST /relationships: Working
- [ ] GET /quality/report: Working

#### 2.2 Data Integrity Verification

```bash
# Verify all data migrated correctly
python verify_green_data.py

# Expected output:
# Total items: 1330
# Average quality: 0.89
# Integrity: 100%
```

- [ ] All 1,330 items present
- [ ] Quality scores correct
- [ ] Relationships intact (71 total)
- [ ] No orphaned data
- [ ] Cross-domain links valid

#### 2.3 Performance Validation

```bash
# Run performance tests against Green
python performance_validation.py --target http://localhost:5001

# Expected: All targets met
# - Label search: <1ms
# - Domain search: <5ms
# - Cache hit: >95%
# - Startup: <150ms
```

- [ ] Label search: <1ms ✓
- [ ] Domain search: <5ms ✓
- [ ] Cache hit rate: >95% ✓
- [ ] All benchmarks passing
- [ ] No performance degradation

#### 2.4 Load Test (Simulated Traffic)

```bash
# Run load test against Green
locust -f load_test.py \
  --host http://localhost:5001 \
  -u 100 -r 10 --run-time 5m

# Expected: <500ms response time, <0.1% error rate
```

- [ ] Response time acceptable
- [ ] Error rate <0.1%
- [ ] No memory issues
- [ ] No timeout errors

#### 2.5 Security Validation

```bash
# Run security tests against Green
python security_tests.py --target http://localhost:5001

# Expected: All tests passing
```

- [ ] SQL injection: Blocked ✓
- [ ] XSS attacks: Blocked ✓
- [ ] Invalid input: Rejected ✓
- [ ] Rate limiting: Active ✓
- [ ] CORS: Properly configured ✓

#### 2.6 Comprehensive Smoke Test

```bash
# Run complete workflow on Green
python production_smoke_test.py --target http://localhost:5001

# Expected: All tests passing
# 1. Add item → Success
# 2. Create relationship → Success
# 3. Search → Results correct
# 4. Quality report → All metrics present
```

- [ ] Create item: ✓
- [ ] Update item: ✓
- [ ] Search item: ✓
- [ ] Create relationship: ✓
- [ ] Quality report: ✓
- [ ] All workflows: ✓

#### 2.7 Green Environment Sign-Off

- [ ] All validation tests passing (100%)
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Ready for traffic

**GREEN ENVIRONMENT STATUS: READY ✓**

### Phase 3: Traffic Switch (5 minutes)

#### 3.1 Pre-Switch Notification

```bash
# Notify team of imminent switch
curl -X POST https://slack.webhook.com/... \
  -d '{"text":"Traffic switch to Green in 2 minutes"}'
```

- [ ] Team notified
- [ ] Monitoring teams standing by
- [ ] Support team standing by

#### 3.2 Switch Load Balancer

```bash
# CRITICAL: Switch traffic from Blue to Green
python switch_load_balancer.py \
  --from blue \
  --to green \
  --health-check-timeout 30s

# Expected: Traffic switches instantly
```

**TRAFFIC SWITCHING IN PROGRESS...**

- [ ] Health check passes
- [ ] Load balancer updated
- [ ] Traffic routed to Green
- [ ] Status: 100% Green traffic

#### 3.3 Immediate Health Verification (Critical Window)

```bash
# Verify Green is handling traffic
curl https://api.example.com/health -v

# Expected: 200 OK, Green version
```

- [ ] Health endpoint: Responding ✓
- [ ] Response time: Normal ✓
- [ ] No 5xx errors
- [ ] No timeout errors

#### 3.4 Monitor Error Rate (Next 2 minutes)

```bash
# Watch error rate in real-time
python monitor_errors.py --duration 2m --threshold 0.1%

# Expected: Error rate remains <0.1%
```

- [ ] Error rate: <0.1% ✓
- [ ] No cascading failures
- [ ] Database connections: Stable
- [ ] Cache operations: Normal

### Phase 4: Post-Switch Validation (30 minutes)

#### 4.1 Extended Monitoring (10 minutes)

```bash
# Monitor for 10 minutes looking for issues
python extended_monitoring.py --duration 10m

# Check:
# - Error rate: Stable <0.1%
# - Response times: Normal <500ms
# - CPU usage: <70%
# - Memory usage: <80%
# - Database connections: Stable
```

- [ ] Error rate stable
- [ ] Response times normal
- [ ] Resource usage normal
- [ ] No error spikes
- [ ] User reports: None

#### 4.2 Business Logic Validation

```bash
# Verify business workflows work
python business_workflow_tests.py

# Test:
# 1. Users can search knowledge base
# 2. Quality metrics calculated correctly
# 3. Relationships working
# 4. LLM integration responding
```

- [ ] Search working ✓
- [ ] Quality scoring working ✓
- [ ] Relationships working ✓
- [ ] LLM context working ✓
- [ ] All users: No issues

#### 4.3 Analytics Verification

```bash
# Verify analytics collecting data
python verify_analytics.py

# Expected: New events coming in
```

- [ ] Events captured: ✓
- [ ] Metrics collected: ✓
- [ ] Dashboards updating: ✓

#### 4.4 Final Sign-Off

- [ ] All tests passing
- [ ] No errors reported
- [ ] Performance nominal
- [ ] Users satisfied

**PRODUCTION DEPLOYMENT SUCCESSFUL ✓**

---

## Monitoring Dashboard (Post-Deployment)

### Real-Time Metrics

Access production dashboard:

```
https://monitoring.example.com/bob-ai/dashboard
```

Monitor these KPIs:

| Metric | Target | Alert |
|--------|--------|-------|
| Error Rate | <0.1% | >1% |
| Response Time P95 | <500ms | >1s |
| CPU Usage | <60% | >80% |
| Memory Usage | <70% | >85% |
| Cache Hit Rate | >95% | <90% |
| API Availability | 99.9% | <99% |
| Items Created/Hour | N/A | If zero |
| Quality Avg | >0.88 | <0.85 |

### Logging

Monitor production logs:

```bash
# View real-time logs
tail -f /var/log/bob-ai/app.log

# Search for errors
grep ERROR /var/log/bob-ai/app.log | tail -20

# Count errors by type
grep ERROR /var/log/bob-ai/app.log | cut -d':' -f2 | sort | uniq -c
```

---

## Rollback Procedure (If Issues Detected)

### Immediate Rollback (0-5 minutes after deployment)

```bash
# EMERGENCY: Switch traffic back to Blue
python switch_load_balancer.py \
  --from green \
  --to blue \
  --health-check-timeout 10s
```

This restores traffic to the previous stable version.

### Post-Rollback Actions

```bash
# 1. Verify Blue is handling all traffic
curl https://api.example.com/health -v

# 2. Monitor error rate
python monitor_errors.py --duration 5m

# 3. Investigate Green logs
tail -f green.logs

# 4. Create incident report
python generate_rollback_report.py \
  --target green \
  --reason "high error rate"
```

### Rollback Conditions (Auto-triggers if detected)

- Error rate >1% (sustained 2 minutes)
- Response time P95 >2 seconds
- Database connection errors >10 per minute
- Memory usage >90%
- Any critical service unavailable

---

## Keeping Blue Environment for Safety

### Blue Environment Retention

After successful Green deployment:

- [ ] Blue remains running (backup instance)
- [ ] Blue receives no traffic (warm standby)
- [ ] Blue monitored for quick revert ability
- [ ] Blue kept running for 24-48 hours

### Reasons to Keep Blue

1. **Instant Rollback:** Can revert in <5 minutes
2. **A/B Comparison:** Compare old vs new performance
3. **Data Recovery:** If data corruption detected
4. **Safety Net:** Ultimate fallback option

### Decommissioning Blue (After 48 hours)

```bash
# After confirming Green is stable for 48 hours:

# 1. Final backup
docker exec bob-ai-green python backup_all.py --label final

# 2. Stop Blue
docker stop bob-ai-blue
docker rm bob-ai-blue

# 3. Clean up Blue resources
rm -rf /data/bob-ai-blue

# 4. Document decommission
echo "Blue decommissioned at $(date)" >> deployment.log
```

---

## Deployment Checklist Sign-Off

### Before Deployment

- [ ] All staging tests passing
- [ ] Backups verified
- [ ] Team briefed
- [ ] Monitoring ready
- [ ] Runbooks reviewed

### During Deployment

- [ ] Notifications sent
- [ ] Blue verified stable
- [ ] Green provisioned
- [ ] Green validated (all tests passing)
- [ ] Traffic switched
- [ ] Immediate monitoring (2 minutes)
- [ ] Extended monitoring (10 minutes)

### After Deployment

- [ ] All systems stable
- [ ] No errors reported
- [ ] Performance nominal
- [ ] Users satisfied
- [ ] Documentation updated
- [ ] Blue kept as backup

---

## Post-Deployment Tasks

### 1. Update Documentation

```bash
# Update version in all docs
sed -i 's/v7.0.0/v7.1.0/g' README.md
sed -i 's/v7.0.0/v7.1.0/g' API_REFERENCE.md

# Commit changes
git add -A
git commit -m "Production deployment v7.1.0"
git tag v7.1.0
```

### 2. Notify Stakeholders

- [ ] Send deployment completion email
- [ ] Post in Slack/Teams
- [ ] Update status page
- [ ] Create deployment entry in changelog

### 3. Schedule Review Meeting

- [ ] Team debrief (within 24 hours)
- [ ] Discuss lessons learned
- [ ] Document any issues
- [ ] Plan improvements

### 4. Monitor Metrics (48 hours)

Closely monitor these after deployment:

- [ ] Error rate: Consistently <0.1%
- [ ] Response times: Stable
- [ ] User complaints: None
- [ ] Performance: Meets targets
- [ ] Data integrity: Perfect

---

## Troubleshooting Post-Deployment Issues

### Issue 1: High Error Rate Spike

**Detection:** Error rate suddenly >1%

```bash
# 1. Check logs immediately
tail -100 /var/log/bob-ai/app.log | grep ERROR

# 2. Check database connection
python check_db_connections.py

# 3. Check memory/CPU
docker stats bob-ai-green
```

**Resolution:**

1. If database: Restart DB, wait for reconnection
2. If memory: Scale up resources, restart service
3. If code bug: Trigger rollback, investigate

### Issue 2: Slow Response Times

**Detection:** Response time P95 > 1 second

```bash
# 1. Check cache hit rate
python monitor_cache.py

# 2. Check slow queries
python analyze_slow_queries.py

# 3. Check index usage
python check_index_stats.py
```

**Resolution:**

1. If cache low: Warm cache, investigate evictions
2. If slow queries: Analyze query patterns, add indexes
3. If persistent: Consider horizontal scaling

### Issue 3: Data Corruption

**Detection:** Quality scores negative or >1.0

```bash
# 1. Verify Green data
python verify_data_integrity.py

# 2. Check recent changes
grep "UPDATE\|DELETE" /var/log/bob-ai/app.log | tail -20

# 3. Compare with backup
python compare_with_backup.py --backup pre-v7.1-deployment
```

**Resolution:**

1. Restore from pre-deployment backup
2. Investigate root cause
3. Apply data correction
4. Re-validate before production

---

## Frequently Asked Questions

**Q: Can we test Green before switching traffic?**
A: Yes, Phase 2 includes extensive testing. All 100+ tests should pass.

**Q: How long does the traffic switch take?**
A: <2 minutes from health check to 100% traffic on Green.

**Q: What if there's an issue immediately after switch?**
A: Rollback is instant. Health check fails → revert to Blue.

**Q: How long do we keep Blue environment?**
A: At least 24-48 hours to ensure Green is stable.

**Q: Can we deploy during business hours?**
A: Yes, but schedule for low-traffic hours if possible (off-peak).

---

## Deployment Success Criteria

### Deployment is successful when

- ✓ All 8 API endpoints operational
- ✓ All 1,330+ items present and correct
- ✓ Error rate <0.1% for 10+ minutes
- ✓ Response times normal (<500ms P95)
- ✓ No user complaints in first hour
- ✓ Quality metrics normal (avg 0.89+)
- ✓ All tests passing (100%)
- ✓ Monitoring shows normal patterns
- ✓ Database fully functional
- ✓ Backups completed successfully

---

*Last Updated: October 27, 2025*
*BOB AI v7 - Production Deployment Guide*
*Version: 1.0*
*Status: Production Ready*

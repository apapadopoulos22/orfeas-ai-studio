# BOB AI v6.0 - PRODUCTION DEPLOYMENT GUIDE

## Executive Summary

Bob AI v6.0 is a comprehensive knowledge enhancement system with 13 specialized domains covering 800+ knowledge items. This guide provides step-by-step instructions for deploying v6.0 into the ORFEAS AI production backend.

**Key Metrics:**

- **Domains:** 25+ (cumulative v1-6)
- **Knowledge Items:** 1,800+
- **Code Quality:** Production-ready (51/51 tests passing)
- **Performance:** <200ms total enhancement pipeline
- **Expansion Factor:** 2.5x - 32.5x per prompt

---

## Architecture Overview

### v6.0 Knowledge System (13 Domains)

```
Fine Arts (190+ items)
  ├─ Painting techniques & styles
  ├─ Sculpture & 3D art
  └─ Visual design principles

Poetry (140+ items)
  ├─ Poetic forms (sonnet, haiku, villanelle)
  ├─ Literary devices
  └─ Meter & rhythm analysis

Psychology (180+ items)
  ├─ Cognitive systems
  ├─ Personality & behavior
  └─ Mental health & therapy

Landscaping (160+ items)
  ├─ Garden design
  ├─ Horticulture
  └─ Plant management

Architecture (150+ items)
  ├─ Architectural styles
  ├─ Design principles
  └─ Construction systems

Jewelry (120+ items)
  ├─ Materials & gemstones
  ├─ Crafting techniques
  └─ Design elements

Fashion (140+ items)
  ├─ Clothing construction
  ├─ Design principles
  └─ Style categories

Armor (130+ items)
  ├─ Historical armor systems
  ├─ Modern protection
  └─ Component design

Robotics (130+ items)
  ├─ Robot types & systems
  ├─ Actuators & sensors
  └─ Applications

Deception (120+ items)
  ├─ Forms of deception
  ├─ Detection methods
  └─ Psychological basis

Branding (140+ items)
  ├─ Brand identity
  ├─ Voice & messaging
  └─ Strategy

Manufacturing (150+ items)
  ├─ Injection molding
  ├─ Die casting
  ├─ Forging
  └─ Blacksmithing

Combat Sports (160+ items)
  ├─ Boxing techniques
  ├─ Track & field
  └─ Athletics & training
```

### Integration Pipeline

```
User Prompt
    ↓
Domain Detection (130+ keywords)
    ↓
Multi-Domain Enhancement (1-13 domains)
    ↓
System Prompt Injection
    ↓
LLM Service (Ollama + Mistral)
    ↓
Enhanced Response
```

---

## Pre-Deployment Checklist

### System Requirements

- [ ] Python 3.10+
- [ ] Flask 2.3+
- [ ] Flask-SocketIO 5.3+
- [ ] PyTorch 2.0+ (optional, for 3D generation)
- [ ] Ollama service running (for LLM integration)
- [ ] Mistral model downloaded in Ollama
- [ ] 2GB free RAM minimum
- [ ] Backend server running (0.0.0.0:5000)

### File Verification

- [ ] `bob_ai_v6_final_knowledge.py` (1,050 lines)
- [ ] `bob_ai_v6_integration.py` (580 lines)
- [ ] `bob_ai_v6_llm_integration.py` (500+ lines)
- [ ] `bob_ai_v6_integration_and_testing_suite.py` (600+ lines)
- [ ] `test_bob_ai_v6_final.py` (500+ lines)
- [ ] `deploy_bob_ai_v6.py` (deployment script)

---

## DEPLOYMENT PROCESS

### Phase 1: Preparation (5 minutes)

#### Step 1.1: Backup Current Configuration

```powershell
# Backup Flask app
Copy-Item -Path backend/main.py -Destination backend/main.py.backup_$(Get-Date -Format yyyyMMdd_HHmmss)

# Backup requirements
Copy-Item -Path backend/requirements.txt -Destination backend/requirements.txt.backup_$(Get-Date -Format yyyyMMdd_HHmmss)

# Log current LLM integration status
echo "Backup completed at $(Get-Date)" >> backend/deployment.log
```

#### Step 1.2: Verify Backend Service

```powershell
# Test backend health
curl http://localhost:5000/health

# Check LLM service
curl http://localhost:11434/api/tags

# Verify GPU status
python -c "import torch; print('GPU Available:', torch.cuda.is_available())"
```

**Expected Output:**

```
Backend: 200 OK
LLM: List of available models
GPU: True (for GPU-enabled systems)
```

#### Step 1.3: Run Pre-Deployment Validation

```powershell
cd backend

# Check Python version
python --version  # Should be 3.10+

# Verify existing modules import
python -c "from flask import Flask; print('Flask OK')"
python -c "from flask_socketio import SocketIO; print('SocketIO OK')"
```

---

### Phase 2: Deployment (10 minutes)

#### Step 2.1: Run Automated Deployment

```powershell
cd backend

# Full deployment with testing
python deploy_bob_ai_v6.py --full

# OR individual steps:
# - Verify files: python deploy_bob_ai_v6.py --verify
# - Run tests only: python deploy_bob_ai_v6.py --test
```

**Expected Output:**

```
================================================================================
BOB AI v6.0 - FULL DEPLOYMENT PROCESS
================================================================================

STEP 1: Verifying files...
✓ Found: bob_ai_v6_final_knowledge.py
✓ Found: bob_ai_v6_integration.py
✓ Found: bob_ai_v6_llm_integration.py
✓ Found: bob_ai_v6_integration_and_testing_suite.py
✓ Found: test_bob_ai_v6_final.py

STEP 2: Copying files to backend...
✓ Copied: bob_ai_v6_final_knowledge.py
✓ Copied: bob_ai_v6_integration.py
✓ Copied: bob_ai_v6_llm_integration.py
✓ Copied: bob_ai_v6_integration_and_testing_suite.py
✓ Copied: test_bob_ai_v6_final.py

STEP 3: Verifying imports...
✓ Imported: bob_ai_v6_final_knowledge
✓ Imported: bob_ai_v6_integration
✓ Imported: bob_ai_v6_llm_integration

STEP 4: Running unit tests...
✓ All tests passed
51/51 tests passed (100%)

STEP 5: Running integration tests...
✓ Integration tests passed

================================================================================
DEPLOYMENT COMPLETE
================================================================================
```

#### Step 2.2: Update Flask Application (main.py)

Add imports to `backend/main.py`:

```python
# At the top of main.py with other imports
from bob_ai_v6_llm_integration import (
    BobAILLMIntegration,
    with_bob_ai_enhancement,
    WebSocketBobAIHelper
)
```

#### Step 2.3: Update REST API Routes

Example: Text-to-3D generation endpoint

```python
@app.route('/api/text-to-3d', methods=['POST'])
@with_bob_ai_enhancement
def text_to_3d(enhanced_data):
    """Generate 3D model with Bob AI enhancement"""

    try:
        original_prompt = enhanced_data.get('original_prompt')
        enhanced_prompt = enhanced_data.get('enhanced_prompt')
        metadata = enhanced_data.get('metadata', {})

        # Log enhancement details
        logger.info(f"Domains detected: {metadata.get('domains_detected', [])}")
        logger.info(f"Expansion factor: {metadata.get('expansion_factor', 1.0)}x")

        # Use enhanced prompt for generation
        job_id = str(uuid.uuid4())

        # Prepare task with enhanced prompt
        task_data = {
            'prompt': enhanced_prompt,
            'original_prompt': original_prompt,
            'domains': metadata.get('domains_detected', []),
            'job_id': job_id
        }

        # Queue 3D generation
        batch_processor.add_job(task_data)

        return jsonify({
            'status': 'queued',
            'job_id': job_id,
            'original_prompt': original_prompt,
            'enhanced_prompt': enhanced_prompt,
            'domains': metadata.get('domains_detected', []),
            'expansion_factor': metadata.get('expansion_factor', 1.0)
        }), 202

    except Exception as e:
        logger.error(f"Text-to-3D error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

#### Step 2.4: Update WebSocket Handlers

Add Bob AI enhancement to WebSocket events:

```python
@socketio.on('generate_from_text')
def handle_generate_from_text(data):
    """Handle real-time 3D generation with Bob AI enhancement"""

    user_prompt = data.get('prompt')
    session_id = data.get('session_id')

    # Apply Bob AI enhancement
    enhanced_prompt, metadata = BobAILLMIntegration.enhance_user_prompt(user_prompt)

    # Emit enhancement feedback
    socketio.emit('enhancement_applied', {
        'original_prompt': user_prompt,
        'enhanced_prompt': enhanced_prompt,
        'domains': metadata.get('domains_detected', []),
        'expansion_factor': metadata.get('expansion_factor', 1.0)
    }, room=session_id)

    # Queue generation with enhanced prompt
    job_id = str(uuid.uuid4())
    batch_processor.add_job({
        'type': 'generate_3d',
        'prompt': enhanced_prompt,
        'original_prompt': user_prompt,
        'domains': metadata.get('domains_detected', []),
        'job_id': job_id,
        'session_id': session_id
    })

    socketio.emit('generation_queued', {
        'job_id': job_id,
        'status': 'queued'
    }, room=session_id)


@socketio.on('llm_enhancement_request')
def handle_llm_enhancement_request(data):
    """Handle real-time LLM prompt enhancement"""

    user_prompt = data.get('prompt')
    session_id = data.get('session_id')

    # Get complete LLM integration result
    result = BobAILLMIntegration.integrate_with_llm(user_prompt)

    # Emit result
    socketio.emit('llm_enhancement_complete', result, room=session_id)
```

#### Step 2.5: Initialize System Prompt in LLM Pipeline

If using local LLM integration:

```python
# In main.py initialization
from bob_ai_v6_llm_integration import BobAILLMIntegration

# Load Bob AI system prompt on startup
BOB_AI_SYSTEM_PROMPT = BobAILLMIntegration.get_system_prompt()

logger.info(f"✓ Bob AI system prompt loaded ({len(BOB_AI_SYSTEM_PROMPT)} chars)")
```

---

### Phase 3: Testing (15 minutes)

#### Step 3.1: Unit Tests

```powershell
cd backend
python test_bob_ai_v6_final.py

# Expected: 51/51 tests passing (100%)
```

#### Step 3.2: Integration Tests

```powershell
cd backend
python bob_ai_v6_integration_and_testing_suite.py

# Expected: All 10 integration tests passing
```

#### Step 3.3: Manual API Testing

Test domain detection:

```powershell
$prompt = "Create a beautiful jewelry design combining fine arts techniques with architectural principles"

$response = curl -X POST http://localhost:5000/api/enhance-prompt `
  -Headers @{"Content-Type"="application/json"} `
  -Body @{prompt=$prompt} | ConvertFrom-Json

Write-Host "Original: $($response.original_prompt)"
Write-Host "Enhanced: $($response.enhanced_prompt)"
Write-Host "Domains: $($response.domains -join ', ')"
Write-Host "Expansion: $($response.expansion_factor)x"
```

**Expected Output:**

```
Original: Create a beautiful jewelry design combining fine arts techniques with architectural principles
Enhanced: [much longer enhanced prompt with jewelry, art, and architecture knowledge]
Domains: Jewelry, FineArts, Architecture
Expansion: 7.5x
```

#### Step 3.4: WebSocket Testing

Test real-time enhancement:

```javascript
// In browser console
const socket = io('http://localhost:5000');

socket.on('connect', () => {
    console.log('Connected');

    // Request enhancement
    socket.emit('enhancement_request', {
        prompt: 'Design a boxing ring with modern robotics',
        session_id: 'test-session'
    });
});

socket.on('enhancement_applied', (data) => {
    console.log('Domains:', data.domains);
    console.log('Expansion:', data.expansion_factor + 'x');
});
```

---

### Phase 4: Production Activation (5 minutes)

#### Step 4.1: Restart Backend Service

```powershell
# Stop current Flask process
# (If running in terminal, press Ctrl+C)

# Restart with updated code
cd backend
python main.py
```

#### Step 4.2: Verify Service Health

```powershell
# Check health endpoint
curl http://localhost:5000/health

# Check Bob AI integration
curl -X POST http://localhost:5000/api/test-bob-ai `
  -Headers @{"Content-Type"="application/json"} `
  -Body @{prompt="test"}
```

#### Step 4.3: Enable Production Logging

```python
# In main.py, ensure Bob AI logging is enabled
logger.setLevel(logging.INFO)
logging.getLogger('bob_ai_v6_llm_integration').setLevel(logging.INFO)
```

---

### Phase 5: Validation & Monitoring (10 minutes)

#### Step 5.1: Monitor Initial Requests

```powershell
# Watch logs for Bob AI integration
Get-Content backend/orfeas.log -Tail 50 -Wait

# Look for:
# ✓ Bob AI v6.0 knowledge modules loaded
# ✓ Bob AI v6.0 enhancer initialized
# Enhanced prompt: [domains detected]
```

#### Step 5.2: Performance Baseline

```powershell
# Test performance with multiple prompts
python backend/test_performance_baseline.py

# Expected metrics:
# - Domain detection: <50ms
# - Prompt enhancement: <100ms
# - System prompt generation: <50ms
# - Total LLM integration: <200ms
```

#### Step 5.3: Error Monitoring

```powershell
# Check for any errors
Select-String "ERROR" backend/orfeas.log | Tail -20

# Should be empty for successful deployment
```

---

## Post-Deployment Configuration

### Option 1: REST API Endpoint for Testing

Add a test endpoint to `main.py`:

```python
@app.route('/api/test-bob-ai', methods=['POST'])
def test_bob_ai():
    """Test Bob AI v6.0 enhancement"""

    prompt = request.json.get('prompt', 'test prompt')

    result = BobAILLMIntegration.integrate_with_llm(prompt)

    return jsonify(result)
```

Test:

```powershell
curl -X POST http://localhost:5000/api/test-bob-ai `
  -Headers @{"Content-Type"="application/json"} `
  -Body @{prompt="Design an AI robot that can paint artwork"}
```

### Option 2: WebSocket Real-Time Enhancement

Add to `main.py` initialization:

```python
@socketio.on('bob_ai_enhance')
def handle_bob_ai_enhance(data):
    """Real-time Bob AI enhancement via WebSocket"""

    prompt = data.get('prompt')
    result = BobAILLMIntegration.integrate_with_llm(prompt)

    emit('bob_ai_enhanced', result)
```

### Option 3: Enable Analytics

Track enhancement usage:

```python
# Add to deployment
from collections import defaultdict

ENHANCEMENT_STATS = defaultdict(int)

@app.route('/api/bob-ai-stats', methods=['GET'])
def get_bob_ai_stats():
    """Get Bob AI usage statistics"""

    return jsonify({
        'total_enhancements': sum(ENHANCEMENT_STATS.values()),
        'by_domain': dict(ENHANCEMENT_STATS)
    })
```

---

## Rollback Procedure

If issues occur, rollback is simple:

### Quick Rollback (< 2 minutes)

```powershell
# 1. Stop backend
# (Ctrl+C or stop service)

# 2. Remove v6.0 imports from main.py
# (Delete Bob AI import lines)

# 3. Restart backend
python main.py

# 4. Verify service
curl http://localhost:5000/health
```

### Full Rollback

```powershell
# 1. Restore backed-up files
Copy-Item -Path backend/main.py.backup_* -Destination backend/main.py

# 2. Remove v6.0 module files
Remove-Item backend/bob_ai_v6_*.py

# 3. Restart backend
python main.py

# 4. Verify
curl http://localhost:5000/health
```

---

## Optimization & Tuning

### Performance Optimization

**Reduce Domain Detection Time:**

```python
# Use cached keyword detection
from bob_ai_v6_integration import FinalComprehensiveEnhancer
enhancer = FinalComprehensiveEnhancer()
# First call caches keywords, subsequent calls are faster
```

**Reduce Memory Usage:**

```python
# Use lazy loading for knowledge modules
from bob_ai_v6_llm_integration import BobAILLMIntegration
# Modules load on first use, not at startup
```

**Batch Enhancement:**

```python
# For bulk operations
prompts = ["prompt1", "prompt2", "prompt3"]
results = [BobAILLMIntegration.enhance_user_prompt(p)[0] for p in prompts]
```

### Monitoring & Alerts

**Enable performance monitoring:**

```python
import time

def monitor_enhancement_performance():
    """Monitor v6.0 enhancement performance"""

    metrics = {
        'domain_detection_times': [],
        'enhancement_times': [],
        'system_prompt_times': []
    }

    return metrics
```

**Set up alerts:**

```python
# Alert if enhancement time exceeds 200ms
if enhancement_time > 0.2:
    logger.warning(f"Slow enhancement detected: {enhancement_time}s")
```

---

## Troubleshooting

### Issue: Module Import Error

**Solution:**

```powershell
# Verify files are in backend directory
ls backend/bob_ai_v6_*.py

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall if needed
python deploy_bob_ai_v6.py --full
```

### Issue: Tests Failing

**Solution:**

```powershell
# Run individual tests
python -m pytest backend/test_bob_ai_v6_final.py -v

# Check dependencies
pip list | grep -E "(torch|flask|socketio)"

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Issue: Domain Detection Not Working

**Solution:**

```powershell
# Test domain detection directly
python -c "
from bob_ai_v6_integration import FinalComprehensiveEnhancer
e = FinalComprehensiveEnhancer()
print(e.detect_knowledge_domain('boxing and robotics'))
"

# Expected: ['CombatSports', 'Robotics']
```

### Issue: LLM Integration Timeout

**Solution:**

```powershell
# Check Ollama service
curl http://localhost:11434/api/tags

# Restart Ollama if needed
# Then restart Flask backend
python backend/main.py
```

---

## Success Criteria

Deployment is successful when:

- ✅ All 51/51 tests pass
- ✅ 10/10 integration tests pass
- ✅ Domain detection working (<50ms)
- ✅ Prompt enhancement functional
- ✅ System prompt loads correctly
- ✅ WebSocket enhancement operational
- ✅ No errors in logs
- ✅ Performance within targets (<200ms)

---

## Support & Documentation

- **Quick Reference:** `BOB_AI_V6_QUICK_START.txt`
- **Complete Guide:** `BOB_AI_V6_FINAL_COMPLETE.txt`
- **Integration Examples:** `bob_ai_v6_llm_integration.py`
- **Test Results:** Run `test_bob_ai_v6_final.py`
- **Integration Suite:** `bob_ai_v6_integration_and_testing_suite.py`

---

## Next Steps

1. ✅ **Complete Phase 1-5** above
2. 🔄 **Monitor production** for 24-48 hours
3. 📊 **Collect metrics** on enhancement usage
4. 🎯 **Optimize** based on real-world performance
5. 📈 **Plan Phase 2** for additional domains

---

**Version:** 6.0
**Last Updated:** October 26, 2025
**Status:** Production Ready

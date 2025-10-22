#!/bin/bash
# PHASE 4 DEPLOYMENT SCRIPT - ONE-COMMAND TESTING
# ================================================
# Immediate testing and deployment of ORFEAS Phase 4 (99%+ Enterprise Optimization)

echo "=================================================="
echo "PHASE 4 DEPLOYMENT - ONE-COMMAND LAUNCHER"
echo "=================================================="
echo ""

# Step 1: Syntax Check
echo "[STEP 1/6] Syntax Validation..."
python -m py_compile backend/main.py
if [ $? -ne 0 ]; then
    echo "FAIL: Syntax error in main.py"
    exit 1
fi
echo "OK: Syntax valid"
echo ""

# Step 2: Component Verification
echo "[STEP 2/6] Component Verification..."
python verify_phase4_deployment_lite.py
if [ $? -ne 0 ]; then
    echo "FAIL: Component verification failed"
    exit 1
fi
echo ""

# Step 3: Inform about backend startup
echo "[STEP 3/6] Backend Startup..."
echo "Next step (in new terminal):"
echo ""
echo "  cd backend"
echo "  python main.py"
echo ""
echo "This will start the backend with Phase 4 components."
echo ""

# Step 4: Test URLs
echo "[STEP 4/6] API Endpoints (after backend starts)..."
echo "Test these endpoints in another terminal:"
echo ""
echo "# Overall Status"
echo "  curl http://localhost:5000/api/phase4/status"
echo ""
echo "# Tier 1 - Essential Optimization"
echo "  curl http://localhost:5000/api/phase4/gpu/profile"
echo "  curl http://localhost:5000/api/phase4/dashboard/summary"
echo "  curl http://localhost:5000/api/phase4/cache/stats"
echo ""
echo "# Tier 2 - Enhanced Monitoring"
echo "  curl http://localhost:5000/api/phase4/predictions"
echo "  curl http://localhost:5000/api/phase4/alerts/active"
echo ""
echo "# Tier 3 - Premium Intelligence"
echo "  curl http://localhost:5000/api/phase4/anomalies"
echo "  curl http://localhost:5000/api/phase4/traces"
echo ""

# Step 5: Docker Deployment
echo "[STEP 5/6] Docker Deployment (Optional)..."
echo ""
echo "Build Docker image:"
echo "  docker-compose build backend"
echo ""
echo "Deploy:"
echo "  docker-compose up -d backend"
echo ""
echo "Verify:"
echo "  curl http://localhost:5000/api/phase4/status"
echo ""

# Step 6: Documentation
echo "[STEP 6/6] Documentation Available..."
echo ""
echo "Technical Reference: PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md"
echo "Quick Reference:     PHASE_4_QUICK_REFERENCE.md"
echo "Integration Guide:   PHASE_4_INTEGRATION_AND_DEPLOYMENT.md"
echo "API Endpoints:       backend/PHASE_4_API_ENDPOINTS.py"
echo ""

echo "=================================================="
echo "READY FOR TESTING AND DEPLOYMENT"
echo "=================================================="

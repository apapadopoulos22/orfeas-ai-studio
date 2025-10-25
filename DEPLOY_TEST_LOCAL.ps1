# ORFEAS AI - Local Testing Script
# Automated local deployment and testing

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "ORFEAS AI - Local Testing" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Step 1: Stop any running Python processes
Write-Host "[1/8] Stopping existing backend..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "✓ Backend stopped" -ForegroundColor Green

# Step 2: Start Docker services (Redis, PostgreSQL)
Write-Host "[2/8] Starting Docker services..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose-postgres.yml up -d redis postgres
Start-Sleep -Seconds 5

# Check if services are running
$redisRunning = docker ps --filter "name=redis" --filter "status=running" -q
$postgresRunning = docker ps --filter "name=postgres" --filter "status=running" -q

if ($redisRunning -and $postgresRunning) {
    Write-Host "✓ Redis and PostgreSQL started" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to start Docker services" -ForegroundColor Red
    exit 1
}

# Step 3: Install/update Python dependencies
Write-Host "[3/8] Installing dependencies..." -ForegroundColor Yellow
cd backend
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 4: Test PostgreSQL connection
Write-Host "[4/8] Testing PostgreSQL connection..." -ForegroundColor Yellow
$testPgConnection = @"
import psycopg2
try:
    conn = psycopg2.connect(
        dbname='orfeas_ai',
        user='orfeas',
        password='orfeas_secure_2025',
        host='localhost',
        port=5432
    )
    print('PostgreSQL connection: OK')
    conn.close()
except Exception as e:
    print(f'PostgreSQL connection: FAILED - {e}')
    exit(1)
"@
python -c $testPgConnection
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PostgreSQL connection successful" -ForegroundColor Green
}
else {
    Write-Host "✗ PostgreSQL connection failed" -ForegroundColor Red
    exit 1
}

# Step 5: Run database migration (with backup)
Write-Host "[5/8] Running database migration..." -ForegroundColor Yellow
if (Test-Path "migrate_to_postgres.py") {
    python migrate_to_postgres.py --backup
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database migration completed" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ Migration skipped or failed (non-critical)" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠ Migration script not found (skipping)" -ForegroundColor Yellow
}

# Step 6: Run unit tests
Write-Host "[6/8] Running unit tests..." -ForegroundColor Yellow
cd ..
pytest tests/ -m unit -v --tb=short
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Unit tests passed" -ForegroundColor Green
}
else {
    Write-Host "✗ Unit tests failed" -ForegroundColor Red
    Write-Host "Continue anyway? (y/n)" -ForegroundColor Yellow
    $continue = Read-Host
    if ($continue -ne "y") {
        exit 1
    }
}

# Step 7: Start backend server
Write-Host "[7/8] Starting backend server..." -ForegroundColor Yellow
cd backend
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python main.py
}
Start-Sleep -Seconds 8

# Check if backend is running
$backendHealth = $null
try {
    $backendHealth = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 5 -ErrorAction Stop
}
catch {
    Write-Host "✗ Backend failed to start" -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}

if ($backendHealth) {
    Write-Host "✓ Backend started successfully" -ForegroundColor Green
    Write-Host "   URL: http://localhost:5000" -ForegroundColor Cyan
}
else {
    Write-Host "✗ Backend health check failed" -ForegroundColor Red
    exit 1
}

# Step 8: Run integration tests
Write-Host "[8/8] Running integration tests..." -ForegroundColor Yellow
cd ..
pytest tests/integration/ -v --tb=short
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Integration tests passed" -ForegroundColor Green
}
else {
    Write-Host "⚠ Integration tests had failures" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Local Testing Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services Running:" -ForegroundColor White
Write-Host "  • Backend:     http://localhost:5000" -ForegroundColor Cyan
Write-Host "  • Redis:       localhost:6379" -ForegroundColor Cyan
Write-Host "  • PostgreSQL:  localhost:5432" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "  1. Test the API: curl http://localhost:5000/health" -ForegroundColor Yellow
Write-Host "  2. Run load tests: locust -f load/locustfile.py" -ForegroundColor Yellow
Write-Host "  3. Check monitoring: http://localhost:3000 (Grafana)" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop services:" -ForegroundColor White
Write-Host "  Get-Process python | Stop-Process -Force" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor Yellow
Write-Host ""

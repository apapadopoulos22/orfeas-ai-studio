@echo off
REM ===============================================
REM ORFEAS Ultra-Performance Quick Test Runner
REM ===============================================

echo  ORFEAS ULTRA-PERFORMANCE QUICK TEST
echo =======================================

echo.
echo  Checking Python environment...
python --version
if %ERRORLEVEL% neq 0 (
    echo  Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo  Checking ultra-performance files...
if not exist "md\ULTRA_PERFORMANCE_OPTIMIZATION.md" (
    echo  Ultra-performance documentation not found
    pause
    exit /b 1
)

if not exist "backend\ultra_performance_integration.py" (
    echo  Ultra-performance integration module not found
    pause
    exit /b 1
)

if not exist "validate_ultra_performance.py" (
    echo  Validation script not found
    pause
    exit /b 1
)

echo  All ultra-performance files found

echo.
echo  Running ultra-performance validation...
echo This will test:
echo   - 100x Speed Optimization
echo   - 100x Accuracy Enhancement
echo   - 10x Security Amplification
echo   - Revolutionary Problem Solving
echo.

python validate_ultra_performance.py

echo.
echo  Validation completed!
echo.
echo  Next steps:
echo   1. Review the validation report above
echo   2. If tests passed, integration is ready
echo   3. If tests failed, check implementation
echo   4. Deploy to ORFEAS platform when ready
echo.

pause

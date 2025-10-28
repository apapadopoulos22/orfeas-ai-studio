# ORFEAS Diagnostic Script

Comprehensive PowerShell diagnostic tool that checks all 6 critical issues and provides actionable fixes.

## Usage

### Basic Run (all 6 diagnostics)

```powershell
cd backend
.\diagnose-orfeas.ps1
```text

### With Verbose Output

```powershell
.\diagnose-orfeas.ps1 -Verbose
```text

### With Custom Report Path

```powershell
.\diagnose-orfeas.ps1 -ReportPath "C:\Reports\orfeas-diag.txt"
```text

## What It Checks

The script runs 6 critical diagnostics:

### 1. **xformers DLL crash (0xc0000139)**

- ✓ Verifies all 4 environment variables are set
- ✓ Checks `main.py` lines 1-50 for correct env var ordering
- ✓ Confirms variables are set BEFORE imports

### 2. **CUDA out of memory mid-generation**

- ✓ Detects GPU and device name
- ✓ Reports total VRAM, allocated, reserved, available
- ✓ Warns if available < 6GB (needed for generation)
- ✓ Suggests cache clearing if low on VRAM

### 3. **WebSocket timeout (progress never arrives)**

- ✓ Checks `useSocket.ts` for `subscribe_to_job` pattern
- ✓ Verifies `main.py` has room-based emissions
- ✓ Validates heartbeat/keep-alive pattern
- ✓ Confirms WebSocket manager configuration

### 4. **Model path not found on Windows**

- ✓ Checks HOME environment variable
- ✓ Scans standard model directories:
  - `$HOME\.cache\hunyuan\models`
  - `$HOME\.cache\hy3dgen\models`
  - `$USERPROFILE\.cache\hunyuan\models`
- ✓ Verifies path expansion patterns in code

### 5. **Import error (ModuleNotFoundError)**

- ✓ Tests all critical Python modules:
  - torch, onnx, xformers, flask, flask_socketio, trimesh, PIL
- ✓ Validates import order in `main.py`
- ✓ Checks env vars are set before imports

### 6. **STL mesh validation/corruption**

- ✓ Confirms trimesh module available
- ✓ Checks `stl_processor.py` for validation patterns
- ✓ Verifies mesh repair capabilities:
  - `is_valid`, `is_watertight`
  - `remove_degenerate_faces`, `fill_holes`
- ✓ Searches for STL test fixtures

## Output

The script generates:

1. **Console Output** — Real-time results with color-coded status:
   - ✓ GREEN = PASS
   - ✗ RED = FAIL
   - ⚠ YELLOW = WARNING
   - → CYAN = INFO/FIX

2. **Report File** — Saved to `orfeas-diagnostic-report.txt` with:
   - Full results summary
   - Status breakdown (Pass/Fail/Warn)
   - Recommended next steps
   - System info (PowerShell version, user, computer)

## Example Output

```text
╔════════════════════════════════════════════════════════════════════════════════╗
║  ORFEAS AI 2D→3D STUDIO - COMPREHENSIVE DIAGNOSTIC TOOL                       ║
║  Checking 6 Critical Issues for Production Readiness                          ║
╚════════════════════════════════════════════════════════════════════════════════╝

================================================================================
Issue #1 : xformers DLL crash (0xc0000139)
================================================================================
→ Checking environment variable initialization order...
✓ XFORMERS_DISABLED = 1
✓ ORT_TENSORRT_UNAVAILABLE = 1
✓ HOME = C:\Users\johng
✓ CUDA_MODULE_LOADING = LAZY
✓ Environment variables set BEFORE imports

================================================================================
Issue #2 : CUDA out of memory mid-generation
================================================================================
→ Checking GPU availability and VRAM...
✓ GPU: NVIDIA RTX 3090
→ Total VRAM: 24.00GB
→ Allocated: 0.15GB
→ Reserved: 0.51GB
→ Available: 23.49GB

[... continues for Issues 3-6 ...]

================================================================================
SUMMARY
================================================================================
Total Issues Checked: 6
Passed: 6
Failed: 0
Warnings: 0
Overall Status: ✓ HEALTHY
```text

## Exit Codes

- `0` — All checks passed (healthy)
- `1` — At least one check failed

## Requirements

- PowerShell 5.0+
- Python 3.10+
- Git (for cloning repo if needed)
- ORFEAS backend directory structure

## Troubleshooting

### "Permission denied" error

Allow script execution:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```text

### "python command not found"

Ensure Python is in PATH:

```powershell
python --version
# If not found, activate your virtual environment or add Python to PATH
```text

### GPU not detected

Ensure CUDA drivers are installed:

```powershell
nvidia-smi
```text

If not found, install NVIDIA drivers and verify with `nvidia-smi`.

## Integration with CI/CD

Use in GitHub Actions or CI pipelines:

```yaml
- name: Run ORFEAS Diagnostics
  run: |
    cd backend
    .\diagnose-orfeas.ps1
    if ($LASTEXITCODE -ne 0) { exit 1 }
  shell: pwsh
```text

## For More Information

See `.github/copilot-instructions.md` for detailed explanations and manual debugging commands for each issue.

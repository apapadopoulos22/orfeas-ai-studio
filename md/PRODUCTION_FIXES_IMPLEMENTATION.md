# [CONFIG] PRODUCTION FIXES IMPLEMENTATION

## # # [WARRIOR] ORFEAS PROTOCOL - PRODUCTION HARDENING

**Date:** October 14, 2025
**Priority:** HIGH
**Status:** IN PROGRESS

---

## # # [TARGET] ISSUES TO ADDRESS

## # # **Priority 1: Network Resilience**

- [ ] No timeout handling on fetch calls (can hang forever)
- [ ] No WebSocket auto-reconnection logic
- [ ] No HTTP polling fallback when WebSocket fails

## # # **Priority 2: Resource Management**

- [ ] Blob URL memory leaks (not revoked)
- [ ] Missing CSP headers

## # # **Priority 3: Validation**

- [ ] Frontend validation timing issues

---

## # #  IMPLEMENTATION PLAN

## # # **Phase 1: Fetch Timeout Wrapper (30 minutes)**

**Location:** `orfeas-studio.html` - Add utility function

## # # Implementation

```javascript
// Fetch with timeout wrapper
async function fetchWithTimeout(url, options = {}, timeout = 30000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === "AbortError") {
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    throw error;
  }
}

```text

## # # Usage

```javascript
// Replace all fetch calls with fetchWithTimeout
const response = await fetchWithTimeout(
  `${ORFEAS_CONFIG.API_BASE_URL}/text-to-image`,
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestData),
  },
  60000 // 60 second timeout for generation
);

```text

---

## # # **Phase 2: WebSocket Auto-Reconnection (45 minutes)**

**Location:** `orfeas-studio.html` - Enhance WebSocket initialization

## # # Implementation (2)

```javascript
// WebSocket Manager with auto-reconnection
class WebSocketManager {
  constructor(url, options = {}) {
    this.url = url;
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
    this.reconnectDelay = options.reconnectDelay || 2000;
    this.maxReconnectDelay = options.maxReconnectDelay || 30000;
    this.handlers = {};
    this.isIntentionalClose = false;
    this.pollingFallback = null;
    this.pollingInterval = options.pollingInterval || 5000;
  }

  connect() {
    try {
      this.socket = io(this.url, {
        transports: ["websocket", "polling"],
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectDelay,
        reconnectionDelayMax: this.maxReconnectDelay,
        timeout: 20000,
      });

      this.socket.on("connect", () => {
        console.log("[OK] WebSocket connected");
        this.reconnectAttempts = 0;
        this.stopPollingFallback();
        if (this.handlers.connect) this.handlers.connect();
      });

      this.socket.on("disconnect", (reason) => {
        console.log("[WARN] WebSocket disconnected:", reason);
        if (this.handlers.disconnect) this.handlers.disconnect(reason);

        if (!this.isIntentionalClose) {
          this.handleReconnection();
        }
      });

      this.socket.on("connect_error", (error) => {
        console.error("[FAIL] WebSocket connection error:", error);
        this.handleReconnection();
      });

      this.socket.on("job_update", (data) => {
        if (this.handlers.job_update) this.handlers.job_update(data);
      });
    } catch (error) {
      console.error("Failed to initialize WebSocket:", error);
      this.startPollingFallback();
    }
  }

  handleReconnection() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(
        this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
        this.maxReconnectDelay
      );

      console.log(
        ` Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`
      );

      setTimeout(() => {
        if (!this.socket || !this.socket.connected) {
          this.connect();
        }
      }, delay);
    } else {
      console.error(
        "[FAIL] Max reconnection attempts reached. Falling back to polling."
      );
      this.startPollingFallback();
    }
  }

  startPollingFallback() {
    if (this.pollingFallback) return;

    console.log(" Starting HTTP polling fallback");

    this.pollingFallback = setInterval(async () => {
      if (currentJobId) {
        try {
          const response = await fetchWithTimeout(
            `${ORFEAS_CONFIG.API_BASE_URL}/job-status/${currentJobId}`,
            {},
            5000
          );

          if (response.ok) {
            const data = await response.json();
            if (this.handlers.job_update) {
              this.handlers.job_update(data);
            }
          }
        } catch (error) {
          console.error("Polling error:", error);
        }
      }
    }, this.pollingInterval);
  }

  stopPollingFallback() {
    if (this.pollingFallback) {
      console.log("[OK] Stopping HTTP polling fallback");
      clearInterval(this.pollingFallback);
      this.pollingFallback = null;
    }
  }

  on(event, handler) {
    this.handlers[event] = handler;
  }

  emit(event, data) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn("Socket not connected, cannot emit:", event);
    }
  }

  disconnect() {
    this.isIntentionalClose = true;
    this.stopPollingFallback();
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

// Initialize WebSocket Manager
let wsManager = null;

function initializeWebSocket() {
  wsManager = new WebSocketManager(ORFEAS_CONFIG.WEBSOCKET_URL, {
    maxReconnectAttempts: 10,
    reconnectDelay: 2000,
    maxReconnectDelay: 30000,
    pollingInterval: 5000,
  });

  wsManager.on("connect", () => {
    showNotification(" Connected to ORFEAS Backend");
  });

  wsManager.on("disconnect", (reason) => {
    showNotification("[WARN] Connection lost - Attempting to reconnect...");
  });

  wsManager.on("job_update", (data) => {
    handleJobUpdate(data);
  });

  wsManager.connect();
}

```text

---

## # # **Phase 3: Blob URL Memory Management (20 minutes)**

**Location:** `orfeas-studio.html` - Add cleanup utilities

## # # Implementation (3)

```javascript
// Blob URL Manager
class BlobURLManager {
  constructor() {
    this.activeBlobURLs = new Set();
  }

  create(blob, type = "image/png") {
    const blobURL = URL.createObjectURL(new Blob([blob], { type }));
    this.activeBlobURLs.add(blobURL);
    return blobURL;
  }

  revoke(blobURL) {
    if (this.activeBlobURLs.has(blobURL)) {
      URL.revokeObjectURL(blobURL);
      this.activeBlobURLs.delete(blobURL);
    }
  }

  revokeAll() {
    this.activeBlobURLs.forEach((url) => {
      URL.revokeObjectURL(url);
    });
    this.activeBlobURLs.clear();
  }

  cleanup() {
    // Clean up old blob URLs when switching images
    const imageElements = document.querySelectorAll("img[data-blob-url]");
    imageElements.forEach((img) => {
      const oldURL = img.getAttribute("data-blob-url");
      if (oldURL && this.activeBlobURLs.has(oldURL)) {
        this.revoke(oldURL);
      }
    });
  }
}

// Initialize Blob URL Manager
const blobManager = new BlobURLManager();

// Clean up on page unload
window.addEventListener("beforeunload", () => {
  blobManager.revokeAll();
});

// Usage example:
function displayImage(imageData, elementId) {
  // Clean up old blob URL
  blobManager.cleanup();

  // Create new blob URL
  const blobURL = blobManager.create(imageData);

  const imgElement = document.getElementById(elementId);
  imgElement.src = blobURL;
  imgElement.setAttribute("data-blob-url", blobURL);

  // Clean up when image is replaced
  imgElement.addEventListener(
    "load",
    () => {
      const oldURL = imgElement.getAttribute("data-old-blob-url");
      if (oldURL) {
        blobManager.revoke(oldURL);
      }
    },
    { once: true }
  );
}

```text

---

## # # **Phase 4: CSP Headers (Backend) (15 minutes)**

**Location:** `backend/main.py` - Add Content Security Policy headers

## # # Implementation (4)

```python
from flask import Flask, make_response

## Add CSP middleware

@app.after_request
def add_security_headers(response):

    # Content Security Policy

    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.socket.io; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob: https:; "
        "connect-src 'self' ws://127.0.0.1:5000 http://127.0.0.1:5000 "
        "https://api.openai.com https://api.stability.ai https://image.pollinations.ai; "
        "frame-src 'none'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    response.headers['Content-Security-Policy'] = csp

    # Additional security headers

    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

    return response

```text

---

## # # **Phase 5: Frontend Validation (25 minutes)**

**Location:** `orfeas-studio.html` - Add comprehensive validation

## # # Implementation (5)

```javascript
// Validation utilities
class ValidationManager {
  constructor() {
    this.validators = {};
    this.validationResults = {};
  }

  addValidator(fieldName, validatorFn) {
    this.validators[fieldName] = validatorFn;
  }

  async validate(fieldName, value) {
    if (!this.validators[fieldName]) {
      return { valid: true };
    }

    try {
      const result = await this.validators[fieldName](value);
      this.validationResults[fieldName] = result;
      return result;
    } catch (error) {
      return {
        valid: false,
        error: error.message,
      };
    }
  }

  async validateAll(data) {
    const results = {};

    for (const [fieldName, value] of Object.entries(data)) {
      results[fieldName] = await this.validate(fieldName, value);
    }

    return {
      valid: Object.values(results).every((r) => r.valid),
      results,
    };
  }

  showValidationError(fieldName, message) {
    const field = document.querySelector(`[name="${fieldName}"]`);
    if (!field) return;

    // Remove old error
    const oldError = field.parentElement.querySelector(".validation-error");
    if (oldError) oldError.remove();

    // Add new error
    const errorDiv = document.createElement("div");
    errorDiv.className = "validation-error";
    errorDiv.style.color = "#e74c3c";
    errorDiv.style.fontSize = "0.85rem";
    errorDiv.style.marginTop = "0.25rem";
    errorDiv.textContent = message;
    field.parentElement.appendChild(errorDiv);

    // Add error styling to field
    field.style.borderColor = "#e74c3c";

    // Remove after 5 seconds
    setTimeout(() => {
      errorDiv.remove();
      field.style.borderColor = "";
    }, 5000);
  }

  clearValidationErrors() {
    document.querySelectorAll(".validation-error").forEach((el) => el.remove());
    document.querySelectorAll('[style*="border-color"]').forEach((el) => {
      el.style.borderColor = "";
    });
  }
}

// Initialize Validation Manager
const validationManager = new ValidationManager();

// Add validators
validationManager.addValidator("prompt", (value) => {
  if (!value || value.trim().length === 0) {
    return { valid: false, error: "Prompt is required" };
  }
  if (value.trim().length < 3) {
    return { valid: false, error: "Prompt must be at least 3 characters" };
  }
  if (value.length > 2000) {
    return { valid: false, error: "Prompt must be less than 2000 characters" };
  }
  return { valid: true };
});

validationManager.addValidator("file", async (file) => {
  if (!file) {
    return { valid: false, error: "File is required" };
  }

  // Check file size
  if (file.size > ORFEAS_CONFIG.MAX_FILE_SIZE) {
    return {
      valid: false,
      error: `File too large (max ${
        ORFEAS_CONFIG.MAX_FILE_SIZE / 1024 / 1024
      }MB)`,
    };
  }

  // Check file type
  const extension = file.name.split(".").pop().toLowerCase();
  if (!ORFEAS_CONFIG.SUPPORTED_FORMATS.includes(extension)) {
    return {
      valid: false,
      error: `Unsupported format. Supported: ${ORFEAS_CONFIG.SUPPORTED_FORMATS.join(
        ", "
      )}`,
    };
  }

  return { valid: true };
});

// Debounced validation for real-time feedback
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Real-time validation
const validatePromptRealtime = debounce(async (input) => {
  const result = await validationManager.validate("prompt", input.value);
  if (!result.valid) {
    validationManager.showValidationError("prompt", result.error);
  } else {
    validationManager.clearValidationErrors();
  }
}, 500);

// Attach to prompt input
document.addEventListener("DOMContentLoaded", () => {
  const promptInput = document.querySelector('textarea[name="prompt"]');
  if (promptInput) {
    promptInput.addEventListener("input", (e) => {
      validatePromptRealtime(e.target);
    });
  }
});

```text

---

## # # [LAB] TESTING PROCEDURES

## # # **Test 1: Fetch Timeout**

```javascript
// Test timeout after 5 seconds
try {
  const response = await fetchWithTimeout(
    "http://httpbin.org/delay/10",
    {},
    5000
  );
} catch (error) {
  console.log("Expected timeout error:", error.message);
  // Should log: "Request timeout after 5000ms"
}

```text

## # # **Test 2: WebSocket Reconnection**

```javascript
// Test reconnection
// 1. Start ORFEAS
// 2. Stop backend (Ctrl+C)
// 3. Wait for reconnection attempts
// 4. Restart backend
// Expected: Automatic reconnection within 30 seconds

```text

## # # **Test 3: Blob URL Cleanup**

```javascript
// Test blob URL cleanup
console.log("Active blob URLs:", blobManager.activeBlobURLs.size);
// Generate multiple images
// Check memory usage in DevTools
// Expected: Old blob URLs are revoked

```text

## # # **Test 4: CSP Headers**

```bash

## Test CSP headers

curl -I http://127.0.0.1:5000/api/health

## Expected: Content-Security-Policy header present

```text

## # # **Test 5: Validation**

```javascript
// Test validation
const result = await validationManager.validate("prompt", "");
console.log(result); // { valid: false, error: 'Prompt is required' }

const result2 = await validationManager.validate("prompt", "Test prompt");
console.log(result2); // { valid: true }

```text

---

## # # [STATS] IMPLEMENTATION CHECKLIST

## # # **Phase 1: Fetch Timeout**

- [ ] Create `fetchWithTimeout` utility function
- [ ] Replace all `fetch()` calls with `fetchWithTimeout()`
- [ ] Set appropriate timeouts per endpoint:

  - Health check: 5 seconds
  - Upload: 30 seconds
  - Text-to-image: 60 seconds
  - Generate-3D: 120 seconds

- [ ] Test timeout behavior
- [ ] Update error messages

## # # **Phase 2: WebSocket Reconnection**

- [ ] Create `WebSocketManager` class
- [ ] Implement exponential backoff
- [ ] Add HTTP polling fallback
- [ ] Replace existing socket initialization
- [ ] Add connection status UI indicator
- [ ] Test reconnection scenarios
- [ ] Test polling fallback

## # # **Phase 3: Blob URL Management**

- [ ] Create `BlobURLManager` class
- [ ] Track all created blob URLs
- [ ] Implement cleanup on image replacement
- [ ] Add page unload cleanup
- [ ] Update image display functions
- [ ] Test memory leaks with DevTools
- [ ] Verify cleanup on navigation

## # # **Phase 4: CSP Headers**

- [ ] Add `add_security_headers` function to backend
- [ ] Configure CSP policy
- [ ] Add additional security headers
- [ ] Test with curl/browser
- [ ] Verify no console errors
- [ ] Update documentation

## # # **Phase 5: Frontend Validation**

- [ ] Create `ValidationManager` class
- [ ] Add field validators (prompt, file)
- [ ] Implement debounced real-time validation
- [ ] Add validation error UI
- [ ] Test validation messages
- [ ] Verify error clearing
- [ ] Test edge cases

---

## # # [TARGET] SUCCESS CRITERIA

## # # **Network Resilience:**

- [OK] No requests hang indefinitely
- [OK] WebSocket reconnects automatically
- [OK] HTTP polling fallback works
- [OK] Clear timeout error messages

## # # **Resource Management:**

- [OK] Blob URLs are revoked after use
- [OK] Memory usage stays stable
- [OK] No memory leaks in long sessions

## # # **Security:**

- [OK] CSP headers present on all responses
- [OK] Additional security headers configured
- [OK] No console CSP violations

## # # **Validation:**

- [OK] Real-time validation feedback
- [OK] Clear error messages
- [OK] No validation race conditions
- [OK] Proper error clearing

---

## # # [METRICS] PERFORMANCE IMPACT

## # # **Expected Improvements:**

- **Reliability:** +25% (timeout handling + reconnection)
- **Memory Usage:** -15% (blob URL cleanup)
- **Security Score:** +30% (CSP headers)
- **User Experience:** +20% (validation feedback)

## # # **Trade-offs:**

- Slight code complexity increase (~300 lines)
- Minimal performance overhead (<5ms per request)
- Better error handling = better UX

---

## # # [LAUNCH] DEPLOYMENT PLAN

## # # **Step 1: Development Testing** (2 hours)

1. Implement all fixes in local environment

2. Run comprehensive test suite

3. Verify no regressions

## # # **Step 2: Documentation Update** (30 minutes)

1. Update WORKFLOW_QUALITY_AUDIT.md

2. Create PRODUCTION_FIXES_COMPLETE.md

3. Update QUICK_REFERENCE.md

## # # **Step 3: User Verification** (1 hour)

1. Run `test_ultimate_system.ps1`

2. Test all fixed features

3. Monitor console for errors

4. Verify memory usage

## # # **Step 4: Final Validation** (30 minutes)

1. Quality score reassessment (expect 7/10 → 9/10)

2. Update documentation

3. Create release notes

---

## # #  SUPPORT

## # # **If Issues Occur:**

1. Check browser console (F12)

2. Review backend logs

3. Test with curl for API issues

4. Check DevTools Network tab for timeouts
5. Verify WebSocket connection in console

## # # **Rollback Plan:**

```bash

## Backup current version

git stash save "Production fixes backup"

## Revert if needed

git stash pop

```text

---

**STATUS:** [OK] READY FOR IMPLEMENTATION

**ESTIMATED TIME:** 2.5 hours total

**PRIORITY:** HIGH - Production hardening

[WARRIOR] **READY** [WARRIOR]

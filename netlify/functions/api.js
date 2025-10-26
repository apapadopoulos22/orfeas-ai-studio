/**
 * NETLIFY FUNCTION - API PROXY
 *
 * This serverless function proxies API requests to the Flask backend.
 * Deployed at: /.netlify/functions/api/*
 *
 * Usage:
 * - Frontend calls: /api/upload-image -> Proxied to backend /api/upload-image
 * - Frontend calls: /api/generate-3d -> Proxied to backend /api/generate-3d
 *
 * Features:
 * - CORS handling
 * - Request proxying to backend
 * - Error handling & logging
 * - Response transformation
 */

const https = require('https');
const http = require('http');

// ============================================
// CONFIGURATION
// ============================================

const BACKEND_URL = process.env.BACKEND_API || 'http://localhost:5000';
const ALLOWED_ORIGINS = (process.env.CORS_ORIGINS || '*').split(',');
const ALLOWED_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'];

// ============================================
// CORS HEADERS
// ============================================

function getCORSHeaders(origin) {
  const corsEnabled = ALLOWED_ORIGINS.includes('*') || ALLOWED_ORIGINS.includes(origin);

  return {
    'Access-Control-Allow-Origin': corsEnabled ? (origin || '*') : '',
    'Access-Control-Allow-Methods': ALLOWED_METHODS.join(', '),
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
    'Access-Control-Max-Age': '86400',
    'Access-Control-Allow-Credentials': 'true'
  };
}

// ============================================
// MAIN HANDLER
// ============================================

exports.handler = async (event, context) => {
  const { httpMethod, path, headers, body, queryStringParameters } = event;
  const origin = headers.origin || headers.Origin || '';

  console.log(`[API] ${httpMethod} ${path}`);
  console.log(`[API] Origin: ${origin}`);

  // Handle CORS preflight
  if (httpMethod === 'OPTIONS') {
    return {
      statusCode: 204,
      headers: getCORSHeaders(origin),
      body: ''
    };
  }

  try {
    // Extract API path (remove /.netlify/functions/api prefix)
    const apiPath = path.replace('/.netlify/functions/api', '') || '/';
    const backendURL = new URL(apiPath, BACKEND_URL);

    // Add query parameters
    if (queryStringParameters) {
      Object.keys(queryStringParameters).forEach(key => {
        backendURL.searchParams.append(key, queryStringParameters[key]);
      });
    }

    console.log(`[API] Proxying to: ${backendURL.toString()}`);

    // Proxy request to backend
    const response = await proxyRequest(
      backendURL.toString(),
      {
        method: httpMethod,
        headers: sanitizeHeaders(headers),
        body: body && httpMethod !== 'GET' ? body : undefined
      }
    );

    return {
      statusCode: response.statusCode,
      headers: {
        ...getCORSHeaders(origin),
        ...response.headers,
        'Content-Type': response.headers['content-type'] || 'application/json'
      },
      body: response.body,
      isBase64Encoded: response.isBase64Encoded || false
    };

  } catch (error) {
    console.error('[API] Error:', error.message);

    return {
      statusCode: 502,
      headers: getCORSHeaders(origin),
      body: JSON.stringify({
        error: 'Backend proxy error',
        message: error.message,
        timestamp: new Date().toISOString()
      })
    };
  }
};

// ============================================
// HELPER: PROXY REQUEST
// ============================================

function proxyRequest(url, options) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const isHttps = urlObj.protocol === 'https:';
    const client = isHttps ? https : http;

    const reqOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: options.method,
      headers: {
        ...options.headers,
        'Host': urlObj.hostname,
        'User-Agent': 'Netlify-Function/1.0'
      },
      timeout: 30000 // 30 second timeout
    };

    const req = client.request(reqOptions, (res) => {
      let data = '';

      res.on('data', chunk => {
        data += chunk;
      });

      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: data,
          isBase64Encoded: !isTextContent(res.headers['content-type'])
        });
      });
    });

    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Backend request timeout'));
    });

    if (options.body) {
      req.write(options.body);
    }

    req.end();
  });
}

// ============================================
// HELPER: CHECK CONTENT TYPE
// ============================================

function isTextContent(contentType) {
  if (!contentType) return true;
  return contentType.includes('text') ||
         contentType.includes('json') ||
         contentType.includes('xml');
}

// ============================================
// HELPER: SANITIZE HEADERS
// ============================================

function sanitizeHeaders(headers) {
  const sanitized = { ...headers };

  // Remove problematic headers
  delete sanitized['host'];
  delete sanitized['connection'];
  delete sanitized['content-length'];
  delete sanitized['transfer-encoding'];

  return sanitized;
}

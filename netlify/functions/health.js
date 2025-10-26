/**
 * NETLIFY FUNCTION - HEALTH CHECK
 *
 * Deployed at: /.netlify/functions/health
 * Usage: curl https://your-site.netlify.app/.netlify/functions/health
 */

const https = require('https');
const http = require('http');

exports.handler = async (event, context) => {
  try {
    const backendURL = process.env.BACKEND_API || 'http://localhost:5000';

    console.log('[HEALTH] Checking backend health:', backendURL);

    // Check backend health
    const backendHealthy = await checkBackendHealth(backendURL);

    const status = {
      status: backendHealthy ? 'operational' : 'degraded',
      timestamp: new Date().toISOString(),
      components: {
        frontend: 'operational',
        backend: backendHealthy ? 'operational' : 'unavailable',
        environment: process.env.ENVIRONMENT || 'production'
      },
      uptime: process.uptime(),
      memoryUsage: {
        heapUsed: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
        heapTotal: Math.round(process.memoryUsage().heapTotal / 1024 / 1024)
      }
    };

    return {
      statusCode: backendHealthy ? 200 : 503,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify(status, null, 2)
    };

  } catch (error) {
    console.error('[HEALTH] Error:', error);

    return {
      statusCode: 503,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        status: 'error',
        error: error.message,
        timestamp: new Date().toISOString()
      })
    };
  }
};

function checkBackendHealth(backendURL) {
  return new Promise((resolve) => {
    try {
      const urlObj = new URL(backendURL + '/health');
      const isHttps = urlObj.protocol === 'https:';
      const client = isHttps ? https : http;

      const req = client.get(
        urlObj.toString(),
        { timeout: 5000 },
        (res) => {
          resolve(res.statusCode >= 200 && res.statusCode < 300);
        }
      );

      req.on('error', () => resolve(false));
      req.on('timeout', () => {
        req.destroy();
        resolve(false);
      });

    } catch (error) {
      resolve(false);
    }
  });
}

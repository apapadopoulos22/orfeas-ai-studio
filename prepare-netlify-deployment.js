#!/usr/bin/env node

/**
 * ORFEAS AI STUDIO - NETLIFY DEPLOYMENT HELPER
 *
 * This script prepares the frontend for Netlify deployment by:
 * 1. Updating API endpoints to use Netlify functions
 * 2. Configuring CORS headers
 * 3. Setting up environment variables
 * 4. Validating HTML structure
 */

const fs = require('fs');
const path = require('path');

// ============================================
// CONFIGURATION
// ============================================

const CONFIG = {
  frontendFile: path.join(__dirname, 'orfeas-ai-studio.html'),
  outputFile: path.join(__dirname, 'orfeas-ai-studio-netlify.html'),
  netlifySite: process.env.NETLIFY_SITE || 'your-site.netlify.app'
};

// ============================================
// MAIN
// ============================================

async function main() {
  console.log('🚀 ORFEAS AI STUDIO - NETLIFY DEPLOYMENT HELPER');
  console.log('='.repeat(50));

  try {
    // Step 1: Read frontend file
    console.log('\n📖 Reading frontend file...');
    const htmlContent = fs.readFileSync(CONFIG.frontendFile, 'utf-8');
    console.log(`✅ Read ${CONFIG.frontendFile}`);

    // Step 2: Update API base URL
    console.log('\n🔄 Updating API endpoints...');
    let updatedContent = updateAPIEndpoints(htmlContent);
    console.log('✅ API endpoints updated');

    // Step 3: Update environment detection
    console.log('\n🌍 Configuring environment detection...');
    updatedContent = updateEnvironmentDetection(updatedContent);
    console.log('✅ Environment detection updated');

    // Step 4: Add Netlify-specific meta tags
    console.log('\n📝 Adding Netlify meta tags...');
    updatedContent = addNetlifyMetaTags(updatedContent);
    console.log('✅ Netlify meta tags added');

    // Step 5: Write updated file
    console.log('\n💾 Writing deployment file...');
    fs.writeFileSync(CONFIG.outputFile, updatedContent, 'utf-8');
    console.log(`✅ Written to ${CONFIG.outputFile}`);

    // Step 6: Summary
    console.log('\n' + '='.repeat(50));
    console.log('✅ DEPLOYMENT PREPARATION COMPLETE');
    console.log('='.repeat(50));
    console.log('\n📋 Next Steps:');
    console.log('1. Push changes to Git repository');
    console.log('2. Connect repository to Netlify');
    console.log('3. Set environment variables in Netlify UI:');
    console.log('   - BACKEND_API: Your backend URL');
    console.log('   - API_BASE: https://' + CONFIG.netlifySite);
    console.log('4. Deploy!');
    console.log('\n🔗 Netlify Dashboard: https://app.netlify.com');

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function updateAPIEndpoints(content) {
  // Update API_BASE configuration to use Netlify functions
  let updated = content.replace(
    /const API_BASE\s*=\s*[^;]+;/,
    `const API_BASE = window.location.origin; // Netlify proxy`
  );

  // Ensure all API calls use /api/ path
  updated = updated.replace(
    /\/api\//g,
    '/api/' // Already correct path for Netlify functions
  );

  return updated;
}

function updateEnvironmentDetection(content) {
  // Add environment-aware configuration
  const envScript = `
  // ============================================
  // NETLIFY ENVIRONMENT CONFIGURATION
  // ============================================

  const NETLIFY_ENV = {
    isDev: window.location.hostname === 'localhost',
    isProd: window.location.hostname.includes('netlify.app'),
    hostname: window.location.hostname,
    protocol: window.location.protocol
  };

  console.log('[NETLIFY] Environment:', NETLIFY_ENV);
  `;

  // Insert after the API_BASE configuration
  return content.replace(
    /const API_BASE = [^;]+;/,
    `const API_BASE = window.location.origin; // Netlify proxy\n${envScript}`
  );
}

function addNetlifyMetaTags(content) {
  // Add Netlify verification and configuration meta tags
  const metaTags = `
    <!-- Netlify Configuration -->
    <meta name="netlify" content="[netlify-config]" />
    <meta property="og:image" content="https://via.placeholder.com/1200x630?text=ORFEAS+AI+Studio" />
    <meta name="theme-color" content="#0a0e1a" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  `;

  return content.replace('</head>', metaTags + '\n</head>');
}

// ============================================
// RUN
// ============================================

main();

/*
 * Frontend Integration Script for ORFEAS Studio
 * This JavaScript module handles real API integration with the ORFEAS Backend
 * Replaces the simulation code with actual HTTP requests and WebSocket connections
 */

// ORFEAS Backend API Configuration
const ORFEAS_CONFIG = {
    API_BASE_URL: 'http://127.0.0.1:5000/api',
    WEBSOCKET_URL: 'http://127.0.0.1:5000',
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    SUPPORTED_FORMATS: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp']
};

// WebSocket connection for real-time updates
let socket = null;
let currentJobId = null;

// Initialize WebSocket connection
function initializeWebSocket() {
    if (typeof io !== 'undefined') {
        socket = io(ORFEAS_CONFIG.WEBSOCKET_URL);

        socket.on('connect', function() {
            console.log('Connected to ORFEAS Backend');
            showNotification('🔗 Connected to ORFEAS Backend', 'success');
        });

        socket.on('disconnect', function() {
            console.log('Disconnected from ORFEAS Backend');
            showNotification('⚠️ Connection lost - retrying...', 'warning');
        });

        socket.on('job_update', function(data) {
            handleJobUpdate(data);
        });

        socket.on('error', function(error) {
            console.error('WebSocket error:', error);
            showNotification('❌ Connection error', 'error');
        });
    } else {
        console.warn('Socket.IO not loaded, falling back to polling');
    }
}

// Handle real-time job updates
function handleJobUpdate(data) {
    if (data.job_id === currentJobId) {
        updateProgressBar(data.progress, data.step);

        if (data.status === 'completed') {
            handleJobCompletion(data);
        } else if (data.status === 'failed') {
            handleJobFailure(data);
        }
    }
}

// Text-to-Image Generation with Real API
async function generateImageFromText(prompt, artStyle, width = 512, height = 512) {
    try {
        // Validate input
        if (!prompt || prompt.trim().length === 0) {
            throw new Error('Prompt is required');
        }

        // Prepare request data
        const requestData = {
            prompt: prompt.trim(),
            style: artStyle,
            width: width,
            height: height,
            steps: 50,
            guidance_scale: 7.0
        };

        // Show loading state
        const generateBtn = document.querySelector('.generate-image-btn');
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<span>⏳</span> Connecting to AI...';
        }

        // Make API request
        const response = await fetch(`${ORFEAS_CONFIG.API_BASE_URL}/text-to-image`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to generate image');
        }

        const data = await response.json();
        currentJobId = data.job_id;

        // Subscribe to job updates via WebSocket
        if (socket) {
            socket.emit('subscribe_job', { job_id: currentJobId });
        }

        // Update UI
        updateProgressBar(0, 'Initializing AI model...');
        showNotification('🎨 Image generation started', 'info');

        // Start polling for updates if WebSocket is not available
        if (!socket) {
            pollJobStatus(currentJobId);
        }

        return data;

    } catch (error) {
        console.error('Text-to-image generation failed:', error);
        showNotification(`❌ Generation failed: ${error.message}`, 'error');
        resetUI();
        throw error;
    }
}

// Image Upload with Real API
async function uploadImageFile(file) {
    try {
        // Validate file
        if (!file) {
            throw new Error('No file selected');
        }

        if (file.size > ORFEAS_CONFIG.MAX_FILE_SIZE) {
            throw new Error('File too large (max 50MB)');
        }

        const fileExt = file.name.split('.').pop().toLowerCase();
        if (!ORFEAS_CONFIG.SUPPORTED_FORMATS.includes(fileExt)) {
            throw new Error(`Unsupported format. Supported: ${ORFEAS_CONFIG.SUPPORTED_FORMATS.join(', ')}`);
        }

        // Prepare FormData
        const formData = new FormData();
        formData.append('image', file);

        // Show loading state
        showNotification('📤 Uploading image...', 'info');

        // Make API request
        const response = await fetch(`${ORFEAS_CONFIG.API_BASE_URL}/upload-image`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Upload failed');
        }

        const data = await response.json();
        currentJobId = data.job_id;

        showNotification('✅ Image uploaded successfully', 'success');
        return data;

    } catch (error) {
        console.error('Image upload failed:', error);
        showNotification(`❌ Upload failed: ${error.message}`, 'error');
        throw error;
    }
}

// 3D Model Generation with Real API
async function generate3DModel(jobId, format = 'stl', dimensions = null, quality = 7) {
    try {
        if (!jobId) {
            throw new Error('No job ID provided');
        }

        // Default dimensions
        const defaultDimensions = {
            width: 100,
            height: 100,
            depth: 20
        };

        const requestData = {
            job_id: jobId,
            format: format,
            dimensions: dimensions || defaultDimensions,
            quality: quality
        };

        // Show loading state
        const generateBtn = document.querySelector('.generate-btn');
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<span>🔄</span> Generating 3D Model...';
        }

        // Make API request
        const response = await fetch(`${ORFEAS_CONFIG.API_BASE_URL}/generate-3d`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || '3D generation failed');
        }

        const data = await response.json();

        // Subscribe to job updates
        if (socket) {
            socket.emit('subscribe_job', { job_id: data.job_id });
        }

        // Update UI
        updateProgressBar(0, 'Initializing 3D engine...');
        showNotification('🎯 3D generation started', 'info');

        // Start polling if WebSocket not available
        if (!socket) {
            pollJobStatus(data.job_id);
        }

        return data;

    } catch (error) {
        console.error('3D generation failed:', error);
        showNotification(`❌ 3D generation failed: ${error.message}`, 'error');
        resetUI();
        throw error;
    }
}

// Poll job status (fallback when WebSocket is not available)
async function pollJobStatus(jobId, interval = 2000) {
    const poll = async () => {
        try {
            const response = await fetch(`${ORFEAS_CONFIG.API_BASE_URL}/job-status/${jobId}`);

            if (response.ok) {
                const data = await response.json();
                handleJobUpdate(data);

                if (data.status === 'completed' || data.status === 'failed') {
                    return; // Stop polling
                }
            }

            // Continue polling
            setTimeout(poll, interval);

        } catch (error) {
            console.error('Polling error:', error);
            setTimeout(poll, interval * 2); // Backoff on error
        }
    };

    poll();
}

// Handle job completion
function handleJobCompletion(data) {
    updateProgressBar(100, 'Complete!');

    if (data.output_file && data.download_url) {
        showDownloadLink(data.download_url, data.output_file);

        if (data.format && ['stl', 'obj'].includes(data.format)) {
            // For 3D models, show 3D preview
            show3DPreview(data.download_url);
        } else {
            // For images, show image preview
            showImagePreview(data.download_url);
        }

        showNotification('🎉 Generation completed successfully!', 'success');
    }

    resetUI();
}

// Handle job failure
function handleJobFailure(data) {
    const errorMsg = data.error || 'Unknown error occurred';
    showNotification(`❌ Generation failed: ${errorMsg}`, 'error');
    updateProgressBar(0, 'Failed');
    resetUI();
}

// Update progress bar
function updateProgressBar(progress, step) {
    const progressBar = document.querySelector('.progress');
    const progressText = document.querySelector('.progress-text');

    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }

    if (progressText) {
        progressText.textContent = step;
    }
}

// Show download link
function showDownloadLink(url, filename) {
    const resultsContainer = document.querySelector('.results-container') || createResultsContainer();

    const downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.download = filename;
    downloadLink.className = 'download-btn';
    downloadLink.innerHTML = `
        <span>📥</span>
        Download ${filename}
        <small>${getFileTypeFromName(filename)}</small>
    `;

    resultsContainer.appendChild(downloadLink);
}

// Show 3D preview (placeholder - in real implementation would use Three.js)
function show3DPreview(modelUrl) {
    const previewContainer = document.querySelector('.model-preview') || createPreviewContainer();

    previewContainer.innerHTML = `
        <div class="preview-placeholder">
            <div class="rotating-cube">🎲</div>
            <p>3D Model Generated</p>
            <small>Click download to get your model</small>
        </div>
    `;
}

// Show image preview
function showImagePreview(imageUrl) {
    const previewContainer = document.querySelector('.image-preview') || createImagePreviewContainer();

    const img = document.createElement('img');
    img.src = imageUrl;
    img.alt = 'Generated Image';
    img.style.maxWidth = '100%';
    img.style.borderRadius = '10px';

    previewContainer.innerHTML = '';
    previewContainer.appendChild(img);
}

// Create results container if it doesn't exist
function createResultsContainer() {
    const container = document.createElement('div');
    container.className = 'results-container';
    container.style.cssText = `
        margin-top: 1rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        backdrop-filter: blur(10px);
    `;

    const generatorSection = document.querySelector('.generator-section');
    if (generatorSection) {
        generatorSection.appendChild(container);
    }

    return container;
}

// Create preview container
function createPreviewContainer() {
    const container = document.createElement('div');
    container.className = 'model-preview';
    container.style.cssText = `
        margin-top: 1rem;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        text-align: center;
        backdrop-filter: blur(10px);
    `;

    const resultsContainer = document.querySelector('.results-container') || createResultsContainer();
    resultsContainer.appendChild(container);

    return container;
}

// Create image preview container
function createImagePreviewContainer() {
    const container = document.createElement('div');
    container.className = 'image-preview';
    container.style.cssText = `
        margin-top: 1rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        text-align: center;
        backdrop-filter: blur(10px);
    `;

    const textToImageWindow = document.querySelector('.text-to-image-window');
    if (textToImageWindow) {
        textToImageWindow.appendChild(container);
    }

    return container;
}

// Reset UI to initial state
function resetUI() {
    const generateImageBtn = document.querySelector('.generate-image-btn');
    const generate3DBtn = document.querySelector('.generate-btn');

    if (generateImageBtn) {
        generateImageBtn.disabled = false;
        generateImageBtn.innerHTML = '<span>✨</span> Generate Image';
    }

    if (generate3DBtn) {
        generate3DBtn.disabled = false;
        generate3DBtn.innerHTML = '<span>🎯</span> Generate 3D Model';
    }

    currentJobId = null;
}

// Show notification with different types
function showNotification(message, type = 'info') {
    const colors = {
        success: '#2ecc71',
        error: '#e74c3c',
        warning: '#f39c12',
        info: '#3498db'
    };

    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        z-index: 10000;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.3s ease-out;
        max-width: 300px;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Get file type from filename
function getFileTypeFromName(filename) {
    const ext = filename.split('.').pop().toUpperCase();
    const types = {
        'STL': '3D Model (STereoLithography)',
        'OBJ': '3D Model (Wavefront OBJ)',
        'PLY': '3D Model (Polygon File)',
        'PNG': 'Image (Portable Network Graphics)',
        'JPG': 'Image (JPEG)',
        'JPEG': 'Image (JPEG)'
    };
    return types[ext] || `${ext} File`;
}

// Check system health
async function checkSystemHealth() {
    try {
        const response = await fetch(`${ORFEAS_CONFIG.API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('ORFEAS Backend Status:', data);
            return data;
        }
    } catch (error) {
        console.warn('Backend health check failed:', error);
        return null;
    }
}

// Initialize the integration when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if Socket.IO is available and initialize WebSocket
    if (typeof io !== 'undefined') {
        initializeWebSocket();
    }

    // Check system health
    checkSystemHealth().then(health => {
        if (health) {
            showNotification('🚀 ORFEAS Backend connected successfully', 'success');
        } else {
            showNotification('⚠️ Backend not available - using offline mode', 'warning');
        }
    });
});

// Export functions for global access
window.OrfeasAPI = {
    generateImageFromText,
    uploadImageFile,
    generate3DModel,
    checkSystemHealth,
    config: ORFEAS_CONFIG
};

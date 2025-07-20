/**
 * Faculty Attendance System - Face Capture Module
 * 
 * This module handles face capture functionality, image processing,
 * and AI recognition simulation for the attendance system.
 */

window.FaceCaptureModule = {
    // Configuration
    config: {
        maxImageSize: 16 * 1024 * 1024, // 16MB
        allowedFormats: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp'],
        recognitionDelay: 2000, // 2 seconds simulation delay
        maxFacesDetected: 5,
        confidenceThreshold: 0.7
    },
    
    // State management
    state: {
        isProcessing: false,
        capturedImage: null,
        recognitionResults: [],
        selectedFaculty: []
    },
    
    // Initialize the module
    init: function() {
        this.initializeEventListeners();
        this.initializeCamera();
        this.setupImagePreview();
        console.log('Face Capture Module initialized');
    }
};

// Event Listeners
FaceCaptureModule.initializeEventListeners = function() {
    // Image upload handler
    const imageInput = document.getElementById('captured_image');
    if (imageInput) {
        imageInput.addEventListener('change', this.handleImageUpload.bind(this));
    }
    
    // Camera button (if exists)
    const cameraBtn = document.getElementById('cameraBtn');
    if (cameraBtn) {
        cameraBtn.addEventListener('click', this.openCamera.bind(this));
    }
    
    // Manual faculty selection
    const facultyCheckboxes = document.querySelectorAll('input[name="manual_faculty_ids"]');
    facultyCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', this.handleManualSelection.bind(this));
    });
    
    // Simulate recognition button
    const simulateBtn = document.getElementById('simulateRecognition');
    if (simulateBtn) {
        simulateBtn.addEventListener('click', this.simulateRecognition.bind(this));
    }
    
    // Clear selection button
    const clearBtn = document.getElementById('clearSelection');
    if (clearBtn) {
        clearBtn.addEventListener('click', this.clearSelection.bind(this));
    }
};

// Handle image upload
FaceCaptureModule.handleImageUpload = function(event) {
    const file = event.target.files[0];
    
    if (!file) {
        this.clearImagePreview();
        return;
    }
    
    // Validate file
    const validation = this.validateImage(file);
    if (!validation.valid) {
        this.showError(validation.errors.join('<br>'));
        event.target.value = '';
        return;
    }
    
    this.state.capturedImage = file;
    this.displayImagePreview(file);
    this.enableRecognitionControls();
    
    // Auto-start recognition if enabled
    if (document.getElementById('autoRecognition')?.checked) {
        setTimeout(() => {
            this.simulateRecognition();
        }, 500);
    }
};

// Validate uploaded image
FaceCaptureModule.validateImage = function(file) {
    const errors = [];
    
    // Check file type
    if (!this.config.allowedFormats.includes(file.type)) {
        errors.push('Invalid file format. Please upload a valid image file (JPEG, PNG, GIF, BMP).');
    }
    
    // Check file size
    if (file.size > this.config.maxImageSize) {
        errors.push(`File size exceeds maximum limit of ${this.formatFileSize(this.config.maxImageSize)}.`);
    }
    
    // Check if file is actually an image
    if (!file.type.startsWith('image/')) {
        errors.push('Selected file is not a valid image.');
    }
    
    return {
        valid: errors.length === 0,
        errors: errors
    };
};

// Display image preview
FaceCaptureModule.displayImagePreview = function(file) {
    const previewContainer = document.getElementById('capturePreview');
    if (!previewContainer) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        previewContainer.innerHTML = `
            <div class="image-preview-container">
                <img src="${e.target.result}" alt="Captured Image" class="img-fluid rounded shadow" 
                     style="max-width: 100%; max-height: 300px; object-fit: contain;">
                <div class="image-info mt-2">
                    <small class="text-muted">
                        <i class="fas fa-image me-1"></i>
                        ${file.name} (${this.formatFileSize(file.size)})
                    </small>
                </div>
                <div class="recognition-status mt-2" id="recognitionStatus">
                    <span class="badge bg-info">
                        <i class="fas fa-clock me-1"></i>Ready for recognition
                    </span>
                </div>
            </div>
        `;
        
        // Add loading animation
        previewContainer.querySelector('img').style.opacity = '0';
        setTimeout(() => {
            previewContainer.querySelector('img').style.transition = 'opacity 0.3s ease';
            previewContainer.querySelector('img').style.opacity = '1';
        }, 100);
    };
    
    reader.readAsDataURL(file);
};

// Clear image preview
FaceCaptureModule.clearImagePreview = function() {
    const previewContainer = document.getElementById('capturePreview');
    if (previewContainer) {
        previewContainer.innerHTML = `
            <i class="fas fa-camera fa-3x text-muted"></i>
            <p class="text-muted mt-2">Upload or capture image for recognition</p>
        `;
    }
    
    this.state.capturedImage = null;
    this.state.recognitionResults = [];
    this.disableRecognitionControls();
};

// Enable recognition controls
FaceCaptureModule.enableRecognitionControls = function() {
    const simulateBtn = document.getElementById('simulateRecognition');
    if (simulateBtn) {
        simulateBtn.disabled = false;
        simulateBtn.classList.remove('btn-secondary');
        simulateBtn.classList.add('btn-success');
    }
};

// Disable recognition controls
FaceCaptureModule.disableRecognitionControls = function() {
    const simulateBtn = document.getElementById('simulateRecognition');
    if (simulateBtn) {
        simulateBtn.disabled = true;
        simulateBtn.classList.remove('btn-success');
        simulateBtn.classList.add('btn-secondary');
    }
};

// Simulate AI face recognition
FaceCaptureModule.simulateRecognition = function() {
    if (!this.state.capturedImage || this.state.isProcessing) {
        return;
    }
    
    this.state.isProcessing = true;
    this.showRecognitionProgress();
    
    // Simulate processing delay
    setTimeout(() => {
        this.processRecognition();
    }, this.config.recognitionDelay);
};

// Show recognition progress
FaceCaptureModule.showRecognitionProgress = function() {
    const statusElement = document.getElementById('recognitionStatus');
    if (statusElement) {
        statusElement.innerHTML = `
            <span class="badge bg-warning">
                <i class="fas fa-spinner fa-spin me-1"></i>Processing with AI...
            </span>
        `;
    }
    
    // Update simulate button
    const simulateBtn = document.getElementById('simulateRecognition');
    if (simulateBtn) {
        simulateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
        simulateBtn.disabled = true;
    }
    
    // Show progress in preview
    const previewContainer = document.getElementById('capturePreview');
    if (previewContainer) {
        const progressOverlay = document.createElement('div');
        progressOverlay.className = 'recognition-overlay';
        progressOverlay.innerHTML = `
            <div class="text-center text-white">
                <div class="spinner-border mb-2" role="status">
                    <span class="visually-hidden">Processing...</span>
                </div>
                <div>AI Processing...</div>
                <small>Analyzing faces in image</small>
            </div>
        `;
        progressOverlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
        `;
        
        const container = previewContainer.querySelector('.image-preview-container');
        if (container) {
            container.style.position = 'relative';
            container.appendChild(progressOverlay);
        }
    }
};

// Process recognition results
FaceCaptureModule.processRecognition = function() {
    // Simulate AI recognition results
    const recognitionResults = this.generateMockRecognitionResults();
    
    this.state.recognitionResults = recognitionResults;
    this.state.isProcessing = false;
    
    // Update UI with results
    this.displayRecognitionResults(recognitionResults);
    this.updateRecognitionStatus(recognitionResults);
    this.resetRecognitionButton();
    
    // Remove progress overlay
    const overlay = document.querySelector('.recognition-overlay');
    if (overlay) {
        overlay.remove();
    }
    
    // Show success message
    if (recognitionResults.length > 0) {
        FacultyAttendanceSystem.ui.showToast(
            `Recognized ${recognitionResults.length} faculty member(s)`, 
            'success'
        );
    } else {
        FacultyAttendanceSystem.ui.showToast(
            'No registered faculty members found in the image', 
            'warning'
        );
    }
};

// Generate mock recognition results
FaceCaptureModule.generateMockRecognitionResults = function() {
    const faculty = Array.from(document.querySelectorAll('input[name="manual_faculty_ids"]'))
        .map(input => ({
            id: input.value,
            name: input.nextElementSibling.textContent.trim().split('\n')[0],
            department: input.nextElementSibling.querySelector('small')?.textContent || 'Unknown'
        }));
    
    if (faculty.length === 0) return [];
    
    // Randomly select 0-3 faculty members to simulate recognition
    const numRecognized = Math.floor(Math.random() * Math.min(4, faculty.length + 1));
    const recognized = [];
    
    for (let i = 0; i < numRecognized; i++) {
        const randomFaculty = faculty[Math.floor(Math.random() * faculty.length)];
        if (!recognized.find(r => r.id === randomFaculty.id)) {
            recognized.push({
                ...randomFaculty,
                confidence: (Math.random() * 0.3 + 0.7).toFixed(2), // 0.70-1.00
                boundingBox: {
                    x: Math.floor(Math.random() * 200),
                    y: Math.floor(Math.random() * 200),
                    width: Math.floor(Math.random() * 100 + 50),
                    height: Math.floor(Math.random() * 120 + 60)
                }
            });
        }
    }
    
    return recognized;
};

// Display recognition results
FaceCaptureModule.displayRecognitionResults = function(results) {
    const resultsContainer = document.getElementById('recognitionResults') || 
                           this.createRecognitionResultsContainer();
    
    if (results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                No faces recognized. You can manually select faculty members below.
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="alert alert-success">
            <i class="fas fa-check-circle me-2"></i>
            Successfully recognized ${results.length} faculty member(s)
        </div>
        <div class="recognized-faculty">
    `;
    
    results.forEach(faculty => {
        html += `
            <div class="recognized-item d-flex align-items-center justify-content-between p-3 border rounded mb-2">
                <div class="d-flex align-items-center">
                    <div class="faculty-avatar me-3">
                        <div class="bg-success rounded-circle d-flex align-items-center justify-content-center" 
                             style="width: 40px; height: 40px;">
                            <small class="text-white fw-bold">${faculty.name.substring(0, 2).toUpperCase()}</small>
                        </div>
                    </div>
                    <div>
                        <strong>${faculty.name}</strong>
                        <br>
                        <small class="text-muted">${faculty.department}</small>
                    </div>
                </div>
                <div class="text-end">
                    <span class="badge bg-success">
                        <i class="fas fa-eye me-1"></i>${(faculty.confidence * 100).toFixed(0)}%
                    </span>
                    <br>
                    <small class="text-muted">Confidence</small>
                </div>
            </div>
        `;
        
        // Auto-select the corresponding checkbox
        const checkbox = document.querySelector(`input[value="${faculty.id}"]`);
        if (checkbox) {
            checkbox.checked = true;
            checkbox.dispatchEvent(new Event('change'));
        }
    });
    
    html += '</div>';
    resultsContainer.innerHTML = html;
    resultsContainer.style.display = 'block';
    
    // Animate results
    resultsContainer.style.opacity = '0';
    setTimeout(() => {
        resultsContainer.style.transition = 'opacity 0.5s ease';
        resultsContainer.style.opacity = '1';
    }, 100);
};

// Create recognition results container
FaceCaptureModule.createRecognitionResultsContainer = function() {
    const container = document.createElement('div');
    container.id = 'recognitionResults';
    container.className = 'recognition-results mt-3';
    container.style.display = 'none';
    
    const captureSection = document.querySelector('.face-capture-area');
    if (captureSection) {
        captureSection.parentNode.insertBefore(container, captureSection.nextSibling);
    }
    
    return container;
};

// Update recognition status
FaceCaptureModule.updateRecognitionStatus = function(results) {
    const statusElement = document.getElementById('recognitionStatus');
    if (statusElement) {
        if (results.length > 0) {
            statusElement.innerHTML = `
                <span class="badge bg-success">
                    <i class="fas fa-check-circle me-1"></i>
                    ${results.length} face(s) recognized
                </span>
            `;
        } else {
            statusElement.innerHTML = `
                <span class="badge bg-warning">
                    <i class="fas fa-exclamation-triangle me-1"></i>
                    No faces recognized
                </span>
            `;
        }
    }
};

// Reset recognition button
FaceCaptureModule.resetRecognitionButton = function() {
    const simulateBtn = document.getElementById('simulateRecognition');
    if (simulateBtn) {
        simulateBtn.innerHTML = '<i class="fas fa-redo me-1"></i>Re-analyze Image';
        simulateBtn.disabled = false;
        simulateBtn.classList.remove('btn-secondary');
        simulateBtn.classList.add('btn-info');
    }
};

// Handle manual faculty selection
FaceCaptureModule.handleManualSelection = function(event) {
    const checkbox = event.target;
    const facultyId = checkbox.value;
    
    if (checkbox.checked) {
        if (!this.state.selectedFaculty.includes(facultyId)) {
            this.state.selectedFaculty.push(facultyId);
        }
    } else {
        this.state.selectedFaculty = this.state.selectedFaculty.filter(id => id !== facultyId);
    }
    
    this.updateSelectionCounter();
};

// Update selection counter
FaceCaptureModule.updateSelectionCounter = function() {
    const counter = document.getElementById('selectionCounter');
    if (counter) {
        const count = this.state.selectedFaculty.length;
        counter.textContent = count;
        counter.className = count > 0 ? 'badge bg-primary' : 'badge bg-secondary';
    }
};

// Clear all selections
FaceCaptureModule.clearSelection = function() {
    // Clear manual selections
    document.querySelectorAll('input[name="manual_faculty_ids"]').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Clear recognition results
    const resultsContainer = document.getElementById('recognitionResults');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
    
    // Reset state
    this.state.selectedFaculty = [];
    this.state.recognitionResults = [];
    
    // Update UI
    this.updateSelectionCounter();
    this.updateRecognitionStatus([]);
    
    FacultyAttendanceSystem.ui.showToast('Selection cleared', 'info');
};

// Initialize camera (placeholder for future webcam integration)
FaceCaptureModule.initializeCamera = function() {
    // This would initialize webcam access in a real implementation
    console.log('Camera initialization placeholder');
};

// Open camera (placeholder)
FaceCaptureModule.openCamera = function() {
    FacultyAttendanceSystem.ui.showToast('Camera feature coming soon!', 'info');
};

// Setup image preview enhancements
FaceCaptureModule.setupImagePreview = function() {
    // Add drag and drop functionality
    const previewArea = document.getElementById('capturePreview');
    if (previewArea) {
        previewArea.addEventListener('dragover', this.handleDragOver.bind(this));
        previewArea.addEventListener('drop', this.handleDrop.bind(this));
        previewArea.addEventListener('click', this.handlePreviewClick.bind(this));
    }
};

// Handle drag over
FaceCaptureModule.handleDragOver = function(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
};

// Handle drop
FaceCaptureModule.handleDrop = function(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const imageInput = document.getElementById('captured_image');
        if (imageInput) {
            imageInput.files = files;
            imageInput.dispatchEvent(new Event('change'));
        }
    }
};

// Handle preview click
FaceCaptureModule.handlePreviewClick = function() {
    const imageInput = document.getElementById('captured_image');
    if (imageInput && !this.state.capturedImage) {
        imageInput.click();
    }
};

// Utility function to format file size
FaceCaptureModule.formatFileSize = function(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Show error message
FaceCaptureModule.showError = function(message) {
    FacultyAttendanceSystem.ui.showToast(message, 'danger');
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('captured_image')) {
        FaceCaptureModule.init();
    }
});

// Submit attendance form
document.getElementById('faceCaptureForm')?.addEventListener('submit', function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    // Send data to server
    fetch('/attendance/capture', {
        method: 'POST',
        body: formData
    })
    .then(async response => {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            const data = await response.json();
            alert(data.message || "Submitted successfully");
        } else {
            return response.text().then(html => {
                document.open();
                document.write(html);
                document.close();
            });
        }
    })
    .catch(error => {
        console.error('Error submitting form:', error);
        alert("An error occurred while marking attendance.");
    });
});

// Expose to global scope
window.FCM = FaceCaptureModule;
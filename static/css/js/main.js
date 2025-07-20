/**
 * Faculty Attendance System - Main JavaScript
 * 
 * This file contains common functionality used across the application
 */

// Global application object
window.FacultyAttendanceSystem = {
    // Configuration
    config: {
        autoRefreshInterval: 30000, // 30 seconds
        animationDuration: 300,
        debounceDelay: 300,
        maxFileSize: 16 * 1024 * 1024, // 16MB
        allowedImageTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp']
    },
    
    // Utility functions
    utils: {},
    
    // UI functions
    ui: {},
    
    // API functions
    api: {},
    
    // Initialize application
    init: function() {
        this.initializeEventListeners();
        this.initializeTooltips();
        this.initializeAnimations();
        this.initializeFormValidation();
        console.log('Faculty Attendance System initialized');
    }
};

// Utility Functions
FacultyAttendanceSystem.utils = {
    /**
     * Debounce function to limit API calls
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Format date to readable string
     */
    formatDate: function(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        switch(format) {
            case 'YYYY-MM-DD':
                return `${year}-${month}-${day}`;
            case 'DD/MM/YYYY':
                return `${day}/${month}/${year}`;
            case 'YYYY-MM-DD HH:mm:ss':
                return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
            case 'HH:mm':
                return `${hours}:${minutes}`;
            default:
                return d.toLocaleDateString();
        }
    },
    
    /**
     * Validate file type and size
     */
    validateFile: function(file) {
        const errors = [];
        
        if (!file) {
            errors.push('No file selected');
            return errors;
        }
        
        // Check file type
        if (!this.config.allowedImageTypes.includes(file.type)) {
            errors.push('Invalid file type. Please select a valid image file (JPG, PNG, GIF, BMP)');
        }
        
        // Check file size
        if (file.size > this.config.maxFileSize) {
            errors.push('File size too large. Maximum size is 16MB');
        }
        
        return errors;
    },
    
    /**
     * Generate unique ID
     */
    generateId: function() {
        return 'id_' + Math.random().toString(36).substr(2, 9);
    },
    
    /**
     * Copy text to clipboard
     */
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Copied to clipboard', 'success');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showToast('Copied to clipboard', 'success');
        }
    },
    
    /**
     * Format file size
     */
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
};

// UI Functions
FacultyAttendanceSystem.ui = {
    /**
     * Show loading spinner
     */
    showLoading: function(element, text = 'Loading...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            const spinner = `
                <div class="loading-overlay">
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <div class="mt-2">${text}</div>
                    </div>
                </div>
            `;
            element.style.position = 'relative';
            element.insertAdjacentHTML('beforeend', spinner);
        }
    },
    
    /**
     * Hide loading spinner
     */
    hideLoading: function(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            const overlay = element.querySelector('.loading-overlay');
            if (overlay) {
                overlay.remove();
            }
        }
    },
    
    /**
     * Show toast notification
     */
    showToast: function(message, type = 'info', duration = 3000) {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toastId = FacultyAttendanceSystem.utils.generateId();
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: duration
        });
        
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    },
    
    /**
     * Create toast container if it doesn't exist
     */
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    },
    
    /**
     * Get appropriate icon for toast type
     */
    getToastIcon: function(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'primary': 'info-circle'
        };
        return icons[type] || 'info-circle';
    },
    
    /**
     * Animate element
     */
    animateElement: function(element, animation) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            element.style.animation = animation;
            element.addEventListener('animationend', () => {
                element.style.animation = '';
            }, { once: true });
        }
    },
    
    /**
     * Smooth scroll to element
     */
    scrollToElement: function(element, offset = 0) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
            const offsetPosition = elementPosition - offset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    }
};

// API Functions
FacultyAttendanceSystem.api = {
    /**
     * Make API request
     */
    request: function(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        return fetch(url, finalOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('API request failed:', error);
                FacultyAttendanceSystem.ui.showToast('Request failed. Please try again.', 'danger');
                throw error;
            });
    },
    
    /**
     * Get faculty data
     */
    getFaculty: function() {
        return this.request('/faculty/api/search');
    },
    
    /**
     * Get attendance summary
     */
    getAttendanceSummary: function() {
        return this.request('/attendance/api/today-summary');
    }
};

// Event Listeners
FacultyAttendanceSystem.initializeEventListeners = function() {
    // File input preview
    document.addEventListener('change', function(e) {
        if (e.target.type === 'file' && e.target.accept && e.target.accept.includes('image')) {
            FacultyAttendanceSystem.handleImagePreview(e.target);
        }
    });
    
    // Form submission loading states
    document.addEventListener('submit', function(e) {
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn && !submitBtn.disabled) {
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
            submitBtn.disabled = true;
            
            // Reset button after 10 seconds as safety measure
            setTimeout(() => {
                if (submitBtn.disabled) {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
            }, 10000);
        }
    });
    
    // Auto-resize textareas
    document.addEventListener('input', function(e) {
        if (e.target.tagName === 'TEXTAREA') {
            e.target.style.height = 'auto';
            e.target.style.height = e.target.scrollHeight + 'px';
        }
    });
    
    // Search functionality
    const searchInputs = document.querySelectorAll('[data-search-target]');
    searchInputs.forEach(input => {
        input.addEventListener('keyup', FacultyAttendanceSystem.utils.debounce(function() {
            FacultyAttendanceSystem.handleSearch(this);
        }, FacultyAttendanceSystem.config.debounceDelay));
    });
    
    // Copy buttons
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-copy-text]')) {
            const text = e.target.getAttribute('data-copy-text');
            FacultyAttendanceSystem.utils.copyToClipboard(text);
        }
    });
    
    // Confirm dialogs
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-confirm]')) {
            const message = e.target.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        }
    });
};

// Image Preview Handler
FacultyAttendanceSystem.handleImagePreview = function(input) {
    const file = input.files[0];
    const previewContainer = input.closest('.form-group, .mb-3')?.querySelector('.image-preview') ||
                           document.querySelector('#imagePreview');
    
    if (!file || !previewContainer) return;
    
    // Validate file
    const errors = FacultyAttendanceSystem.utils.validateFile(file);
    if (errors.length > 0) {
        FacultyAttendanceSystem.ui.showToast(errors.join('<br>'), 'danger');
        input.value = '';
        previewContainer.style.display = 'none';
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const img = previewContainer.querySelector('img') || document.createElement('img');
        img.src = e.target.result;
        img.className = 'img-thumbnail';
        img.style.maxWidth = '200px';
        img.style.maxHeight = '200px';
        
        if (!previewContainer.querySelector('img')) {
            previewContainer.appendChild(img);
        }
        
        // Add file info
        let fileInfo = previewContainer.querySelector('.file-info');
        if (!fileInfo) {
            fileInfo = document.createElement('div');
            fileInfo.className = 'file-info mt-2';
            previewContainer.appendChild(fileInfo);
        }
        
        fileInfo.innerHTML = `
            <small class="text-muted">
                <i class="fas fa-file-image me-1"></i>
                ${file.name} (${FacultyAttendanceSystem.utils.formatFileSize(file.size)})
            </small>
        `;
        
        previewContainer.style.display = 'block';
        FacultyAttendanceSystem.ui.animateElement(img, 'fadeIn 0.3s ease-in');
    };
    
    reader.readAsDataURL(file);
};

// Search Handler
FacultyAttendanceSystem.handleSearch = function(input) {
    const target = input.getAttribute('data-search-target');
    const searchTerm = input.value.toLowerCase();
    const targetElements = document.querySelectorAll(target);
    
    targetElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            element.style.display = '';
        } else {
            element.style.display = 'none';
        }
    });
};

// Initialize Tooltips
FacultyAttendanceSystem.initializeTooltips = function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
};

// Initialize Animations
FacultyAttendanceSystem.initializeAnimations = function() {
    // Observe elements for animation
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements with animation class
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
};

// Initialize Form Validation
FacultyAttendanceSystem.initializeFormValidation = function() {
    // Add custom validation styles
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.checkValidity() === false) {
            e.preventDefault();
            e.stopPropagation();
            
            // Focus on first invalid field
            const firstInvalid = form.querySelector(':invalid');
            if (firstInvalid) {
                firstInvalid.focus();
                FacultyAttendanceSystem.ui.scrollToElement(firstInvalid, 100);
            }
        }
        
        form.classList.add('was-validated');
    });
};

// Auto-refresh functionality
FacultyAttendanceSystem.startAutoRefresh = function() {
    setInterval(() => {
        // Update attendance summary if on dashboard
        if (document.getElementById('todaySummary')) {
            FacultyAttendanceSystem.api.getAttendanceSummary()
                .then(data => {
                    document.getElementById('presentCount').textContent = data.present;
                    document.getElementById('absentCount').textContent = data.absent;
                    document.getElementById('totalCount').textContent = data.total_faculty;
                })
                .catch(error => {
                    console.error('Failed to refresh attendance summary:', error);
                });
        }
    }, FacultyAttendanceSystem.config.autoRefreshInterval);
};

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    FacultyAttendanceSystem.ui.showToast('An error occurred. Please refresh the page.', 'danger');
});

// Page visibility change handler
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // Page became visible, refresh data if needed
        console.log('Page visible, refreshing data...');
    }
});

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    FacultyAttendanceSystem.init();
    FacultyAttendanceSystem.startAutoRefresh();
});

// Expose to global scope for debugging
window.FAS = FacultyAttendanceSystem;

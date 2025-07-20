/**
 * Faculty Attendance System - Dashboard Charts Module
 * 
 * This module handles all chart creation and data visualization
 * for the dashboard analytics.
 */

window.DashboardCharts = {
    // Chart instances
    charts: {},
    
    // Chart configurations
    config: {
        colors: {
            primary: '#0d6efd',
            success: '#198754',
            danger: '#dc3545',
            warning: '#ffc107',
            info: '#0dcaf0',
            secondary: '#6c757d',
            light: '#f8f9fa',
            dark: '#212529'
        },
        animation: {
            duration: 1000,
            easing: 'easeInOutQuart'
        }
    },
    
    // Initialize all charts
    init: function() {
        this.initializeWeeklyChart();
        this.initializeDepartmentChart();
        this.initializeMonthlyChart();
        this.initializeTrendChart();
        console.log('Dashboard Charts initialized');
    }
};

// Initialize weekly attendance chart
DashboardCharts.initializeWeeklyChart = function() {
    const ctx = document.getElementById('weeklyChart');
    if (!ctx) return;
    
    // Fetch weekly data
    fetch('/dashboard/api/weekly-stats')
        .then(response => response.json())
        .then(data => {
            this.createWeeklyChart(ctx, data);
        })
        .catch(error => {
            console.error('Failed to load weekly stats:', error);
            this.showChartError(ctx, 'Failed to load weekly attendance data');
        });
};

// Create weekly attendance chart
DashboardCharts.createWeeklyChart = function(ctx, data) {
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.day),
            datasets: [
                {
                    label: 'Present',
                    data: data.map(d => d.present),
                    borderColor: this.config.colors.success,
                    backgroundColor: this.config.colors.success + '20',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.config.colors.success,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                },
                {
                    label: 'Absent',
                    data: data.map(d => d.absent),
                    borderColor: this.config.colors.danger,
                    backgroundColor: this.config.colors.danger + '20',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.config.colors.danger,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: this.config.animation,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Last 7 Days Attendance Trend',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: this.config.colors.dark
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: this.config.colors.primary,
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            const item = data[context[0].dataIndex];
                            return item.date;
                        },
                        afterBody: function(context) {
                            const item = data[context[0].dataIndex];
                            return [`Attendance Rate: ${item.percentage}%`];
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            weight: '500'
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        precision: 0,
                        font: {
                            weight: '500'
                        }
                    }
                }
            }
        }
    });
    
    this.charts.weekly = chart;
};

// Initialize department distribution chart
DashboardCharts.initializeDepartmentChart = function() {
    const ctx = document.getElementById('departmentChart');
    if (!ctx) return;
    
    // Fetch department data
    fetch('/dashboard/api/department-stats')
        .then(response => response.json())
        .then(data => {
            this.createDepartmentChart(ctx, data);
        })
        .catch(error => {
            console.error('Failed to load department stats:', error);
            this.showChartError(ctx, 'Failed to load department data');
        });
};

// Create department distribution chart
DashboardCharts.createDepartmentChart = function(ctx, data) {
    const colors = [
        this.config.colors.primary,
        this.config.colors.success,
        this.config.colors.warning,
        this.config.colors.info,
        this.config.colors.danger,
        this.config.colors.secondary,
        '#ff6b6b',
        '#4ecdc4',
        '#45b7d1',
        '#96ceb4',
        '#feca57',
        '#ff9ff3'
    ];
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.department),
            datasets: [{
                data: data.map(d => d.present),
                backgroundColor: colors.slice(0, data.length),
                borderColor: '#fff',
                borderWidth: 3,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: this.config.animation,
            plugins: {
                title: {
                    display: true,
                    text: "Today's Attendance by Department",
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: this.config.colors.dark
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 11,
                            weight: '500'
                        },
                        generateLabels: function(chart) {
                            const labels = Chart.defaults.plugins.legend.labels.generateLabels(chart);
                            return labels.map((label, index) => {
                                const item = data[index];
                                label.text = `${label.text} (${item.present}/${item.total})`;
                                return label;
                            });
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: this.config.colors.primary,
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const item = data[context.dataIndex];
                            return [
                                `${item.department}`,
                                `Present: ${item.present}`,
                                `Absent: ${item.absent}`,
                                `Total: ${item.total}`,
                                `Rate: ${item.percentage}%`
                            ];
                        }
                    }
                }
            }
        }
    });
    
    this.charts.department = chart;
};

// Initialize monthly attendance chart
DashboardCharts.initializeMonthlyChart = function() {
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;
    
    // Fetch monthly data
    fetch('/dashboard/api/monthly-stats')
        .then(response => response.json())
        .then(data => {
            this.createMonthlyChart(ctx, data);
        })
        .catch(error => {
            console.error('Failed to load monthly stats:', error);
            this.showChartError(ctx, 'Failed to load monthly data');
        });
};

// Create monthly attendance chart
DashboardCharts.createMonthlyChart = function(ctx, data) {
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => `Day ${d.day}`),
            datasets: [
                {
                    label: 'Present',
                    data: data.map(d => d.present),
                    backgroundColor: this.config.colors.success + 'DD',
                    borderColor: this.config.colors.success,
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false
                },
                {
                    label: 'Absent',
                    data: data.map(d => d.absent),
                    backgroundColor: this.config.colors.danger + 'DD',
                    borderColor: this.config.colors.danger,
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: this.config.animation,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Current Month Daily Attendance',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: this.config.colors.dark
                },
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: this.config.colors.primary,
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        title: function(context) {
                            const item = data[context[0].dataIndex];
                            return item.date;
                        },
                        afterBody: function(context) {
                            const item = data[context[0].dataIndex];
                            return [`Attendance Rate: ${item.percentage}%`];
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: false,
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxTicksLimit: 15,
                        font: {
                            weight: '500'
                        }
                    }
                },
                y: {
                    stacked: false,
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        precision: 0,
                        font: {
                            weight: '500'
                        }
                    }
                }
            }
        }
    });
    
    this.charts.monthly = chart;
};

// Initialize attendance trends chart
DashboardCharts.initializeTrendChart = function() {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;
    
    // Fetch trend data
    fetch('/dashboard/api/attendance-trends')
        .then(response => response.json())
        .then(data => {
            this.createTrendChart(ctx, data);
        })
        .catch(error => {
            console.error('Failed to load trend data:', error);
            this.showChartError(ctx, 'Failed to load trend data');
        });
};

// Create attendance trends chart
DashboardCharts.createTrendChart = function(ctx, data) {
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => this.formatDateLabel(d.date)),
            datasets: [{
                label: 'Attendance Rate (%)',
                data: data.map(d => d.percentage),
                borderColor: this.config.colors.primary,
                backgroundColor: this.config.colors.primary + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: this.config.colors.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: this.config.animation,
            plugins: {
                title: {
                    display: true,
                    text: 'Attendance Trends (Last 30 Days)',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: this.config.colors.dark
                },
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: this.config.colors.primary,
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        title: function(context) {
                            const item = data[context[0].dataIndex];
                            return item.date;
                        },
                        label: function(context) {
                            const item = data[context.dataIndex];
                            return [
                                `Attendance Rate: ${item.percentage}%`,
                                `Present: ${item.present} faculty`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxTicksLimit: 10,
                        font: {
                            weight: '500'
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        },
                        font: {
                            weight: '500'
                        }
                    }
                }
            }
        }
    });
    
    this.charts.trend = chart;
};

// Show chart error
DashboardCharts.showChartError = function(ctx, message) {
    const container = ctx.parentElement;
    container.innerHTML = `
        <div class="d-flex align-items-center justify-content-center h-100">
            <div class="text-center text-muted">
                <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                <p>${message}</p>
                <button class="btn btn-sm btn-outline-primary" onclick="location.reload()">
                    <i class="fas fa-redo me-1"></i>Retry
                </button>
            </div>
        </div>
    `;
};

// Format date label for charts
DashboardCharts.formatDateLabel = function(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
    });
};

// Update all charts with new data
DashboardCharts.updateCharts = function() {
    Object.keys(this.charts).forEach(chartKey => {
        const chart = this.charts[chartKey];
        if (chart) {
            chart.update('active');
        }
    });
};

// Destroy all charts
DashboardCharts.destroyCharts = function() {
    Object.keys(this.charts).forEach(chartKey => {
        const chart = this.charts[chartKey];
        if (chart) {
            chart.destroy();
        }
    });
    this.charts = {};
};

// Initialize charts function for global access
window.initializeDashboardCharts = function() {
    DashboardCharts.init();
};

// Auto-refresh charts every 5 minutes
setInterval(() => {
    if (Object.keys(DashboardCharts.charts).length > 0) {
        console.log('Auto-refreshing dashboard charts...');
        DashboardCharts.destroyCharts();
        DashboardCharts.init();
    }
}, 300000); // 5 minutes

// Handle window resize
window.addEventListener('resize', DashboardCharts.utils.debounce(() => {
    DashboardCharts.updateCharts();
}, 300));

// Expose to global scope
window.DashboardCharts = DashboardCharts;

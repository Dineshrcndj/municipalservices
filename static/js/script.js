// Form validation and submission
document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    
                    // Create error message
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.style.color = '#f72585';
                        errorMsg.style.fontSize = '0.85rem';
                        errorMsg.style.marginTop = '0.5rem';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                    errorMsg.textContent = 'This field is required';
                } else {
                    field.classList.remove('error');
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
    
    // Service card animations
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Admin functionality
    if (document.querySelector('.admin-dashboard')) {
        initializeAdminDashboard();
    }
    
    // Status update modal
    const statusUpdateModal = document.getElementById('statusUpdateModal');
    if (statusUpdateModal) {
        initializeStatusUpdateModal();
    }
});

function initializeAdminDashboard() {
    // Update stats based on filters
    const filters = document.querySelectorAll('.filter-select, .filter-input');
    filters.forEach(filter => {
        filter.addEventListener('change', updateDashboardStats);
    });
    
    // Export buttons
    const exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            const status = document.querySelector(`#${type}-status`).value;
            const date = document.querySelector(`#${type}-date`).value;
            
            window.location.href = `/admin/download-excel?type=${type}&status=${status}&date=${date}`;
        });
    });
    
    // Update status buttons
    document.querySelectorAll('.update-status-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const recordId = this.dataset.id;
            const recordType = this.dataset.type;
            const currentStatus = this.dataset.status;
            
            showStatusUpdateModal(recordId, recordType, currentStatus);
        });
    });
}

function showStatusUpdateModal(recordId, recordType, currentStatus) {
    const modal = document.getElementById('statusUpdateModal');
    const form = document.getElementById('statusUpdateForm');
    
    // Set form data
    form.dataset.id = recordId;
    form.dataset.type = recordType;
    form.dataset.currentStatus = currentStatus;
    
    // Reset form
    document.getElementById('amountPaid').value = '';
    
    // Show modal
    modal.classList.add('active');
}

function initializeStatusUpdateModal() {
    const modal = document.getElementById('statusUpdateModal');
    const form = document.getElementById('statusUpdateForm');
    const cancelBtn = document.getElementById('cancelStatusUpdate');
    
    // Close modal on cancel
    cancelBtn.addEventListener('click', function() {
        modal.classList.remove('active');
    });
    
    // Close modal on outside click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
    
    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const recordId = this.dataset.id;
        const recordType = this.dataset.type;
        const amountPaid = document.getElementById('amountPaid').value;
        
        // Show loading state
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.innerHTML = '<div class="spinner"></div>';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch('/admin/update-status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: recordId,
                    type: recordType,
                    status: 'completed',
                    amount_paid: amountPaid
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Reload the page to show updated status
                window.location.reload();
            } else {
                alert('Failed to update status. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        } finally {
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            modal.classList.remove('active');
        }
    });
}

async function updateDashboardStats() {
    const recordType = this ? this.dataset.type : 'property_tax';
    const period = document.getElementById(`${recordType}-period`).value;
    
    try {
        const response = await fetch(`/admin/stats?type=${recordType}&period=${period}`);
        const data = await response.json();
        
        // Update stats display
        document.getElementById(`${recordType}-total`).textContent = data.total;
        document.getElementById(`${recordType}-pending`).textContent = data.pending;
        document.getElementById(`${recordType}-completed`).textContent = data.completed;
        document.getElementById(`${recordType}-amount`).textContent = `₹${data.total_amount}`;
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Mobile menu toggle
function toggleMobileMenu() {
    const nav = document.querySelector('.admin-nav .nav-links');
    nav.classList.toggle('active');
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Download CSV function (alternative to Excel)
function downloadCSV(data, filename) {
    const csvContent = "data:text/csv;charset=utf-8," + data;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
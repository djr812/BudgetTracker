// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Add form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Add confirmation for delete actions
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                event.preventDefault();
            }
        });
    });

    // Add date validation
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const today = new Date();
            if (selectedDate > today) {
                alert('Please select a date that is not in the future.');
                this.value = '';
            }
        });
    });

    // Add amount validation
    const amountInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    amountInputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 0) {
                alert('Amount cannot be negative.');
                this.value = '';
            }
        });
    });

    // Add time validation
    const timeInputs = document.querySelectorAll('input[type="time"]');
    timeInputs.forEach(input => {
        input.addEventListener('change', function() {
            const selectedTime = this.value;
            const [hours, minutes] = selectedTime.split(':');
            if (hours > 23 || minutes > 59) {
                alert('Please select a valid time.');
                this.value = '';
            }
        });
    });

    // Handle delete transaction
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const transactionId = this.dataset.id;
            if (confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
                fetch(`/transactions/${transactionId}/delete`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove the row from the table
                        this.closest('tr').remove();
                        // Show success message
                        alert('Transaction deleted successfully');
                    } else {
                        alert('Error deleting transaction: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error deleting transaction. Please try again.');
                });
            }
        });
    });

    // Edit Category Modal
    const editModal = new bootstrap.Modal(document.getElementById('editCategoryModal'));
    const editButtons = document.querySelectorAll('.edit-category');
    const categoryDeleteButtons = document.querySelectorAll('.delete-category');
    const editForm = document.getElementById('editCategoryForm');
    const saveEditButton = document.getElementById('saveEditCategory');

    // Handle edit button clicks
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const categoryId = this.dataset.id;
            const categoryName = this.dataset.name;
            
            document.getElementById('editCategoryId').value = categoryId;
            document.getElementById('editCategoryName').value = categoryName;
            
            editModal.show();
        });
    });

    // Handle save edit button click
    saveEditButton.addEventListener('click', function() {
        const categoryId = document.getElementById('editCategoryId').value;
        const categoryName = document.getElementById('editCategoryName').value;

        fetch(`/categories/${categoryId}/edit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `categoryName=${encodeURIComponent(categoryName)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the table row
                const row = document.querySelector(`.edit-category[data-id="${categoryId}"]`).closest('tr');
                row.querySelector('td:nth-child(2)').textContent = categoryName;
                
                // Close the modal
                editModal.hide();
                
                // Show success message
                alert('Category updated successfully');
            } else {
                alert('Error updating category: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error updating category. Please try again.');
        });
    });

    // Handle delete button clicks
    categoryDeleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const categoryId = this.dataset.id;
            if (confirm('Are you sure you want to delete this category? This action cannot be undone.')) {
                fetch(`/categories/${categoryId}/delete`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove the row from the table
                        this.closest('tr').remove();
                        // Show success message
                        alert('Category deleted successfully');
                    } else {
                        alert('Error deleting category: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error deleting category. Please try again.');
                });
            }
        });
    });
});

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

// Show/hide password
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
    input.setAttribute('type', type);
}

// Add transaction form validation
function validateTransactionForm() {
    const amount = document.getElementById('amount').value;
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;
    const category = document.getElementById('category').value;
    const description = document.getElementById('description').value;

    if (!amount || !date || !time || !category || !description) {
        alert('Please fill in all fields.');
        return false;
    }

    if (parseFloat(amount) <= 0) {
        alert('Amount must be greater than 0.');
        return false;
    }

    return true;
}

// Add category form validation
function validateCategoryForm() {
    const categoryName = document.getElementById('categoryName').value;
    const categoryId = document.getElementById('categoryId').value;

    if (!categoryName || !categoryId) {
        alert('Please fill in all fields.');
        return false;
    }

    if (categoryId.length < 4 || categoryId.length > 4) {
        alert('Category ID must be exactly 4 characters.');
        return false;
    }

    return true;
}

// Add budget form validation
function validateBudgetForm() {
    const budget = document.getElementById('budget').value;

    if (!budget) {
        alert('Please enter a budget amount.');
        return false;
    }

    if (parseFloat(budget) <= 0) {
        alert('Budget must be greater than 0.');
        return false;
    }

    return true;
}

// Export report function
function exportReport(reportType, format) {
    window.location.href = `/reports/export/${reportType}/${format}`;
} 
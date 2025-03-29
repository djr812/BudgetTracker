import config from './config.js';

// Make config available globally
window.config = config;

// Initialize modals globally
let deleteTransactionModalInstance = null;
let deleteCategoryModalInstance = null;
let editCategoryModalInstance = null;

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Initialize toast
    const toastElement = document.getElementById('notificationToast');
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });

    /**
     * Function Name: showNotification
     * Description: Displays a notification message to the user.
     * @param {string} message - The message to display in the notification.
     * @param {string} type - The type of notification to display (success, error, warning).
     * @returns {void}
     * @throws {Error} [Description of the conditions under which an error is thrown]
     * @example showNotification('Transaction deleted successfully');
     */
    function showNotification(message, type = 'success') {
        const toastBody = document.getElementById('notificationMessage');
        toastBody.textContent = message;
        
        // Update toast styling based on type
        toastElement.className = 'toast';
        if (type === 'success') {
            toastElement.classList.add('bg-success', 'text-white');
        } else if (type === 'error') {
            toastElement.classList.add('bg-danger', 'text-white');
        } else if (type === 'warning') {
            toastElement.classList.add('bg-warning', 'text-dark');
        }
        
        toast.show();
    }

    // Make showNotification available globally
    window.showNotification = showNotification;

    // Form validation
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

    // Add date validation
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const today = new Date();
            if (selectedDate > today) {
                showNotification('Please select a date that is not in the future.', 'warning');
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
                showNotification('Amount cannot be negative.', 'warning');
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
                showNotification('Please select a valid time.', 'warning');
                this.value = '';
            }
        });
    });

    // Initialize modals
    const deleteTransactionModal = document.getElementById('deleteTransactionModal');
    const deleteCategoryModal = document.getElementById('deleteCategoryModal');
    const editCategoryModal = document.getElementById('editCategoryModal');
    
    if (deleteTransactionModal) {
        deleteTransactionModalInstance = new bootstrap.Modal(deleteTransactionModal);
        // Store the transaction ID in the modal element itself
        deleteTransactionModal.dataset.transactionId = null;
    }
    if (deleteCategoryModal) {
        deleteCategoryModalInstance = new bootstrap.Modal(deleteCategoryModal);
    }
    if (editCategoryModal) {
        editCategoryModalInstance = new bootstrap.Modal(editCategoryModal);
    }

    // Handle delete button clicks for transactions using event delegation
    document.addEventListener('click', function(event) {
        const deleteButton = event.target.closest('.delete-btn');
        if (deleteButton && deleteTransactionModal) {
            const transactionId = deleteButton.dataset.id;
            const transactionDate = deleteButton.dataset.date;
            const transactionTime = deleteButton.dataset.time;
            const transactionCategory = deleteButton.dataset.category;
            const transactionDescription = deleteButton.dataset.description;
            const transactionAmount = deleteButton.dataset.amount;
            
            // Store the transaction ID in the modal element
            deleteTransactionModal.dataset.transactionId = transactionId;
            
            // Populate modal with transaction details
            document.getElementById('deleteTransactionDate').textContent = transactionDate;
            document.getElementById('deleteTransactionTime').textContent = transactionTime;
            document.getElementById('deleteTransactionCategory').textContent = transactionCategory;
            document.getElementById('deleteTransactionDescription').textContent = transactionDescription;
            document.getElementById('deleteTransactionAmount').textContent = transactionAmount;
            
            // Show the modal
            deleteTransactionModalInstance.show();
        }
    });

    // Handle confirm delete transaction
    const confirmDeleteTransactionBtn = document.getElementById('confirmDeleteTransaction');
    if (confirmDeleteTransactionBtn) {
        confirmDeleteTransactionBtn.addEventListener('click', function() {
            const transactionId = deleteTransactionModal.dataset.transactionId;
            if (!transactionId) return;

            fetch(`${config.serverURL}transactions/${transactionId}/delete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the row from the table
                    const row = document.querySelector(`.delete-btn[data-id="${transactionId}"]`).closest('tr');
                    if (row) {
                        row.remove();
                        showNotification('Transaction deleted successfully');
                    }
                } else {
                    showNotification('Error deleting transaction: ' + data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error deleting transaction. Please try again.', 'error');
            })
            .finally(() => {
                deleteTransactionModalInstance.hide();
            });
        });
    }

    // Handle edit button clicks for categories using event delegation
    document.addEventListener('click', function(event) {
        const editButton = event.target.closest('.edit-category');
        if (editButton && editCategoryModalInstance) {
            const categoryId = editButton.dataset.id;
            const categoryName = editButton.dataset.name;
            
            document.getElementById('editCategoryId').value = categoryId;
            document.getElementById('editCategoryName').value = categoryName;
            
            editCategoryModalInstance.show();
        }
    });

    // Handle save edit button click for categories
    const saveEditButton = document.getElementById('saveEditCategory');
    if (saveEditButton) {
        saveEditButton.addEventListener('click', function() {
            const categoryId = document.getElementById('editCategoryId').value;
            const categoryName = document.getElementById('editCategoryName').value;

            fetch(`${config.serverURL}categories/${categoryId}/edit`, {
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
                    editCategoryModalInstance.hide();
                    
                    // Show success message
                    showNotification('Category updated successfully');
                } else {
                    showNotification('Error updating category: ' + data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error updating category. Please try again.', 'error');
            });
        });
    }

    // Handle delete button clicks for categories using event delegation
    document.addEventListener('click', function(event) {
        const deleteButton = event.target.closest('.delete-category');
        if (deleteButton && deleteCategoryModalInstance) {
            const categoryId = deleteButton.dataset.id;
            const categoryName = deleteButton.dataset.name;
            
            // Populate modal with category details
            document.getElementById('deleteCategoryId').textContent = categoryId;
            document.getElementById('deleteCategoryName').textContent = categoryName;
            
            deleteCategoryModalInstance.show();
        }
    });

    // Handle confirm delete category
    const confirmDeleteCategoryBtn = document.getElementById('confirmDeleteCategory');
    if (confirmDeleteCategoryBtn) {
        confirmDeleteCategoryBtn.addEventListener('click', function() {
            const categoryId = document.getElementById('deleteCategoryId').textContent;
            const button = document.querySelector(`.delete-category[data-id="${categoryId}"]`);
            if (button) {
                deleteCategory(button);
                deleteCategoryModalInstance.hide();
            }
        });
    }

    /**
     * Function Name: deleteCategory
     * Description: Deletes a category and updates the UI accordingly.
     * @param {HTMLElement} button - The delete button element that triggered the deletion.
     * @returns {void}
     * @throws {Error} Throws an error if the API call fails.
     * @example deleteCategory(buttonElement);
     */
    function deleteCategory(button) {
        const categoryId = button.dataset.id;
        fetch(`${config.serverURL}categories/${categoryId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the row from the table
                button.closest('tr').remove();
                // Show success message
                showNotification('Category deleted successfully');
            } else {
                showNotification('Error deleting category: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error deleting category. Please try again.', 'error');
        });
    }

    // Handle add category form submission
    const categoryForm = document.getElementById('categoryForm');
    if (categoryForm) {
        categoryForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const categoryId = document.getElementById('categoryId').value;
            const categoryName = document.getElementById('categoryName').value;

            fetch(`${config.serverURL}categories/add`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `categoryId=${encodeURIComponent(categoryId)}&categoryName=${encodeURIComponent(categoryName)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Add new row to the table
                    const tbody = document.getElementById('categoryTableBody');
                    const newRow = document.createElement('tr');
                    newRow.dataset.id = categoryId;
                    newRow.innerHTML = `
                        <td style="width: 20% !important; text-align: left;">${categoryId}</td>
                        <td style="width: 50% !important; text-align: left;">${categoryName}</td>
                        <td style="width: 30% !important; text-align: center;">
                            <button type="button" class="btn btn-sm btn-outline-primary edit-category" 
                                    data-id="${categoryId}" 
                                    data-name="${categoryName}">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-danger delete-category" 
                                    data-id="${categoryId}"
                                    data-name="${categoryName}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(newRow);
                    
                    // Clear the form and reset validation state
                    categoryForm.reset();
                    categoryForm.classList.remove('was-validated');
                    
                    // Show success message
                    showNotification('Category added successfully');
                } else {
                    showNotification('Error adding category: ' + data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error adding category. Please try again.', 'error');
            });
        });
    }
});

/**
 * Function Name: formatCurrency
 * Description: Formats a number as a currency string.
 * @param {number} amount - The amount to format.
 * @returns {string} The formatted currency string.
 * @example formatCurrency(123.45); // Returns "$123.45"
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Function Name: formatDate
 * Description: Formats a date object or string into a standardized string format.
 * @param {Date|string} date - The date to format.
 * @returns {string} The formatted date string.
 * @example formatDate(new Date()); // Returns date in format "MM/DD/YYYY"
 */
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

/**
 * Function Name: togglePassword
 * Description: Toggles the visibility of a password input field.
 * @param {string} inputId - The ID of the password input element.
 * @returns {void}
 * @example togglePassword('passwordField');
 */
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
    input.setAttribute('type', type);
}

/**
 * Function Name: validateTransactionForm
 * Description: Validates the transaction form inputs before submission.
 * @returns {boolean} True if the form is valid, false otherwise.
 * @example if (validateTransactionForm()) { submitForm(); }
 */
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

/**
 * Function Name: validateBudgetForm
 * Description: Validates the budget form inputs before submission.
 * @returns {boolean} True if the form is valid, false otherwise.
 * @example if (validateBudgetForm()) { submitForm(); }
 */
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

/**
 * Function Name: exportReport
 * Description: Initiates the export of a report in the specified format.
 * @param {string} reportType - The type of report to export (category, date, time).
 * @param {string} format - The format to export the report in (csv, pdf).
 * @returns {void}
 * @example exportReport('category', 'csv');
 */
function exportReport(reportType, format) {
    window.location.href = `/reports/export/${reportType}/${format}`;
} 
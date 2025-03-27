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
    
    let deleteTransactionModalInstance = null;
    let deleteCategoryModalInstance = null;
    let editCategoryModalInstance = null;
    
    if (deleteTransactionModal) {
        deleteTransactionModalInstance = new bootstrap.Modal(deleteTransactionModal);
    }
    if (deleteCategoryModal) {
        deleteCategoryModalInstance = new bootstrap.Modal(deleteCategoryModal);
    }
    if (editCategoryModal) {
        editCategoryModalInstance = new bootstrap.Modal(editCategoryModal);
    }

    // Handle delete transaction
    const transactionDeleteButtons = document.querySelectorAll('.delete-btn');
    let transactionToDelete = null;

    transactionDeleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            transactionToDelete = this;
            if (deleteTransactionModalInstance) {
                // Populate modal with transaction details
                document.getElementById('deleteTransactionDate').textContent = this.dataset.date;
                document.getElementById('deleteTransactionCategory').textContent = this.dataset.category;
                document.getElementById('deleteTransactionDescription').textContent = this.dataset.description;
                document.getElementById('deleteTransactionAmount').textContent = this.dataset.amount;
                
                deleteTransactionModalInstance.show();
            } else {
                // Fallback to simple confirmation if modal is not available
                if (confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
                    deleteTransaction(this);
                }
            }
        });
    });

    // Handle confirm delete transaction
    const confirmDeleteTransactionBtn = document.getElementById('confirmDeleteTransaction');
    if (confirmDeleteTransactionBtn) {
        confirmDeleteTransactionBtn.addEventListener('click', function() {
            if (transactionToDelete) {
                deleteTransaction(transactionToDelete);
                deleteTransactionModalInstance.hide();
            }
        });
    }

    /**
     * Function Name: deleteTransaction
     * Description: Deletes a transaction and updates the UI accordingly.
     * @param {HTMLElement} button - The delete button element that triggered the deletion.
     * @returns {void}
     * @throws {Error} Throws an error if the API call fails.
     * @example deleteTransaction(buttonElement);
     */
    function deleteTransaction(button) {
        const transactionId = button.dataset.id;
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
                button.closest('tr').remove();
                // Show success message
                showNotification('Transaction deleted successfully');
            } else {
                showNotification('Error deleting transaction: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error deleting transaction. Please try again.', 'error');
        });
    }

    // Handle edit button clicks for categories
    const editButtons = document.querySelectorAll('.edit-category');
    if (editButtons.length > 0 && editCategoryModalInstance) {
        editButtons.forEach(button => {
            button.addEventListener('click', function() {
                const categoryId = this.dataset.id;
                const categoryName = this.dataset.name;
                
                document.getElementById('editCategoryId').value = categoryId;
                document.getElementById('editCategoryName').value = categoryName;
                
                editCategoryModalInstance.show();
            });
        });
    }

    // Handle save edit button click for categories
    const saveEditButton = document.getElementById('saveEditCategory');
    if (saveEditButton) {
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

    // Handle delete button clicks for categories
    const categoryDeleteButtons = document.querySelectorAll('.delete-category');
    if (categoryDeleteButtons.length > 0) {
        categoryDeleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const categoryId = this.dataset.id;
                const categoryName = this.dataset.name;
                
                if (deleteCategoryModalInstance) {
                    // Populate modal with category details
                    document.getElementById('deleteCategoryId').textContent = categoryId;
                    document.getElementById('deleteCategoryName').textContent = categoryName;
                    
                    deleteCategoryModalInstance.show();
                } else {
                    // Fallback to simple confirmation if modal is not available
                    if (confirm('Are you sure you want to delete this category? This action cannot be undone.')) {
                        deleteCategory(this);
                    }
                }
            });
        });
    }

    // Handle confirm delete category
    const confirmDeleteCategoryBtn = document.getElementById('confirmDeleteCategory');
    if (confirmDeleteCategoryBtn) {
        confirmDeleteCategoryBtn.addEventListener('click', function() {
            const button = document.querySelector('.delete-category[data-id="' + 
                document.getElementById('deleteCategoryId').textContent + '"]');
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

    // Category form submission
    const categoryForm = document.getElementById('categoryForm');
    if (categoryForm) {
        categoryForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch('/categories/add', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success notification
                    showNotification('Category added successfully!', 'success');
                    
                    // Clear the form
                    categoryForm.reset();
                    
                    // Optionally refresh the page or update the categories list
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    // Show error notification
                    showNotification(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error adding category. Please try again.', 'error');
            });
        });
    }

    /**
     * Function Name: validateCategoryForm
     * Description: Validates the category form inputs before submission.
     * @returns {boolean} True if the form is valid, false otherwise.
     * @example if (validateCategoryForm()) { submitForm(); }
     */
    function validateCategoryForm() {
        const categoryName = document.getElementById('categoryName').value;
        const categoryId = document.getElementById('categoryId').value;

        if (!categoryName || !categoryId) {
            showNotification('Please fill in all fields.', 'warning');
            return false;
        }

        if (categoryId.length < 4 || categoryId.length > 4) {
            showNotification('Category ID must be exactly 4 characters.', 'warning');
            return false;
        }

        return true;
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
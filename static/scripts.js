document.addEventListener('DOMContentLoaded', function() {
    const depositForm = document.getElementById('depositForm');
    const expenseForm = document.getElementById('expenseForm');
    const savingsBalanceSpan = document.getElementById('savingsBalance');
    const expenseList = document.getElementById('expenseList');
    const userDataTable = document.getElementById('userDataTable');
    const userDataTableBody = document.getElementById('userDataTableBody');
    const noDataMessage = document.getElementById('noDataMessage');
    const saveBtn = document.getElementById('saveBtn');

    // Handle Deposit Form Submission
    if (depositForm) {
        depositForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const depositAmount = document.getElementById('depositAmount').value;

            fetch('/expense_tracker', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    depositAmount: depositAmount
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    savingsBalanceSpan.textContent = data.new_savings;
                    document.getElementById('depositAmount').value = '';
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Handle Expense Form Submission
    if (expenseForm) {
        expenseForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const expenseDate = document.getElementById('expenseDate').value;
            const expenseUsage = document.getElementById('expenseUsage').value;
            const expenseAmount = document.getElementById('expenseAmount').value;

            fetch('/expense_tracker', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    expenseDate: expenseDate,
                    expenseUsage: expenseUsage,
                    expenseAmount: expenseAmount
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the savings balance
                    savingsBalanceSpan.textContent = data.new_savings;
                    // Add the new expense to the list
                    const newExpense = document.createElement('li');
                    newExpense.textContent = `${expenseDate} - ${expenseUsage}: $${expenseAmount}`;
                    expenseList.appendChild(newExpense);

                    // Clear form fields
                    document.getElementById('expenseDate').value = '';
                    document.getElementById('expenseUsage').value = '';
                    document.getElementById('expenseAmount').value = '';
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Fetch user data when on the user data page
    if (window.location.pathname === '/user_data') {
        fetch('/get_user_data')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    // Show message if no data
                    userDataTable.style.display = 'none';
                    noDataMessage.style.display = 'block';
                } else {
                    // Hide message and show table
                    noDataMessage.style.display = 'none';
                    userDataTable.style.display = 'table';

                    // Populate table
                    userDataTableBody.innerHTML = `
                        <tr>
                            <td>${data.full_name}</td>
                            <td>${data.email}</td>
                            <td>${data.job}</td>
                            <td>$${data.monthly_income}</td>
                            <td>$${data.annual_income}</td>
                            <td>$${data.savings}</td>
                        </tr>
                    `;
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Handle Save Button Click
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            alert('User data saved successfully!');
        });
    }
});

// Utility function to show/hide elements
function toggleDisplay(element, displayStyle) {
    element.style.display = displayStyle;
}

// Initialize essential form popup
function initEssentialFormPopup() {
    const popup = document.getElementById('essential-form-popup');
    const btn = document.getElementById('essential-btn');
    const closeBtn = document.querySelector('.close-btn');

    btn.onclick = function() {
        popup.style.display = 'block';
        fetchWarehouses(); // Fetch warehouses when popup opens
    }

    closeBtn.onclick = function() {
        popup.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == popup) {
            popup.style.display = 'none';
        }
    }
}

// Fetch available warehouses
async function fetchWarehouses() {
    try {
        const response = await fetch('/admin/warehouse_manager/get_warehouse_details');
        if (!response.ok) {
            console.error('Server error when fetching warehouses:', response.status);
            // Add a default option to the dropdown
            const warehouseSelect = document.getElementById('warehouse');
            warehouseSelect.innerHTML = '<option value="">Select a warehouse</option>';
            warehouseSelect.innerHTML += '<option value="default">Default Warehouse</option>';
            return;
        }
        
        const data = await response.json();
        if (data.success && data.warehouses) {
            const warehouseSelect = document.getElementById('warehouse');
            warehouseSelect.innerHTML = '<option value="">Select a warehouse</option>';
            
            data.warehouses.forEach(warehouse => {
                if (warehouse.status === 'Operational') {
                    const option = document.createElement('option');
                    option.value = warehouse.wid;
                    option.textContent = `${warehouse.name} - ${warehouse.location}`;
                    warehouseSelect.appendChild(option);
                }
            });
        }
    } catch (error) {
        console.error('Error fetching warehouses:', error);
        // Add a default option to the dropdown
        const warehouseSelect = document.getElementById('warehouse');
        warehouseSelect.innerHTML = '<option value="">Select a warehouse</option>';
        warehouseSelect.innerHTML += '<option value="default">Default Warehouse</option>';
    }
}

// Initialize item group handlers
function initItemGroupHandlers() {
    const addItemBtn = document.getElementById('add-item-btn');
    const itemsContainer = document.getElementById('items-container');

    // Initially disable the Add Another Item button
    addItemBtn.disabled = true;
    addItemBtn.style.opacity = '0.5';
    addItemBtn.style.cursor = 'not-allowed';

    // Add event listeners to the first item's inputs to enable the Add Another Item button
    const firstItemGroup = document.querySelector('.item-group');
    if (firstItemGroup) {
        // Add remove button to the first item group
        addRemoveButton(firstItemGroup);
        
        // Add input event listeners
        const inputs = firstItemGroup.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('input', validateCurrentItem);
        });
    }

    addItemBtn.onclick = function() {
        // Minimize all existing item groups
        const existingItemGroups = document.querySelectorAll('.item-group:not(.minimized)');
        existingItemGroups.forEach(group => {
            minimizeItemGroup(group);
        });

        // Create a new item group
        const newItemGroup = document.createElement('div');
        newItemGroup.className = 'item-group';
        newItemGroup.innerHTML = `
            <div class="item-fields">
                <label for="item">Item:</label>
                <input type="text" class="item-name" name="item[]" required>

                <label for="quantity">Quantity:</label>
                <input type="number" class="item-quantity" name="quantity[]" min="1" required>

                <label for="condition">Condition:</label>
                <select class="item-condition" name="condition[]">
                    <option value="new">Unused</option>
                    <option value="used">Used (Good)</option>
                    <option value="used-fair">Used (Fair)</option>
                </select>
            </div>
        `;
        
        // Add remove button to the new item group
        addRemoveButton(newItemGroup);
        
        // Add the new item group to the container
        itemsContainer.appendChild(newItemGroup);
        
        // Add input event listeners to the new item group
        const inputs = newItemGroup.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('input', validateCurrentItem);
        });
        
        // Disable the Add Another Item button until the new item is filled out
        addItemBtn.disabled = true;
        addItemBtn.style.opacity = '0.5';
        addItemBtn.style.cursor = 'not-allowed';
    };
}

// Function to validate the current item and enable/disable the Add Another Item button
function validateCurrentItem() {
    const addItemBtn = document.getElementById('add-item-btn');
    const currentItemGroup = document.querySelector('.item-group:not(.minimized)');
    
    if (currentItemGroup) {
        const itemName = currentItemGroup.querySelector('.item-name').value.trim();
        const itemQuantity = currentItemGroup.querySelector('.item-quantity').value;
        const itemCondition = currentItemGroup.querySelector('.item-condition').value;
        
        // Enable the button only if all fields are filled
        if (itemName && itemQuantity > 0 && itemCondition) {
            addItemBtn.disabled = false;
            addItemBtn.style.opacity = '1';
            addItemBtn.style.cursor = 'pointer';
        } else {
            addItemBtn.disabled = true;
            addItemBtn.style.opacity = '0.5';
            addItemBtn.style.cursor = 'not-allowed';
        }
    }
}

// Function to minimize an item group
function minimizeItemGroup(itemGroup) {
    // Get the item details
    const itemName = itemGroup.querySelector('.item-name').value || 'Unnamed Item';
    const itemQuantity = itemGroup.querySelector('.item-quantity').value || '0';
    const itemCondition = itemGroup.querySelector('.item-condition').value;
    
    // Create the minimized view
    const itemDetails = document.createElement('div');
    itemDetails.className = 'item-details';
    
    // Create item summary
    const itemSummary = document.createElement('div');
    itemSummary.className = 'item-summary';
    itemSummary.textContent = `${itemName} (${itemQuantity}) - ${itemCondition}`;
    
    // Create action buttons
    const itemActions = document.createElement('div');
    itemActions.className = 'item-actions';
    
    // Create edit button
    const editBtn = document.createElement('button');
    editBtn.type = 'button';
    editBtn.className = 'edit-item-btn';
    editBtn.textContent = 'Edit';
    editBtn.onclick = function(e) {
        e.stopPropagation();
        expandItemGroup(itemGroup);
    };
    
    // Create remove button
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'remove-item-btn';
    removeBtn.textContent = 'Remove';
    removeBtn.onclick = function(e) {
        e.stopPropagation();
        // Remove the item group
        itemGroup.remove();
        
        // Check if there are any item groups left
        const allItemGroups = document.querySelectorAll('.item-group');
        if (allItemGroups.length === 0) {
            // If no items left, create a new empty item group
            const itemsContainer = document.getElementById('items-container');
            const newItemGroup = document.createElement('div');
            newItemGroup.className = 'item-group';
            newItemGroup.innerHTML = `
                <div class="item-fields">
                    <label for="item">Item:</label>
                    <input type="text" class="item-name" name="item[]" required>

                    <label for="quantity">Quantity:</label>
                    <input type="number" class="item-quantity" name="quantity[]" min="1" required>

                    <label for="condition">Condition:</label>
                    <select class="item-condition" name="condition[]">
                        <option value="new">Unused</option>
                        <option value="used">Used (Good)</option>
                        <option value="used-fair">Used (Fair)</option>
                    </select>
                </div>
            `;
            
            // Add remove button to the new item group
            addRemoveButton(newItemGroup);
            
            // Add the new item group to the container
            itemsContainer.appendChild(newItemGroup);
            
            // Add input event listeners to the new item group
            const inputs = newItemGroup.querySelectorAll('input, select');
            inputs.forEach(input => {
                input.addEventListener('input', validateCurrentItem);
            });
            
            // Disable the Add Another Item button until the new item is filled out
            const addItemBtn = document.getElementById('add-item-btn');
            addItemBtn.disabled = true;
            addItemBtn.style.opacity = '0.5';
            addItemBtn.style.cursor = 'not-allowed';
        }
    };
    
    // Add buttons to actions
    itemActions.appendChild(editBtn);
    itemActions.appendChild(removeBtn);
    
    // Add summary and actions to details
    itemDetails.appendChild(itemSummary);
    itemDetails.appendChild(itemActions);
    
    // Add details to item group
    itemGroup.appendChild(itemDetails);
    
    // Add minimized class
    itemGroup.classList.add('minimized');
    
    // Add click event to expand on click
    itemGroup.onclick = function(e) {
        // Don't expand if clicking on buttons
        if (e.target.tagName !== 'BUTTON') {
            expandItemGroup(itemGroup);
        }
    };
}

// Function to expand a minimized item group
function expandItemGroup(itemGroup) {
    // Remove minimized class
    itemGroup.classList.remove('minimized');
    
    // Remove the details element
    const detailsElement = itemGroup.querySelector('.item-details');
    if (detailsElement) {
        detailsElement.remove();
    }
    
    // Remove click event
    itemGroup.onclick = null;
    
    // Minimize all other item groups
    const allItemGroups = document.querySelectorAll('.item-group.minimized');
    allItemGroups.forEach(group => {
        if (group !== itemGroup) {
            // Do nothing, already minimized
        }
    });
}

// Function to add a remove button to an item group
function addRemoveButton(itemGroup) {
    // Create remove button
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'remove-item-btn';
    removeBtn.textContent = 'Remove Item';
    
    // Add click event to remove the item group
    removeBtn.onclick = function() {
        // Remove the item group
        itemGroup.remove();
        
        // Check if there are any item groups left
        const allItemGroups = document.querySelectorAll('.item-group');
        if (allItemGroups.length === 0) {
            // If no items left, create a new empty item group
            const itemsContainer = document.getElementById('items-container');
            const newItemGroup = document.createElement('div');
            newItemGroup.className = 'item-group';
            newItemGroup.innerHTML = `
                <div class="item-fields">
                    <label for="item">Item:</label>
                    <input type="text" class="item-name" name="item[]" required>

                    <label for="quantity">Quantity:</label>
                    <input type="number" class="item-quantity" name="quantity[]" min="1" required>

                    <label for="condition">Condition:</label>
                    <select class="item-condition" name="condition[]">
                        <option value="new">Unused</option>
                        <option value="used">Used (Good)</option>
                        <option value="used-fair">Used (Fair)</option>
                    </select>
                </div>
            `;
            
            // Add remove button to the new item group
            addRemoveButton(newItemGroup);
            
            // Add the new item group to the container
            itemsContainer.appendChild(newItemGroup);
            
            // Add input event listeners to the new item group
            const inputs = newItemGroup.querySelectorAll('input, select');
            inputs.forEach(input => {
                input.addEventListener('input', validateCurrentItem);
            });
            
            // Disable the Add Another Item button until the new item is filled out
            const addItemBtn = document.getElementById('add-item-btn');
            addItemBtn.disabled = true;
            addItemBtn.style.opacity = '0.5';
            addItemBtn.style.cursor = 'not-allowed';
        }
    };
    
    // Add the remove button to the item group
    itemGroup.appendChild(removeBtn);
}

// Validate form before submission
function validateForm(event) {
    const quantities = document.querySelectorAll('.item-quantity');
    const warehouse = document.getElementById('warehouse');
    let isValid = true;

    quantities.forEach(quantity => {
        if (quantity.value <= 0) {
            alert('Quantity must be greater than zero.');
            isValid = false;
        }
    });

    if (!warehouse.value) {
        alert('Please select a warehouse.');
        isValid = false;
    }

    if (!isValid) {
        event.preventDefault();
    }
}

// Submit donation form
function submitDonationForm(event) {
    event.preventDefault();

    const items = document.querySelectorAll('.item-group');
    const itemData = Array.from(items).map(item => ({
        name: item.querySelector('.item-name').value,
        quantity: item.querySelector('.item-quantity').value,
        condition: item.querySelector('.item-condition').value
    }));

    const warehouseId = document.getElementById('warehouse').value;
    const phone = document.getElementById('phone').value;
    const address = document.getElementById('address').value;

    // Validate form data
    if (!warehouseId) {
        alert('Please select a warehouse');
        return;
    }

    if (!phone) {
        alert('Please enter your phone number');
        return;
    }

    if (!address) {
        alert('Please enter your address');
        return;
    }

    if (itemData.length === 0) {
        alert('Please add at least one item');
        return;
    }

    // Show loading indicator
    const submitButton = document.querySelector('.submit-button');
    let originalText = '';
    if (submitButton) {
        originalText = submitButton.textContent;
        submitButton.textContent = 'Submitting...';
        submitButton.disabled = true;
    }

    fetch('/user/donate_items', {
        method: 'POST',
        body: JSON.stringify({ 
            items: itemData,
            warehouse_id: warehouseId,
            phone: phone,
            address: address
        }),
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || `Server error: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert('Donation submitted successfully!');
                // Reset form or redirect as needed
                window.location.reload();
            } else {
                alert(data.error || 'Failed to submit donation');
            }
        })
        .catch(error => {
            alert(error.message || 'Error submitting donation');
        })
        .finally(() => {
            if (submitButton) {
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
}

let donationChart; // Store the chart instance globally

// Render donation summary chart
function renderDonationChart(itemSummary) {
    const labels = Object.keys(itemSummary);
    const quantities = Object.values(itemSummary);

    const ctx = document.getElementById('myChart').getContext('2d');

    // Destroy the existing chart instance if it exists
    if (donationChart) {
        donationChart.destroy();
    }

    // Create a new chart instance
    donationChart = new Chart(ctx, {
        type: 'doughnut', // Doughnut chart
        data: {
            labels: labels,
            datasets: [{
                data: quantities,
                backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1'], // Add more colors if needed
                borderColor: '#000',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true // Show legend for doughnut chart
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const total = context.dataset.data.reduce((sum, value) => sum + value, 0);
                            const percentage = ((context.raw / total) * 100).toFixed(2);
                            return `${context.label}: ${context.raw} units (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Fetch and display donation summary
function fetchDonationSummary() {
    fetch('/user/user-donation-summary')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data) {
                const amountDonated = data.amount_donated;
                const itemsDonated = data.items_donated;

                // Aggregate item quantities
                const itemSummary = itemsDonated.reduce((summary, [itemName, quantity]) => {
                    summary[itemName] = (summary[itemName] || 0) + parseInt(quantity, 10);
                    return summary;
                }, {});

                renderDonationChart(itemSummary);

                document.getElementById('amount-donated').textContent = amountDonated ? `Amount Donated: ₹${amountDonated}` : 'Amount Donated: None';
                document.getElementById('items-donated').innerHTML = Object.keys(itemSummary).length > 0
                    ? `Items Donated: ${Object.entries(itemSummary).map(([label, quantity]) => `<br>${label}: ${quantity} units`).join(", ")}`
                    : "Items Donated: None";
            } else {
                console.error("Failed to fetch donation summary:", data.error);
                // Set default values when data is not available
                document.getElementById('amount-donated').textContent = 'Amount Donated: None';
                document.getElementById('items-donated').innerHTML = "Items Donated: None";
            }
        })
        .catch(error => {
            console.error("Error fetching donation summary:", error);
            // Set default values when there's an error
            document.getElementById('amount-donated').textContent = 'Amount Donated: None';
            document.getElementById('items-donated').innerHTML = "Items Donated: None";
        });
}

// Initialize all event listeners and fetch data on DOMContentLoaded
document.addEventListener("DOMContentLoaded", function () {
    initEssentialFormPopup();
    initItemGroupHandlers();

    const essentialForm = document.getElementById('essential-form');
    essentialForm.addEventListener('submit', validateForm);
    essentialForm.addEventListener('submit', submitDonationForm);

    fetchDonationSummary();
});
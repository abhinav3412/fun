// Main document ready handler
document.addEventListener('DOMContentLoaded', function() {
    const volunteerForm = document.getElementById('volunteer-form');
    const roleIdInput = document.getElementById('role_id');

    if (!volunteerForm || !roleIdInput) {
        console.error('Required form elements not found');
        return;
    }

    // Function to validate role ID format
    function validateRoleId(roleId) {
        // Allow both formats: "R123" or "123"
        const pattern = /^(R?\d+)$/;
        return pattern.test(roleId);
    }

    // Add input validation for role_id
    roleIdInput.addEventListener('input', function() {
        const value = this.value;
        if (value && !validateRoleId(value)) {
            this.setCustomValidity('Please enter a valid Role ID (e.g., R123 or 123)');
        } else {
            this.setCustomValidity('');
        }
    });

    // Handle form submission
    volunteerForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const roleId = roleIdInput.value;
        if (!validateRoleId(roleId)) {
            alert('Please enter a valid Role ID (e.g., R123 or 123)');
            return;
        }

        // Get form data
        const formData = {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            mobile: document.getElementById('mobile').value.trim(),
            location: document.getElementById('location').value.trim(),
            role: document.getElementById('role').value,
            role_id: roleId.trim()
        };

        // Debug log
        console.log('Sending form data:', formData);

        // Validate all required fields
        for (const [key, value] of Object.entries(formData)) {
            if (!value) {
                alert(`Please fill in the ${key} field`);
                return;
            }
        }

        try {
            const response = await fetch('/volunteer/apply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            console.log('Server response:', result);  // Debug log

            if (response.ok) {
                alert('Your volunteer application has been submitted successfully!');
                volunteerForm.reset();
            } else {
                console.error('Error response:', result);  // Debug log
                alert('Error submitting application: ' + (result.message || 'Please try again'));
            }
        } catch (error) {
            console.error('Fetch error:', error);  // Debug log
            alert('An error occurred while submitting your application. Please try again.');
        }
    });

    // Handle role selection and auto-fill role ID
    const roleSelect = document.getElementById('role');
    if (roleSelect) {
        roleSelect.addEventListener('change', function() {
            const selectedOption = this.value;
            
            // Map of roles to their IDs
            const roleIdMap = {
                'Food Distribution Volunteer': 'R123',
                'Medical Aid Volunteer': 'R124',
                'Rescue Operation Volunteer': 'R125',
                'Shelter Management Volunteer': 'R126',
                'Logistics Coordinator': 'R127',
                'Counseling Volunteer': 'R128',
                'Water Sanitation Volunteer': 'R129',
                'Child Care Volunteer': 'R130',
                'Elderly Care Volunteer': 'R131',
                'Animal Rescue Volunteer': 'R132',
                'Community Liaison Volunteer': 'R133'
            };

            // Set the role ID based on the selected role
            roleIdInput.value = roleIdMap[selectedOption] || '';
            // Trigger validation
            roleIdInput.dispatchEvent(new Event('input'));
        });
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const userList = document.getElementById("user-list");
    const userModal = document.getElementById("user-modal");
    const closeModalBtn = document.querySelector(".close-btn");
    const userForm = document.getElementById("user-form");
    const addUserBtn = document.getElementById("add-user-btn");
    const roleSelect = document.getElementById("role");
    const viewPasswordBtn = document.getElementById("view-password");
    const passwordInput = document.getElementById("password");
    
    const searchNameInput = document.getElementById("name-filter"); // Name filter input
    const searchLocationInput = document.getElementById("location-filter"); // Location filter input

    let editingUserId = null;
    let usersData = []; // Store all users for filtering

    // Toggle password visibility
    viewPasswordBtn.addEventListener("click", () => {
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);
        viewPasswordBtn.textContent = type === "password" ? "Show" : "Hide";
    });

    // Fetch and Render Users
    async function fetchAndRenderUsers() {
        try {
            const response = await fetch("/admin/get_all_users");
            if (!response.ok) throw new Error("Failed to fetch users");
            usersData = await response.json(); // Store data for filtering
            renderUsers(usersData);
        } catch (error) {
            console.error("Error fetching users:", error);
        }
    }

    // Render Users from Data
    function renderUsers(users) {
        userList.innerHTML = "";
        users.forEach((user) => {
            const row = document.createElement("tr");
            const isCurrentUser = user.uid === currentUserId; // currentUserId should be set in the template
            row.innerHTML = `
                <td>${user.uid}</td>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>${user.location || "N/A"}</td>
                <td>${user.mobile || "N/A"}</td>
                <td>${user.role}</td>
                <td>
                    <button class="edit-btn" data-id="${user.uid}">Edit</button>
                    <button class="delete-btn" data-id="${user.uid}" ${isCurrentUser ? 'disabled title="You cannot delete your own account"' : ''}>Delete</button>
                </td>
            `;
            userList.appendChild(row);
        });

        attachEventListeners();
    }

    // Attach Event Listeners to Buttons
    function attachEventListeners() {
        document.querySelectorAll(".delete-btn").forEach(button => {
            button.addEventListener("click", (e) => {
                deleteUser(e.target.dataset.id);
            });
        });

        document.querySelectorAll(".edit-btn").forEach(button => {
            button.addEventListener("click", (e) => {
                openEditModal(e.target.dataset.id);
            });
        });
    }

    // Filter Users by Name
    function filterByName() {
        const query = searchNameInput.value.toLowerCase().trim();
        const filteredUsers = usersData.filter(user =>
            user.username.toLowerCase().includes(query)
        );
        renderUsers(filteredUsers);
    }

    // Filter Users by Location
    function filterByLocation() {
        const query = searchLocationInput.value.toLowerCase().trim();
        const filteredUsers = usersData.filter(user =>
            user.location && user.location.toLowerCase().includes(query)
        );
        renderUsers(filteredUsers);
    }

    // Delete User Function
    async function deleteUser(userId) {
        const confirmMessage = "Are you sure you want to delete this user?";
        const forceConfirmMessage = 
            "WARNING: Force deleting a user will:\n" +
            "1. Delete ALL their donations\n" +
            "2. Delete ALL their activity records\n" +
            "3. Remove ALL their warehouse/camp manager assignments\n" +
            "4. Delete the user account\n\n" +
            "This action CANNOT be undone. Are you sure you want to proceed?";

        if (!confirm(confirmMessage)) return;

        try {
            const response = await fetch(`/admin/delete_user/${userId}`, { method: "DELETE" });
            const data = await response.json();
            
            if (!response.ok) {
                // Show error message in a more user-friendly way
                const errorMessage = data.error || 'Failed to delete user';
                
                // If deletion failed due to related records, offer force delete
                if (errorMessage.includes('related records') || errorMessage.includes('donations')) {
                    if (confirm(forceConfirmMessage)) {
                        // Attempt force delete
                        const forceResponse = await fetch(`/admin/delete_user/${userId}?force=true`, { method: "DELETE" });
                        const forceData = await forceResponse.json();
                        
                        if (!forceResponse.ok) {
                            alert(forceData.error || 'Failed to force delete user');
                            return;
                        }
                        
                        alert(forceData.message || 'User force deleted successfully');
                        fetchAndRenderUsers();
                        return;
                    }
                }
                
                alert(errorMessage);
                return;
            }
            
            // Show success message
            alert(data.message || 'User deleted successfully');
            fetchAndRenderUsers();
        } catch (error) {
            console.error("Error deleting user:", error);
            alert("An error occurred while deleting the user. Please try again.");
        }
    }

    // Open Modal for Editing User
    async function openEditModal(userId) {
        try {
            const response = await fetch(`/admin/get_user/${userId}`);
            if (!response.ok) throw new Error("Failed to fetch user data");

            const user = await response.json();
            const isCurrentUser = userId === currentUserId;

            document.getElementById("username").value = user.username;
            document.getElementById("password").value = ""; // Clear password field for security
            document.getElementById("email").value = user.email;
            document.getElementById("location").value = user.location || "";
            document.getElementById("mobile").value = user.mobile || "";
            document.getElementById("role").value = user.role;
            document.getElementById("associated-camp-id").value = user.associated_camp_id || "";

            // Disable role selection for current user
            const roleSelect = document.getElementById("role");
            roleSelect.disabled = isCurrentUser;
            if (isCurrentUser) {
                roleSelect.title = "You cannot change your own role";
            }

            editingUserId = userId;
            userModal.style.display = "block";
        } catch (error) {
            console.error("Error fetching user details:", error);
        }
    }

    // Open Modal for Adding New User
    function openAddModal() {
        userForm.reset();
        editingUserId = null;
        userModal.style.display = "block";
    }

    // Handle Form Submission (Add or Edit User)
    userForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        let userData = {
            username: document.getElementById("username").value.trim(),
            email: document.getElementById("email").value.trim(),
            password: document.getElementById("password").value.trim(),
            location: document.getElementById("location").value.trim(),
            mobile: document.getElementById("mobile").value.trim(),
            role: document.getElementById("role").value,
            associated_camp_id: document.getElementById("associated-camp-id").value.trim()
        };

        console.log("Form data before processing:", userData);

        if (editingUserId) {
            Object.keys(userData).forEach((key) => {
                if (userData[key] === "" || userData[key] === null) {
                    delete userData[key];
                }
            });
        } else {
            if (!userData.username || !userData.email || !userData.password) {
                alert("Please fill in all required fields");
                return;
            }
        }

        console.log("Form data after processing:", userData);

        try {
            const url = editingUserId
                ? `/admin/update_user/${editingUserId}`
                : "/admin/add_user";
            const method = editingUserId ? "PUT" : "POST";

            console.log(`Sending ${method} request to ${url} with data:`, userData);

            const response = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(userData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Failed to save user");
            }

            const responseData = await response.json();
            console.log("Server response:", responseData);

            userModal.style.display = "none";
            fetchAndRenderUsers();
        } catch (error) {
            console.error("Error saving user:", error);
            alert(error.message);
        }
    });

    // Close Modal Button
    closeModalBtn.addEventListener("click", () => {
        userModal.style.display = "none";
    });

    // Open Add User Modal on Button Click
    addUserBtn.addEventListener("click", openAddModal);

    // Close Modal if clicked outside content
    window.addEventListener("click", (e) => {
        if (e.target === userModal) {
            userModal.style.display = "none";
        }
    });

    // Attach Filter Event Listeners
    searchNameInput.addEventListener("input", filterByName);
    searchLocationInput.addEventListener("input", filterByLocation);
    document.getElementById("clear-filters").addEventListener("click", () => {
        searchNameInput.value = "";
        searchLocationInput.value = "";
        renderUsers(usersData);
    });

    // Initial load of users
    fetchAndRenderUsers();
});

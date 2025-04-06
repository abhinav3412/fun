// Function to toggle between login and signup forms
function toggleForms() {
    const wrapper = document.querySelector('.wrapper');
    wrapper.classList.toggle('active');
}

// Add event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const signInBtnLink = document.querySelector('.signInBtn-link');
    const signUpBtnLink = document.querySelector('.signUpBtn-link');
    const loginForm = document.querySelector('.form-wrapper.sign-in form');
    const signupForm = document.querySelector('.form-wrapper.sign-up form');
    const emailInput = document.getElementById('login-email');
    const passwordInput = document.getElementById('login-password');
    
    // Add click event listeners for form toggling
    if (signInBtnLink) {
        signInBtnLink.addEventListener('click', function(e) {
            e.preventDefault();
            toggleForms();
        });
    }
    
    if (signUpBtnLink) {
        signUpBtnLink.addEventListener('click', function(e) {
            e.preventDefault();
            toggleForms();
        });
    }
    
    // Add form validation for login form
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = emailInput.value.trim();
            const password = passwordInput.value.trim();
            
            if (!email || !password) {
                e.preventDefault();
                alert('Please enter both email and password');
                return;
            }
            
            // Basic email format validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert('Please enter a valid email address');
                return;
            }
        });
    }
    
    // Add form validation for signup form
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();
            const mobile = document.getElementById('mobile').value.trim();
            
            // Check if all required fields are filled
            if (!username || !email || !password || !mobile) {
                e.preventDefault();
                alert('Please fill in all required fields');
                return;
            }
            
            // Validate email format
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert('Please enter a valid email address');
                return;
            }
            
            // Validate password length
            if (password.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters long');
                return;
            }
            
            // Validate username length
            if (username.length < 3) {
                e.preventDefault();
                alert('Username must be at least 3 characters long');
                return;
            }
            
            // Check if there are any validation errors displayed
            const emailError = document.getElementById('email-error');
            const usernameError = document.getElementById('username-error');
            const phoneError = document.getElementById('phone-error');
            
            if ((emailError && emailError.style.display === 'block') || 
                (usernameError && usernameError.style.display === 'block') || 
                (phoneError && phoneError.style.display === 'block')) {
                e.preventDefault();
                alert('Please fix the validation errors before submitting');
                return;
            }
        });
    }
    
    // Add input validation for email field
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value.trim();
            if (email) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    this.classList.add('error');
                    alert('Please enter a valid email address');
                } else {
                    this.classList.remove('error');
                }
            }
        });
    }
    
    // Add input validation for password field
    if (passwordInput) {
        passwordInput.addEventListener('blur', function() {
            const password = this.value.trim();
            if (!password) {
                this.classList.add('error');
                alert('Please enter your password');
            } else {
                this.classList.remove('error');
            }
        });
    }
});
import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword
} from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { auth } from "./firebase-config.js";

document.addEventListener('DOMContentLoaded', () => {
    // Shared toast function
    function showToast(message, type = "success") {
        const toastEl = document.getElementById('toast-message');
        if (!toastEl) return;
        toastEl.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0 show`;
        toastEl.querySelector('.toast-body').textContent = message;
        setTimeout(() => toastEl.classList.remove('show'), 3000);
    }

    // Password Toggle Logic
    const toggleBtns = document.querySelectorAll('.password-toggle');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.previousElementSibling;
            const icon = btn.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });
    });

    const authForm = document.getElementById('auth-form');
    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('auth-email').value.trim();
            const password = document.getElementById('auth-password').value;
            const confirmPasswordEl = document.getElementById('auth-password-confirm');
            const errorEl = document.getElementById('auth-error');
            const submitBtn = document.getElementById('auth-submit-btn');

            if (errorEl) errorEl.classList.add('d-none');
            if (submitBtn) submitBtn.disabled = true;

            try {
                // 1. Email Validation (Strict)
                const emailRegex = /^[a-zA-Z0-9._%+-]+@(gmail\.com|yahoo\.com)$/;
                if (!emailRegex.test(email)) {
                    throw new Error("Only @gmail.com and @yahoo.com email addresses are allowed.");
                }

                if (email !== email.toLowerCase()) {
                    throw new Error("Email must be in lowercase");
                }

                // 2. Password Validation (Complex)
                // Rules: 6+ chars, 1 uppercase, 1 digit, 1 special char
                const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$/;
                if (!passwordRegex.test(password)) {
                    throw new Error("Password must be 6+ chars, incl. 1 uppercase, 1 digit, and 1 special character (@$!%*?&)");
                }

                // 3. Signup Specifics
                if (confirmPasswordEl) {
                    if (password !== confirmPasswordEl.value) {
                        throw new Error("Passwords do not match.");
                    }
                    await createUserWithEmailAndPassword(auth, email, password);
                    // header.js onAuthStateChanged will handle redirect
                } else {
                    await signInWithEmailAndPassword(auth, email, password);
                    // header.js onAuthStateChanged will handle redirect
                }
                // Re-enable button on success (redirect will happen via header.js)
                if (submitBtn) submitBtn.disabled = false;
            } catch (err) {
                console.error("Auth Error:", err.code, err.message);
                let userFriendlyMsg = err.message;

                // Handle Firebase specific errors
                if (err.code === 'auth/email-already-in-use') {
                    userFriendlyMsg = "Account already exists";
                } else if (err.code === 'auth/invalid-credential' || err.code === 'auth/user-not-found' || err.code === 'auth/wrong-password') {
                    userFriendlyMsg = "Invalid credentials";
                } else if (err.code === 'auth/invalid-email') {
                    userFriendlyMsg = "Enter valid email";
                } else if (err.code === 'auth/weak-password') {
                    userFriendlyMsg = "Password is too weak";
                }

                if (errorEl) {
                    errorEl.textContent = userFriendlyMsg;
                    errorEl.classList.remove('d-none');
                }
                if (submitBtn) submitBtn.disabled = false;
            }
        });
    }
});

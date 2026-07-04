import { onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { auth } from "./firebase-config.js";

// Global navigation check
onAuthStateChanged(auth, (user) => {
    const navUserEmail = document.getElementById('nav-user-email');
    const navAuthControls = document.getElementById('nav-auth-controls');
    const path = window.location.pathname;
    const isAuthPage = path.endsWith('index.html') || path.endsWith('/') || path.endsWith('signup.html');

    if (user) {
        if (navUserEmail) navUserEmail.textContent = user.email;
        if (navAuthControls) navAuthControls.classList.remove('d-none');

        // Redirect if logged in user is on login/signup pages
        if (isAuthPage) {
            window.location.href = 'generate.html';
        }
    } else {
        if (navUserEmail) navUserEmail.textContent = '';
        if (navAuthControls) navAuthControls.classList.add('d-none');

        // Redirect if logged out user is on protected pages
        if (!isAuthPage) {
            window.location.href = 'index.html';
        }
    }
});

// Logout listener
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('nav-logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await signOut(auth);
                window.location.href = 'index.html';
            } catch (err) {
                console.error("Logout failed", err);
            }
        });
    }
});

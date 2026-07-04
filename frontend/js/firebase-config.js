import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyChtSAqBkq78Bjx_TXI0xp3NgQ2EYH3L00",
    authDomain: "mbicg-4c56a.firebaseapp.com",
    projectId: "mbicg-4c56a",
    storageBucket: "mbicg-4c56a.firebasestorage.app",
    messagingSenderId: "199607578354",
    appId: "1:199607578354:web:b833c90b970d749e876a6b"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Backend URL: auto-detect local vs production
// For local dev: http://localhost:8000
// For Hugging Face Spaces production: replace with your Space URL
const BACKEND_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000"
    :"https://sudheshna-ravula-micg-backend.hf.space"; // ← update this for production

export { app, auth, BACKEND_URL };

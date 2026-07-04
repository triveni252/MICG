# Mood-Based Multilingual Image Caption Generator

This document is a comprehensive guide to the **Mood-Based Multilingual Image Caption Generator** project. It outlines the architecture, setup, development workflow, deployment instructions, and useful tips for contributors and operators.

---

## 🚀 Project Overview

The application allows users to upload images and receive automatic captions in multiple languages with a mood component. It includes:

- **Backend**: A FastAPI web service that processes images using an AI pipeline and stores results in Firebase.
- **Frontend**: A simple HTML/JavaScript interface that interacts with the backend and allows users to sign up, log in, generate captions, and view saved results.
- **Data Storage**: Firebase Firestore for user authentication and saving captioned images.


## 📁 Repository Structure

```
MICG PROJECT/
├── backend/            # FastAPI service, AI pipeline, Firebase integration
├── frontend/           # Static HTML/CSS/JS client
├── README.md           # Quick start and deployment overview
├── DOCUMENTATION_GUIDE.md  # This detailed guide
├── firestore.rules     # Firestore security rules
├── firebase_instructions.md  # Firebase setup notes
└── ...
```

---

## 🛠️ Backend

### Technologies

- Python 3.10+
- FastAPI
- Docker (for deployment on Hugging Face Spaces)
- Firebase Admin SDK
- A custom captioning pipeline (`services/caption_pipeline.py`)

### Setup (Local Development)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (Windows shown):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file using the provided template and include:
   - `FIREBASE_SERVICE_ACCOUNT_KEY` (path or JSON string)
   - `ALLOWED_ORIGINS` (frontend URL for CORS)
5. Place your `serviceAccountKey.json` in the backend root if using a file reference.

6. Start the server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Key Modules

- `main.py`: FastAPI application and routes
- `firebase_admin_setup.py`: Firebase initialization helper
- `services/firestore_service.py`: Firestore helper functions
- `services/caption_pipeline.py`: Image processing and caption generation logic

### Testing Tools

Several test scripts exist in the backend root, such as:
- `test_hf.py` / `test_mistral.py` — calls to external HF inference endpoints
- `test_hf_token.py` — validates HF API tokens
- `test_pipeline_endpoints.py` — local pipeline endpoint tests

---

## 🧩 Frontend

### Technologies

- Vanilla HTML, CSS, and JavaScript (no framework)
- Firebase Web SDK for auth and Firestore

### Setup (Local Development)

Since the frontend is static, you can serve it with any static server. Example using Python:

```bash
cd frontend
python -m http.server 3000
```

Then open http://localhost:3000 in your browser.

### Configuration

Create a `.env` file in the `frontend/` directory and include your Firebase configuration object and the backend URL:

```bash
VITE_BACKEND_URL=https://your-space.hf.space
FIREBASE_API_KEY=...
FIREBASE_AUTH_DOMAIN=...
# etc.
```

### Important Scripts

- `app.js` — core app logic
- `auth.js` — Firebase auth helpers
- `generate.js` — handles image uploads and caption requests
- `saved.js` — fetching and displaying saved caption histories
- `header.js` — UI header and logout button

---

## ☁️ Deployment

### Backend: Hugging Face Spaces (Docker)

1. Create a new **Docker Space** at https://huggingface.co/spaces.
2. Push the contents of the `backend/` directory to the Space repository.
3. In Space **Settings → Secrets**, add:
   - `FIREBASE_SERVICE_ACCOUNT_KEY` (the JSON contents or a path to an uploaded file)
   - `ALLOWED_ORIGINS` set to your frontend URL (e.g. `https://your-frontend.vercel.app`)
4. The Space will build automatically using the provided `Dockerfile`.

### Frontend: Vercel

1. Push the repository to GitHub.
2. Connect the `frontend/` folder to Vercel via `Create a new project → Import Git Repository`.
3. Set the following environment variable in Vercel settings:
   - `VITE_BACKEND_URL` = your backend (HF Space) URL
4. Set build command to `npm run build` and output directory to `dist`.

---

## 🔐 Firebase Configuration

1. Create a new Firebase project.
2. Enable **Authentication → Email/Password**.
3. Enable **Cloud Firestore** and choose appropriate location.
4. Apply the security rules found in `firestore.rules` to restrict access to authenticated users and owners of documents.
5. Download the `serviceAccountKey.json` file for backend usage and copy the `firebaseConfig` object into `frontend/.env`.

> 🔧 _Refer to_ `firebase_instructions.md` for additional guidance and common troubleshooting steps.

---

## 📦 Firestore Schema

- **users/
  └─ {uid}** — user profile info (created on signup)
- **images/
  └─ {docId}** — stored caption records including:
    - `userId` (owner)
    - `imageUrl` or base64 data
    - `caption` text
    - `language` code
    - `mood` label
    - `timestamp`

Access is controlled so users can only read/write their own images.

---

## 📝 Contribution Guidelines

1. Fork the repo and create feature branches.
2. Follow the existing code style (PEP8 for Python, plain JS conventions for frontend).
3. Add tests when applicable, especially for backend endpoints or pipeline logic.
4. Update this documentation with any architectural changes or new configuration steps.

---

## 📚 Additional Resources

- `firebase_instructions.md` — deep dive into Firebase setup.
- `implementation_plan.md` — previously used planning document with ideas and rules (may contain helpful context).
- `firestore.rules` — security rule definitions.

---

## ✅ Quick Checklist

- [ ] Backend `.env` configured with Firebase key & allowed origins.
- [ ] Frontend `.env` configured with Firebase config & backend URL.
- [ ] Firebase project created and Firestore rules applied.
- [ ] Hugging Face Space built and secrets set.
- [ ] Vercel project deployed with environment variables.

---

**Enjoy working with the Mood-Based Multilingual Image Caption Generator!**

Feel free to explore, extend, and ask questions as you go.
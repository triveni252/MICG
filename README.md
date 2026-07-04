# Mood-Based Multilingual Image Caption Generator

## Project Structure
```
backend/   → FastAPI + AI pipeline (deploy to Hugging Face Spaces)
frontend/  → React + Vite (deploy to Vercel)
```

## Backend Setup (Local Dev)

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create `.env` (copy from `.env` template) and add your `serviceAccountKey.json` from Firebase.

```bash
uvicorn main:app --reload --port 8000
```

## Frontend Setup

```bash
cd frontend
# Since this is a static HTML app, you can use any static server.
# For example, using Python:
python -m http.server 3000
# Or using Node's serve: npx serve . -p 3000

# Then open http://localhost:3000 in your browser
```

## Deploy: Backend → Hugging Face Spaces

1. Create a **Docker** Space on [huggingface.co/spaces](https://huggingface.co/spaces)
2. Push the `backend/` folder contents to the Space repo
3. In Space Settings → **Secrets**, add:
   - `FIREBASE_SERVICE_ACCOUNT_KEY` contents (paste JSON as a secret or use a path after uploading)
   - `ALLOWED_ORIGINS` = your Vercel frontend URL
4. HF Spaces will build the Docker image automatically

## Deploy: Frontend → Vercel

1. Push repo to GitHub
2. Connect `frontend/` folder to [vercel.com](https://vercel.com)
3. Set env var: `VITE_BACKEND_URL` = your HF Space URL (e.g. `https://username-micg-api.hf.space`)
4. Build command: `npm run build` | Output: `dist`

## Firebase Setup

1. Create Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
2. Enable **Authentication → Email/Password**
3. Enable **Firestore Database**
4. Apply Firestore security rules from `implementation_plan.md`
5. Download `serviceAccountKey.json` for backend
6. Copy `firebaseConfig` object for frontend `.env`
+

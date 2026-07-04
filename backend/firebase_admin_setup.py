import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Header, HTTPException, status
import os
import json
from dotenv import load_dotenv

load_dotenv()

_initialized = False


def initialize_firebase():
    """Initialize Firebase Admin SDK once. Safe to call multiple times."""
    global _initialized
    if _initialized:
        return

    # First try: load from FIREBASE_CREDENTIALS secret (JSON string in env)
    creds_json = os.getenv("FIREBASE_CREDENTIALS")
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
            _initialized = True
            return
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Firebase from FIREBASE_CREDENTIALS secret: {e}")

    # Second try: load from file path
    key_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "./serviceAccountKey.json")
    if os.path.exists(key_path):
        try:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            _initialized = True
            return
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Firebase from file '{key_path}': {e}")

    raise RuntimeError(
        "Firebase credentials not found. Set FIREBASE_CREDENTIALS secret (JSON string) "
        "or FIREBASE_SERVICE_ACCOUNT_KEY env variable pointing to the key file."
    )


# Initialize on module load
initialize_firebase()


async def verify_token(authorization: str = Header(None)) -> dict:
    """
    FastAPI dependency — extracts and verifies a Firebase ID token from the
    'Authorization: Bearer <token>' header.
    Returns the decoded token dict (includes uid, email, etc.).
    """
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header. Expected: 'Bearer <token>'.",
        )
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        return None
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token has expired. Please sign in again.",
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
        )

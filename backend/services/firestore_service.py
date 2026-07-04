from firebase_admin import firestore
from datetime import datetime, timezone
from typing import Optional

COLLECTION = "captions"


def _get_db():
    """Return Firestore client. Called lazily so Firebase is already initialized."""
    return firestore.client()


def save_caption(
    user_id: str,
    text: str,
    mood: str,
    language: str,
    style: str,
) -> str:
    """Persist a caption to Firestore under the authenticated user. Returns doc ID."""
    db = _get_db()
    doc_ref = db.collection(COLLECTION).document()
    doc_ref.set({
        "userId":    user_id,
        "text":      text.strip(),
        "mood":      mood,
        "language":  language,
        "style":     style,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    })
    return doc_ref.id


def get_captions(user_id: str) -> list:
    """Retrieve all captions for the authenticated user, ordered newest first."""
    db = _get_db()
    results = []
    
    try:
        # Evaluate the stream IMMEDIATELY to catch index errors
        docs = list(
            db.collection(COLLECTION)
            .where("userId", "==", user_id)
            .order_by("createdAt", direction=firestore.Query.DESCENDING)
            .stream()
        )
    except Exception as e:
        # Fallback: fetch without ordering if composite index not yet created
        docs = list(
            db.collection(COLLECTION)
            .where("userId", "==", user_id)
            .stream()
        )

    for doc in docs:
        data = doc.to_dict()
        if data:
            data["id"] = doc.id
            results.append(data)

    # Sort client-side as a safety net (or primary sort if fallback was used)
    results.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    return results


def delete_caption(user_id: str, caption_id: str) -> bool:
    """Delete a caption from Firestore. Only deletes if it belongs to the user."""
    db = _get_db()
    doc_ref = db.collection(COLLECTION).document(caption_id)
    doc = doc_ref.get()
    if not doc.exists:
        return False
    data = doc.to_dict()
    if data.get("userId") != user_id:
        return False
    doc_ref.delete()
    return True

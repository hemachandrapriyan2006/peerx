"""
PeerX Supabase Service
Handles all database operations and auth verification.
"""

from supabase import create_client, Client
from config import settings
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase client
_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """Get or create Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            logger.warning("Supabase credentials not configured. Database operations will fail.")
            raise ValueError("Supabase URL and Anon Key must be set in environment variables.")
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return _supabase_client


def get_authenticated_client(access_token: str) -> Client:
    """Create a Supabase client authenticated with a user's JWT."""
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    client.postgrest.auth(access_token)
    return client


# ── Auth Helpers ───────────────────────────────────────────

def verify_token(access_token: str) -> Optional[dict]:
    """Verify a Supabase JWT and return the user data."""
    try:
        client = get_supabase()
        user = client.auth.get_user(access_token)
        if user and user.user:
            return {"id": user.user.id, "email": user.user.email}
        return None
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None


# ── Profile Operations ─────────────────────────────────────

def get_profile(user_id: str, access_token: str) -> Optional[dict]:
    """Get user profile by ID."""
    try:
        client = get_authenticated_client(access_token)
        result = client.table("profiles").select("*").eq("id", user_id).single().execute()
        return result.data
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        return None


def update_profile(user_id: str, data: dict, access_token: str) -> Optional[dict]:
    """Update user profile."""
    try:
        client = get_authenticated_client(access_token)
        data["updated_at"] = "now()"
        result = client.table("profiles").update(data).eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return None


# ── Session Operations ─────────────────────────────────────

_in_memory_sessions = {}


def create_session(user_id: str, data: dict, access_token: str) -> Optional[dict]:
    """Create a new learning session."""
    topic = data.get("topic") or "General Topic"
    subject = data.get("subject", "General")
    goal = data.get("goal") or f"Understand {topic}"
    difficulty = data.get("difficulty", 2)

    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        logger.warning("Supabase credentials not configured. Returning mock session.")
        import uuid
        mock_id = f"session-{uuid.uuid4().hex[:8]}"
        session_obj = {
            "id": mock_id,
            "user_id": user_id,
            "topic": topic,
            "subject": subject,
            "goal": goal,
            "difficulty": difficulty,
            "status": "active",
            "created_at": "now()"
        }
        _in_memory_sessions[mock_id] = session_obj
        return session_obj
    try:
        client = get_authenticated_client(access_token)
        data["user_id"] = user_id
        result = client.table("learning_sessions").insert(data).execute()
        if result.data:
            session_obj = result.data[0]
            _in_memory_sessions[session_obj["id"]] = session_obj
            return session_obj
        return None
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        import uuid
        mock_id = f"session-{uuid.uuid4().hex[:8]}"
        session_obj = {
            "id": mock_id,
            "user_id": user_id,
            "topic": topic,
            "subject": subject,
            "difficulty": difficulty,
            "status": "active"
        }
        _in_memory_sessions[mock_id] = session_obj
        return session_obj


def get_session(session_id: str, access_token: str) -> Optional[dict]:
    """Get session by ID."""
    if session_id in _in_memory_sessions:
        return _in_memory_sessions[session_id]

    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        mock_obj = {
            "id": session_id,
            "topic": "General Topic",
            "subject": "General",
            "difficulty": 2,
            "status": "active"
        }
        _in_memory_sessions[session_id] = mock_obj
        return mock_obj
    try:
        client = get_authenticated_client(access_token)
        result = client.table("learning_sessions").select("*").eq("id", session_id).single().execute()
        if result.data:
            _in_memory_sessions[session_id] = result.data
            return result.data
    except Exception as e:
        logger.error(f"Error fetching session: {e}")

    fallback_obj = _in_memory_sessions.get(session_id, {
        "id": session_id,
        "topic": "General Topic",
        "subject": "General",
        "difficulty": 2,
        "status": "active"
    })
    _in_memory_sessions[session_id] = fallback_obj
    return fallback_obj



def update_session(session_id: str, data: dict, access_token: str) -> Optional[dict]:
    """Update a learning session."""
    if session_id in _in_memory_sessions:
        _in_memory_sessions[session_id].update(data)

    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        return {"id": session_id, **data}
    try:
        client = get_authenticated_client(access_token)
        result = client.table("learning_sessions").update(data).eq("id", session_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        return {"id": session_id, **data}
    try:
        client = get_authenticated_client(access_token)
        result = client.table("learning_sessions").update(data).eq("id", session_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        return {"id": session_id, **data}


def get_user_sessions(user_id: str, access_token: str, limit: int = 10) -> List[dict]:
    """Get recent sessions for a user."""
    try:
        client = get_authenticated_client(access_token)
        result = (client.table("learning_sessions")
                  .select("*")
                  .eq("user_id", user_id)
                  .order("started_at", desc=True)
                  .limit(limit)
                  .execute())
        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        return []


# ── Attempt Operations ─────────────────────────────────────

def create_attempt(data: dict, access_token: str) -> Optional[dict]:
    """Record a learning attempt."""
    try:
        client = get_authenticated_client(access_token)
        result = client.table("learning_attempts").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating attempt: {e}")
        return None


def get_session_attempts(session_id: str, access_token: str) -> List[dict]:
    """Get all attempts for a session."""
    try:
        client = get_authenticated_client(access_token)
        result = (client.table("learning_attempts")
                  .select("*")
                  .eq("session_id", session_id)
                  .order("created_at", desc=True)
                  .execute())
        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching attempts: {e}")
        return []


def get_user_attempts(user_id: str, access_token: str, limit: int = 50) -> List[dict]:
    """Get recent attempts for a user."""
    try:
        client = get_authenticated_client(access_token)
        result = (client.table("learning_attempts")
                  .select("*")
                  .eq("user_id", user_id)
                  .order("created_at", desc=True)
                  .limit(limit)
                  .execute())
        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching user attempts: {e}")
        return []


# ── Knowledge Gap Operations ──────────────────────────────

def create_knowledge_gap(data: dict, access_token: str) -> Optional[dict]:
    """Record a knowledge gap."""
    try:
        client = get_authenticated_client(access_token)
        result = client.table("knowledge_gaps").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating knowledge gap: {e}")
        return None


def get_user_knowledge_gaps(user_id: str, access_token: str, status: str = None) -> List[dict]:
    """Get knowledge gaps for a user."""
    try:
        client = get_authenticated_client(access_token)
        query = client.table("knowledge_gaps").select("*").eq("user_id", user_id)
        if status:
            query = query.eq("status", status)
        result = query.order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching knowledge gaps: {e}")
        return []


def update_knowledge_gap(gap_id: str, data: dict, access_token: str) -> Optional[dict]:
    """Update a knowledge gap status."""
    try:
        client = get_authenticated_client(access_token)
        data["updated_at"] = "now()"
        result = client.table("knowledge_gaps").update(data).eq("id", gap_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error updating knowledge gap: {e}")
        return None


# ── Progress Operations ────────────────────────────────────

def get_or_create_progress(user_id: str, topic: str, access_token: str) -> Optional[dict]:
    """Get or create a progress record for a user+topic."""
    try:
        client = get_authenticated_client(access_token)
        result = (client.table("learning_progress")
                  .select("*")
                  .eq("user_id", user_id)
                  .eq("topic", topic)
                  .execute())
        if result.data:
            return result.data[0]
        # Create new progress record
        new_progress = {
            "user_id": user_id,
            "topic": topic,
            "questions_attempted": 0,
            "questions_correct": 0,
            "accuracy": 0.0,
            "mastery_score": 0.0,
            "current_difficulty": 1
        }
        insert_result = client.table("learning_progress").insert(new_progress).execute()
        return insert_result.data[0] if insert_result.data else None
    except Exception as e:
        logger.error(f"Error with progress: {e}")
        return None


def update_progress(progress_id: str, data: dict, access_token: str) -> Optional[dict]:
    """Update a progress record."""
    try:
        client = get_authenticated_client(access_token)
        data["last_activity"] = "now()"
        result = client.table("learning_progress").update(data).eq("id", progress_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        return None


def get_user_progress(user_id: str, access_token: str) -> List[dict]:
    """Get all progress records for a user."""
    try:
        client = get_authenticated_client(access_token)
        result = (client.table("learning_progress")
                  .select("*")
                  .eq("user_id", user_id)
                  .order("last_activity", desc=True)
                  .execute())
        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching progress: {e}")
        return []


# ── AI Interaction Operations ──────────────────────────────

def log_ai_interaction(data: dict, access_token: str) -> Optional[dict]:
    """Log an AI agent interaction."""
    try:
        client = get_authenticated_client(access_token)
        result = client.table("ai_interactions").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error logging AI interaction: {e}")
        return None


def get_session_interactions(session_id: str, access_token: str) -> List[dict]:
    """Get all AI interactions for a session."""
    try:
        client = get_authenticated_client(access_token)
        result = (client.table("ai_interactions")
                  .select("*")
                  .eq("session_id", session_id)
                  .order("created_at", desc=False)
                  .execute())
        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching interactions: {e}")
        return []


# ── Challenge Operations ───────────────────────────────────

def create_challenge(data: dict, access_token: str) -> Optional[dict]:
    """Create a new challenge."""
    try:
        client = get_authenticated_client(access_token)
        result = client.table("challenges").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating challenge: {e}")
        return None


def get_user_challenges(user_id: str, access_token: str, completed: bool = None) -> List[dict]:
    """Get challenges for a user."""
    try:
        client = get_authenticated_client(access_token)
        query = client.table("challenges").select("*").eq("user_id", user_id)
        if completed is not None:
            query = query.eq("completed", completed)
        result = query.order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching challenges: {e}")
        return []

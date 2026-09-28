"""
PeerX Progress API Routes
Handles progress history and topic-wise analytics.
"""

from fastapi import APIRouter, HTTPException, Header
from services import supabase_service as db
from api.auth import get_current_user
from typing import Optional

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("")
async def get_progress(authorization: Optional[str] = Header(None)):
    """Get all learning progress for the current user."""
    user = await get_current_user(authorization)
    progress = db.get_user_progress(user["id"], user["access_token"])

    return {
        "success": True,
        "data": progress
    }


@router.get("/history")
async def get_progress_history(authorization: Optional[str] = Header(None)):
    """Get learning attempt history for charts."""
    user = await get_current_user(authorization)
    attempts = db.get_user_attempts(user["id"], user["access_token"], limit=50)

    # Format for charting: list of {date, score, topic}
    history = []
    for attempt in reversed(attempts):  # Chronological order
        history.append({
            "date": attempt.get("created_at", ""),
            "score": attempt.get("score", 0),
            "correctness": attempt.get("correctness", ""),
            "reasoning_quality": attempt.get("reasoning_quality", "")
        })

    return {
        "success": True,
        "data": history
    }


@router.get("/topics")
async def get_topic_progress(authorization: Optional[str] = Header(None)):
    """Get topic-wise mastery breakdown."""
    user = await get_current_user(authorization)
    progress = db.get_user_progress(user["id"], user["access_token"])

    topics = []
    for p in progress:
        if p.get("questions_attempted", 0) > 0:
            topics.append({
                "topic": p.get("topic", ""),
                "mastery_score": p.get("mastery_score", 0),
                "accuracy": p.get("accuracy", 0),
                "questions_attempted": p.get("questions_attempted", 0),
                "questions_correct": p.get("questions_correct", 0),
                "current_difficulty": p.get("current_difficulty", 1)
            })

    return {
        "success": True,
        "data": topics
    }

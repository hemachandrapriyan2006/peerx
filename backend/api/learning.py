"""
PeerX Learning API Routes
Handles dashboard, recommendations, and knowledge gaps.
"""

from fastapi import APIRouter, HTTPException, Header
from services import supabase_service as db
from services.orchestrator import orchestrator
from services.learning_analyzer import (
    calculate_mastery_score, get_weak_concepts,
    get_strongest_topic, get_weakest_topic, calculate_accuracy
)
from api.auth import get_current_user
from typing import Optional

router = APIRouter(prefix="/api", tags=["learning"])


@router.get("/dashboard")
async def get_dashboard(authorization: Optional[str] = Header(None)):
    """Get aggregated dashboard data for the current user."""
    user = await get_current_user(authorization)
    user_id = user["id"]
    token = user["access_token"]

    # Fetch all data
    progress = db.get_user_progress(user_id, token)
    sessions = db.get_user_sessions(user_id, token, limit=5)
    gaps = db.get_user_knowledge_gaps(user_id, token, status="active")
    attempts = db.get_user_attempts(user_id, token, limit=50)

    # Calculate aggregates
    total_questions = sum(p.get("questions_attempted", 0) for p in progress)
    total_correct = sum(p.get("questions_correct", 0) for p in progress)
    overall_accuracy = calculate_accuracy(total_correct, total_questions)

    # Overall mastery (average across topics)
    mastery_scores = [p.get("mastery_score", 0) for p in progress if p.get("questions_attempted", 0) > 0]
    overall_mastery = round(sum(mastery_scores) / len(mastery_scores), 1) if mastery_scores else 0.0

    topics_studied = list(set(p.get("topic", "") for p in progress if p.get("questions_attempted", 0) > 0))
    weak_concepts = get_weak_concepts(gaps)

    # Recommendations
    try:
        recommendation = orchestrator.get_recommendations(user_id, token)
    except Exception:
        recommendation = None

    return {
        "success": True,
        "data": {
            "overall_mastery": overall_mastery,
            "total_sessions": len(sessions),
            "total_questions": total_questions,
            "total_correct": total_correct,
            "overall_accuracy": overall_accuracy,
            "topics_studied": topics_studied,
            "weak_concepts": weak_concepts[:5],
            "recent_sessions": sessions[:5],
            "recommended_challenge": recommendation,
            "knowledge_gaps": [
                {
                    "id": g.get("id"),
                    "topic": g.get("topic", ""),
                    "concept": g.get("concept", ""),
                    "severity": g.get("severity", "medium"),
                    "status": g.get("status", "active"),
                    "created_at": g.get("created_at")
                } for g in gaps[:10]
            ]
        }
    }


@router.get("/knowledge-gaps")
async def get_knowledge_gaps(authorization: Optional[str] = Header(None)):
    """Get all knowledge gaps for the current user."""
    user = await get_current_user(authorization)
    gaps = db.get_user_knowledge_gaps(user["id"], user["access_token"])

    return {
        "success": True,
        "data": gaps
    }


@router.get("/recommendations")
async def get_recommendations(authorization: Optional[str] = Header(None)):
    """Get personalized learning recommendations."""
    user = await get_current_user(authorization)

    try:
        result = orchestrator.get_recommendations(user["id"], user["access_token"])
        return {"success": True, "data": result}
    except Exception as e:
        return {
            "success": True,
            "data": {
                "message": "Start a learning session to get personalized recommendations!",
                "recommended_topic": "Java OOP",
                "recommended_difficulty": 1
            }
        }

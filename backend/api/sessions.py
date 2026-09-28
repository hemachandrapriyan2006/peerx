"""
PeerX Sessions API Routes
Handles learning sessions, mentor, challenger, answer submission, and challenges.
"""

from fastapi import APIRouter, HTTPException, Header
from models.schemas import (
    SessionCreate, AnswerSubmit
)
from services.orchestrator import orchestrator
from services import supabase_service as db
from api.auth import get_current_user
from typing import Optional

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("")
@router.post("/start")
async def create_session(data: SessionCreate, authorization: Optional[str] = Header(None)):
    """
    Create a new learning session.
    Returns session + mentor explanation + challenger question.
    """
    if not data.topic or not data.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required to start a learning session.")

    user = await get_current_user(authorization)

    print(f"Received topic: {data.topic}", flush=True)
    logger.info(f"Received topic: {data.topic}")

    try:
        result = orchestrator.start_session(
            user_id=user["id"],
            topic=data.topic.strip(),
            subject=data.subject,
            goal=data.goal,
            difficulty=data.difficulty or 1,
            access_token=user["access_token"]
        )
        session_id = result.get("session", {}).get("id", "unknown")
        result["current_stage"] = 1

        print(f"Created session: {session_id}", flush=True)
        logger.info(f"Created session: {session_id}")
        print(f"Initial stage: 1", flush=True)
        logger.info(f"Initial stage: 1")

        return {"success": True, "data": result, "session_id": session_id, "topic": data.topic.strip(), "current_stage": 1}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@router.get("/{session_id}")
async def get_session(session_id: str, authorization: Optional[str] = Header(None)):
    """Get session details with interaction history."""
    user = await get_current_user(authorization)

    session = db.get_session(session_id, user["access_token"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get interactions for this session
    interactions = db.get_session_interactions(session_id, user["access_token"])
    attempts = db.get_session_attempts(session_id, user["access_token"])

    return {
        "success": True,
        "data": {
            "session": session,
            "interactions": interactions,
            "attempts": attempts
        }
    }


@router.post("/{session_id}/mentor")
async def get_mentor_response(session_id: str, authorization: Optional[str] = Header(None)):
    """Get a mentor explanation for the current session topic."""
    user = await get_current_user(authorization)

    session = db.get_session(session_id, user["access_token"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    from agents.mentor import mentor_agent

    # Get existing gaps
    gaps = db.get_user_knowledge_gaps(user["id"], user["access_token"], status="active")
    gap_concepts = [g["concept"] for g in gaps if g.get("topic", "").lower() == session["topic"].lower()]

    result = mentor_agent.explain(
        topic=session["topic"],
        subject=session["subject"],
        difficulty=session["difficulty"],
        knowledge_gaps=gap_concepts
    )

    db.log_ai_interaction({
        "session_id": session_id,
        "agent_type": "mentor",
        "input_context": f"Re-explain {session['topic']}",
        "output": result.get("explanation", "")
    }, user["access_token"])

    return {"success": True, "data": result}


@router.post("/{session_id}/challenge")
async def get_challenger_question(session_id: str, authorization: Optional[str] = Header(None)):
    """Get a challenger question for the current session."""
    user = await get_current_user(authorization)

    session = db.get_session(session_id, user["access_token"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    from agents.challenger import challenger_agent

    result = challenger_agent.challenge(
        topic=session["topic"],
        subject=session["subject"],
        difficulty=session["difficulty"]
    )

    db.log_ai_interaction({
        "session_id": session_id,
        "agent_type": "challenger",
        "input_context": f"Challenge question for {session['topic']}",
        "output": result.get("question", "")
    }, user["access_token"])

    return {"success": True, "data": result}


@router.post("/{session_id}/answer")
async def submit_answer(session_id: str, data: AnswerSubmit,
                        authorization: Optional[str] = Header(None)):
    """
    Submit a student's answer.
    Triggers the full review pipeline:
    Reviewer → Knowledge Gaps → Progress Update → Difficulty Adjustment → Next Challenge
    """
    user = await get_current_user(authorization)

    session = db.get_session(session_id, user["access_token"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Determine the question being answered
    question = data.question
    if not question:
        # Use the last challenger question or challenge
        interactions = db.get_session_interactions(session_id, user["access_token"])
        for interaction in reversed(interactions):
            if interaction.get("agent_type") in ("challenger", "problem_solver"):
                question = interaction.get("output", "")
                break

    if not question:
        question = f"Explain {session['topic']}"

    try:
        result = orchestrator.process_answer(
            session_id=session_id,
            user_id=user["id"],
            question=question,
            student_answer=data.answer,
            access_token=user["access_token"]
        )
        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process answer: {str(e)}")


@router.post("/{session_id}/creative")
async def get_creative_perspective(session_id: str, authorization: Optional[str] = Header(None)):
    """Get a creative alternative perspective for the session topic."""
    user = await get_current_user(authorization)

    try:
        result = orchestrator.get_creative_perspective(session_id, user["access_token"])
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/next-challenge")
async def generate_next_challenge(session_id: str, authorization: Optional[str] = Header(None)):
    """Generate a new challenge based on current progress and gaps."""
    user = await get_current_user(authorization)

    session = db.get_session(session_id, user["access_token"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    from agents.problem_solver import problem_solver_agent

    # Get gaps and scores
    gaps = db.get_user_knowledge_gaps(user["id"], user["access_token"], status="active")
    gap_concepts = [g["concept"] for g in gaps if g.get("topic", "").lower() == session["topic"].lower()]

    attempts = db.get_session_attempts(session_id, user["access_token"])
    scores = [a["score"] for a in attempts if a.get("score") is not None]

    result = problem_solver_agent.generate_challenge(
        topic=session["topic"],
        subject=session["subject"],
        difficulty=session["difficulty"],
        knowledge_gaps=gap_concepts,
        previous_scores=scores[-5:]
    )

    # Save challenge
    db.create_challenge({
        "session_id": session_id,
        "user_id": user["id"],
        "topic": session["topic"],
        "concept": result.get("concept", session["topic"]),
        "difficulty": session["difficulty"],
        "question": result.get("question", ""),
        "expected_skill": result.get("expected_skill", ""),
        "completed": False
    }, user["access_token"])

    db.log_ai_interaction({
        "session_id": session_id,
        "agent_type": "problem_solver",
        "input_context": f"Next challenge for {session['topic']}",
        "output": result.get("question", "")
    }, user["access_token"])

    return {"success": True, "data": result}


@router.post("/{session_id}/complete")
async def complete_session(session_id: str, authorization: Optional[str] = Header(None)):
    """Mark a session as completed."""
    user = await get_current_user(authorization)

    result = db.update_session(session_id, {
        "status": "completed",
        "completed_at": "now()"
    }, user["access_token"])

    if not result:
        raise HTTPException(status_code=500, detail="Failed to complete session")
    return {"success": True, "data": result}


@router.post("/{session_id}/agent/{agent_type}")
async def get_agent_response(session_id: str, agent_type: str, data: dict = None, authorization: Optional[str] = Header(None)):
    """Get a response from a specific agent for the session."""
    user = await get_current_user(authorization)
    session = db.get_session(session_id, user["access_token"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    topic = session["topic"]
    subject = session.get("subject", "General")
    difficulty = session.get("difficulty", 2)

    if agent_type == "mentor":
        from agents.mentor import mentor_agent
        result = mentor_agent.explain(topic=topic, subject=subject, difficulty=difficulty)
        return {"success": True, "data": {"message": result.get("explanation", ""), **result}}
    elif agent_type == "creative":
        from agents.creative import creative_agent
        result = creative_agent.create_perspective(topic=topic, subject=subject, difficulty=difficulty)
        return {"success": True, "data": {"message": result.get("perspective", ""), **result}}
    elif agent_type == "challenger":
        from agents.challenger import challenger_agent
        result = challenger_agent.challenge(topic=topic, subject=subject, difficulty=difficulty)
        return {"success": True, "data": {"message": result.get("question", ""), **result}}
    else:
        return {"success": True, "data": {"message": f"Agent {agent_type} received your query regarding {topic}."}}


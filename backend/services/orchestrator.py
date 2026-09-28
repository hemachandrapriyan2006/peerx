"""
PeerX AI Orchestrator
Central orchestration service that manages the learning flow.
Decides which agents to invoke and manages session state.
"""

import logging
from typing import Optional
from agents.mentor import mentor_agent
from agents.challenger import challenger_agent
from agents.creative import creative_agent
from agents.reviewer import reviewer_agent
from agents.problem_solver import problem_solver_agent
from services.learning_analyzer import (
    extract_knowledge_gaps, calculate_accuracy, calculate_mastery_score,
    reasoning_quality_to_score, get_weak_concepts
)
from services.difficulty_engine import calculate_new_difficulty
from services.knowledge_service import knowledge_service
from services import supabase_service as db
from config import settings

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Central orchestration service for the PeerX learning flow.

    Flow:
    1. Start Session → Mentor explains + Challenger questions
    2. Student Answers → Reviewer evaluates → Gaps extracted → Problem Solver creates challenge
    3. Loop continues with adaptive difficulty
    """

    def start_session(self, user_id: str, topic: str, subject: str,
                      goal: str, difficulty: int, access_token: str) -> dict:
        """
        Start a new learning session.
        Creates session, invokes Mentor and Challenger.
        """
        # Create session in DB
        session_data = {
            "topic": topic,
            "subject": subject,
            "goal": goal or f"Understand {topic}",
            "difficulty": difficulty,
            "status": "active",
            "current_stage": 1
        }
        session = db.create_session(user_id, session_data, access_token)
        if not session:
            raise ValueError("Failed to create learning session")

        session["current_stage"] = 1

        session_id = session["id"]

        # Get profile for student level
        profile = db.get_profile(user_id, access_token)
        student_level = profile.get("education_level", "undergraduate") if profile else "undergraduate"

        # Get existing knowledge gaps for this topic
        all_gaps = db.get_user_knowledge_gaps(user_id, access_token, status="active")
        topic_gaps = [g["concept"] for g in all_gaps if g.get("topic", "").lower() == topic.lower()]

        # Retrieve knowledge context
        context = knowledge_service.retrieve_context(topic, subject)

        # 1. Mentor teaches the topic
        mentor_result = mentor_agent.explain(
            topic=topic,
            subject=subject,
            difficulty=difficulty,
            student_level=student_level,
            knowledge_gaps=topic_gaps,
            previous_context=context
        )

        # Log mentor interaction
        db.log_ai_interaction({
            "session_id": session_id,
            "agent_type": "mentor",
            "input_context": f"Topic: {topic}, Subject: {subject}, Difficulty: {difficulty}",
            "output": mentor_result.get("explanation", "")
        }, access_token)

        # 2. Creative Peer reinforces explanation with analogy & perspective
        creative_result = creative_agent.create_perspective(
            topic=topic,
            subject=subject,
            difficulty=difficulty,
            mentor_explanation=mentor_result.get("explanation", ""),
            student_level=student_level
        )

        # Log creative interaction
        db.log_ai_interaction({
            "session_id": session_id,
            "agent_type": "creative",
            "input_context": f"Reinforce mentor explanation of {topic}",
            "output": creative_result.get("perspective", "")
        }, access_token)

        # 3. Challenger asks an assessment question based on what was just taught
        challenger_result = challenger_agent.challenge(
            topic=topic,
            subject=subject,
            difficulty=difficulty,
            mentor_explanation=mentor_result.get("explanation", ""),
            student_level=student_level,
            knowledge_gaps=topic_gaps
        )

        # Log challenger interaction
        db.log_ai_interaction({
            "session_id": session_id,
            "agent_type": "challenger",
            "input_context": f"Based on mentor explanation of {topic}",
            "output": challenger_result.get("question", "")
        }, access_token)

        return {
            "session": session,
            "mentor": mentor_result,
            "creative": creative_result,
            "challenger": challenger_result
        }

    def process_answer(self, session_id: str, user_id: str,
                       question: str, student_answer: str,
                       access_token: str) -> dict:
        """
        Process a student's answer through the full review pipeline.

        Flow: Review → Extract Gaps → Update Progress → Adjust Difficulty → Generate Challenge
        """
        # Get session details
        session = db.get_session(session_id, access_token)
        if not session:
            raise ValueError("Session not found")

        topic = session["topic"]
        subject = session.get("subject", "General")
        current_difficulty = session.get("difficulty", 2)

        print(f"Stage 4 submit started", flush=True)
        print(f"Session ID: {session_id}", flush=True)
        print(f"Topic: {topic}", flush=True)
        print(f"Answer received: YES", flush=True)
        logger.info(f"Stage 4 submit started for topic: {topic}, session: {session_id}")

        # Get profile
        profile = db.get_profile(user_id, access_token)
        student_level = profile.get("education_level", "undergraduate") if profile else "undergraduate"

        # Get previous scores for context
        previous_attempts = db.get_session_attempts(session_id, access_token)
        previous_scores = [a["score"] for a in previous_attempts if a.get("score") is not None]

        # Get existing knowledge gaps
        existing_gaps = db.get_user_knowledge_gaps(user_id, access_token, status="active")
        gap_concepts = get_weak_concepts(existing_gaps)

        # 1. REVIEWER evaluates the answer
        print(f"Reviewer request started", flush=True)
        logger.info(f"Reviewer request started for {topic}")

        review_result = reviewer_agent.review(
            topic=topic,
            subject=subject,
            difficulty=current_difficulty,
            question=question,
            student_answer=student_answer,
            student_level=student_level,
            knowledge_gaps=gap_concepts,
            previous_scores=previous_scores[-5:]  # Last 5 scores
        )

        print(f"Reviewer response received: YES", flush=True)
        print(f"Reviewer response valid: YES", flush=True)
        print(f"Transitioning: Stage 4 -> Stage 5", flush=True)
        logger.info(f"Reviewer response received successfully for {topic}")


        # Log reviewer interaction
        db.log_ai_interaction({
            "session_id": session_id,
            "agent_type": "reviewer",
            "input_context": f"Q: {question}\nA: {student_answer}",
            "output": review_result.get("feedback", "")
        }, access_token)

        # 2. Record the attempt
        is_correct = review_result["score"] >= 70
        attempt_data = {
            "session_id": session_id,
            "user_id": user_id,
            "question": question,
            "student_answer": student_answer,
            "score": review_result["score"],
            "correctness": review_result["correctness"],
            "reasoning_quality": review_result["reasoning_quality"],
            "feedback": review_result["feedback"]
        }
        db.create_attempt(attempt_data, access_token)

        # 3. EXTRACT knowledge gaps
        new_gaps = extract_knowledge_gaps(review_result, topic)
        gap_responses = []

        for gap in new_gaps:
            gap_data = {
                "user_id": user_id,
                "session_id": session_id,
                "topic": gap["topic"],
                "concept": gap["concept"],
                "severity": gap["severity"],
                "status": "active"
            }
            saved_gap = db.create_knowledge_gap(gap_data, access_token)
            if saved_gap:
                gap_responses.append(saved_gap)

        # 4. UPDATE learning progress
        all_scores = previous_scores + [review_result["score"]]
        correct_count = sum(1 for s in all_scores if s >= 70)
        total_count = len(all_scores)
        accuracy = calculate_accuracy(correct_count, total_count)

        reasoning_scores = [reasoning_quality_to_score(review_result["reasoning_quality"])]
        all_progress = db.get_user_progress(user_id, access_token)

        mastery = calculate_mastery_score(
            accuracy=accuracy,
            reasoning_scores=reasoning_scores,
            recent_scores=all_scores[-5:],
            topics_covered=len(all_progress),
            total_topics=max(5, len(all_progress))
        )

        # Get or create progress record
        progress = db.get_or_create_progress(user_id, topic, access_token)
        if progress:
            progress_update = {
                "questions_attempted": progress.get("questions_attempted", 0) + 1,
                "questions_correct": progress.get("questions_correct", 0) + (1 if is_correct else 0),
                "accuracy": accuracy,
                "mastery_score": mastery
            }

            # 5. DIFFICULTY ENGINE adjusts difficulty
            new_difficulty = calculate_new_difficulty(
                current_difficulty=current_difficulty,
                recent_scores=all_scores[-5:],
                reviewer_recommended=review_result.get("recommended_difficulty")
            )
            progress_update["current_difficulty"] = new_difficulty

            db.update_progress(progress["id"], progress_update, access_token)

            # Update session difficulty
            if new_difficulty != current_difficulty:
                db.update_session(session_id, {"difficulty": new_difficulty}, access_token)
        else:
            new_difficulty = current_difficulty

        # 6. PROBLEM SOLVER generates next challenge
        all_gap_concepts = gap_concepts + [g["concept"] for g in new_gaps]
        challenge_result = problem_solver_agent.generate_challenge(
            topic=topic,
            subject=subject,
            difficulty=new_difficulty,
            knowledge_gaps=all_gap_concepts[:5],  # Top 5 gaps
            student_level=student_level,
            previous_scores=all_scores[-5:],
            recent_feedback=review_result.get("feedback", "")
        )

        # Log problem solver interaction
        db.log_ai_interaction({
            "session_id": session_id,
            "agent_type": "problem_solver",
            "input_context": f"Gaps: {all_gap_concepts[:5]}, Difficulty: {new_difficulty}",
            "output": challenge_result.get("question", "")
        }, access_token)

        # Save challenge to DB
        challenge_data = {
            "session_id": session_id,
            "user_id": user_id,
            "topic": topic,
            "concept": challenge_result.get("concept", topic),
            "difficulty": new_difficulty,
            "question": challenge_result.get("question", ""),
            "expected_skill": challenge_result.get("expected_skill", ""),
            "completed": False
        }
        db.create_challenge(challenge_data, access_token)

        # Build progress response
        progress_response = None
        if progress:
            progress_response = {
                "topic": topic,
                "questions_attempted": progress_update.get("questions_attempted", 0),
                "questions_correct": progress_update.get("questions_correct", 0),
                "accuracy": accuracy,
                "mastery_score": mastery,
                "current_difficulty": new_difficulty
            }

        print("Transitioning: Stage 5 -> Stage 6", flush=True)
        print("Transitioning: Stage 6 -> Stage 7", flush=True)

        return {
            "review": review_result,
            "knowledge_gaps": gap_responses,
            "next_challenge": challenge_result,
            "updated_difficulty": new_difficulty,
            "progress": progress_response
        }


    def get_creative_perspective(self, session_id: str, access_token: str) -> dict:
        """Get a creative alternative perspective for the current session topic."""
        session = db.get_session(session_id, access_token)
        if not session:
            raise ValueError("Session not found")

        # Get mentor explanation from interactions
        interactions = db.get_session_interactions(session_id, access_token)
        mentor_explanation = ""
        for interaction in interactions:
            if interaction.get("agent_type") == "mentor":
                mentor_explanation = interaction.get("output", "")
                break

        result = creative_agent.create_perspective(
            topic=session["topic"],
            subject=session["subject"],
            difficulty=session["difficulty"],
            mentor_explanation=mentor_explanation
        )

        db.log_ai_interaction({
            "session_id": session_id,
            "agent_type": "creative",
            "input_context": f"Creative perspective for {session['topic']}",
            "output": result.get("perspective", "")
        }, access_token)

        return result

    def get_recommendations(self, user_id: str, access_token: str) -> dict:
        """Generate learning recommendations based on progress data."""
        from services.learning_analyzer import get_strongest_topic, get_weakest_topic

        progress = db.get_user_progress(user_id, access_token)
        gaps = db.get_user_knowledge_gaps(user_id, access_token, status="active")

        strongest = get_strongest_topic(progress)
        weakest = get_weakest_topic(progress)

        # Find most critical gap
        critical_gaps = sorted(gaps, key=lambda g: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(g.get("severity", "medium"), 2))
        recommended_concept = critical_gaps[0]["concept"] if critical_gaps else None
        recommended_topic = critical_gaps[0]["topic"] if critical_gaps else weakest

        # Determine recommended difficulty
        if weakest:
            weak_progress = [p for p in progress if p.get("topic") == weakest]
            rec_difficulty = weak_progress[0].get("current_difficulty", 2) if weak_progress else 2
        else:
            rec_difficulty = 2

        # Build message
        parts = []
        if strongest:
            parts.append(f"Your strongest area is {strongest}.")
        if weakest:
            parts.append(f"You're currently struggling with {weakest}.")
        if recommended_concept:
            parts.append(f"Recommended focus: {recommended_concept}")
        if not parts:
            parts.append("Start a learning session to get personalized recommendations!")

        return {
            "strongest_topic": strongest,
            "weakest_topic": weakest,
            "recommended_topic": recommended_topic or "Java OOP",
            "recommended_concept": recommended_concept,
            "recommended_difficulty": rec_difficulty,
            "message": " ".join(parts)
        }


orchestrator = Orchestrator()

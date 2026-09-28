"""
Reviewer Agent
Evaluates student answers with structured scoring.
"""

import logging
from services.ai_service import generate_json
from prompts.reviewer_prompt import get_reviewer_prompt

logger = logging.getLogger(__name__)


class ReviewerAgent:
    """The Reviewer AI evaluates student answers."""

    def review(self, topic: str, subject: str, difficulty: int,
               question: str, student_answer: str,
               student_level: str = "undergraduate",
               knowledge_gaps: list = None,
               previous_scores: list = None) -> dict:
        """
        Evaluate a student's answer.

        Returns dict with: score, correctness, reasoning_quality,
                          strengths, weaknesses, knowledge_gaps, feedback
        """
        system_prompt = get_reviewer_prompt(
            topic=topic,
            subject=subject,
            difficulty=difficulty,
            question=question,
            student_answer=student_answer,
            student_level=student_level,
            knowledge_gaps=knowledge_gaps,
            previous_scores=previous_scores
        )

        user_prompt = f"Evaluate this student answer about '{topic}':\n\nQuestion: {question}\n\nStudent's Answer: {student_answer}"

        result = generate_json(system_prompt, user_prompt)

        # Validate and normalize the result
        score = result.get("score", 50)
        if isinstance(score, str):
            try:
                score = int(score)
            except ValueError:
                score = 50
        score = max(0, min(100, score))

        correctness = result.get("correctness", "partially_correct")
        valid_correctness = ["correct", "mostly_correct", "partially_correct", "incorrect"]
        if correctness not in valid_correctness:
            correctness = "partially_correct"

        reasoning = result.get("reasoning_quality", "fair")
        valid_reasoning = ["excellent", "good", "fair", "poor"]
        if reasoning not in valid_reasoning:
            reasoning = "fair"

        rec_diff = result.get("recommended_difficulty", difficulty)
        if isinstance(rec_diff, str):
            try:
                rec_diff = int(rec_diff)
            except ValueError:
                rec_diff = difficulty
        rec_diff = max(1, min(5, rec_diff))

        return {
            "agent": "reviewer",
            "score": score,
            "correctness": correctness,
            "reasoning_quality": reasoning,
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "knowledge_gaps": result.get("knowledge_gaps", []),
            "feedback": result.get("feedback", "Review completed."),
            "recommended_difficulty": rec_diff
        }


reviewer_agent = ReviewerAgent()

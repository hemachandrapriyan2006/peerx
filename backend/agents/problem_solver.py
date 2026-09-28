"""
Problem Solver Agent
Generates personalized challenges based on student performance.
"""

import logging
from services.ai_service import generate_json
from prompts.problem_solver_prompt import get_problem_solver_prompt

logger = logging.getLogger(__name__)


class ProblemSolverAgent:
    """The Problem Solver AI creates personalized learning challenges."""

    def generate_challenge(self, topic: str, subject: str, difficulty: int,
                           knowledge_gaps: list = None,
                           student_level: str = "undergraduate",
                           previous_scores: list = None,
                           recent_feedback: str = "") -> dict:
        """
        Generate a personalized challenge targeting knowledge gaps.

        Returns dict with: question, difficulty, concept, expected_skill, hint
        """
        system_prompt = get_problem_solver_prompt(
            topic=topic,
            subject=subject,
            difficulty=difficulty,
            knowledge_gaps=knowledge_gaps,
            student_level=student_level,
            previous_scores=previous_scores,
            recent_feedback=recent_feedback
        )

        user_prompt = f"Generate a {difficulty}/5 difficulty challenge about '{topic}' in {subject}."

        if knowledge_gaps:
            user_prompt += f"\nTarget these knowledge gaps: {', '.join(knowledge_gaps)}"

        result = generate_json(system_prompt, user_prompt)

        # Validate difficulty
        challenge_difficulty = result.get("difficulty", difficulty)
        if isinstance(challenge_difficulty, str):
            try:
                challenge_difficulty = int(challenge_difficulty)
            except ValueError:
                challenge_difficulty = difficulty
        challenge_difficulty = max(1, min(5, challenge_difficulty))

        return {
            "agent": "problem_solver",
            "question": result.get("question", "Explain the key concepts of this topic."),
            "difficulty": challenge_difficulty,
            "concept": result.get("concept", topic),
            "expected_skill": result.get("expected_skill", ""),
            "hint": result.get("hint", None)
        }


problem_solver_agent = ProblemSolverAgent()

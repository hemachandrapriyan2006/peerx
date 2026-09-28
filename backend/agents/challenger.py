"""
Challenger Agent
Challenges the student's understanding with probing questions.
"""

import logging
from services.ai_service import generate_json
from prompts.challenger_prompt import get_challenger_prompt

logger = logging.getLogger(__name__)


class ChallengerAgent:
    """The Challenger AI tests deep understanding."""

    def challenge(self, topic: str, subject: str, difficulty: int,
                  mentor_explanation: str = "",
                  student_level: str = "undergraduate",
                  knowledge_gaps: list = None,
                  previous_context: str = "") -> dict:
        """
        Generate a challenging question for the student.

        Returns dict with: question, purpose, follow_up_hint
        """
        system_prompt = get_challenger_prompt(
            topic=topic,
            subject=subject,
            difficulty=difficulty,
            mentor_explanation=mentor_explanation,
            student_level=student_level,
            knowledge_gaps=knowledge_gaps,
            previous_context=previous_context
        )

        user_prompt = f"Challenge the student's understanding of '{topic}' in {subject}."

        if mentor_explanation:
            user_prompt += f"\n\nThe mentor just explained:\n{mentor_explanation[:500]}"

        result = generate_json(system_prompt, user_prompt)

        return {
            "agent": "challenger",
            "question": result.get("question", "Can you explain this concept in your own words?"),
            "purpose": result.get("purpose", ""),
            "follow_up_hint": result.get("follow_up_hint", None)
        }


challenger_agent = ChallengerAgent()

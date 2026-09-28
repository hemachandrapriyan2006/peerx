"""
Creative Peer Agent
Provides alternative perspectives and real-world analogies.
"""

import logging
from services.ai_service import generate_json
from prompts.creative_prompt import get_creative_prompt

logger = logging.getLogger(__name__)


class CreativeAgent:
    """The Creative Peer AI offers alternative ways to understand concepts."""

    def create_perspective(self, topic: str, subject: str, difficulty: int,
                           mentor_explanation: str = "",
                           student_level: str = "undergraduate",
                           previous_context: str = "") -> dict:
        """
        Generate a creative alternative explanation.

        Returns dict with: perspective, analogy, real_world_example
        """
        system_prompt = get_creative_prompt(
            topic=topic,
            subject=subject,
            difficulty=difficulty,
            mentor_explanation=mentor_explanation,
            student_level=student_level,
            previous_context=previous_context
        )

        user_prompt = f"Provide a creative alternative perspective on '{topic}' in {subject}."

        result = generate_json(system_prompt, user_prompt)

        return {
            "agent": "creative",
            "perspective": result.get("perspective", "Let me give you a different way to think about this..."),
            "analogy": result.get("analogy", ""),
            "real_world_example": result.get("real_world_example", "")
        }


creative_agent = CreativeAgent()

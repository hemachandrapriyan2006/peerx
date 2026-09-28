"""
Mentor Agent
Explains concepts clearly and adapts to student level.
"""

import logging
from services.ai_service import generate_json
from prompts.mentor_prompt import get_mentor_prompt

logger = logging.getLogger(__name__)


class MentorAgent:
    """The Mentor AI explains topics and builds understanding."""

    def explain(self, topic: str, subject: str, difficulty: int,
                student_level: str = "undergraduate",
                knowledge_gaps: list = None,
                previous_context: str = "") -> dict:
        """
        Generate a mentor explanation for the given topic.

        Returns dict with: explanation, example, key_takeaway, hint
        """
        print(f"Mentor topic: {topic}", flush=True)
        logger.info(f"Mentor topic: {topic}")

        system_prompt = get_mentor_prompt(
            topic=topic,
            subject=subject,
            difficulty=difficulty,
            student_level=student_level,
            knowledge_gaps=knowledge_gaps,
            previous_context=previous_context
        )

        user_prompt = f"Teach the student the following topic: {topic}. Do not teach any other topic. First explain what {topic} means, then explain its important concepts, give examples, and check that the explanation is appropriate for a beginner."

        if knowledge_gaps:
            user_prompt += f" Pay special attention to these areas: {', '.join(knowledge_gaps)}"

        print(f"Gemini prompt topic: {topic}", flush=True)
        logger.info(f"Gemini prompt topic: {topic}")

        result = generate_json(system_prompt, user_prompt)

        # Ensure required fields and check candidate key names
        explanation_text = (
            result.get("explanation")
            or result.get("content")
            or result.get("message")
            or result.get("text")
            or result.get("teaching_content")
            or result.get("perspective")
        )
        if not explanation_text or not str(explanation_text).strip():
            explanation_text = f"Hello! I am Mentor AI. Let's learn about {topic} in {subject}. {topic} is a key concept that helps structure data and logic effectively."

        return {
            "agent": "mentor",
            "explanation": explanation_text,
            "code_example": result.get("code_example") or result.get("code"),
            "example": result.get("example") or result.get("real_world_example") or f"In real-world {subject} applications, {topic} is widely used.",
            "key_takeaway": result.get("key_takeaway") or result.get("takeaway") or f"Mastering {topic} builds core understanding in {subject}.",
            "hint": result.get("hint")
        }



mentor_agent = MentorAgent()

"""
PeerX Difficulty Engine
Adjusts difficulty based on student performance.
"""

import logging
from config import settings

logger = logging.getLogger(__name__)

# Difficulty level labels
DIFFICULTY_LABELS = {
    1: "Beginner",
    2: "Easy",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert"
}


def calculate_new_difficulty(current_difficulty: int, recent_scores: list,
                              reviewer_recommended: int = None) -> int:
    """
    Calculate new difficulty based on recent performance.

    Uses configurable thresholds from settings:
    - < 40%: Decrease difficulty
    - 40-70%: Maintain or provide guided practice
    - 70-85%: Moderate increase
    - > 85%: Increase difficulty

    Args:
        current_difficulty: Current difficulty level (1-5)
        recent_scores: List of recent scores (0-100)
        reviewer_recommended: Difficulty recommended by reviewer (optional)

    Returns:
        New difficulty level (1-5)
    """
    if not recent_scores:
        return current_difficulty

    # Weight recent scores more heavily
    weighted_avg = _weighted_average(recent_scores)

    new_difficulty = current_difficulty

    if weighted_avg < settings.DIFFICULTY_DECREASE_THRESHOLD:
        # Score < 40%: Reduce difficulty
        new_difficulty = max(1, current_difficulty - 1)
        logger.info(f"Difficulty decreased: {weighted_avg:.1f}% avg → level {new_difficulty}")

    elif weighted_avg < settings.DIFFICULTY_MAINTAIN_HIGH:
        # 40-70%: Keep current difficulty (guided practice zone)
        new_difficulty = current_difficulty
        logger.info(f"Difficulty maintained: {weighted_avg:.1f}% avg → level {new_difficulty}")

    elif weighted_avg < settings.DIFFICULTY_HARD_INCREASE:
        # 70-85%: Moderate increase
        new_difficulty = min(5, current_difficulty + 1)
        logger.info(f"Difficulty moderately increased: {weighted_avg:.1f}% avg → level {new_difficulty}")

    else:
        # > 85%: Full increase
        new_difficulty = min(5, current_difficulty + 1)
        logger.info(f"Difficulty increased: {weighted_avg:.1f}% avg → level {new_difficulty}")

    # Consider reviewer recommendation (if provided, average with calculated)
    if reviewer_recommended is not None:
        reviewer_recommended = max(1, min(5, reviewer_recommended))
        # Weighted blend: 60% calculated, 40% reviewer
        blended = round(0.6 * new_difficulty + 0.4 * reviewer_recommended)
        new_difficulty = max(1, min(5, blended))

    return new_difficulty


def _weighted_average(scores: list) -> float:
    """
    Calculate weighted average where recent scores have more weight.
    Most recent score gets highest weight.
    """
    if not scores:
        return 0.0

    if len(scores) == 1:
        return float(scores[0])

    # Assign increasing weights to more recent scores
    n = len(scores)
    weights = [i + 1 for i in range(n)]
    total_weight = sum(weights)

    weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
    return weighted_sum / total_weight


def get_difficulty_label(difficulty: int) -> str:
    """Get human-readable difficulty label."""
    return DIFFICULTY_LABELS.get(difficulty, "Unknown")


def get_starting_difficulty(education_level: str = "undergraduate") -> int:
    """Determine starting difficulty based on education level."""
    level_map = {
        "high_school": 1,
        "undergraduate": 2,
        "graduate": 3,
        "postgraduate": 4,
        "professional": 3
    }
    return level_map.get(education_level.lower(), 2)

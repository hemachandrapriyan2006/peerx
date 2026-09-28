"""
PeerX Learning Analyzer
Computes mastery scores, extracts knowledge gaps, and tracks progress.
"""

import logging
from typing import List, Optional
from config import settings

logger = logging.getLogger(__name__)

# Reasoning quality to numeric score mapping
REASONING_SCORES = {
    "excellent": 100,
    "good": 75,
    "fair": 50,
    "poor": 25
}


def calculate_mastery_score(accuracy: float, reasoning_scores: list,
                            recent_scores: list, topics_covered: int,
                            total_topics: int = 5) -> float:
    """
    Calculate overall mastery score using weighted components.

    Weights (from config):
    - Accuracy: 40%
    - Reasoning quality: 25%
    - Recent performance: 25%
    - Topic coverage: 10%

    Returns: Mastery score (0-100)
    """
    # Component 1: Accuracy (0-100)
    accuracy_score = min(100.0, max(0.0, accuracy))

    # Component 2: Average reasoning quality (0-100)
    if reasoning_scores:
        avg_reasoning = sum(reasoning_scores) / len(reasoning_scores)
    else:
        avg_reasoning = 50.0

    # Component 3: Recent performance (0-100)
    if recent_scores:
        # Weight recent scores more heavily
        n = len(recent_scores)
        weights = [i + 1 for i in range(n)]
        total_weight = sum(weights)
        recent_avg = sum(s * w for s, w in zip(recent_scores, weights)) / total_weight
    else:
        recent_avg = 0.0

    # Component 4: Topic coverage (0-100)
    if total_topics > 0:
        coverage = (topics_covered / total_topics) * 100
    else:
        coverage = 0.0

    # Weighted combination
    mastery = (
        settings.MASTERY_WEIGHT_ACCURACY * accuracy_score +
        settings.MASTERY_WEIGHT_REASONING * avg_reasoning +
        settings.MASTERY_WEIGHT_RECENT * recent_avg +
        settings.MASTERY_WEIGHT_COVERAGE * coverage
    )

    return round(min(100.0, max(0.0, mastery)), 1)


def extract_knowledge_gaps(review_result: dict, topic: str) -> list:
    """
    Extract knowledge gap records from a reviewer's evaluation.

    Returns list of dicts: [{topic, concept, severity}, ...]
    """
    gaps = []
    raw_gaps = review_result.get("knowledge_gaps", [])
    score = review_result.get("score", 50)

    # Determine severity based on score
    if score < 30:
        default_severity = "critical"
    elif score < 50:
        default_severity = "high"
    elif score < 70:
        default_severity = "medium"
    else:
        default_severity = "low"

    for gap_concept in raw_gaps:
        if isinstance(gap_concept, str) and gap_concept.strip():
            gaps.append({
                "topic": topic,
                "concept": gap_concept.strip(),
                "severity": default_severity,
                "status": "active"
            })

    # Also extract from weaknesses if they look like knowledge gaps
    weaknesses = review_result.get("weaknesses", [])
    existing_concepts = {g["concept"].lower() for g in gaps}

    for weakness in weaknesses:
        if isinstance(weakness, str) and weakness.strip():
            # Avoid duplicates
            if weakness.strip().lower() not in existing_concepts:
                gaps.append({
                    "topic": topic,
                    "concept": weakness.strip(),
                    "severity": default_severity,
                    "status": "active"
                })

    return gaps


def calculate_accuracy(correct: int, total: int) -> float:
    """Calculate accuracy percentage."""
    if total == 0:
        return 0.0
    return round((correct / total) * 100, 1)


def reasoning_quality_to_score(quality: str) -> int:
    """Convert reasoning quality string to numeric score."""
    return REASONING_SCORES.get(quality, 50)


def analyze_performance_trend(scores: list) -> str:
    """
    Analyze if the student's performance is improving, declining, or stable.

    Returns: "improving", "declining", or "stable"
    """
    if len(scores) < 3:
        return "stable"

    recent = scores[-3:]
    older = scores[:-3] if len(scores) > 3 else scores[:2]

    recent_avg = sum(recent) / len(recent)
    older_avg = sum(older) / len(older)

    diff = recent_avg - older_avg

    if diff > 10:
        return "improving"
    elif diff < -10:
        return "declining"
    return "stable"


def get_weak_concepts(knowledge_gaps: list) -> list:
    """Get list of weak concept names from knowledge gaps."""
    return [
        gap.get("concept", "")
        for gap in knowledge_gaps
        if gap.get("status") in ("active", "improving")
        and gap.get("concept")
    ]


def get_strongest_topic(progress_records: list) -> Optional[str]:
    """Find the topic with highest mastery score."""
    if not progress_records:
        return None
    best = max(progress_records, key=lambda p: p.get("mastery_score", 0))
    return best.get("topic")


def get_weakest_topic(progress_records: list) -> Optional[str]:
    """Find the topic with lowest mastery score that has been attempted."""
    attempted = [p for p in progress_records if p.get("questions_attempted", 0) > 0]
    if not attempted:
        return None
    worst = min(attempted, key=lambda p: p.get("mastery_score", 100))
    return worst.get("topic")

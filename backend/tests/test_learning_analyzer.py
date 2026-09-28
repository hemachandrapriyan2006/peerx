"""
Tests for learning analyzer in services/learning_analyzer.py
"""

import pytest
from services.learning_analyzer import (
    calculate_mastery_score, extract_knowledge_gaps, analyze_performance_trend
)

def test_calculate_mastery_score():
    score = calculate_mastery_score(
        accuracy=80.0,
        reasoning_scores=[80, 90],
        recent_scores=[75, 85],
        topics_covered=3,
        total_topics=5
    )
    assert 0.0 <= score <= 100.0

def test_extract_knowledge_gaps():
    review_result = {
        "score": 45,
        "knowledge_gaps": ["Binary Tree Traversal", "Recursion Base Case"],
        "weaknesses": ["Time Complexity Analysis"]
    }
    gaps = extract_knowledge_gaps(review_result, topic="Data Structures")
    assert len(gaps) == 3
    assert gaps[0]["concept"] == "Binary Tree Traversal"

def test_analyze_performance_trend():
    trend = analyze_performance_trend([50, 55, 60, 80, 85, 90])
    assert trend == "improving"


"""
Tests for difficulty engine in services/difficulty_engine.py
"""

import pytest
from services.difficulty_engine import (
    calculate_new_difficulty, get_difficulty_label, get_starting_difficulty
)

def test_difficulty_adaptation_increase():
    # Weighted avg high -> difficulty should increase
    res = calculate_new_difficulty(
        current_difficulty=2,
        recent_scores=[90, 95, 92]
    )
    assert res == 3

def test_difficulty_adaptation_decrease():
    # Weighted avg low -> difficulty should decrease
    res = calculate_new_difficulty(
        current_difficulty=3,
        recent_scores=[20, 25, 30]
    )
    assert res == 2

def test_difficulty_bounds():
    # Below 1 stays 1
    res_easy = calculate_new_difficulty(
        current_difficulty=1,
        recent_scores=[10, 10]
    )
    assert res_easy == 1

    # Above 5 stays 5
    res_expert = calculate_new_difficulty(
        current_difficulty=5,
        recent_scores=[95, 95, 95]
    )
    assert res_expert == 5

def test_difficulty_labels():
    assert get_difficulty_label(1) == "Beginner"
    assert get_difficulty_label(5) == "Expert"

def test_starting_difficulty():
    assert get_starting_difficulty("undergraduate") == 2
    assert get_starting_difficulty("high_school") == 1


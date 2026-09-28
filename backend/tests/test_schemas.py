"""
Tests for Pydantic schemas in models/schemas.py
"""

import pytest
from models.schemas import (
    SessionCreate, AnswerSubmit, ProfileResponse, AgentResponse, ChallengeResponse, AgentType
)

def test_session_create_schema():
    data = SessionCreate(subject="Computer Science", topic="Binary Search Trees", difficulty=2)
    assert data.subject == "Computer Science"
    assert data.topic == "Binary Search Trees"
    assert data.difficulty == 2

def test_answer_submit_schema():
    data = AnswerSubmit(answer="A BST keeps left node smaller and right node larger.", question="What is a BST?")
    assert data.answer.startswith("A BST")
    assert data.question == "What is a BST?"

def test_profile_response_schema():
    profile = ProfileResponse(
        id="user-123",
        email="student@test.com",
        full_name="Alice Student"
    )
    assert profile.full_name == "Alice Student"

def test_agent_response_schema():
    msg = AgentResponse(
        agent=AgentType.CHALLENGER,
        message="What happens to performance when the tree becomes unbalanced?"
    )
    assert msg.agent == "challenger"

def test_challenge_response_schema():
    c = ChallengeResponse(
        question="Implement insertion into a BST.",
        difficulty=2,
        concept="Tree Insertion",
        hint="Consider recursion"
    )
    assert c.hint == "Consider recursion"


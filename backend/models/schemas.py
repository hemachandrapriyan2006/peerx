"""
PeerX Pydantic Schemas
All request/response models for the API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ── Enums ──────────────────────────────────────────────────

class Correctness(str, Enum):
    CORRECT = "correct"
    MOSTLY_CORRECT = "mostly_correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"


class ReasoningQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GapStatus(str, Enum):
    ACTIVE = "active"
    IMPROVING = "improving"
    RESOLVED = "resolved"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class AgentType(str, Enum):
    MENTOR = "mentor"
    CHALLENGER = "challenger"
    CREATIVE = "creative"
    REVIEWER = "reviewer"
    PROBLEM_SOLVER = "problem_solver"


# ── Profile ────────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    education_level: Optional[str] = None
    preferred_subject: Optional[str] = None
    learning_goal: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    education_level: Optional[str] = None
    preferred_subject: Optional[str] = None
    learning_goal: Optional[str] = None
    created_at: Optional[str] = None


# ── Session ────────────────────────────────────────────────

class SessionCreate(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    subject: str = Field(..., min_length=1, max_length=100)
    goal: Optional[str] = None
    difficulty: Optional[int] = Field(default=1, ge=1, le=5)


class SessionResponse(BaseModel):
    id: str
    user_id: str
    topic: str
    subject: str
    difficulty: int
    goal: Optional[str] = None
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


# ── Answer Submission ──────────────────────────────────────

class AnswerSubmit(BaseModel):
    answer: str = Field(..., min_length=1)
    question: Optional[str] = None


# ── Agent Response ─────────────────────────────────────────

class AgentResponse(BaseModel):
    agent: AgentType
    message: str
    data: Optional[dict] = None


# ── Mentor Response ────────────────────────────────────────

class MentorResponse(BaseModel):
    agent: str = "mentor"
    explanation: str
    example: Optional[str] = None
    key_takeaway: Optional[str] = None
    hint: Optional[str] = None


# ── Challenger Response ────────────────────────────────────

class ChallengerResponse(BaseModel):
    agent: str = "challenger"
    question: str
    purpose: Optional[str] = None
    follow_up_hint: Optional[str] = None


# ── Creative Response ──────────────────────────────────────

class CreativeResponse(BaseModel):
    agent: str = "creative"
    perspective: str
    analogy: Optional[str] = None
    real_world_example: Optional[str] = None


# ── Review Response ────────────────────────────────────────

class ReviewResponse(BaseModel):
    agent: str = "reviewer"
    score: int = Field(..., ge=0, le=100)
    correctness: str
    reasoning_quality: str
    strengths: List[str] = []
    weaknesses: List[str] = []
    knowledge_gaps: List[str] = []
    feedback: str
    recommended_difficulty: Optional[int] = None


# ── Challenge Response ─────────────────────────────────────

class ChallengeResponse(BaseModel):
    agent: str = "problem_solver"
    question: str
    difficulty: int = Field(..., ge=1, le=5)
    concept: Optional[str] = None
    expected_skill: Optional[str] = None
    hint: Optional[str] = None


# ── Progress ───────────────────────────────────────────────

class ProgressResponse(BaseModel):
    topic: str
    questions_attempted: int = 0
    questions_correct: int = 0
    accuracy: float = 0.0
    mastery_score: float = 0.0
    current_difficulty: int = 1
    last_activity: Optional[str] = None


# ── Knowledge Gap ──────────────────────────────────────────

class KnowledgeGapResponse(BaseModel):
    id: Optional[str] = None
    topic: str
    concept: str
    severity: str
    status: str
    created_at: Optional[str] = None


# ── Dashboard ──────────────────────────────────────────────

class DashboardResponse(BaseModel):
    overall_mastery: float = 0.0
    total_sessions: int = 0
    total_questions: int = 0
    total_correct: int = 0
    overall_accuracy: float = 0.0
    topics_studied: List[str] = []
    weak_concepts: List[str] = []
    recent_sessions: List[dict] = []
    recommended_challenge: Optional[dict] = None
    knowledge_gaps: List[KnowledgeGapResponse] = []


# ── Recommendation ─────────────────────────────────────────

class RecommendationResponse(BaseModel):
    strongest_topic: Optional[str] = None
    weakest_topic: Optional[str] = None
    recommended_topic: Optional[str] = None
    recommended_concept: Optional[str] = None
    recommended_difficulty: int = 1
    message: str = ""


# ── Orchestrator ───────────────────────────────────────────

class SessionStartResponse(BaseModel):
    session: SessionResponse
    mentor: MentorResponse
    challenger: ChallengerResponse


class AnswerReviewResponse(BaseModel):
    review: ReviewResponse
    knowledge_gaps: List[KnowledgeGapResponse] = []
    next_challenge: Optional[ChallengeResponse] = None
    updated_difficulty: int = 1
    progress: Optional[ProgressResponse] = None


# ── Generic API Response ───────────────────────────────────

class APIResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None

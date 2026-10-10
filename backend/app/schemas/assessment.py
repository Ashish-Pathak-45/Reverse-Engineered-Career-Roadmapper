from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class AssessmentQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    skill_tested: str
    # Note: correct_index and explanation withheld during test delivery

class AssessmentOut(BaseModel):
    id: int
    title: str
    topic: str
    difficulty: str
    estimated_minutes: int
    questions: List[Dict[str, Any]]

    class Config:
        from_attributes = True

class AssessmentSubmitRequest(BaseModel):
    answers: Dict[str, int]  # question_id -> option_index

class AssessmentResultOut(BaseModel):
    id: int
    assessment_id: int
    score: float
    total_questions: int
    correct_count: int
    weak_topics: List[str]
    question_reviews: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        from_attributes = True

class SkillGapAnalyzeRequest(BaseModel):
    current_skills: List[str]
    target_role: str
    roadmap_id: Optional[int] = None

class SkillGapItem(BaseModel):
    skill: str
    status: str  # "mastered", "in_progress", "missing", "needs_improvement"
    category: str
    priority: str  # "High", "Medium", "Low"
    estimated_hours: int
    is_verified: bool = False
    explanation: str

class SkillGapAnalyzeOut(BaseModel):
    target_role: str
    overall_match_percentage: float
    existing_skills: List[str]
    skills_needing_improvement: List[str]
    missing_skills: List[str]
    prerequisite_gaps: List[str]
    skill_breakdown: List[SkillGapItem]
    total_estimated_learning_hours: int
    recommended_immediate_action: str

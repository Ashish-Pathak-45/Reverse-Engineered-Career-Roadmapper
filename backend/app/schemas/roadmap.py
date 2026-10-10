from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class RoadmapGenerateRequest(BaseModel):
    dream_job: str
    target_company: str
    education_level: Optional[str] = "Undergraduate"
    current_skills: List[str] = []
    current_experience: Optional[str] = "Beginner with academic coursework"
    timeline: Optional[str] = "12 Months"
    weekly_hours: Optional[int] = 14
    learning_format: Optional[str] = "Hands-on projects and documentation"
    salary_aspiration: Optional[str] = None

class RoadmapNodeOut(BaseModel):
    id: int
    roadmap_id: int
    node_id: str
    title: str
    category: str
    difficulty: str
    estimated_hours: int
    status: str
    description: str
    deliverable: str
    completion_criteria: str
    recommended_next_action: Optional[str] = None
    phase: str
    position_x: float
    position_y: float
    order_index: int
    is_self_reported: bool
    assessment_score: Optional[float] = None
    resources: List[Dict[str, Any]] = []
    practical_assignments: List[str] = []

    class Config:
        from_attributes = True

class RoadmapEdgeOut(BaseModel):
    id: int
    roadmap_id: int
    source_node_id: str
    target_node_id: str
    edge_type: str

    class Config:
        from_attributes = True

class WeeklySprintOut(BaseModel):
    id: int
    roadmap_id: int
    week_number: int
    goals: List[str] = []
    tasks: List[Dict[str, Any]] = []
    planned_hours: int
    completed_hours: int
    status: str
    review_notes: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True

class RoadmapOut(BaseModel):
    id: int
    user_id: int
    title: str
    dream_job: str
    target_company: str
    timeline: str
    weekly_hours: int
    current_phase: str
    progress_percentage: float
    starting_skill_assessment: Optional[str] = None
    completion_criteria: Optional[str] = None
    suggested_next_action: Optional[str] = None
    is_archived: bool
    metadata_json: Dict[str, Any] = {}
    nodes: List[RoadmapNodeOut] = []
    edges: List[RoadmapEdgeOut] = []
    sprints: List[WeeklySprintOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoadmapSummaryOut(BaseModel):
    id: int
    title: str
    dream_job: str
    target_company: str
    timeline: str
    weekly_hours: int
    current_phase: str
    progress_percentage: float
    is_archived: bool
    node_count: int
    created_at: datetime

class RoadmapNodeUpdate(BaseModel):
    status: Optional[str] = None
    is_self_reported: Optional[bool] = None
    assessment_score: Optional[float] = None

class ReplanRequest(BaseModel):
    reason: Optional[str] = "Adjustment based on progress"
    new_weekly_hours: Optional[int] = None
    known_skills: Optional[List[str]] = None
    target_role_adjustment: Optional[str] = None

class CareerCompareRequest(BaseModel):
    career_a: str
    career_b: str

class CareerCompareOut(BaseModel):
    career_a: str
    career_b: str
    summary_a: str
    summary_b: str
    shared_skills: List[str]
    unique_skills_a: List[str]
    unique_skills_b: List[str]
    learning_effort_a: str
    learning_effort_b: str
    common_tools_a: List[str]
    common_tools_b: List[str]
    interview_focus_a: str
    interview_focus_b: str
    transition_difficulty: str
    recommendation: str

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ProjectRecommendationOut(BaseModel):
    id: int
    title: str
    target_career: str
    difficulty: str
    problem_statement: str
    learning_objectives: List[str]
    prerequisites: List[str]
    dataset_requirements: str
    tech_stack: List[str]
    implementation_milestones: List[str]
    testing_strategy: str
    evaluation_metrics: str
    deployment_options: str
    readme_outline: str
    interview_questions: List[str]
    demonstrates: str

    class Config:
        from_attributes = True

class ProjectEvidenceCreate(BaseModel):
    roadmap_id: Optional[int] = None
    node_id: Optional[str] = None
    title: str
    description: str
    related_skill: str
    evidence_type: str = "github"  # github, deployed_app, report, assessment, certificate, demo
    evidence_url: Optional[str] = None

class ProjectEvidenceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    evidence_url: Optional[str] = None
    verification_status: Optional[str] = None
    evaluation_notes: Optional[str] = None

class ProjectEvidenceOut(BaseModel):
    id: int
    user_id: int
    roadmap_id: Optional[int] = None
    node_id: Optional[str] = None
    title: str
    description: str
    related_skill: str
    evidence_type: str
    evidence_url: Optional[str] = None
    verification_status: str
    evaluation_notes: Optional[str] = None
    submitted_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

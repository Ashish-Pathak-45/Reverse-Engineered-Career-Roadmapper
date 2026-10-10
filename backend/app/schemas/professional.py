from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ProfessionalMilestoneOut(BaseModel):
    id: int
    year: str
    title: str
    organization: str
    description: str
    milestone_type: str
    order_index: int

    class Config:
        from_attributes = True

class ProfessionalSkillOut(BaseModel):
    id: int
    skill_name: str
    association_type: str

    class Config:
        from_attributes = True

class ProfessionalOut(BaseModel):
    id: int
    slug: str
    full_name: str
    profile_image: Optional[str] = None
    current_role: str
    organization: str
    category: str
    verified_date: str
    summary: str
    bio_citation: str
    education_history: List[Dict[str, Any]] = []
    original_sources: List[Dict[str, Any]] = []
    learning_takeaways: List[str] = []
    suggested_student_adaptation: Dict[str, Any] = {}
    milestones: List[ProfessionalMilestoneOut] = []
    skills: List[ProfessionalSkillOut] = []
    is_saved: Optional[bool] = False

    class Config:
        from_attributes = True

class CompareWithProfessionalOut(BaseModel):
    professional_name: str
    professional_role: str
    user_target_role: str
    similarities: List[str]
    shared_skills: List[str]
    potential_skill_gaps: List[str]
    different_milestones: List[str]
    suggested_projects: List[str]
    recommended_next_steps: List[str]
    disclaimer: str = "This comparison identifies transferable learning patterns from documented public biographies. It does not imply replicating someone else's journey."

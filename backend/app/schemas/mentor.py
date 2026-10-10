from typing import Optional, List, Dict
from pydantic import BaseModel

class MentorChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str

class MentorChatRequest(BaseModel):
    message: str
    roadmap_id: Optional[int] = None
    action_preset: Optional[str] = None  # explain_milestone, weekly_plan, concept_explain, project_recommend, interview_prep
    conversation_history: List[MentorChatMessage] = []

class MentorChatResponse(BaseModel):
    reply: str
    suggested_actions: List[str] = []
    referenced_milestones: List[str] = []
    ai_mode: str  # "gemini_pro" or "heuristic_intelligence"
    disclaimer: str = "PATHFORGE AI Mentor provides algorithmic educational guidance. Career trajectories and interview formats may vary by company."

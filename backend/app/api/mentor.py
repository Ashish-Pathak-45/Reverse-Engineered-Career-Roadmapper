import logging
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.roadmap import Roadmap
from app.schemas.mentor import MentorChatRequest, MentorChatResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mentor", tags=["Contextual AI Career Mentor"])

@router.post("/chat", response_model=MentorChatResponse)
def mentor_chat(
    req: MentorChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Fetch user's active roadmap & context
    roadmap = None
    if req.roadmap_id:
        roadmap = db.query(Roadmap).filter(Roadmap.id == req.roadmap_id, Roadmap.user_id == user.id).first()
    if not roadmap:
        roadmap = db.query(Roadmap).filter(Roadmap.user_id == user.id, Roadmap.is_archived == False).first()

    context_str = f"User: {user.full_name}\n"
    target_role = "Software Engineer"
    target_company = "Tech Industry"
    active_milestone = None
    completed_milestones = []
    available_milestones = []

    if roadmap:
        target_role = roadmap.dream_job
        target_company = roadmap.target_company
        context_str += f"Target Goal: {roadmap.dream_job} at {roadmap.target_company}\n"
        context_str += f"Timeline: {roadmap.timeline}, Weekly Study Hours: {roadmap.weekly_hours}\n"
        context_str += f"Current Phase: {roadmap.current_phase}, Progress: {roadmap.progress_percentage}%\n"

        for n in roadmap.nodes:
            if n.status == "completed":
                completed_milestones.append(n.title)
            elif n.status == "available" and not active_milestone:
                active_milestone = n.title
            if n.status == "available":
                available_milestones.append(n.title)

    if not active_milestone and available_milestones:
        active_milestone = available_milestones[0]
    elif not active_milestone:
        active_milestone = "Foundational Core Architecture"

    # 2. Try Gemini if available
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)

            system_instruction = f"""
You are the PATHFORGE AI Contextual Career Mentor.
You are helping {user.full_name} achieve their goal of becoming a {target_role} at {target_company}.
User Context:
{context_str}
Active Milestone in Progress: {active_milestone}
Completed Milestones: {", ".join(completed_milestones) if completed_milestones else "None yet"}
Available Next Milestones: {", ".join(available_milestones)}

Provide clear, encouraging, highly specific, and actionable advice. Reference their actual roadmap milestones directly.
Do not make generic platitudes.
"""
            chat = model.start_chat(history=[])
            resp = chat.send_message(f"{system_instruction}\n\nStudent Message: {req.message}")
            return MentorChatResponse(
                reply=resp.text.strip(),
                suggested_actions=[
                    f"Work on '{active_milestone}' deliverable",
                    "Take a diagnostic assessment",
                    "Add project evidence to portfolio"
                ],
                referenced_milestones=[active_milestone] if active_milestone else [],
                ai_mode="gemini_pro"
            )
        except Exception as e:
            logger.warning(f"Mentor Gemini call failed: {e}. Using Contextual Heuristic Mentor.")

    # 3. Contextual Heuristic AI Mentor
    msg_lower = req.message.lower()

    if req.action_preset == "explain_milestone" or "milestone" in msg_lower or "next" in msg_lower:
        reply = (
            f"Here is your focused breakdown for your current milestone: **{active_milestone}**.\n\n"
            f"1. **Core Objective**: Master the principles and deliver an artifact solving a realistic problem.\n"
            f"2. **Recommended Schedule**: Dedicate {round(roadmap.weekly_hours/2) if roadmap else 7} hours this week to conceptual drills and code implementations.\n"
            f"3. **Deliverable Check**: Ensure you write clean tests and push a well-documented Git commit to your evidence portfolio once finished.\n\n"
            f"Would you like me to walk through a mock interview question or outline the repository structure?"
        )
        actions = ["Outline repository structure", "Give me a practice question", "Show recommended resources"]
    elif req.action_preset == "weekly_plan" or "week" in msg_lower or "plan" in msg_lower:
        reply = (
            f"Here is your customized **Weekly Sprint Plan** targeting {target_role}:\n\n"
            f"- **Monday–Tuesday**: 4 Hours on **{active_milestone}** foundational documentation and syntax.\n"
            f"- **Wednesday–Thursday**: 5 Hours building the practical code assignment and unit test suite.\n"
            f"- **Friday**: 2 Hours reviewing edge cases and running self-evaluations.\n"
            f"- **Weekend**: 3 Hours packaging your project into the Career Evidence Portfolio.\n\n"
            f"Total commitment: {roadmap.weekly_hours if roadmap else 14} Hours. Consistency beats cramming!"
        )
        actions = ["Mark tasks in sprint planner", "Explain core concept", "Simulate interview question"]
    elif req.action_preset == "interview_prep" or "interview" in msg_lower:
        reply = (
            f"Let's prepare for your upcoming technical screens at **{target_company}** for the **{target_role}** role.\n\n"
            f"Top technical areas tested:\n"
            f"1. **Algorithmic Mechanics**: Time & space complexity tradeoffs in real systems.\n"
            f"2. **Architectural Tradeoffs**: For example, when would you choose an asynchronous worker queue over synchronous REST calls?\n"
            f"3. **Milestone Project Defense**: You will be asked to explain design decisions made during **{active_milestone}**.\n\n"
            f"Try answering: *'How did you validate and test your deliverable for {active_milestone}?'*"
        )
        actions = ["Submit answer for evaluation", "Test my system design knowledge", "Take diagnostic assessment"]
    else:
        reply = (
            f"Hello {user.full_name}! I'm tracking your progression toward **{target_role}** at **{target_company}**.\n\n"
            f"You are currently working through **{roadmap.current_phase if roadmap else 'Phase 1: Foundations'}** "
            f"with milestone **{active_milestone}** ready for action.\n\n"
            f"How can I accelerate your learning today? We can break down difficult concepts, plan your sprint, or review project deliverables."
        )
        actions = ["Explain my next milestone", "Create weekly sprint schedule", "Practice interview questions"]

    return MentorChatResponse(
        reply=reply,
        suggested_actions=actions,
        referenced_milestones=[active_milestone] if active_milestone else [],
        ai_mode="heuristic_intelligence"
    )

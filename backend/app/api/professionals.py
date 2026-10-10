from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api.deps import get_db, get_current_user, get_optional_user
from app.models.user import User
from app.models.professional import ProfessionalProfile, SavedProfile
from app.models.roadmap import Roadmap
from app.schemas.professional import ProfessionalOut, CompareWithProfessionalOut

router = APIRouter(prefix="/professionals", tags=["Success Stories & Verified Career Journeys"])

@router.get("", response_model=List[ProfessionalOut])
def list_professionals(
    search: Optional[str] = Query(None, description="Search by name, role, or organization"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skill: Optional[str] = Query(None, description="Filter by skill"),
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    query = db.query(ProfessionalProfile)

    if category:
        query = query.filter(ProfessionalProfile.category == category)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                ProfessionalProfile.full_name.ilike(s),
                ProfessionalProfile.current_role.ilike(s),
                ProfessionalProfile.organization.ilike(s),
                ProfessionalProfile.summary.ilike(s)
            )
        )

    profiles = query.all()

    # Filter by skill if requested
    if skill:
        skill_lower = skill.lower().strip()
        profiles = [
            p for p in profiles
            if any(skill_lower in s.skill_name.lower() for s in p.skills)
        ]

    # Annotate is_saved if user logged in
    saved_ids = set()
    if user:
        saved_records = db.query(SavedProfile.professional_id).filter(SavedProfile.user_id == user.id).all()
        saved_ids = {r[0] for r in saved_records}

    results = []
    for p in profiles:
        out = ProfessionalOut.model_validate(p)
        out.is_saved = p.id in saved_ids
        results.append(out)

    return results

@router.get("/{slug_or_id}", response_model=ProfessionalOut)
def get_professional(
    slug_or_id: str,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    query = db.query(ProfessionalProfile)
    if slug_or_id.isdigit():
        prof = query.filter(ProfessionalProfile.id == int(slug_or_id)).first()
    else:
        prof = query.filter(ProfessionalProfile.slug == slug_or_id).first()

    if not prof:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional profile not found.")

    out = ProfessionalOut.model_validate(prof)
    if user:
        saved = db.query(SavedProfile).filter(SavedProfile.user_id == user.id, SavedProfile.professional_id == prof.id).first()
        out.is_saved = bool(saved)

    return out

@router.post("/{prof_id}/save")
def toggle_save_professional(
    prof_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prof = db.query(ProfessionalProfile).filter(ProfessionalProfile.id == prof_id).first()
    if not prof:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    existing = db.query(SavedProfile).filter(SavedProfile.user_id == user.id, SavedProfile.professional_id == prof_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"saved": False, "message": "Profile removed from bookmarks."}
    else:
        db.add(SavedProfile(user_id=user.id, professional_id=prof_id))
        db.commit()
        return {"saved": True, "message": "Profile saved to bookmarks."}

@router.get("/{prof_id}/compare", response_model=CompareWithProfessionalOut)
def compare_with_professional(
    prof_id: int,
    roadmap_id: Optional[int] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prof = db.query(ProfessionalProfile).filter(ProfessionalProfile.id == prof_id).first()
    if not prof:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional profile not found.")

    # Find user's active roadmap or profile
    roadmap = None
    if roadmap_id:
        roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user.id).first()
    if not roadmap:
        roadmap = db.query(Roadmap).filter(Roadmap.user_id == user.id, Roadmap.is_archived == False).first()

    user_target = roadmap.dream_job if roadmap else (user.profile.target_career if user.profile else "Software Engineer")
    user_skills = []
    if roadmap:
        user_skills = [n.title for n in roadmap.nodes if n.status == "completed"]
    if user.profile and user.profile.technical_skills:
        user_skills.extend(user.profile.technical_skills)
    user_skills_lower = [s.lower() for s in user_skills]

    prof_skills = [s.skill_name for s in prof.skills]

    shared = [s for s in prof_skills if any(u in s.lower() or s.lower() in u for u in user_skills_lower)]
    gaps = [s for s in prof_skills if s not in shared]

    return CompareWithProfessionalOut(
        professional_name=prof.full_name,
        professional_role=f"{prof.current_role} ({prof.organization})",
        user_target_role=user_target,
        similarities=[
            f"Both paths target high-impact technical mastery in {prof.category}.",
            f"Foundation in core programming, mathematics, and empirical problem solving.",
            f"Focus on practical project artifacts before scaling to larger systems."
        ],
        shared_skills=shared if shared else ["Core Programming", "Problem Solving", "Git"],
        potential_skill_gaps=gaps[:5] if gaps else ["Deep Systems Architecture", "Empirical Benchmarking"],
        different_milestones=[
            f"{prof.full_name}'s path featured early research and high-risk exploratory breakthroughs at {prof.organization}.",
            "Your path focuses on direct industry engineering competency, production pipelines, and technical screens."
        ],
        suggested_projects=[
            f"Build a miniature prototype inspired by {prof.full_name}'s early milestone: {prof.milestones[0].title if prof.milestones else 'Core Architecture'}",
            f"Implement an open-source evaluation benchmark reproducing verified results."
        ],
        recommended_next_steps=[
            f"Strengthen foundational gaps in: {gaps[0] if gaps else 'Advanced Systems'}",
            "Maintain an open, reproducible evidence repository demonstrating code quality.",
            "Study verified technical presentations and publications from official sources."
        ]
    )

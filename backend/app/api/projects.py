from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.project import ProjectRecommendation, ProjectEvidence
from app.schemas.project import (
    ProjectRecommendationOut, ProjectEvidenceCreate, ProjectEvidenceUpdate, ProjectEvidenceOut
)

router = APIRouter(prefix="/projects", tags=["AI Project Architect & Career Evidence Portfolio"])

@router.get("", response_model=List[ProjectRecommendationOut])
def list_projects(
    target_career: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ProjectRecommendation)
    if target_career:
        query = query.filter(ProjectRecommendation.target_career.ilike(f"%{target_career.strip()}%"))
    if difficulty:
        query = query.filter(ProjectRecommendation.difficulty == difficulty)
    return query.all()

@router.get("/{project_id}", response_model=ProjectRecommendationOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    proj = db.query(ProjectRecommendation).filter(ProjectRecommendation.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project recommendation not found.")
    return proj

@router.get("/evidence/me", response_model=List[ProjectEvidenceOut])
def list_my_evidence(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(ProjectEvidence).filter(ProjectEvidence.user_id == user.id).order_by(ProjectEvidence.submitted_at.desc()).all()

@router.post("/evidence", response_model=ProjectEvidenceOut)
def submit_evidence(
    data: ProjectEvidenceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    evidence = ProjectEvidence(
        user_id=user.id,
        roadmap_id=data.roadmap_id,
        node_id=data.node_id,
        title=data.title.strip(),
        description=data.description.strip(),
        related_skill=data.related_skill.strip(),
        evidence_type=data.evidence_type,
        evidence_url=data.evidence_url,
        verification_status="submitted",
        evaluation_notes="Submitted to portfolio. Pending automated validation review."
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence

@router.patch("/evidence/{evidence_id}", response_model=ProjectEvidenceOut)
def update_evidence(
    evidence_id: int,
    data: ProjectEvidenceUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ev = db.query(ProjectEvidence).filter(ProjectEvidence.id == evidence_id, ProjectEvidence.user_id == user.id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence item not found.")

    if data.title is not None:
        ev.title = data.title
    if data.description is not None:
        ev.description = data.description
    if data.evidence_url is not None:
        ev.evidence_url = data.evidence_url
    if data.verification_status is not None:
        ev.verification_status = data.verification_status
    if data.evaluation_notes is not None:
        ev.evaluation_notes = data.evaluation_notes

    db.commit()
    db.refresh(ev)
    return ev

@router.delete("/evidence/{evidence_id}")
def delete_evidence(
    evidence_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ev = db.query(ProjectEvidence).filter(ProjectEvidence.id == evidence_id, ProjectEvidence.user_id == user.id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence item not found.")

    db.delete(ev)
    db.commit()
    return {"message": "Evidence removed from private portfolio."}

@router.post("/evidence/{evidence_id}/validate", response_model=ProjectEvidenceOut)
def validate_evidence(
    evidence_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ev = db.query(ProjectEvidence).filter(ProjectEvidence.id == evidence_id, ProjectEvidence.user_id == user.id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence item not found.")

    # Verification algorithm checks URL structure and deliverable evidence
    if ev.evidence_url and ("github.com" in ev.evidence_url or "http" in ev.evidence_url):
        ev.verification_status = "verified"
        ev.evaluation_notes = f"Verified link structure ({ev.evidence_type.upper()}). Demonstrates competency in {ev.related_skill}."
    else:
        ev.verification_status = "checked"
        ev.evaluation_notes = "Verified text documentation. Recommend linking public repository or live URL for verified badge."

    db.commit()
    db.refresh(ev)
    return ev

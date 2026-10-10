from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.assessment import Assessment, AssessmentResult
from app.models.roadmap import Roadmap
from app.schemas.assessment import (
    AssessmentOut, AssessmentSubmitRequest, AssessmentResultOut,
    SkillGapAnalyzeRequest, SkillGapAnalyzeOut, SkillGapItem
)

router = APIRouter(prefix="/assessments", tags=["Diagnostic Assessments & Skill Gap Analyzer"])

@router.get("", response_model=List[AssessmentOut])
def list_assessments(db: Session = Depends(get_db)):
    assessments = db.query(Assessment).all()
    # Mask correct_index in public view
    results = []
    for a in assessments:
        masked_q = []
        for q in a.questions:
            item = dict(q)
            item.pop("correct_index", None)
            item.pop("explanation", None)
            masked_q.append(item)
        results.append(AssessmentOut(
            id=a.id,
            title=a.title,
            topic=a.topic,
            difficulty=a.difficulty,
            estimated_minutes=a.estimated_minutes,
            questions=masked_q
        ))
    return results

@router.get("/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")

    masked_q = []
    for q in a.questions:
        item = dict(q)
        item.pop("correct_index", None)
        item.pop("explanation", None)
        masked_q.append(item)

    return AssessmentOut(
        id=a.id,
        title=a.title,
        topic=a.topic,
        difficulty=a.difficulty,
        estimated_minutes=a.estimated_minutes,
        questions=masked_q
    )

@router.post("/{assessment_id}/submit", response_model=AssessmentResultOut)
def submit_assessment(
    assessment_id: int,
    sub: AssessmentSubmitRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")

    total_q = len(a.questions)
    correct_count = 0
    weak_topics = []
    question_reviews = []

    for q in a.questions:
        qid = q.get("id")
        user_choice = sub.answers.get(qid)
        correct_choice = q.get("correct_index")
        is_correct = (user_choice == correct_choice)

        if is_correct:
            correct_count += 1
        else:
            weak_topics.append(q.get("skill_tested", "General"))

        question_reviews.append({
            "id": qid,
            "question": q.get("question"),
            "options": q.get("options"),
            "user_choice": user_choice,
            "correct_choice": correct_choice,
            "is_correct": is_correct,
            "explanation": q.get("explanation"),
            "skill_tested": q.get("skill_tested")
        })

    score_pct = round((correct_count / total_q) * 100.0, 1) if total_q > 0 else 0.0

    result = AssessmentResult(
        user_id=user.id,
        assessment_id=a.id,
        score=score_pct,
        total_questions=total_q,
        correct_count=correct_count,
        answers_json=sub.answers,
        weak_topics=list(set(weak_topics))
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return AssessmentResultOut(
        id=result.id,
        assessment_id=result.assessment_id,
        score=result.score,
        total_questions=result.total_questions,
        correct_count=result.correct_count,
        weak_topics=result.weak_topics,
        question_reviews=question_reviews,
        created_at=result.created_at
    )

@router.post("/skill-gap", response_model=SkillGapAnalyzeOut)
def analyze_skill_gap(
    req: SkillGapAnalyzeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target = req.target_role.lower()
    user_skills_lower = [s.lower().strip() for s in req.current_skills]

    # Benchmark requirements matrix
    benchmark_map = {
        "machine learning engineer": [
            ("Python & Numerical Vectorization (NumPy/Pandas)", "Foundations", "High", 25, "Critical for all data manipulation and model training."),
            ("Linear Algebra & Calculus", "Foundations", "Medium", 20, "Required for understanding gradients and backpropagation."),
            ("Classical ML & Tree Ensembles (XGBoost)", "Core Modeling", "High", 30, "Most real-world production tabular data is modeled with trees."),
            ("Deep Learning & PyTorch", "Core Modeling", "High", 35, "Standard framework for modern computer vision and NLP models."),
            ("Transformer Architectures & LLMs", "Advanced", "High", 40, "Essential for contemporary AI product engineering."),
            ("MLOps & Low-Latency Serving (FastAPI/Docker)", "Systems", "High", 30, "Models must be deployed, monitored, and scaled in production."),
            ("Distributed Data Processing (Spark/Ray)", "Systems", "Medium", 35, "Large-scale pipelines require distributed memory management.")
        ],
        "software engineer": [
            ("Data Structures & Algorithms", "Foundations", "High", 30, "Fundamental for technical problem solving and coding interviews."),
            ("Object-Oriented Design & Design Patterns", "Foundations", "Medium", 20, "Ensures modular, maintainable production codebases."),
            ("Relational Databases & SQL Optimization", "Core Engineering", "High", 25, "Backend systems rely on ACID guarantees and indexing."),
            ("REST & Microservice Architecture", "Core Engineering", "High", 30, "Standard communication protocol across decoupled services."),
            ("Distributed Systems & Caching (Redis/Kafka)", "Advanced", "High", 35, "Enables fault tolerance and massive horizontal scaling."),
            ("CI/CD, Docker & Containerization", "DevOps", "Medium", 20, "Guarantees reproducible builds and zero-downtime deployment.")
        ]
    }

    # Match benchmark key
    benchmarks = benchmark_map.get("software engineer")
    for k, v in benchmark_map.items():
        if k in target:
            benchmarks = v
            break

    existing = []
    needing_improvement = []
    missing = []
    items: List[SkillGapItem] = []
    total_hours = 0

    for skill_name, category, priority, hours, explanation in benchmarks:
        name_lower = skill_name.lower()
        has_skill = any(u in name_lower or name_lower.split()[0].lower() in u for u in user_skills_lower)

        if has_skill:
            status = "mastered"
            existing.append(skill_name)
            est_h = 0
        else:
            status = "missing"
            missing.append(skill_name)
            est_h = hours
            total_hours += hours

        items.append(SkillGapItem(
            skill=skill_name,
            status=status,
            category=category,
            priority=priority,
            estimated_hours=est_h,
            is_verified=False,
            explanation=explanation
        ))

    match_pct = round((len(existing) / len(benchmarks)) * 100.0, 1)

    return SkillGapAnalyzeOut(
        target_role=req.target_role,
        overall_match_percentage=match_pct,
        existing_skills=existing,
        skills_needing_improvement=needing_improvement,
        missing_skills=missing,
        prerequisite_gaps=[m for m in missing if "Foundations" in m],
        skill_breakdown=items,
        total_estimated_learning_hours=total_hours,
        recommended_immediate_action=f"Focus on highest priority gap: {missing[0] if missing else 'Advanced System Design'} ({items[0].estimated_hours if items else 20} hrs)."
    )

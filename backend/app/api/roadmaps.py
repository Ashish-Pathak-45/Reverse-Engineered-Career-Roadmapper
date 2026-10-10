from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.roadmap import Roadmap, RoadmapNode, RoadmapEdge, WeeklySprint
from app.schemas.roadmap import (
    RoadmapGenerateRequest, RoadmapOut, RoadmapSummaryOut, RoadmapNodeUpdate,
    ReplanRequest, CareerCompareRequest, CareerCompareOut
)
from app.services.ai_engine import generate_roadmap_ai, replan_roadmap_ai, compare_careers_ai
from app.services.graph_engine import (
    can_complete_node, update_graph_states_on_change, calculate_progress
)

router = APIRouter(prefix="/roadmaps", tags=["Career Roadmaps"])

@router.post("/generate", response_model=RoadmapOut)
def generate_roadmap(
    req: RoadmapGenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Generate via AI engine
    generated = generate_roadmap_ai(req)

    # 2. Persist in database
    pct, current_phase = calculate_progress(generated["nodes"])
    roadmap = Roadmap(
        user_id=user.id,
        title=generated["title"],
        dream_job=req.dream_job.strip(),
        target_company=req.target_company.strip(),
        timeline=req.timeline,
        weekly_hours=req.weekly_hours,
        current_phase=current_phase,
        progress_percentage=pct,
        starting_skill_assessment=generated.get("starting_skill_assessment"),
        completion_criteria=generated.get("completion_criteria"),
        suggested_next_action=generated.get("suggested_next_action"),
        metadata_json={"ai_mode": generated.get("ai_mode", "heuristic")}
    )
    db.add(roadmap)
    db.flush()

    # 3. Add nodes
    for idx, n in enumerate(generated["nodes"]):
        r_node = RoadmapNode(
            roadmap_id=roadmap.id,
            node_id=n["node_id"],
            title=n["title"],
            category=n.get("category", "Core Skills"),
            difficulty=n.get("difficulty", "Intermediate"),
            estimated_hours=n.get("estimated_hours", 20),
            status=n.get("status", "locked"),
            description=n["description"],
            deliverable=n["deliverable"],
            completion_criteria=n["completion_criteria"],
            recommended_next_action=n.get("recommended_next_action"),
            phase=n.get("phase", "Phase 1"),
            position_x=n.get("position_x", 0.0),
            position_y=n.get("position_y", 0.0),
            order_index=idx,
            is_self_reported=n.get("is_self_reported", False),
            resources=n.get("resources", []),
            practical_assignments=n.get("practical_assignments", [])
        )
        db.add(r_node)

    # 4. Add edges
    for e in generated.get("edges", []):
        db.add(RoadmapEdge(
            roadmap_id=roadmap.id,
            source_node_id=e["source_node_id"],
            target_node_id=e["target_node_id"],
            edge_type=e.get("edge_type", "prerequisite")
        ))

    # 5. Add sprints
    for s in generated.get("sprints", []):
        db.add(WeeklySprint(
            roadmap_id=roadmap.id,
            week_number=s.get("week_number", 1),
            goals=s.get("goals", []),
            tasks=s.get("tasks", []),
            planned_hours=s.get("planned_hours", req.weekly_hours),
            completed_hours=0,
            status="active"
        ))

    db.commit()
    db.refresh(roadmap)
    return roadmap

@router.get("", response_model=List[RoadmapSummaryOut])
def list_my_roadmaps(
    archived: Optional[bool] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Roadmap).filter(Roadmap.user_id == user.id)
    if archived is not None:
        query = query.filter(Roadmap.is_archived == archived)
    roadmaps = query.order_by(Roadmap.created_at.desc()).all()

    return [
        RoadmapSummaryOut(
            id=r.id,
            title=r.title,
            dream_job=r.dream_job,
            target_company=r.target_company,
            timeline=r.timeline,
            weekly_hours=r.weekly_hours,
            current_phase=r.current_phase,
            progress_percentage=r.progress_percentage,
            is_archived=r.is_archived,
            node_count=len(r.nodes),
            created_at=r.created_at
        )
        for r in roadmaps
    ]

@router.get("/{roadmap_id}", response_model=RoadmapOut)
def get_roadmap(
    roadmap_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user.id).first()
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found or access denied."
        )
    return roadmap

@router.patch("/{roadmap_id}", response_model=RoadmapOut)
def update_roadmap(
    roadmap_id: int,
    title: Optional[str] = None,
    is_archived: Optional[bool] = None,
    weekly_hours: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user.id).first()
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")
    
    if title is not None:
        roadmap.title = title
    if is_archived is not None:
        roadmap.is_archived = is_archived
    if weekly_hours is not None:
        roadmap.weekly_hours = weekly_hours

    db.commit()
    db.refresh(roadmap)
    return roadmap

@router.delete("/{roadmap_id}")
def delete_roadmap(
    roadmap_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user.id).first()
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")
    
    db.delete(roadmap)
    db.commit()
    return {"message": "Roadmap deleted successfully."}

@router.patch("/{roadmap_id}/nodes/{node_id}", response_model=RoadmapOut)
def update_roadmap_node(
    roadmap_id: int,
    node_id: str,
    update: RoadmapNodeUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user.id).first()
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")

    node = next((n for n in roadmap.nodes if n.node_id == node_id), None)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Milestone node '{node_id}' not found.")

    # 1. Enforce prerequisite dependency rules when advancing state
    if update.status in ["completed", "in_progress"] and node.status != "completed":
        can_complete, unmet = can_complete_node(node_id, roadmap.nodes, roadmap.edges)
        if not can_complete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot unlock or complete '{node.title}' until prerequisites are satisfied: {', '.join(unmet)}"
            )

    # 2. Update target node
    if update.status:
        node.status = update.status
    if update.is_self_reported is not None:
        node.is_self_reported = update.is_self_reported
    if update.assessment_score is not None:
        node.assessment_score = update.assessment_score

    # 3. Recalculate graph states and unlock downstream nodes
    update_graph_states_on_change(roadmap.nodes, roadmap.edges)

    # 4. Recalculate progress & active phase
    pct, current_phase = calculate_progress(roadmap.nodes)
    roadmap.progress_percentage = pct
    roadmap.current_phase = current_phase

    # Update suggested next action
    next_node = next((n for n in roadmap.nodes if n.status == "available"), None)
    if next_node:
        roadmap.suggested_next_action = f"Next milestone available: {next_node.title} ({next_node.estimated_hours}h)"
    elif pct >= 100:
        roadmap.suggested_next_action = "All roadmap milestones complete! Ready for technical portfolio interviews."

    db.commit()
    db.refresh(roadmap)
    return roadmap

@router.post("/{roadmap_id}/replan", response_model=RoadmapOut)
def replan_roadmap(
    roadmap_id: int,
    req: ReplanRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user.id).first()
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")

    # Convert nodes & edges to dicts for replan logic
    nodes_dicts = [
        {
            "node_id": n.node_id,
            "title": n.title,
            "category": n.category,
            "difficulty": n.difficulty,
            "estimated_hours": n.estimated_hours,
            "status": n.status,
            "description": n.description,
            "deliverable": n.deliverable,
            "completion_criteria": n.completion_criteria,
            "phase": n.phase,
            "is_self_reported": n.is_self_reported
        }
        for n in roadmap.nodes
    ]
    edges_dicts = [
        {"source_node_id": e.source_node_id, "target_node_id": e.target_node_id}
        for e in roadmap.edges
    ]

    replan_result = replan_roadmap_ai(nodes_dicts, edges_dicts, req)

    # Update in database
    node_map = { n.node_id: n for n in roadmap.nodes }
    for updated in replan_result["nodes"]:
        n = node_map.get(updated["node_id"])
        if n:
            n.status = updated["status"]
            n.is_self_reported = updated.get("is_self_reported", n.is_self_reported)

    if req.new_weekly_hours:
        roadmap.weekly_hours = req.new_weekly_hours

    pct, current_phase = calculate_progress(roadmap.nodes)
    roadmap.progress_percentage = pct
    roadmap.current_phase = current_phase
    roadmap.suggested_next_action = replan_result["explanation"]

    db.commit()
    db.refresh(roadmap)
    return roadmap

@router.post("/compare", response_model=CareerCompareOut)
def compare_careers(req: CareerCompareRequest):
    return compare_careers_ai(req.career_a, req.career_b)

@router.post("/{roadmap_id}/sprints/{sprint_id}/tasks/{task_id}/toggle")
def toggle_sprint_task(
    roadmap_id: int,
    sprint_id: int,
    task_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user.id).first()
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")
    
    sprint = db.query(WeeklySprint).filter(WeeklySprint.id == sprint_id, WeeklySprint.roadmap_id == roadmap_id).first()
    if not sprint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found.")

    tasks = list(sprint.tasks)
    found = False
    for t in tasks:
        if t.get("id") == task_id:
            t["completed"] = not t.get("completed", False)
            if t["completed"]:
                sprint.completed_hours += t.get("estimated_hours", 2)
            else:
                sprint.completed_hours = max(0, sprint.completed_hours - t.get("estimated_hours", 2))
            found = True
            break

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found in sprint.")

    sprint.tasks = tasks
    db.commit()
    return {"message": "Task toggled", "completed_hours": sprint.completed_hours, "tasks": sprint.tasks}

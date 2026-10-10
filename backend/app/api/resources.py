from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api.deps import get_db, get_current_user, get_optional_user
from app.models.user import User
from app.models.resource import Resource, SavedResource
from app.schemas.resource import ResourceOut

router = APIRouter(prefix="/resources", tags=["Curated Learning Resources"])

@router.get("", response_model=List[ResourceOut])
def list_resources(
    search: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    format_type: Optional[str] = Query(None),
    free_only: Optional[bool] = Query(None),
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    query = db.query(Resource)

    if topic:
        query = query.filter(Resource.topic.ilike(f"%{topic.strip()}%"))
    if format_type:
        query = query.filter(Resource.format == format_type)
    if free_only:
        query = query.filter(Resource.is_free == True)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Resource.title.ilike(s),
                Resource.provider.ilike(s),
                Resource.description.ilike(s)
            )
        )

    resources = query.all()

    saved_ids = set()
    if user:
        records = db.query(SavedResource.resource_id).filter(SavedResource.user_id == user.id).all()
        saved_ids = {r[0] for r in records}

    results = []
    for r in resources:
        item = ResourceOut.model_validate(r)
        item.is_saved = r.id in saved_ids
        results.append(item)

    return results

@router.post("/{resource_id}/save")
def toggle_save_resource(
    resource_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")

    existing = db.query(SavedResource).filter(
        SavedResource.user_id == user.id,
        SavedResource.resource_id == resource_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"saved": False, "message": "Resource removed from bookmarks."}
    else:
        db.add(SavedResource(user_id=user.id, resource_id=resource_id))
        db.commit()
        return {"saved": True, "message": "Resource saved to bookmarks."}

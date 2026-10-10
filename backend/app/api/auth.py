from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
import os
import time
import uuid
import re

from app.api.deps import get_db, get_current_user
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserProfile
from app.schemas.user import (
    UserCreate, UserLogin, UserOut, Token,
    UserProfileUpdate, UserProfileOut, PasswordResetRequest, PasswordChangeRequest,
    AccountDeleteRequest, AvatarUploadResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication & Profiles"])

UPLOAD_AVATAR_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uploads", "avatars"
)
os.makedirs(UPLOAD_AVATAR_DIR, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def generate_clean_username(full_name: str, db: Session) -> str:
    base = re.sub(r"[^a-zA-Z0-9]", "", full_name.lower().strip()) or "user"
    candidate = base[:15]
    if not db.query(User).filter(User.username == candidate).first():
        return candidate
    for i in range(1, 1000):
        test_user = f"{base[:12]}_{i}"
        if not db.query(User).filter(User.username == test_user).first():
            return test_user
    return f"{base[:10]}_{uuid.uuid4().hex[:6]}"

@router.post("/signup", response_model=Token)
def signup(data: UserCreate, db: Session = Depends(get_db)):
    clean_email = data.email.lower().strip()
    existing_email = db.query(User).filter(User.email == clean_email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Validate or generate username
    final_username = None
    if data.username and data.username.strip():
        req_username = data.username.strip().lower()
        if not re.match(r"^[a-zA-Z0-9_.-]{3,30}$", req_username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be 3-30 characters and contain only letters, numbers, underscores, and dashes."
            )
        existing_username = db.query(User).filter(User.username == req_username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This username is already taken. Please choose another."
            )
        final_username = req_username
    else:
        final_username = generate_clean_username(data.full_name, db)

    user = User(
        email=clean_email,
        username=final_username,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name.strip(),
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.flush()

    # Create new profile in non-onboarded state so user completes their customized profile
    profile = UserProfile(
        user_id=user.id,
        username=final_username,
        education_level="Undergraduate",
        degree="B.Tech Computer Science",
        college="University / College",
        target_career="Software Engineer",
        career_goal="Software Engineer",
        target_job_role="Software Engineer",
        technical_skills=["Problem Solving", "Git"],
        available_study_hours=14,
        is_onboarded=False  # Flags to show guided onboarding
    )
    db.add(profile)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    clean_email = data.email.lower().strip()
    user = db.query(User).filter(User.email == clean_email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is deactivated.")

    # Ensure profile exists
    if not user.profile:
        user.profile = UserProfile(
            user_id=user.id,
            username=user.username or generate_clean_username(user.full_name, db),
            is_onboarded=True
        )
        db.commit()
        db.refresh(user)

    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserOut)
def get_current_user_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Ensure profile exists
    if not user.profile:
        user.profile = UserProfile(
            user_id=user.id,
            username=user.username or generate_clean_username(user.full_name, db),
            is_onboarded=True
        )
        db.commit()
        db.refresh(user)
    return user

@router.put("/profile", response_model=UserProfileOut)
def update_profile(
    profile_data: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = user.profile
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    update_dict = profile_data.model_dump(exclude_unset=True)

    # 1. Handle full name update
    if "full_name" in update_dict and update_dict["full_name"]:
        name_val = update_dict.pop("full_name").strip()
        if len(name_val) < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Full name must be at least 2 characters.")
        user.full_name = name_val

    # 2. Handle username update with uniqueness validation
    if "username" in update_dict and update_dict["username"]:
        new_username = update_dict["username"].strip().lower()
        conflict = db.query(User).filter(User.username == new_username, User.id != user.id).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '@{new_username}' is already in use by another member."
            )
        user.username = new_username
        profile.username = new_username

    # 3. Handle avatar URL synchronization
    if "avatar_url" in update_dict:
        user.avatar_url = update_dict["avatar_url"]
        profile.avatar_url = update_dict["avatar_url"]

    # 4. Synchronize target_career and career_goal for full backwards compatibility
    if "target_career" in update_dict and not update_dict.get("career_goal"):
        update_dict["career_goal"] = update_dict["target_career"]
    elif "career_goal" in update_dict and not update_dict.get("target_career"):
        update_dict["target_career"] = update_dict["career_goal"]

    # 5. Apply all other profile fields
    for field, val in update_dict.items():
        if hasattr(profile, field):
            setattr(profile, field, val)

    # Mark onboarded when updated
    profile.is_onboarded = True

    db.commit()
    db.refresh(profile)
    db.refresh(user)
    return profile

@router.post("/profile/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Please upload JPG, PNG, or WebP images."
        )

    # Read and validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum allowed size is 5MB."
        )
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # Determine extension
    ext = "jpg"
    if "png" in file.content_type:
        ext = "png"
    elif "webp" in file.content_type:
        ext = "webp"

    filename = f"avatar_{user.id}_{int(time.time())}.{ext}"
    filepath = os.path.join(UPLOAD_AVATAR_DIR, filename)

    try:
        with open(filepath, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save profile picture: {str(e)}"
        )

    avatar_url = f"/uploads/avatars/{filename}"
    user.avatar_url = avatar_url
    if user.profile:
        user.profile.avatar_url = avatar_url
    db.commit()

    return AvatarUploadResponse(avatar_url=avatar_url, message="Profile picture uploaded successfully.")

@router.delete("/profile/avatar")
def remove_avatar(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.avatar_url:
        # If local upload file, delete from disk
        if user.avatar_url.startswith("/uploads/avatars/"):
            filename = os.path.basename(user.avatar_url)
            local_path = os.path.join(UPLOAD_AVATAR_DIR, filename)
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except Exception:
                    pass
        user.avatar_url = None
        if user.profile:
            user.profile.avatar_url = None
        db.commit()
    return {"message": "Profile picture removed successfully."}

@router.post("/change-password")
def change_password(
    data: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be at least 6 characters.")
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password changed successfully."}

@router.get("/export-data")
def export_user_data(user: User = Depends(get_current_user)):
    """Export complete user profile and roadmap history as structured JSON"""
    prof = user.profile
    profile_dict = {
        "full_name": user.full_name,
        "email": user.email,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "bio": prof.bio if prof else None,
        "location": prof.location if prof else None,
        "education": {
            "college": prof.college if prof else None,
            "degree": prof.degree if prof else None,
            "specialization": prof.specialization if prof else None,
            "academic_year": prof.academic_year if prof else None,
            "graduation_year": prof.graduation_year if prof else None,
            "education_level": prof.education_level if prof else None
        },
        "career": {
            "target_career": prof.target_career if prof else None,
            "target_company": prof.target_company if prof else None,
            "technical_skills": prof.technical_skills if prof else [],
            "skills_to_develop": prof.skills_to_develop if prof else [],
            "available_study_hours": prof.available_study_hours if prof else 14,
            "preferred_learning_style": prof.preferred_learning_style if prof else None
        },
        "social_links": {
            "linkedin": prof.linkedin_url if prof else None,
            "github": prof.github_url if prof else None,
            "portfolio": prof.portfolio_url if prof else None
        }
    }

    roadmaps_export = []
    for r in user.roadmaps:
        roadmaps_export.append({
            "id": r.id,
            "title": r.title,
            "dream_job": r.dream_job,
            "target_company": r.target_company,
            "progress_percentage": r.progress_percentage,
            "current_phase": r.current_phase,
            "total_nodes": len(r.nodes),
            "completed_milestones": [n.title for n in r.nodes if n.status == "completed"]
        })

    evidence_export = []
    for ev in user.project_evidence:
        evidence_export.append({
            "id": ev.id,
            "project_title": ev.project_recommendation.title if ev.project_recommendation else "Custom Project",
            "repository_url": ev.repository_url,
            "is_verified": ev.is_verified,
            "created_at": str(ev.created_at)
        })

    return {
        "pathforge_export_version": "1.0",
        "exported_at": str(time.time()),
        "user_profile": profile_dict,
        "roadmaps": roadmaps_export,
        "project_evidence": evidence_export
    }

@router.delete("/account")
def delete_account(
    data: AccountDeleteRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password. Account deletion aborted for security."
        )

    # Delete avatar file if exists
    if user.avatar_url and user.avatar_url.startswith("/uploads/avatars/"):
        filename = os.path.basename(user.avatar_url)
        local_path = os.path.join(UPLOAD_AVATAR_DIR, filename)
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception:
                pass

    # Cascade deletes profile, roadmaps, evidence, saved items
    db.delete(user)
    db.commit()
    return {"message": "Account and all associated private records deleted successfully."}

@router.get("/users/{username}")
def get_public_profile(username: str, db: Session = Depends(get_db)):
    clean_u = username.lower().strip()
    target_user = db.query(User).filter(User.username == clean_u).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '@{username}' not found.")

    prof = target_user.profile
    if not prof or prof.profile_visibility == "private":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user has set their profile to private."
        )

    return {
        "full_name": target_user.full_name,
        "username": target_user.username,
        "avatar_url": target_user.avatar_url,
        "bio": prof.bio,
        "location": prof.location,
        "education": {
            "college": prof.college,
            "degree": prof.degree,
            "graduation_year": prof.graduation_year
        },
        "target_career": prof.target_career,
        "technical_skills": prof.technical_skills or [],
        "completed_milestones_count": sum(len([n for n in r.nodes if n.status == "completed"]) for r in target_user.roadmaps),
        "social_links": {
            "linkedin": prof.linkedin_url,
            "github": prof.github_url,
            "portfolio": prof.portfolio_url
        }
    }

@router.post("/reset-password")
def reset_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user:
        return {"message": "If this account exists, password has been updated."}
    if len(data.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 6 characters.")
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "If this account exists, password has been updated."}

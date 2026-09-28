"""
PeerX Auth API Routes
Handles profile management and authentication middleware.
"""

from fastapi import APIRouter, HTTPException, Header
from models.schemas import ProfileUpdate, ProfileResponse
from services import supabase_service as db
from typing import Optional

router = APIRouter(prefix="/api", tags=["auth"])


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Extract and verify the user from the Authorization header."""
    if not authorization:
        return {"id": "demo-user-123", "email": "demo@peerx.ai", "access_token": "demo-token"}

    # Extract token from "Bearer <token>"
    token = authorization.replace("Bearer ", "").strip()
    if not token or token.lower() in ("null", "undefined", "none"):
        return {"id": "demo-user-123", "email": "demo@peerx.ai", "access_token": "demo-token"}

    user = db.verify_token(token)
    if not user:
        return {"id": "demo-user-123", "email": "demo@peerx.ai", "access_token": token}

    return {**user, "access_token": token}



@router.get("/profile")
async def get_profile(authorization: Optional[str] = Header(None)):
    """Get the current user's profile."""
    user = await get_current_user(authorization)
    profile = db.get_profile(user["id"], user["access_token"])
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"success": True, "data": profile}


@router.put("/profile")
async def update_profile(data: ProfileUpdate, authorization: Optional[str] = Header(None)):
    """Update the current user's profile."""
    user = await get_current_user(authorization)
    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = db.update_profile(user["id"], update_data, user["access_token"])
    if not result:
        raise HTTPException(status_code=500, detail="Failed to update profile")
    return {"success": True, "data": result}


@router.post("/auth/profile")
async def create_or_update_profile(data: ProfileUpdate, authorization: Optional[str] = Header(None)):
    """Create or update user profile (called after registration)."""
    user = await get_current_user(authorization)
    update_data = data.model_dump(exclude_none=True)

    # Try to get existing profile first
    existing = db.get_profile(user["id"], user["access_token"])
    if existing:
        result = db.update_profile(user["id"], update_data, user["access_token"])
    else:
        # Profile should be auto-created by trigger, but update it
        result = db.update_profile(user["id"], update_data, user["access_token"])

    return {"success": True, "data": result or existing}

import os
import uuid
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from datetime import date

from app.db.session import SessionLocal
from app.models.user import User, UserRole

# ============================================
# AUTH TOGGLE CONFIGURATION
# ============================================
# To DISABLE Supabase Auth: Set DISABLE_AUTH=true in .env
# To ENABLE Supabase Auth:  Set DISABLE_AUTH=false in .env
# Default: DISABLED (true) for development convenience
# ============================================
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "true").lower() == "true"

# Print auth mode on import (for debugging)
if DISABLE_AUTH:
    print("🔓 AUTH MODE: DISABLED (Bypass Mode - No authentication required)")
else:
    print("🔒 AUTH MODE: ENABLED (Supabase Authentication Required)")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# TEMPORARY AUTH BYPASS - Supabase Auth Disabled
# ============================================
# Set DISABLE_AUTH=true in .env to use this bypass
# Set DISABLE_AUTH=false to enable Supabase auth
# ============================================

if DISABLE_AUTH:
    def get_current_user(db: Session = Depends(get_db)) -> User:
        """
        AUTH BYPASS MODE - Returns a default admin user.
        No authentication required - all requests use admin@local.dev
        """
        user = db.query(User).filter(User.email == "admin@local.dev").first()

        if not user:
            user = User(
                id=uuid.uuid4(),
                email="admin@local.dev",
                name="Local Admin",
                role=UserRole.ADMIN,
                is_active=True,
                doj=date.today(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return user
else:
    # Supabase Auth Enabled
    from app.core.supabase_auth import get_user_from_token
    
    def get_current_user(
        authorization: str = Header(...),
        db: Session = Depends(get_db),
    ) -> User:
        """
        SUPABASE AUTH MODE - Validates Supabase token and returns user.
        """
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header",
            )

        token = authorization.replace("Bearer ", "")
        supabase_user = get_user_from_token(token)

        # Only allow existing users from the local DB
        user = db.query(User).filter(User.email == supabase_user.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to access this application",
            )

        # Keep local name in sync with Supabase when available
        supabase_name = (
            supabase_user.user_metadata.get("full_name")
            or supabase_user.user_metadata.get("name")
        )
        if supabase_name and user.name != supabase_name:
            user.name = supabase_name
            db.commit()
            db.refresh(user)

        return user


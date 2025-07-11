"""
Users API Endpoints
PowerShare Energy Trading Platform
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.models.user import User
from app.models.energy_transaction import EnergyTransaction
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

# Pydantic models
class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    wallet_address: Optional[str]
    energy_capacity: float
    current_energy: float
    is_active: bool
    reputation_score: float

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    wallet_address: Optional[str] = None
    energy_capacity: Optional[float] = None

class UserStats(BaseModel):
    total_transactions: int
    total_energy_traded: float
    total_earnings: float
    average_rating: float

class UserEnergyUpdate(BaseModel):
    current_energy: float

# API Endpoints
@router.get("/", response_model=List[UserProfile])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of users (paginated)."""
    result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    
    return [
        UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            wallet_address=user.wallet_address,
            energy_capacity=user.energy_capacity,
            current_energy=user.current_energy,
            is_active=user.is_active,
            reputation_score=user.reputation_score
        )
        for user in users
    ]

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        wallet_address=current_user.wallet_address,
        energy_capacity=current_user.energy_capacity,
        current_energy=current_user.current_energy,
        is_active=current_user.is_active,
        reputation_score=current_user.reputation_score
    )

@router.put("/me", response_model=UserProfile)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user profile."""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.wallet_address is not None:
        current_user.wallet_address = user_update.wallet_address
    
    if user_update.energy_capacity is not None:
        if user_update.energy_capacity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Energy capacity cannot be negative"
            )
        current_user.energy_capacity = user_update.energy_capacity
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        wallet_address=current_user.wallet_address,
        energy_capacity=current_user.energy_capacity,
        current_energy=current_user.current_energy,
        is_active=current_user.is_active,
        reputation_score=current_user.reputation_score
    )

@router.put("/me/energy", response_model=UserProfile)
async def update_user_energy(
    energy_update: UserEnergyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's energy level."""
    if energy_update.current_energy < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current energy cannot be negative"
        )
    
    if energy_update.current_energy > current_user.energy_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current energy cannot exceed capacity"
        )
    
    current_user.current_energy = energy_update.current_energy
    await db.commit()
    await db.refresh(current_user)
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        wallet_address=current_user.wallet_address,
        energy_capacity=current_user.energy_capacity,
        current_energy=current_user.current_energy,
        is_active=current_user.is_active,
        reputation_score=current_user.reputation_score
    )

@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's trading statistics."""
    # Get transaction stats
    result = await db.execute(
        select(
            func.count(EnergyTransaction.id).label("total_transactions"),
            func.coalesce(func.sum(EnergyTransaction.amount), 0).label("total_energy_traded"),
            func.coalesce(func.sum(EnergyTransaction.price * EnergyTransaction.amount), 0).label("total_earnings")
        )
        .where(
            (EnergyTransaction.seller_id == current_user.id) |
            (EnergyTransaction.buyer_id == current_user.id)
        )
    )
    
    stats = result.first()
    
    return UserStats(
        total_transactions=stats.total_transactions or 0,
        total_energy_traded=float(stats.total_energy_traded or 0),
        total_earnings=float(stats.total_earnings or 0),
        average_rating=current_user.reputation_score
    )

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfile(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        wallet_address=user.wallet_address,
        energy_capacity=user.energy_capacity,
        current_energy=user.current_energy,
        is_active=user.is_active,
        reputation_score=user.reputation_score
    )

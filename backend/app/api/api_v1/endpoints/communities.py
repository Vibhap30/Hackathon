"""
Communities API Endpoints
PowerShare Energy Trading Platform
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.models.community import Community
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

# Pydantic models
class CommunityCreate(BaseModel):
    name: str
    description: str
    location: Optional[str] = None
    community_type: str = "local"
    max_members: int = 100

class CommunityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    max_members: Optional[int] = None

class CommunityResponse(BaseModel):
    id: int
    name: str
    description: str
    location: Optional[str]
    community_type: str
    creator_id: int
    member_count: int
    max_members: int
    total_energy_capacity: float
    total_current_energy: float
    is_active: bool
    created_at: datetime

class CommunityMember(BaseModel):
    id: int
    email: str
    full_name: str
    energy_capacity: float
    current_energy: float
    reputation_score: float
    joined_at: datetime

class CommunityStats(BaseModel):
    total_members: int
    total_transactions: int
    total_energy_traded: float
    average_energy_price: float
    community_efficiency: float

# API Endpoints
@router.get("/", response_model=List[CommunityResponse])
async def get_communities(
    skip: int = 0,
    limit: int = 100,
    community_type: Optional[str] = None,
    location: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of communities."""
    query = select(Community).where(Community.is_active == True)
    
    if community_type:
        query = query.where(Community.community_type == community_type)
    
    if location:
        query = query.where(Community.location.ilike(f"%{location}%"))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    communities = result.scalars().all()
    
    # Get member counts
    community_responses = []
    for community in communities:
        member_count = len(community.members) if community.members else 0
        total_capacity = sum(member.energy_capacity for member in community.members) if community.members else 0
        total_current = sum(member.current_energy for member in community.members) if community.members else 0
        
        community_responses.append(CommunityResponse(
            id=community.id,
            name=community.name,
            description=community.description,
            location=community.location,
            community_type=community.community_type,
            creator_id=community.creator_id,
            member_count=member_count,
            max_members=community.max_members,
            total_energy_capacity=total_capacity,
            total_current_energy=total_current,
            is_active=community.is_active,
            created_at=community.created_at
        ))
    
    return community_responses

@router.post("/", response_model=CommunityResponse, status_code=status.HTTP_201_CREATED)
async def create_community(
    community_data: CommunityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new community."""
    # Validate community type
    valid_types = ["local", "virtual", "cooperative", "enterprise"]
    if community_data.community_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid community type. Must be one of: {', '.join(valid_types)}"
        )
    
    if community_data.max_members < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum members must be at least 1"
        )
    
    new_community = Community(
        name=community_data.name,
        description=community_data.description,
        location=community_data.location,
        community_type=community_data.community_type,
        creator_id=current_user.id,
        max_members=community_data.max_members,
        is_active=True
    )
    
    db.add(new_community)
    await db.commit()
    await db.refresh(new_community)
    
    # Add creator as first member
    new_community.members.append(current_user)
    await db.commit()
    
    return CommunityResponse(
        id=new_community.id,
        name=new_community.name,
        description=new_community.description,
        location=new_community.location,
        community_type=new_community.community_type,
        creator_id=new_community.creator_id,
        member_count=1,
        max_members=new_community.max_members,
        total_energy_capacity=current_user.energy_capacity,
        total_current_energy=current_user.current_energy,
        is_active=new_community.is_active,
        created_at=new_community.created_at
    )

@router.get("/{community_id}", response_model=CommunityResponse)
async def get_community(
    community_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific community."""
    result = await db.execute(
        select(Community)
        .options(selectinload(Community.members))
        .where(Community.id == community_id, Community.is_active == True)
    )
    community = result.scalar_one_or_none()
    
    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found"
        )
    
    member_count = len(community.members) if community.members else 0
    total_capacity = sum(member.energy_capacity for member in community.members) if community.members else 0
    total_current = sum(member.current_energy for member in community.members) if community.members else 0
    
    return CommunityResponse(
        id=community.id,
        name=community.name,
        description=community.description,
        location=community.location,
        community_type=community.community_type,
        creator_id=community.creator_id,
        member_count=member_count,
        max_members=community.max_members,
        total_energy_capacity=total_capacity,
        total_current_energy=total_current,
        is_active=community.is_active,
        created_at=community.created_at
    )

@router.put("/{community_id}", response_model=CommunityResponse)
async def update_community(
    community_id: int,
    community_update: CommunityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update community (only creator can update)."""
    result = await db.execute(
        select(Community)
        .options(selectinload(Community.members))
        .where(Community.id == community_id, Community.is_active == True)
    )
    community = result.scalar_one_or_none()
    
    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found"
        )
    
    if community.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the community creator can update the community"
        )
    
    if community_update.name is not None:
        community.name = community_update.name
    
    if community_update.description is not None:
        community.description = community_update.description
    
    if community_update.location is not None:
        community.location = community_update.location
    
    if community_update.max_members is not None:
        if community_update.max_members < len(community.members):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set max members below current member count"
            )
        community.max_members = community_update.max_members
    
    await db.commit()
    await db.refresh(community)
    
    member_count = len(community.members) if community.members else 0
    total_capacity = sum(member.energy_capacity for member in community.members) if community.members else 0
    total_current = sum(member.current_energy for member in community.members) if community.members else 0
    
    return CommunityResponse(
        id=community.id,
        name=community.name,
        description=community.description,
        location=community.location,
        community_type=community.community_type,
        creator_id=community.creator_id,
        member_count=member_count,
        max_members=community.max_members,
        total_energy_capacity=total_capacity,
        total_current_energy=total_current,
        is_active=community.is_active,
        created_at=community.created_at
    )

@router.post("/{community_id}/join")
async def join_community(
    community_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a community."""
    result = await db.execute(
        select(Community)
        .options(selectinload(Community.members))
        .where(Community.id == community_id, Community.is_active == True)
    )
    community = result.scalar_one_or_none()
    
    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found"
        )
    
    # Check if user is already a member
    if current_user in community.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this community"
        )
    
    # Check if community is at capacity
    if len(community.members) >= community.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Community is at maximum capacity"
        )
    
    # Add user to community
    community.members.append(current_user)
    await db.commit()
    
    return {"message": "Successfully joined community", "community_name": community.name}

@router.post("/{community_id}/leave")
async def leave_community(
    community_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Leave a community."""
    result = await db.execute(
        select(Community)
        .options(selectinload(Community.members))
        .where(Community.id == community_id, Community.is_active == True)
    )
    community = result.scalar_one_or_none()
    
    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found"
        )
    
    # Check if user is a member
    if current_user not in community.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a member of this community"
        )
    
    # Creator cannot leave their own community (they must transfer ownership first)
    if community.creator_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Community creator cannot leave. Transfer ownership first."
        )
    
    # Remove user from community
    community.members.remove(current_user)
    await db.commit()
    
    return {"message": "Successfully left community", "community_name": community.name}

@router.get("/{community_id}/members", response_model=List[CommunityMember])
async def get_community_members(
    community_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get community members."""
    result = await db.execute(
        select(Community)
        .options(selectinload(Community.members))
        .where(Community.id == community_id, Community.is_active == True)
    )
    community = result.scalar_one_or_none()
    
    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found"
        )
    
    # Check if current user is a member to view member list
    if current_user not in community.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only community members can view the member list"
        )
    
    return [
        CommunityMember(
            id=member.id,
            email=member.email,
            full_name=member.full_name,
            energy_capacity=member.energy_capacity,
            current_energy=member.current_energy,
            reputation_score=member.reputation_score,
            joined_at=member.created_at  # Simplified - would need join table in production
        )
        for member in community.members
    ]

@router.get("/{community_id}/stats", response_model=CommunityStats)
async def get_community_stats(
    community_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get community statistics."""
    result = await db.execute(
        select(Community)
        .options(selectinload(Community.members))
        .where(Community.id == community_id, Community.is_active == True)
    )
    community = result.scalar_one_or_none()
    
    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found"
        )
    
    # Check if current user is a member to view stats
    if current_user not in community.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only community members can view community stats"
        )
    
    # Calculate stats (simplified for demo)
    total_members = len(community.members)
    total_capacity = sum(member.energy_capacity for member in community.members)
    total_current = sum(member.current_energy for member in community.members)
    
    return CommunityStats(
        total_members=total_members,
        total_transactions=0,  # Would need to calculate from EnergyTransaction table
        total_energy_traded=0.0,  # Would need to calculate from EnergyTransaction table
        average_energy_price=0.0,  # Would need to calculate from EnergyTransaction table
        community_efficiency=total_current / max(total_capacity, 1) * 100
    )

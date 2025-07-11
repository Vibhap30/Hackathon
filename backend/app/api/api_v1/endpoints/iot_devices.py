"""
IoT Devices API Endpoints
PowerShare Energy Trading Platform
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.models.iot_device import IoTDevice
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

# Pydantic models
class IoTDeviceCreate(BaseModel):
    device_type: str
    name: str
    location: Optional[str] = None
    specifications: dict = {}

class IoTDeviceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    specifications: Optional[dict] = None
    is_active: Optional[bool] = None

class IoTDeviceResponse(BaseModel):
    id: int
    user_id: int
    device_type: str
    name: str
    location: Optional[str]
    specifications: dict
    energy_production: float
    energy_consumption: float
    status: str
    is_active: bool
    last_reading_at: Optional[datetime]
    created_at: datetime

class DeviceReading(BaseModel):
    energy_production: float
    energy_consumption: float
    status: str = "operational"
    metadata: dict = {}

class DeviceStats(BaseModel):
    total_production: float
    total_consumption: float
    efficiency_ratio: float
    uptime_percentage: float

# API Endpoints
@router.get("/", response_model=List[IoTDeviceResponse])
async def get_user_devices(
    skip: int = 0,
    limit: int = 100,
    device_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's IoT devices."""
    query = select(IoTDevice).where(IoTDevice.user_id == current_user.id)
    
    if device_type:
        query = query.where(IoTDevice.device_type == device_type)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    devices = result.scalars().all()
    
    return [
        IoTDeviceResponse(
            id=device.id,
            user_id=device.user_id,
            device_type=device.device_type,
            name=device.name,
            location=device.location,
            specifications=device.specifications,
            energy_production=device.energy_production,
            energy_consumption=device.energy_consumption,
            status=device.status,
            is_active=device.is_active,
            last_reading_at=device.last_reading_at,
            created_at=device.created_at
        )
        for device in devices
    ]

@router.post("/", response_model=IoTDeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: IoTDeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new IoT device."""
    # Validate device type
    valid_types = ["solar_panel", "wind_turbine", "battery", "smart_meter", "ev_charger", "heat_pump"]
    if device_data.device_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid device type. Must be one of: {', '.join(valid_types)}"
        )
    
    new_device = IoTDevice(
        user_id=current_user.id,
        device_type=device_data.device_type,
        name=device_data.name,
        location=device_data.location,
        specifications=device_data.specifications,
        energy_production=0.0,
        energy_consumption=0.0,
        status="offline",
        is_active=True
    )
    
    db.add(new_device)
    await db.commit()
    await db.refresh(new_device)
    
    return IoTDeviceResponse(
        id=new_device.id,
        user_id=new_device.user_id,
        device_type=new_device.device_type,
        name=new_device.name,
        location=new_device.location,
        specifications=new_device.specifications,
        energy_production=new_device.energy_production,
        energy_consumption=new_device.energy_consumption,
        status=new_device.status,
        is_active=new_device.is_active,
        last_reading_at=new_device.last_reading_at,
        created_at=new_device.created_at
    )

@router.get("/{device_id}", response_model=IoTDeviceResponse)
async def get_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific IoT device."""
    result = await db.execute(
        select(IoTDevice).where(
            IoTDevice.id == device_id,
            IoTDevice.user_id == current_user.id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return IoTDeviceResponse(
        id=device.id,
        user_id=device.user_id,
        device_type=device.device_type,
        name=device.name,
        location=device.location,
        specifications=device.specifications,
        energy_production=device.energy_production,
        energy_consumption=device.energy_consumption,
        status=device.status,
        is_active=device.is_active,
        last_reading_at=device.last_reading_at,
        created_at=device.created_at
    )

@router.put("/{device_id}", response_model=IoTDeviceResponse)
async def update_device(
    device_id: int,
    device_update: IoTDeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update IoT device."""
    result = await db.execute(
        select(IoTDevice).where(
            IoTDevice.id == device_id,
            IoTDevice.user_id == current_user.id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    if device_update.name is not None:
        device.name = device_update.name
    
    if device_update.location is not None:
        device.location = device_update.location
    
    if device_update.specifications is not None:
        device.specifications = device_update.specifications
    
    if device_update.is_active is not None:
        device.is_active = device_update.is_active
        if not device_update.is_active:
            device.status = "offline"
    
    await db.commit()
    await db.refresh(device)
    
    return IoTDeviceResponse(
        id=device.id,
        user_id=device.user_id,
        device_type=device.device_type,
        name=device.name,
        location=device.location,
        specifications=device.specifications,
        energy_production=device.energy_production,
        energy_consumption=device.energy_consumption,
        status=device.status,
        is_active=device.is_active,
        last_reading_at=device.last_reading_at,
        created_at=device.created_at
    )

@router.post("/{device_id}/readings")
async def update_device_reading(
    device_id: int,
    reading: DeviceReading,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update device energy readings."""
    result = await db.execute(
        select(IoTDevice).where(
            IoTDevice.id == device_id,
            IoTDevice.user_id == current_user.id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    if not device.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update readings for inactive device"
        )
    
    # Update device readings
    device.energy_production = reading.energy_production
    device.energy_consumption = reading.energy_consumption
    device.status = reading.status
    device.last_reading_at = datetime.utcnow()
    
    # Update user's current energy based on device production/consumption
    net_energy = reading.energy_production - reading.energy_consumption
    current_user.current_energy += net_energy
    
    # Ensure user's energy doesn't exceed capacity or go negative
    current_user.current_energy = max(0, min(current_user.current_energy, current_user.energy_capacity))
    
    await db.commit()
    
    return {
        "message": "Device reading updated successfully",
        "net_energy": net_energy,
        "user_current_energy": current_user.current_energy
    }

@router.get("/{device_id}/stats", response_model=DeviceStats)
async def get_device_stats(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get device statistics."""
    result = await db.execute(
        select(IoTDevice).where(
            IoTDevice.id == device_id,
            IoTDevice.user_id == current_user.id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Calculate basic stats (in production, this would be from historical data)
    total_production = device.energy_production * 24 * 30  # Simulate monthly production
    total_consumption = device.energy_consumption * 24 * 30  # Simulate monthly consumption
    efficiency_ratio = total_production / max(total_consumption, 1)  # Avoid division by zero
    uptime_percentage = 95.5 if device.status == "operational" else 0.0  # Simulated uptime
    
    return DeviceStats(
        total_production=total_production,
        total_consumption=total_consumption,
        efficiency_ratio=efficiency_ratio,
        uptime_percentage=uptime_percentage
    )

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete IoT device."""
    result = await db.execute(
        select(IoTDevice).where(
            IoTDevice.id == device_id,
            IoTDevice.user_id == current_user.id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    await db.delete(device)
    await db.commit()
    
    return None

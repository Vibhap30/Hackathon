"""
Energy Trading API Endpoints
PowerShare Energy Trading Platform
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.energy_transaction import EnergyTransaction, EnergyOffer, EnergyType, TransactionStatus
from app.services.websocket_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


@router.get("/transactions", response_model=List[dict])
async def get_energy_transactions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TransactionStatus] = None,
    energy_type: Optional[EnergyType] = None,
    db: Session = Depends(get_db)
):
    """Get energy transactions with optional filtering"""
    query = db.query(EnergyTransaction)
    
    if status:
        query = query.filter(EnergyTransaction.status == status)
    if energy_type:
        query = query.filter(EnergyTransaction.energy_type == energy_type)
    
    transactions = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": t.id,
            "transaction_id": t.transaction_id,
            "seller_id": t.seller_id,
            "buyer_id": t.buyer_id,
            "energy_amount_kwh": t.energy_amount_kwh,
            "energy_type": t.energy_type,
            "price_per_kwh": t.price_per_kwh,
            "total_amount": t.total_amount,
            "status": t.status,
            "created_at": t.created_at,
            "carbon_offset_kg": t.carbon_offset_kg,
            "distance_km": t.distance_km
        }
        for t in transactions
    ]


@router.post("/transactions", response_model=dict)
async def create_energy_transaction(
    seller_id: int,
    buyer_id: int,
    energy_amount_kwh: float,
    price_per_kwh: float,
    energy_type: EnergyType = EnergyType.SOLAR,
    db: Session = Depends(get_db)
):
    """Create a new energy transaction"""
    
    # Calculate total amount and platform fee
    total_amount = energy_amount_kwh * price_per_kwh
    platform_fee = total_amount * 0.02  # 2% platform fee
    carbon_offset = energy_amount_kwh * 0.45  # Approximate CO2 offset
    
    transaction = EnergyTransaction(
        transaction_id=str(uuid.uuid4()),
        seller_id=seller_id,
        buyer_id=buyer_id,
        energy_amount_kwh=energy_amount_kwh,
        energy_type=energy_type,
        price_per_kwh=price_per_kwh,
        total_amount=total_amount,
        platform_fee=platform_fee,
        carbon_offset_kg=carbon_offset,
        status=TransactionStatus.PENDING
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Send real-time update via WebSocket
    await manager.send_energy_update({
        "action": "transaction_created",
        "transaction_id": transaction.transaction_id,
        "energy_amount_kwh": energy_amount_kwh,
        "price_per_kwh": price_per_kwh,
        "energy_type": energy_type
    })
    
    return {
        "message": "Energy transaction created successfully",
        "transaction_id": transaction.transaction_id,
        "total_amount": total_amount,
        "platform_fee": platform_fee,
        "carbon_offset_kg": carbon_offset
    }


@router.get("/offers", response_model=List[dict])
async def get_energy_offers(
    skip: int = 0,
    limit: int = 100,
    energy_type: Optional[EnergyType] = None,
    max_price: Optional[float] = None,
    max_distance: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get available energy offers with filtering"""
    query = db.query(EnergyOffer).filter(EnergyOffer.is_active == True)
    
    if energy_type:
        query = query.filter(EnergyOffer.energy_type == energy_type)
    if max_price:
        query = query.filter(EnergyOffer.price_per_kwh <= max_price)
    if max_distance:
        query = query.filter(EnergyOffer.max_distance_km <= max_distance)
    
    offers = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": o.id,
            "offer_id": o.offer_id,
            "seller_id": o.seller_id,
            "energy_amount_kwh": o.energy_amount_kwh,
            "energy_type": o.energy_type,
            "price_per_kwh": o.price_per_kwh,
            "available_from": o.available_from,
            "available_until": o.available_until,
            "max_distance_km": o.max_distance_km,
            "auto_accept": o.auto_accept
        }
        for o in offers
    ]


@router.post("/offers", response_model=dict)
async def create_energy_offer(
    seller_id: int,
    energy_amount_kwh: float,
    price_per_kwh: float,
    energy_type: EnergyType = EnergyType.SOLAR,
    max_distance_km: float = 25.0,
    auto_accept: bool = False,
    db: Session = Depends(get_db)
):
    """Create a new energy offer"""
    
    offer = EnergyOffer(
        offer_id=str(uuid.uuid4()),
        seller_id=seller_id,
        energy_amount_kwh=energy_amount_kwh,
        energy_type=energy_type,
        price_per_kwh=price_per_kwh,
        max_distance_km=max_distance_km,
        auto_accept=auto_accept,
        available_from=datetime.now(),
        available_until=datetime.now().replace(hour=23, minute=59, second=59)
    )
    
    db.add(offer)
    db.commit()
    db.refresh(offer)
    
    # Send real-time update via WebSocket
    await manager.send_market_update({
        "action": "offer_created",
        "offer_id": offer.offer_id,
        "energy_amount_kwh": energy_amount_kwh,
        "price_per_kwh": price_per_kwh,
        "energy_type": energy_type
    })
    
    return {
        "message": "Energy offer created successfully",
        "offer_id": offer.offer_id,
        "estimated_revenue": energy_amount_kwh * price_per_kwh
    }


@router.get("/market-stats", response_model=dict)
async def get_market_statistics(db: Session = Depends(get_db)):
    """Get energy market statistics"""
    
    # Get basic transaction stats
    total_transactions = db.query(EnergyTransaction).count()
    completed_transactions = db.query(EnergyTransaction).filter(
        EnergyTransaction.status == TransactionStatus.COMPLETED
    ).count()
    
    active_offers = db.query(EnergyOffer).filter(EnergyOffer.is_active == True).count()
    
    # Calculate averages
    avg_price_result = db.query(
        db.func.avg(EnergyTransaction.price_per_kwh)
    ).filter(
        EnergyTransaction.status == TransactionStatus.COMPLETED
    ).scalar()
    
    avg_price = float(avg_price_result) if avg_price_result else 0.0
    
    total_energy_traded = db.query(
        db.func.sum(EnergyTransaction.energy_amount_kwh)
    ).filter(
        EnergyTransaction.status == TransactionStatus.COMPLETED
    ).scalar() or 0.0
    
    total_carbon_offset = db.query(
        db.func.sum(EnergyTransaction.carbon_offset_kg)
    ).filter(
        EnergyTransaction.status == TransactionStatus.COMPLETED
    ).scalar() or 0.0
    
    return {
        "total_transactions": total_transactions,
        "completed_transactions": completed_transactions,
        "active_offers": active_offers,
        "average_price_per_kwh": round(avg_price, 4),
        "total_energy_traded_kwh": round(float(total_energy_traded), 2),
        "total_carbon_offset_kg": round(float(total_carbon_offset), 2),
        "market_activity_score": min(10.0, (completed_transactions / max(1, total_transactions)) * 10)
    }


@router.put("/transactions/{transaction_id}/status", response_model=dict)
async def update_transaction_status(
    transaction_id: str,
    new_status: TransactionStatus,
    db: Session = Depends(get_db)
):
    """Update the status of an energy transaction"""
    
    transaction = db.query(EnergyTransaction).filter(
        EnergyTransaction.transaction_id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    old_status = transaction.status
    transaction.status = new_status
    
    if new_status == TransactionStatus.COMPLETED:
        transaction.settlement_time = datetime.now()
    
    db.commit()
    
    # Send real-time update via WebSocket
    await manager.send_energy_update({
        "action": "transaction_status_updated",
        "transaction_id": transaction_id,
        "old_status": old_status,
        "new_status": new_status
    })
    
    return {
        "message": "Transaction status updated successfully",
        "transaction_id": transaction_id,
        "new_status": new_status
    }

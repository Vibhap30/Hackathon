"""
Energy Transaction Model
PowerShare Energy Trading Platform
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.core.database import Base


class EnergyType(str, enum.Enum):
    SOLAR = "solar"
    WIND = "wind"
    HYDRO = "hydro"
    MIXED = "mixed"
    GRID = "grid"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TimeOfDay(str, enum.Enum):
    PEAK = "peak"
    OFF_PEAK = "off_peak"
    SHOULDER = "shoulder"


class EnergyTransaction(Base):
    __tablename__ = "energy_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    
    # Trading Parties
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Energy Details
    energy_amount_kwh = Column(Float, nullable=False)
    energy_type = Column(SQLEnum(EnergyType), default=EnergyType.SOLAR)
    price_per_kwh = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Transaction Metadata
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    time_of_day = Column(SQLEnum(TimeOfDay), default=TimeOfDay.OFF_PEAK)
    distance_km = Column(Float)
    
    # Blockchain & Smart Contracts
    smart_contract_hash = Column(String)
    blockchain_tx_hash = Column(String)
    smart_contract_address = Column(String)
    
    # Environmental Impact
    carbon_offset_kg = Column(Float, default=0.0)
    renewable_certificate_id = Column(String)
    
    # Financial Details
    platform_fee = Column(Float, default=0.0)
    grid_congestion_factor = Column(Float, default=1.0)
    
    # AI & Optimization
    ai_recommended = Column(Boolean, default=False)
    optimization_score = Column(Float)
    
    # Beckn Protocol Integration
    beckn_order_id = Column(String)
    beckn_fulfillment_id = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    scheduled_delivery_time = Column(DateTime(timezone=True))
    actual_delivery_time = Column(DateTime(timezone=True))
    settlement_time = Column(DateTime(timezone=True))
    
    # Additional Data
    extra_data = Column(Text)  # JSON field for additional data
    notes = Column(Text)
    
    # Relationships
    seller = relationship("User", foreign_keys=[seller_id], back_populates="energy_transactions_as_seller")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="energy_transactions_as_buyer")
    
    def __repr__(self):
        return f"<EnergyTransaction(id={self.id}, seller_id={self.seller_id}, buyer_id={self.buyer_id}, amount={self.energy_amount_kwh}kWh)>"


class EnergyOffer(Base):
    __tablename__ = "energy_offers"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(String, unique=True, index=True, nullable=False)
    
    # Seller Information
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Energy Details
    energy_amount_kwh = Column(Float, nullable=False)
    energy_type = Column(SQLEnum(EnergyType), default=EnergyType.SOLAR)
    price_per_kwh = Column(Float, nullable=False)
    
    # Availability
    available_from = Column(DateTime(timezone=True), nullable=False)
    available_until = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Location & Distance
    max_distance_km = Column(Float, default=25.0)
    
    # Matching Criteria
    preferred_buyer_type = Column(String)  # community, individual, utility
    minimum_quantity_kwh = Column(Float, default=1.0)
    
    # AI & Automation
    auto_accept = Column(Boolean, default=False)
    ai_pricing = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    seller = relationship("User")
    
    def __repr__(self):
        return f"<EnergyOffer(id={self.id}, seller_id={self.seller_id}, amount={self.energy_amount_kwh}kWh, price={self.price_per_kwh})>"

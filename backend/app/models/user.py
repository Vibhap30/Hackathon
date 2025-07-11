"""
User Model
PowerShare Energy Trading Platform
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum as SQLEnum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.core.database import Base


class UserType(str, enum.Enum):
    PROSUMER = "prosumer"
    CONSUMER = "consumer"
    UTILITY = "utility"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Profile Information
    user_type = Column(SQLEnum(UserType), default=UserType.CONSUMER)
    phone = Column(String)
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String, default="USA")
    
    # Location for energy trading
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Energy Profile
    household_size = Column(Integer, default=1)
    monthly_energy_consumption_kwh = Column(Float, default=0.0)
    solar_panel_capacity_kw = Column(Float, default=0.0)
    battery_capacity_kwh = Column(Float, default=0.0)
    ev_ownership = Column(Boolean, default=False)
    smart_home_devices = Column(Integer, default=0)
    
    # Financial Information
    annual_income = Column(Integer)
    credit_rating = Column(String)
    wallet_address = Column(String)  # Blockchain wallet
    
    # Preferences
    preferred_energy_source = Column(String, default="any")
    environmental_score = Column(Float, default=5.0)
    community_participation_level = Column(String, default="medium")
    
    # Platform Metadata
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    energy_transactions_as_seller = relationship(
        "EnergyTransaction", 
        foreign_keys="EnergyTransaction.seller_id",
        back_populates="seller"
    )
    energy_transactions_as_buyer = relationship(
        "EnergyTransaction", 
        foreign_keys="EnergyTransaction.buyer_id",
        back_populates="buyer"
    )
    iot_devices = relationship("IoTDevice", back_populates="owner")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, type={self.user_type})>"

"""
Community Model
PowerShare Energy Trading Platform
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum as SQLEnum, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.core.database import Base

# Association table for many-to-many relationship between users and communities
community_members = Table(
    'community_members',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('community_id', Integer, ForeignKey('communities.id'), primary_key=True),
    Column('joined_at', DateTime(timezone=True), server_default=func.now()),
    Column('role', String, default='member'),  # member, admin, moderator
    Column('is_active', Boolean, default=True)
)


class CommunityType(str, enum.Enum):
    URBAN = "urban"
    SUBURBAN = "suburban"
    RURAL = "rural"
    INDUSTRIAL = "industrial"
    RESIDENTIAL = "residential"
    MIXED = "mixed"


class Community(Base):
    __tablename__ = "communities"

    id = Column(Integer, primary_key=True, index=True)
    community_id = Column(String, unique=True, index=True, nullable=False)
    
    # Basic Information
    name = Column(String, nullable=False)
    description = Column(Text)
    community_type = Column(SQLEnum(CommunityType), default=CommunityType.RESIDENTIAL)
    
    # Location
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String, default="USA")
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Community Metrics
    total_households = Column(Integer, default=0)
    prosumer_percentage = Column(Float, default=0.0)
    total_solar_capacity_kw = Column(Float, default=0.0)
    community_battery_kwh = Column(Float, default=0.0)
    
    # Energy Independence
    grid_independence_percentage = Column(Float, default=0.0)
    renewable_percentage = Column(Float, default=0.0)
    energy_storage_capacity_mwh = Column(Float, default=0.0)
    
    # Economic Metrics
    average_energy_price_kwh = Column(Float, default=0.12)
    total_energy_traded_kwh = Column(Float, default=0.0)
    total_trading_volume_usd = Column(Float, default=0.0)
    
    # Environmental Impact
    carbon_reduction_tons_yearly = Column(Float, default=0.0)
    energy_poverty_reduction_percentage = Column(Float, default=0.0)
    
    # Infrastructure
    microgrid_enabled = Column(Boolean, default=False)
    smart_grid_integration = Column(Boolean, default=False)
    ev_charging_stations = Column(Integer, default=0)
    peak_demand_kw = Column(Float, default=0.0)
    
    # Community Features
    resilience_score = Column(Float, default=0.0)
    sustainability_rating = Column(String)
    
    # Management
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    
    # Beckn Protocol Integration
    beckn_provider_id = Column(String)
    beckn_catalog_id = Column(String)
    
    # Timestamps
    established_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional Data
    extra_data = Column(Text)  # JSON field for additional community data
    
    # Relationships
    members = relationship("User", secondary=community_members, backref="communities")
    energy_metrics = relationship("CommunityEnergyMetrics", back_populates="community")
    
    def __repr__(self):
        return f"<Community(id={self.id}, name={self.name}, type={self.community_type})>"


class CommunityEnergyMetrics(Base):
    __tablename__ = "community_energy_metrics"

    id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey("communities.id"), nullable=False)
    
    # Time Period
    date = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String, default="daily")  # daily, weekly, monthly
    
    # Energy Generation
    total_generation_kwh = Column(Float, default=0.0)
    solar_generation_kwh = Column(Float, default=0.0)
    wind_generation_kwh = Column(Float, default=0.0)
    other_renewable_kwh = Column(Float, default=0.0)
    
    # Energy Consumption
    total_consumption_kwh = Column(Float, default=0.0)
    residential_consumption_kwh = Column(Float, default=0.0)
    commercial_consumption_kwh = Column(Float, default=0.0)
    
    # Grid Interaction
    grid_import_kwh = Column(Float, default=0.0)
    grid_export_kwh = Column(Float, default=0.0)
    net_grid_flow_kwh = Column(Float, default=0.0)
    
    # Trading Activity
    internal_trading_kwh = Column(Float, default=0.0)
    external_trading_kwh = Column(Float, default=0.0)
    trading_transactions_count = Column(Integer, default=0)
    average_trading_price_kwh = Column(Float, default=0.0)
    
    # Storage
    battery_charge_kwh = Column(Float, default=0.0)
    battery_discharge_kwh = Column(Float, default=0.0)
    storage_efficiency_percentage = Column(Float, default=0.0)
    
    # Environmental Impact
    carbon_offset_kg = Column(Float, default=0.0)
    renewable_energy_percentage = Column(Float, default=0.0)
    
    # Economic Impact
    energy_cost_savings_usd = Column(Float, default=0.0)
    trading_revenue_usd = Column(Float, default=0.0)
    grid_services_revenue_usd = Column(Float, default=0.0)
    
    # Performance Metrics
    energy_independence_score = Column(Float, default=0.0)
    grid_stability_contribution = Column(Float, default=0.0)
    demand_response_participation_percentage = Column(Float, default=0.0)
    
    # Weather Data
    average_temperature_celsius = Column(Float)
    solar_irradiance_kwh_m2 = Column(Float)
    wind_speed_ms = Column(Float)
    weather_condition = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    community = relationship("Community", back_populates="energy_metrics")
    
    def __repr__(self):
        return f"<CommunityEnergyMetrics(id={self.id}, community_id={self.community_id}, date={self.date})>"

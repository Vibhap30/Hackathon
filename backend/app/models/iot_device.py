"""
IoT Device Model
PowerShare Energy Trading Platform
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.core.database import Base


class DeviceType(str, enum.Enum):
    SMART_THERMOSTAT = "smart_thermostat"
    SMART_WATER_HEATER = "smart_water_heater"
    EV_CHARGER = "ev_charger"
    SMART_DISHWASHER = "smart_dishwasher"
    SMART_WASHING_MACHINE = "smart_washing_machine"
    SMART_DRYER = "smart_dryer"
    SMART_LIGHTING = "smart_lighting"
    SMART_REFRIGERATOR = "smart_refrigerator"
    POOL_PUMP = "pool_pump"
    AIR_CONDITIONING = "air_conditioning"
    HEAT_PUMP = "heat_pump"
    SMART_TV = "smart_tv"
    SOLAR_INVERTER = "solar_inverter"
    BATTERY_STORAGE = "battery_storage"
    SMART_METER = "smart_meter"


class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class SchedulingPreference(str, enum.Enum):
    OFF_PEAK = "off_peak"
    ANYTIME = "anytime"
    PEAK_AVOID = "peak_avoid"
    MANUAL = "manual"


class IoTDevice(Base):
    __tablename__ = "iot_devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    
    # Owner Information
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Device Information
    device_name = Column(String, nullable=False)
    device_type = Column(SQLEnum(DeviceType), nullable=False)
    manufacturer = Column(String)
    model = Column(String)
    firmware_version = Column(String)
    
    # Technical Specifications
    power_rating_kw = Column(Float, default=0.0)
    energy_efficiency_rating = Column(String)
    estimated_daily_consumption_kwh = Column(Float, default=0.0)
    
    # Status & Control
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.OFFLINE)
    is_controllable = Column(Boolean, default=True)
    automation_enabled = Column(Boolean, default=False)
    scheduling_preference = Column(SQLEnum(SchedulingPreference), default=SchedulingPreference.ANYTIME)
    
    # Location
    room = Column(String)
    floor = Column(String)
    
    # Network & Communication
    ip_address = Column(String)
    mac_address = Column(String)
    mqtt_topic = Column(String)
    communication_protocol = Column(String, default="MQTT")
    
    # Current State
    current_power_consumption_kw = Column(Float, default=0.0)
    current_temperature = Column(Float)
    current_settings = Column(Text)  # JSON field
    
    # Security
    encryption_enabled = Column(Boolean, default=True)
    last_security_update = Column(DateTime(timezone=True))
    
    # AI & Optimization
    ai_optimization_enabled = Column(Boolean, default=False)
    learning_mode = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True))
    last_maintenance = Column(DateTime(timezone=True))
    
    # Relationships
    owner = relationship("User", back_populates="iot_devices")
    device_data = relationship("DeviceData", back_populates="device")
    
    def __repr__(self):
        return f"<IoTDevice(id={self.id}, name={self.device_name}, type={self.device_type}, owner_id={self.owner_id})>"


class DeviceData(Base):
    __tablename__ = "device_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("iot_devices.id"), nullable=False)
    
    # Energy Metrics
    power_consumption_kwh = Column(Float, default=0.0)
    usage_hours = Column(Float, default=0.0)
    peak_power_kw = Column(Float, default=0.0)
    
    # Environmental Data
    temperature_celsius = Column(Float)
    humidity_percentage = Column(Float)
    
    # Cost & Efficiency
    energy_cost_usd = Column(Float, default=0.0)
    carbon_footprint_kg = Column(Float, default=0.0)
    efficiency_score = Column(Float)
    
    # Operational Data
    operating_mode = Column(String)
    schedule_adherence = Column(Float)
    error_count = Column(Integer, default=0)
    
    # AI Predictions
    predicted_consumption_kwh = Column(Float)
    optimization_savings_usd = Column(Float)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    date = Column(DateTime(timezone=True))
    
    # Additional data (JSON)
    extra_data = Column(Text)
    
    # Relationships
    device = relationship("IoTDevice", back_populates="device_data")
    
    def __repr__(self):
        return f"<DeviceData(id={self.id}, device_id={self.device_id}, consumption={self.power_consumption_kwh}kWh)>"

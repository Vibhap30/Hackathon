"""
IoT Microservice for PowerShare Platform
Handles IoT device management, readings, and real-time data processing
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PowerShare IoT Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/powershare")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Redis client for real-time data
redis_client = redis.from_url(REDIS_URL)

# Pydantic models
class DeviceReading(BaseModel):
    device_id: str
    energy_production: float
    energy_consumption: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    battery_level: Optional[float] = None
    status: str = "active"
    metadata: Optional[Dict[str, Any]] = {}
    timestamp: Optional[datetime] = None

class DeviceConfig(BaseModel):
    device_id: str
    name: str
    device_type: str
    location: Optional[str] = None
    user_id: int
    specifications: Dict[str, Any]
    reporting_interval: int = 300  # seconds
    thresholds: Dict[str, float] = {}

class AlertRule(BaseModel):
    device_id: str
    parameter: str
    condition: str  # "gt", "lt", "eq", "ne"
    threshold: float
    message: str
    severity: str = "warning"  # "info", "warning", "critical"

# Database helper functions
def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def execute_query(query: str, params: tuple = None, fetch: bool = False):
    """Execute database query"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        
        if fetch:
            result = cursor.fetchall()
            conn.close()
            return result
        else:
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")

# Real-time data processing
class IoTDataProcessor:
    def __init__(self):
        self.alert_rules = {}
        self.device_configs = {}
    
    async def process_reading(self, reading: DeviceReading):
        """Process incoming IoT reading"""
        try:
            # Store in database
            await self.store_reading(reading)
            
            # Cache latest reading in Redis
            await self.cache_latest_reading(reading)
            
            # Check alert rules
            await self.check_alerts(reading)
            
            # Update device statistics
            await self.update_device_stats(reading)
            
            # Publish to real-time subscribers
            await self.publish_reading(reading)
            
        except Exception as e:
            logger.error(f"Error processing reading: {e}")
    
    async def store_reading(self, reading: DeviceReading):
        """Store reading in database"""
        query = """
            INSERT INTO iot_readings 
            (device_id, energy_production, energy_consumption, temperature, 
             humidity, battery_level, status, metadata, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        timestamp = reading.timestamp or datetime.utcnow()
        params = (
            reading.device_id,
            reading.energy_production,
            reading.energy_consumption,
            reading.temperature,
            reading.humidity,
            reading.battery_level,
            reading.status,
            json.dumps(reading.metadata) if reading.metadata else None,
            timestamp
        )
        execute_query(query, params)
    
    async def cache_latest_reading(self, reading: DeviceReading):
        """Cache latest reading in Redis"""
        key = f"device_latest:{reading.device_id}"
        data = reading.dict()
        data['timestamp'] = data['timestamp'].isoformat() if data['timestamp'] else datetime.utcnow().isoformat()
        redis_client.setex(key, 3600, json.dumps(data))  # Cache for 1 hour
    
    async def check_alerts(self, reading: DeviceReading):
        """Check if reading triggers any alerts"""
        device_rules = self.alert_rules.get(reading.device_id, [])
        
        for rule in device_rules:
            value = getattr(reading, rule.parameter, None)
            if value is None:
                continue
            
            triggered = False
            if rule.condition == "gt" and value > rule.threshold:
                triggered = True
            elif rule.condition == "lt" and value < rule.threshold:
                triggered = True
            elif rule.condition == "eq" and value == rule.threshold:
                triggered = True
            elif rule.condition == "ne" and value != rule.threshold:
                triggered = True
            
            if triggered:
                await self.send_alert(reading.device_id, rule, value)
    
    async def send_alert(self, device_id: str, rule: AlertRule, value: float):
        """Send alert notification"""
        alert_data = {
            "device_id": device_id,
            "parameter": rule.parameter,
            "value": value,
            "threshold": rule.threshold,
            "message": rule.message,
            "severity": rule.severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish alert to Redis channel
        redis_client.publish(f"alerts:{device_id}", json.dumps(alert_data))
        
        # Store alert in database
        query = """
            INSERT INTO iot_alerts 
            (device_id, parameter, value, threshold, message, severity, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (device_id, rule.parameter, value, rule.threshold, rule.message, rule.severity, datetime.utcnow())
        execute_query(query, params)
    
    async def update_device_stats(self, reading: DeviceReading):
        """Update device statistics"""
        # Update latest values in device table
        query = """
            UPDATE iot_devices 
            SET energy_production = %s, energy_consumption = %s, 
                status = %s, last_reading_at = %s
            WHERE device_id = %s
        """
        params = (
            reading.energy_production,
            reading.energy_consumption,
            reading.status,
            reading.timestamp or datetime.utcnow(),
            reading.device_id
        )
        execute_query(query, params)
    
    async def publish_reading(self, reading: DeviceReading):
        """Publish reading to real-time subscribers"""
        channel = f"device_readings:{reading.device_id}"
        data = reading.dict()
        data['timestamp'] = data['timestamp'].isoformat() if data['timestamp'] else datetime.utcnow().isoformat()
        redis_client.publish(channel, json.dumps(data))

# Initialize data processor
data_processor = IoTDataProcessor()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "iot-service", "timestamp": datetime.utcnow()}

@app.post("/readings")
async def submit_reading(reading: DeviceReading, background_tasks: BackgroundTasks):
    """Submit IoT device reading"""
    background_tasks.add_task(data_processor.process_reading, reading)
    return {"message": "Reading accepted for processing", "device_id": reading.device_id}

@app.post("/readings/batch")
async def submit_batch_readings(readings: List[DeviceReading], background_tasks: BackgroundTasks):
    """Submit multiple IoT device readings"""
    for reading in readings:
        background_tasks.add_task(data_processor.process_reading, reading)
    return {"message": f"Batch of {len(readings)} readings accepted for processing"}

@app.get("/devices/{device_id}/readings")
async def get_device_readings(
    device_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100
):
    """Get readings for a specific device"""
    query = """
        SELECT * FROM iot_readings 
        WHERE device_id = %s
    """
    params = [device_id]
    
    if start_time:
        query += " AND timestamp >= %s"
        params.append(start_time)
    
    if end_time:
        query += " AND timestamp <= %s"
        params.append(end_time)
    
    query += " ORDER BY timestamp DESC LIMIT %s"
    params.append(limit)
    
    readings = execute_query(query, tuple(params), fetch=True)
    return {"device_id": device_id, "readings": readings}

@app.get("/devices/{device_id}/latest")
async def get_latest_reading(device_id: str):
    """Get latest reading for a device"""
    # Try Redis cache first
    key = f"device_latest:{device_id}"
    cached_data = redis_client.get(key)
    
    if cached_data:
        return {"device_id": device_id, "reading": json.loads(cached_data)}
    
    # Fallback to database
    query = """
        SELECT * FROM iot_readings 
        WHERE device_id = %s 
        ORDER BY timestamp DESC 
        LIMIT 1
    """
    readings = execute_query(query, (device_id,), fetch=True)
    
    if not readings:
        raise HTTPException(status_code=404, detail="No readings found for device")
    
    return {"device_id": device_id, "reading": readings[0]}

@app.get("/devices/{device_id}/statistics")
async def get_device_statistics(
    device_id: str,
    period: str = "24h"  # 1h, 24h, 7d, 30d
):
    """Get device statistics for a period"""
    # Calculate time window
    now = datetime.utcnow()
    if period == "1h":
        start_time = now - timedelta(hours=1)
    elif period == "24h":
        start_time = now - timedelta(days=1)
    elif period == "7d":
        start_time = now - timedelta(days=7)
    elif period == "30d":
        start_time = now - timedelta(days=30)
    else:
        raise HTTPException(status_code=400, detail="Invalid period")
    
    query = """
        SELECT 
            COUNT(*) as reading_count,
            AVG(energy_production) as avg_production,
            AVG(energy_consumption) as avg_consumption,
            MAX(energy_production) as max_production,
            MAX(energy_consumption) as max_consumption,
            MIN(energy_production) as min_production,
            MIN(energy_consumption) as min_consumption,
            SUM(energy_production) as total_production,
            SUM(energy_consumption) as total_consumption
        FROM iot_readings 
        WHERE device_id = %s AND timestamp >= %s
    """
    
    stats = execute_query(query, (device_id, start_time), fetch=True)
    
    if not stats or not stats[0]['reading_count']:
        return {"device_id": device_id, "period": period, "statistics": None}
    
    return {
        "device_id": device_id,
        "period": period,
        "start_time": start_time.isoformat(),
        "end_time": now.isoformat(),
        "statistics": stats[0]
    }

@app.post("/devices/{device_id}/alerts")
async def create_alert_rule(device_id: str, rule: AlertRule):
    """Create alert rule for device"""
    # Store in database
    query = """
        INSERT INTO iot_alert_rules 
        (device_id, parameter, condition, threshold, message, severity)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    params = (device_id, rule.parameter, rule.condition, rule.threshold, rule.message, rule.severity)
    result = execute_query(query, params, fetch=True)
    
    # Update in-memory rules
    if device_id not in data_processor.alert_rules:
        data_processor.alert_rules[device_id] = []
    data_processor.alert_rules[device_id].append(rule)
    
    return {"message": "Alert rule created", "rule_id": result[0]['id']}

@app.get("/devices/{device_id}/alerts")
async def get_device_alerts(
    device_id: str,
    start_time: Optional[datetime] = None,
    limit: int = 50
):
    """Get alerts for a device"""
    query = """
        SELECT * FROM iot_alerts 
        WHERE device_id = %s
    """
    params = [device_id]
    
    if start_time:
        query += " AND timestamp >= %s"
        params.append(start_time)
    
    query += " ORDER BY timestamp DESC LIMIT %s"
    params.append(limit)
    
    alerts = execute_query(query, tuple(params), fetch=True)
    return {"device_id": device_id, "alerts": alerts}

@app.get("/analytics/energy-production")
async def get_energy_production_analytics(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    group_by: str = "hour"  # hour, day, month
):
    """Get energy production analytics across all devices"""
    if not start_time:
        start_time = datetime.utcnow() - timedelta(days=7)
    if not end_time:
        end_time = datetime.utcnow()
    
    # Determine time grouping
    if group_by == "hour":
        time_trunc = "date_trunc('hour', timestamp)"
    elif group_by == "day":
        time_trunc = "date_trunc('day', timestamp)"
    elif group_by == "month":
        time_trunc = "date_trunc('month', timestamp)"
    else:
        raise HTTPException(status_code=400, detail="Invalid group_by parameter")
    
    query = f"""
        SELECT 
            {time_trunc} as time_period,
            SUM(energy_production) as total_production,
            SUM(energy_consumption) as total_consumption,
            AVG(energy_production) as avg_production,
            AVG(energy_consumption) as avg_consumption,
            COUNT(DISTINCT device_id) as active_devices
        FROM iot_readings 
        WHERE timestamp BETWEEN %s AND %s
        GROUP BY {time_trunc}
        ORDER BY time_period
    """
    
    analytics = execute_query(query, (start_time, end_time), fetch=True)
    
    return {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "group_by": group_by,
        "analytics": analytics
    }

@app.get("/analytics/device-performance")
async def get_device_performance_analytics():
    """Get device performance analytics"""
    query = """
        SELECT 
            device_id,
            COUNT(*) as total_readings,
            AVG(energy_production) as avg_production,
            AVG(energy_consumption) as avg_consumption,
            MAX(timestamp) as last_reading,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_readings,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_readings
        FROM iot_readings 
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
        GROUP BY device_id
        ORDER BY avg_production DESC
    """
    
    performance = execute_query(query, fetch=True)
    
    return {"device_performance": performance}

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("IoT Service starting up...")
    
    # Load alert rules from database
    try:
        query = "SELECT * FROM iot_alert_rules WHERE is_active = true"
        rules = execute_query(query, fetch=True)
        
        for rule_data in rules:
            device_id = rule_data['device_id']
            rule = AlertRule(
                device_id=device_id,
                parameter=rule_data['parameter'],
                condition=rule_data['condition'],
                threshold=rule_data['threshold'],
                message=rule_data['message'],
                severity=rule_data['severity']
            )
            
            if device_id not in data_processor.alert_rules:
                data_processor.alert_rules[device_id] = []
            data_processor.alert_rules[device_id].append(rule)
        
        logger.info(f"Loaded {len(rules)} alert rules")
    except Exception as e:
        logger.warning(f"Could not load alert rules: {e}")

async def cleanup_old_readings():
    """Clean up old readings periodically"""
    while True:
        try:
            # Delete readings older than 90 days
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            query = "DELETE FROM iot_readings WHERE timestamp < %s"
            execute_query(query, (cutoff_date,))
            logger.info("Cleaned up old IoT readings")
        except Exception as e:
            logger.error(f"Error cleaning up old readings: {e}")
        
        # Sleep for 24 hours
        await asyncio.sleep(86400)

@app.on_event("startup")
async def start_cleanup_task():
    """Start background cleanup task"""
    asyncio.create_task(cleanup_old_readings())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

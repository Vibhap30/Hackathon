"""
Analytics Microservice for PowerShare Platform
Handles data analytics, reporting, and business intelligence
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import io
import logging
import os
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import uvicorn
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PowerShare Analytics Service", version="1.0.0")

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

# Redis client for caching
redis_client = redis.from_url(REDIS_URL)

# Pydantic models
class AnalyticsRequest(BaseModel):
    metric: str
    timeframe: str  # 1h, 24h, 7d, 30d, 1y
    filters: Optional[Dict[str, Any]] = {}

class MarketAnalytics(BaseModel):
    total_volume: float
    average_price: float
    price_trend: str
    volume_trend: str
    peak_hours: List[int]
    active_traders: int
    price_volatility: float
    market_efficiency: float

class PredictionRequest(BaseModel):
    target: str  # price, demand, supply
    horizon: int  # hours ahead
    features: Optional[List[str]] = None

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

def get_dataframe_from_query(query: str, params: tuple = None):
    """Get pandas DataFrame from database query"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        logger.error(f"DataFrame query failed: {e}")
        raise HTTPException(status_code=500, detail="Data retrieval failed")

# Analytics engine
class AnalyticsEngine:
    def __init__(self):
        self.cache_ttl = 300  # 5 minutes cache
    
    def get_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key"""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    async def get_market_analytics(self, timeframe: str = "24h") -> MarketAnalytics:
        """Get comprehensive market analytics"""
        cache_key = self.get_cache_key("market_analytics", timeframe=timeframe)
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            data = json.loads(cached_result)
            return MarketAnalytics(**data)
        
        # Calculate time range
        end_time = datetime.utcnow()
        if timeframe == "1h":
            start_time = end_time - timedelta(hours=1)
        elif timeframe == "24h":
            start_time = end_time - timedelta(days=1)
        elif timeframe == "7d":
            start_time = end_time - timedelta(days=7)
        elif timeframe == "30d":
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(days=1)
        
        # Get trading data
        query = """
            SELECT 
                amount,
                price,
                EXTRACT(HOUR FROM created_at) as hour,
                created_at,
                seller_id,
                buyer_id
            FROM energy_transactions 
            WHERE created_at BETWEEN %s AND %s
            AND status = 'completed'
        """
        
        df = get_dataframe_from_query(query, (start_time, end_time))
        
        if df.empty:
            # Return default analytics if no data
            analytics = MarketAnalytics(
                total_volume=0,
                average_price=0,
                price_trend="stable",
                volume_trend="stable",
                peak_hours=[],
                active_traders=0,
                price_volatility=0,
                market_efficiency=0
            )
        else:
            # Calculate analytics
            total_volume = df['amount'].sum()
            average_price = df['price'].mean()
            
            # Price trend calculation
            df_sorted = df.sort_values('created_at')
            if len(df_sorted) > 1:
                price_trend = self.calculate_trend(df_sorted['price'].values)
                volume_trend = self.calculate_trend(df_sorted['amount'].values)
            else:
                price_trend = "stable"
                volume_trend = "stable"
            
            # Peak hours
            hourly_volume = df.groupby('hour')['amount'].sum()
            peak_hours = hourly_volume.nlargest(3).index.tolist()
            
            # Active traders
            active_traders = len(set(df['seller_id'].tolist() + df['buyer_id'].tolist()))
            
            # Price volatility (coefficient of variation)
            price_volatility = df['price'].std() / df['price'].mean() if df['price'].mean() > 0 else 0
            
            # Market efficiency (simplified metric)
            market_efficiency = min(100, (1 - price_volatility) * 100) if price_volatility < 1 else 0
            
            analytics = MarketAnalytics(
                total_volume=float(total_volume),
                average_price=float(average_price),
                price_trend=price_trend,
                volume_trend=volume_trend,
                peak_hours=peak_hours,
                active_traders=active_traders,
                price_volatility=float(price_volatility),
                market_efficiency=float(market_efficiency)
            )
        
        # Cache result
        redis_client.setex(cache_key, self.cache_ttl, analytics.json())
        
        return analytics
    
    def calculate_trend(self, values: np.ndarray) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression to determine trend
        x = np.arange(len(values)).reshape(-1, 1)
        y = values.reshape(-1, 1)
        
        model = LinearRegression()
        model.fit(x, y)
        slope = model.coef_[0][0]
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
    
    async def get_price_history(self, timeframe: str = "7d", granularity: str = "hour") -> List[Dict]:
        """Get price history data"""
        cache_key = self.get_cache_key("price_history", timeframe=timeframe, granularity=granularity)
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Calculate time range
        end_time = datetime.utcnow()
        if timeframe == "24h":
            start_time = end_time - timedelta(days=1)
        elif timeframe == "7d":
            start_time = end_time - timedelta(days=7)
        elif timeframe == "30d":
            start_time = end_time - timedelta(days=30)
        elif timeframe == "1y":
            start_time = end_time - timedelta(days=365)
        else:
            start_time = end_time - timedelta(days=7)
        
        # Determine time grouping
        if granularity == "hour":
            time_trunc = "date_trunc('hour', created_at)"
        elif granularity == "day":
            time_trunc = "date_trunc('day', created_at)"
        elif granularity == "month":
            time_trunc = "date_trunc('month', created_at)"
        else:
            time_trunc = "date_trunc('hour', created_at)"
        
        query = f"""
            SELECT 
                {time_trunc} as time_period,
                AVG(price) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                SUM(amount) as volume,
                COUNT(*) as transaction_count
            FROM energy_transactions 
            WHERE created_at BETWEEN %s AND %s
            AND status = 'completed'
            GROUP BY {time_trunc}
            ORDER BY time_period
        """
        
        df = get_dataframe_from_query(query, (start_time, end_time))
        
        # Convert to list of dictionaries
        result = []
        for _, row in df.iterrows():
            result.append({
                "timestamp": row['time_period'].isoformat(),
                "avg_price": float(row['avg_price']),
                "min_price": float(row['min_price']),
                "max_price": float(row['max_price']),
                "volume": float(row['volume']),
                "transaction_count": int(row['transaction_count'])
            })
        
        # Cache result
        redis_client.setex(cache_key, self.cache_ttl, json.dumps(result))
        
        return result
    
    async def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get user-specific analytics"""
        cache_key = self.get_cache_key("user_analytics", user_id=user_id)
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Get user transaction data
        query = """
            SELECT 
                amount,
                price,
                transaction_type,
                created_at,
                CASE WHEN seller_id = %s THEN 'sell' ELSE 'buy' END as side
            FROM energy_transactions 
            WHERE (seller_id = %s OR buyer_id = %s)
            AND status = 'completed'
            AND created_at >= NOW() - INTERVAL '30 days'
        """
        
        df = get_dataframe_from_query(query, (user_id, user_id, user_id))
        
        if df.empty:
            result = {
                "total_energy_sold": 0,
                "total_energy_bought": 0,
                "total_transactions": 0,
                "average_sell_price": 0,
                "average_buy_price": 0,
                "total_revenue": 0,
                "total_cost": 0,
                "net_profit": 0,
                "energy_balance": 0
            }
        else:
            sells = df[df['side'] == 'sell']
            buys = df[df['side'] == 'buy']
            
            total_energy_sold = sells['amount'].sum()
            total_energy_bought = buys['amount'].sum()
            total_transactions = len(df)
            
            avg_sell_price = sells['price'].mean() if not sells.empty else 0
            avg_buy_price = buys['price'].mean() if not buys.empty else 0
            
            total_revenue = (sells['amount'] * sells['price']).sum()
            total_cost = (buys['amount'] * buys['price']).sum()
            net_profit = total_revenue - total_cost
            
            energy_balance = total_energy_sold - total_energy_bought
            
            result = {
                "total_energy_sold": float(total_energy_sold),
                "total_energy_bought": float(total_energy_bought),
                "total_transactions": total_transactions,
                "average_sell_price": float(avg_sell_price),
                "average_buy_price": float(avg_buy_price),
                "total_revenue": float(total_revenue),
                "total_cost": float(total_cost),
                "net_profit": float(net_profit),
                "energy_balance": float(energy_balance)
            }
        
        # Cache result
        redis_client.setex(cache_key, self.cache_ttl, json.dumps(result))
        
        return result
    
    async def get_predictive_analytics(self, target: str = "price", horizon: int = 24) -> List[Dict]:
        """Get predictive analytics using simple forecasting"""
        cache_key = self.get_cache_key("predictions", target=target, horizon=horizon)
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Get historical data for prediction
        query = """
            SELECT 
                created_at,
                price,
                amount
            FROM energy_transactions 
            WHERE status = 'completed'
            AND created_at >= NOW() - INTERVAL '7 days'
            ORDER BY created_at
        """
        
        df = get_dataframe_from_query(query)
        
        if df.empty or len(df) < 10:
            # Not enough data for prediction
            return []
        
        # Simple time series prediction using linear regression
        df['hour'] = pd.to_datetime(df['created_at']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['created_at']).dt.dayofweek
        
        # Aggregate by hour
        hourly_data = df.groupby(df['created_at'].dt.floor('H')).agg({
            'price': 'mean',
            'amount': 'sum'
        }).reset_index()
        
        if len(hourly_data) < 5:
            return []
        
        # Prepare features
        X = np.arange(len(hourly_data)).reshape(-1, 1)
        
        if target == "price":
            y = hourly_data['price'].values
        elif target == "volume":
            y = hourly_data['amount'].values
        else:
            y = hourly_data['price'].values
        
        # Fit model
        model = LinearRegression()
        model.fit(X, y)
        
        # Make predictions
        future_X = np.arange(len(hourly_data), len(hourly_data) + horizon).reshape(-1, 1)
        predictions = model.predict(future_X)
        
        # Generate prediction results
        result = []
        base_time = hourly_data['created_at'].iloc[-1]
        
        for i, pred in enumerate(predictions):
            prediction_time = base_time + timedelta(hours=i+1)
            result.append({
                "timestamp": prediction_time.isoformat(),
                "predicted_value": float(pred),
                "confidence": max(0.5, 1.0 - (i * 0.02))  # Decreasing confidence over time
            })
        
        # Cache result
        redis_client.setex(cache_key, self.cache_ttl, json.dumps(result))
        
        return result

# Initialize analytics engine
analytics_engine = AnalyticsEngine()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "analytics-service", "timestamp": datetime.utcnow()}

@app.get("/market")
async def get_market_analytics(timeframe: str = Query("24h", regex="^(1h|24h|7d|30d)$")):
    """Get market analytics"""
    analytics = await analytics_engine.get_market_analytics(timeframe)
    return analytics

@app.get("/price-history")
async def get_price_history(
    timeframe: str = Query("7d", regex="^(24h|7d|30d|1y)$"),
    granularity: str = Query("hour", regex="^(hour|day|month)$")
):
    """Get price history data"""
    history = await analytics_engine.get_price_history(timeframe, granularity)
    return {"timeframe": timeframe, "granularity": granularity, "data": history}

@app.get("/volume-history")
async def get_volume_history(
    timeframe: str = Query("7d", regex="^(24h|7d|30d|1y)$"),
    granularity: str = Query("hour", regex="^(hour|day|month)$")
):
    """Get volume history data"""
    # Reuse price history logic but focus on volume
    history = await analytics_engine.get_price_history(timeframe, granularity)
    volume_data = [{"timestamp": item["timestamp"], "volume": item["volume"]} for item in history]
    return {"timeframe": timeframe, "granularity": granularity, "data": volume_data}

@app.get("/user/{user_id}")
async def get_user_analytics(user_id: int):
    """Get user analytics"""
    analytics = await analytics_engine.get_user_analytics(user_id)
    return {"user_id": user_id, "analytics": analytics}

@app.get("/community/{community_id}")
async def get_community_analytics(community_id: int):
    """Get community analytics"""
    cache_key = f"community_analytics:{community_id}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return json.loads(cached_result)
    
    # Get community data
    query = """
        SELECT 
            u.id as user_id,
            u.energy_capacity,
            u.current_energy,
            cm.joined_at
        FROM users u
        JOIN community_members cm ON u.id = cm.user_id
        WHERE cm.community_id = %s
    """
    
    df = get_dataframe_from_query(query, (community_id,))
    
    if df.empty:
        result = {
            "member_count": 0,
            "total_capacity": 0,
            "total_current_energy": 0,
            "average_capacity_per_member": 0,
            "capacity_utilization": 0
        }
    else:
        member_count = len(df)
        total_capacity = df['energy_capacity'].sum()
        total_current_energy = df['current_energy'].sum()
        avg_capacity = df['energy_capacity'].mean()
        utilization = (total_current_energy / total_capacity * 100) if total_capacity > 0 else 0
        
        result = {
            "member_count": member_count,
            "total_capacity": float(total_capacity),
            "total_current_energy": float(total_current_energy),
            "average_capacity_per_member": float(avg_capacity),
            "capacity_utilization": float(utilization)
        }
    
    # Cache result
    redis_client.setex(cache_key, 300, json.dumps(result))
    
    return {"community_id": community_id, "analytics": result}

@app.get("/platform")
async def get_platform_analytics():
    """Get platform-wide analytics"""
    cache_key = "platform_analytics"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return json.loads(cached_result)
    
    # Get platform statistics
    queries = {
        "total_users": "SELECT COUNT(*) as count FROM users",
        "active_users": "SELECT COUNT(*) as count FROM users WHERE is_active = true",
        "total_transactions": "SELECT COUNT(*) as count FROM energy_transactions",
        "total_energy_traded": "SELECT SUM(amount) as total FROM energy_transactions WHERE status = 'completed'",
        "total_communities": "SELECT COUNT(*) as count FROM communities",
        "total_devices": "SELECT COUNT(*) as count FROM iot_devices"
    }
    
    result = {}
    for key, query in queries.items():
        data = execute_query(query, fetch=True)
        if data:
            result[key] = data[0].get('count', 0) or data[0].get('total', 0) or 0
        else:
            result[key] = 0
    
    # Calculate additional metrics
    if result['total_transactions'] > 0:
        result['average_transaction_size'] = result['total_energy_traded'] / result['total_transactions']
    else:
        result['average_transaction_size'] = 0
    
    # Cache result
    redis_client.setex(cache_key, 300, json.dumps(result))
    
    return {"platform_analytics": result}

@app.get("/predictive")
async def get_predictive_analytics(
    target: str = Query("price", regex="^(price|volume|demand)$"),
    horizon: int = Query(24, ge=1, le=168)  # 1 hour to 1 week
):
    """Get predictive analytics"""
    predictions = await analytics_engine.get_predictive_analytics(target, horizon)
    return {"target": target, "horizon_hours": horizon, "predictions": predictions}

@app.get("/export")
async def export_analytics_data(
    type: str = Query(..., regex="^(market|user|community|platform|predictions)$"),
    timeframe: str = Query("7d", regex="^(24h|7d|30d|1y)$"),
    format: str = Query("csv", regex="^(csv|json)$")
):
    """Export analytics data"""
    
    # Get data based on type
    if type == "market":
        data = await analytics_engine.get_market_analytics(timeframe)
        export_data = [data.dict()]
    elif type == "price-history":
        export_data = await analytics_engine.get_price_history(timeframe)
    else:
        # Default export
        export_data = [{"message": "Export type not implemented"}]
    
    if format == "csv":
        # Convert to CSV
        df = pd.DataFrame(export_data)
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=analytics_{type}_{timeframe}.csv"}
        )
    else:
        # Return JSON
        return StreamingResponse(
            io.BytesIO(json.dumps(export_data, indent=2).encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=analytics_{type}_{timeframe}.json"}
        )

@app.get("/reports/energy-efficiency")
async def get_energy_efficiency_report():
    """Get energy efficiency report"""
    query = """
        SELECT 
            d.device_type,
            AVG(r.energy_production / NULLIF(r.energy_consumption, 0)) as efficiency_ratio,
            COUNT(*) as reading_count,
            AVG(r.energy_production) as avg_production,
            AVG(r.energy_consumption) as avg_consumption
        FROM iot_readings r
        JOIN iot_devices d ON r.device_id = d.device_id
        WHERE r.timestamp >= NOW() - INTERVAL '7 days'
        GROUP BY d.device_type
        ORDER BY efficiency_ratio DESC
    """
    
    df = get_dataframe_from_query(query)
    
    report = []
    for _, row in df.iterrows():
        report.append({
            "device_type": row['device_type'],
            "efficiency_ratio": float(row['efficiency_ratio']) if row['efficiency_ratio'] else 0,
            "reading_count": int(row['reading_count']),
            "avg_production": float(row['avg_production']),
            "avg_consumption": float(row['avg_consumption'])
        })
    
    return {"energy_efficiency_report": report}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)

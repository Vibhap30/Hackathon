"""
Trading Microservice
PowerShare Energy Trading Platform

Handles P2P energy trading operations, order matching, and trade execution.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json
import redis
import uuid
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PowerShare Trading Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection for order book and real-time data
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Enums
class OrderType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class TradeStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SETTLED = "settled"
    FAILED = "failed"

# Pydantic Models
class EnergyOrder(BaseModel):
    id: str
    user_id: int
    order_type: OrderType
    amount: float
    price: float
    location: Optional[str] = None
    delivery_time: Optional[datetime] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_amount: float = 0.0
    created_at: datetime
    expires_at: Optional[datetime] = None

class CreateOrderRequest(BaseModel):
    order_type: OrderType
    amount: float
    price: float
    location: Optional[str] = None
    delivery_hours: Optional[int] = 24  # Hours from now for delivery
    expires_hours: Optional[int] = 72   # Hours from now for expiration

class Trade(BaseModel):
    id: str
    buy_order_id: str
    sell_order_id: str
    buyer_id: int
    seller_id: int
    amount: float
    price: float
    status: TradeStatus = TradeStatus.PENDING
    blockchain_tx_hash: Optional[str] = None
    executed_at: datetime

class OrderBookEntry(BaseModel):
    order_id: str
    user_id: int
    amount: float
    price: float
    location: Optional[str]
    created_at: datetime

class OrderBook(BaseModel):
    buy_orders: List[OrderBookEntry]
    sell_orders: List[OrderBookEntry]
    last_trade_price: Optional[float] = None
    market_spread: Optional[float] = None

class MarketData(BaseModel):
    current_price: float
    volume_24h: float
    price_change_24h: float
    high_24h: float
    low_24h: float
    active_orders: int
    recent_trades: List[Dict[str, Any]]

# In-memory storage (in production, use proper database)
orders: Dict[str, EnergyOrder] = {}
trades: Dict[str, Trade] = {}

class TradingEngine:
    """Core trading engine for order matching and execution"""
    
    def __init__(self):
        self.order_book_buy = []  # List of buy orders sorted by price (highest first)
        self.order_book_sell = []  # List of sell orders sorted by price (lowest first)
        
    async def add_order(self, order: EnergyOrder) -> List[Trade]:
        """Add order to order book and attempt matching"""
        executed_trades = []
        
        if order.order_type == OrderType.BUY:
            executed_trades = await self._match_buy_order(order)
            if order.status == OrderStatus.PENDING:
                self._add_to_buy_book(order)
        else:
            executed_trades = await self._match_sell_order(order)
            if order.status == OrderStatus.PENDING:
                self._add_to_sell_book(order)
        
        # Store order
        orders[order.id] = order
        
        # Update order book in Redis
        await self._update_order_book_cache()
        
        return executed_trades
    
    async def _match_buy_order(self, buy_order: EnergyOrder) -> List[Trade]:
        """Match buy order against sell orders"""
        executed_trades = []
        remaining_amount = buy_order.amount - buy_order.filled_amount
        
        # Sort sell orders by price (lowest first)
        matching_sells = [
            order for order in self.order_book_sell 
            if order.price <= buy_order.price and self._can_trade(buy_order, order)
        ]
        matching_sells.sort(key=lambda x: x.price)
        
        for sell_order in matching_sells:
            if remaining_amount <= 0:
                break
                
            trade_amount = min(remaining_amount, sell_order.amount - sell_order.filled_amount)
            
            if trade_amount > 0:
                # Create trade
                trade = await self._execute_trade(buy_order, sell_order, trade_amount)
                executed_trades.append(trade)
                
                # Update orders
                buy_order.filled_amount += trade_amount
                sell_order.filled_amount += trade_amount
                remaining_amount -= trade_amount
                
                # Update order statuses
                if buy_order.filled_amount >= buy_order.amount:
                    buy_order.status = OrderStatus.FILLED
                elif buy_order.filled_amount > 0:
                    buy_order.status = OrderStatus.PARTIALLY_FILLED
                    
                if sell_order.filled_amount >= sell_order.amount:
                    sell_order.status = OrderStatus.FILLED
                    self.order_book_sell.remove(sell_order)
                elif sell_order.filled_amount > 0:
                    sell_order.status = OrderStatus.PARTIALLY_FILLED
        
        return executed_trades
    
    async def _match_sell_order(self, sell_order: EnergyOrder) -> List[Trade]:
        """Match sell order against buy orders"""
        executed_trades = []
        remaining_amount = sell_order.amount - sell_order.filled_amount
        
        # Sort buy orders by price (highest first)
        matching_buys = [
            order for order in self.order_book_buy 
            if order.price >= sell_order.price and self._can_trade(sell_order, order)
        ]
        matching_buys.sort(key=lambda x: x.price, reverse=True)
        
        for buy_order in matching_buys:
            if remaining_amount <= 0:
                break
                
            trade_amount = min(remaining_amount, buy_order.amount - buy_order.filled_amount)
            
            if trade_amount > 0:
                # Create trade
                trade = await self._execute_trade(buy_order, sell_order, trade_amount)
                executed_trades.append(trade)
                
                # Update orders
                buy_order.filled_amount += trade_amount
                sell_order.filled_amount += trade_amount
                remaining_amount -= trade_amount
                
                # Update order statuses
                if buy_order.filled_amount >= buy_order.amount:
                    buy_order.status = OrderStatus.FILLED
                    self.order_book_buy.remove(buy_order)
                elif buy_order.filled_amount > 0:
                    buy_order.status = OrderStatus.PARTIALLY_FILLED
                    
                if sell_order.filled_amount >= sell_order.amount:
                    sell_order.status = OrderStatus.FILLED
                elif sell_order.filled_amount > 0:
                    sell_order.status = OrderStatus.PARTIALLY_FILLED
        
        return executed_trades
    
    def _can_trade(self, order1: EnergyOrder, order2: EnergyOrder) -> bool:
        """Check if two orders can trade (location compatibility, etc.)"""
        # In production, implement location-based matching logic
        # For now, allow all trades
        return order1.user_id != order2.user_id
    
    async def _execute_trade(self, buy_order: EnergyOrder, sell_order: EnergyOrder, amount: float) -> Trade:
        """Execute a trade between two orders"""
        trade_id = str(uuid.uuid4())
        
        # Use sell order price (maker gets preference)
        trade_price = sell_order.price
        
        trade = Trade(
            id=trade_id,
            buy_order_id=buy_order.id,
            sell_order_id=sell_order.id,
            buyer_id=buy_order.user_id,
            seller_id=sell_order.user_id,
            amount=amount,
            price=trade_price,
            executed_at=datetime.utcnow()
        )
        
        trades[trade_id] = trade
        
        # Notify trade execution (in production, use message queue)
        await self._notify_trade_execution(trade)
        
        logger.info(f"Trade executed: {amount} kWh at ${trade_price} between users {buy_order.user_id} and {sell_order.user_id}")
        
        return trade
    
    async def _notify_trade_execution(self, trade: Trade):
        """Notify relevant services about trade execution"""
        # In production, publish to message queue for:
        # - User notifications
        # - Blockchain settlement
        # - Analytics updates
        # - IoT device updates
        
        # Store in Redis for real-time updates
        trade_data = trade.dict()
        trade_data['executed_at'] = trade_data['executed_at'].isoformat()
        
        redis_client.lpush('recent_trades', json.dumps(trade_data))
        redis_client.ltrim('recent_trades', 0, 99)  # Keep last 100 trades
        
        # Publish to trading channel
        redis_client.publish('trading_updates', json.dumps({
            'type': 'trade_executed',
            'data': trade_data
        }))
    
    def _add_to_buy_book(self, order: EnergyOrder):
        """Add buy order to order book"""
        self.order_book_buy.append(order)
        self.order_book_buy.sort(key=lambda x: x.price, reverse=True)
    
    def _add_to_sell_book(self, order: EnergyOrder):
        """Add sell order to order book"""
        self.order_book_sell.append(order)
        self.order_book_sell.sort(key=lambda x: x.price)
    
    async def _update_order_book_cache(self):
        """Update order book cache in Redis"""
        buy_orders = [
            {
                'order_id': order.id,
                'user_id': order.user_id,
                'amount': order.amount - order.filled_amount,
                'price': order.price,
                'location': order.location,
                'created_at': order.created_at.isoformat()
            }
            for order in self.order_book_buy[:10]  # Top 10 buy orders
        ]
        
        sell_orders = [
            {
                'order_id': order.id,
                'user_id': order.user_id,
                'amount': order.amount - order.filled_amount,
                'price': order.price,
                'location': order.location,
                'created_at': order.created_at.isoformat()
            }
            for order in self.order_book_sell[:10]  # Top 10 sell orders
        ]
        
        order_book_data = {
            'buy_orders': buy_orders,
            'sell_orders': sell_orders,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        redis_client.setex('order_book', 60, json.dumps(order_book_data))

# Initialize trading engine
trading_engine = TradingEngine()

# API Endpoints
@app.post("/orders", response_model=Dict[str, Any])
async def create_order(
    request: CreateOrderRequest,
    background_tasks: BackgroundTasks,
    user_id: int = 1  # In production, get from JWT token
):
    """Create a new energy trading order"""
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Order amount must be positive")
    
    if request.price <= 0:
        raise HTTPException(status_code=400, detail="Order price must be positive")
    
    # Create order
    order_id = str(uuid.uuid4())
    delivery_time = datetime.utcnow() + timedelta(hours=request.delivery_hours or 24)
    expires_at = datetime.utcnow() + timedelta(hours=request.expires_hours or 72)
    
    order = EnergyOrder(
        id=order_id,
        user_id=user_id,
        order_type=request.order_type,
        amount=request.amount,
        price=request.price,
        location=request.location,
        delivery_time=delivery_time,
        created_at=datetime.utcnow(),
        expires_at=expires_at
    )
    
    # Add to trading engine
    executed_trades = await trading_engine.add_order(order)
    
    # Schedule order expiration check
    background_tasks.add_task(schedule_order_expiration, order_id, expires_at)
    
    return {
        "order": order,
        "executed_trades": executed_trades,
        "message": f"Order created successfully. {len(executed_trades)} trades executed immediately."
    }

@app.get("/orders", response_model=List[EnergyOrder])
async def get_orders(
    user_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    order_type: Optional[OrderType] = None,
    limit: int = 50
):
    """Get orders with optional filtering"""
    
    filtered_orders = list(orders.values())
    
    if user_id:
        filtered_orders = [o for o in filtered_orders if o.user_id == user_id]
    
    if status:
        filtered_orders = [o for o in filtered_orders if o.status == status]
    
    if order_type:
        filtered_orders = [o for o in filtered_orders if o.order_type == order_type]
    
    # Sort by creation time (newest first)
    filtered_orders.sort(key=lambda x: x.created_at, reverse=True)
    
    return filtered_orders[:limit]

@app.get("/orders/{order_id}", response_model=EnergyOrder)
async def get_order(order_id: str):
    """Get specific order by ID"""
    
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return orders[order_id]

@app.delete("/orders/{order_id}")
async def cancel_order(order_id: str, user_id: int = 1):
    """Cancel an order"""
    
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders[order_id]
    
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this order")
    
    if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Cannot cancel order in current status")
    
    # Remove from order book
    if order.order_type == OrderType.BUY and order in trading_engine.order_book_buy:
        trading_engine.order_book_buy.remove(order)
    elif order.order_type == OrderType.SELL and order in trading_engine.order_book_sell:
        trading_engine.order_book_sell.remove(order)
    
    # Update status
    order.status = OrderStatus.CANCELLED
    
    # Update cache
    await trading_engine._update_order_book_cache()
    
    return {"message": "Order cancelled successfully"}

@app.get("/orderbook", response_model=OrderBook)
async def get_order_book():
    """Get current order book"""
    
    # Get from cache if available
    cached_data = redis_client.get('order_book')
    if cached_data:
        data = json.loads(cached_data)
        return OrderBook(
            buy_orders=[OrderBookEntry(**order) for order in data['buy_orders']],
            sell_orders=[OrderBookEntry(**order) for order in data['sell_orders']],
            last_trade_price=get_last_trade_price(),
            market_spread=calculate_market_spread()
        )
    
    # Generate fresh order book
    buy_orders = [
        OrderBookEntry(
            order_id=order.id,
            user_id=order.user_id,
            amount=order.amount - order.filled_amount,
            price=order.price,
            location=order.location,
            created_at=order.created_at
        )
        for order in trading_engine.order_book_buy[:10]
    ]
    
    sell_orders = [
        OrderBookEntry(
            order_id=order.id,
            user_id=order.user_id,
            amount=order.amount - order.filled_amount,
            price=order.price,
            location=order.location,
            created_at=order.created_at
        )
        for order in trading_engine.order_book_sell[:10]
    ]
    
    return OrderBook(
        buy_orders=buy_orders,
        sell_orders=sell_orders,
        last_trade_price=get_last_trade_price(),
        market_spread=calculate_market_spread()
    )

@app.get("/trades", response_model=List[Trade])
async def get_trades(
    user_id: Optional[int] = None,
    limit: int = 50
):
    """Get recent trades"""
    
    filtered_trades = list(trades.values())
    
    if user_id:
        filtered_trades = [t for t in filtered_trades if t.buyer_id == user_id or t.seller_id == user_id]
    
    # Sort by execution time (newest first)
    filtered_trades.sort(key=lambda x: x.executed_at, reverse=True)
    
    return filtered_trades[:limit]

@app.get("/market-data", response_model=MarketData)
async def get_market_data():
    """Get current market data and statistics"""
    
    # Get recent trades from Redis
    recent_trades_data = redis_client.lrange('recent_trades', 0, 9)
    recent_trades = [json.loads(trade) for trade in recent_trades_data]
    
    # Calculate market statistics
    if recent_trades:
        prices = [trade['price'] for trade in recent_trades]
        current_price = prices[0]  # Most recent trade price
        high_24h = max(prices)
        low_24h = min(prices)
        
        # Simple price change calculation
        if len(prices) > 1:
            price_change_24h = prices[0] - prices[-1]
        else:
            price_change_24h = 0.0
    else:
        current_price = 0.25  # Default price
        high_24h = current_price
        low_24h = current_price
        price_change_24h = 0.0
    
    # Calculate volume
    volume_24h = sum(trade['amount'] for trade in recent_trades)
    
    # Count active orders
    active_orders = len([o for o in orders.values() if o.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]])
    
    return MarketData(
        current_price=current_price,
        volume_24h=volume_24h,
        price_change_24h=price_change_24h,
        high_24h=high_24h,
        low_24h=low_24h,
        active_orders=active_orders,
        recent_trades=recent_trades
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "trading",
        "timestamp": datetime.utcnow().isoformat(),
        "order_book_size": {
            "buy_orders": len(trading_engine.order_book_buy),
            "sell_orders": len(trading_engine.order_book_sell)
        },
        "total_orders": len(orders),
        "total_trades": len(trades)
    }

# Helper functions
def get_last_trade_price() -> Optional[float]:
    """Get the price of the last executed trade"""
    if not trades:
        return None
    
    last_trade = max(trades.values(), key=lambda x: x.executed_at)
    return last_trade.price

def calculate_market_spread() -> Optional[float]:
    """Calculate the current bid-ask spread"""
    if not trading_engine.order_book_buy or not trading_engine.order_book_sell:
        return None
    
    best_bid = max(trading_engine.order_book_buy, key=lambda x: x.price).price
    best_ask = min(trading_engine.order_book_sell, key=lambda x: x.price).price
    
    return best_ask - best_bid

async def schedule_order_expiration(order_id: str, expires_at: datetime):
    """Schedule order expiration check"""
    # In production, use a proper task queue like Celery
    sleep_duration = (expires_at - datetime.utcnow()).total_seconds()
    
    if sleep_duration > 0:
        await asyncio.sleep(sleep_duration)
        
        if order_id in orders and orders[order_id].status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]:
            orders[order_id].status = OrderStatus.EXPIRED
            
            # Remove from order book
            order = orders[order_id]
            if order.order_type == OrderType.BUY and order in trading_engine.order_book_buy:
                trading_engine.order_book_buy.remove(order)
            elif order.order_type == OrderType.SELL and order in trading_engine.order_book_sell:
                trading_engine.order_book_sell.remove(order)
            
            await trading_engine._update_order_book_cache()
            
            logger.info(f"Order {order_id} expired")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

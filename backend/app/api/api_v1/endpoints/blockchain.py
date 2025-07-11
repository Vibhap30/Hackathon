"""
Blockchain API Endpoints
PowerShare Energy Trading Platform
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from web3 import Web3
import json

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.energy_transaction import EnergyTransaction

from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

# For demo: file-based coin balance storage
import os
import threading

COIN_BALANCE_FILE = os.path.join(os.path.dirname(__file__), '../../../dummy_coin_balances.json')
COIN_LOCK = threading.Lock()

def load_coin_balances():
    if not os.path.exists(COIN_BALANCE_FILE):
        return {}
    with open(COIN_BALANCE_FILE, 'r') as f:
        try:
            import json
            return json.load(f)
        except Exception:
            return {}

def save_coin_balances(balances):
    with open(COIN_BALANCE_FILE, 'w') as f:
        import json
        json.dump(balances, f)
class CoinCollectResponse(BaseModel):
    message: str
    coins_collected: int
    total_balance: int

@router.post("/tokens/collect", response_model=CoinCollectResponse)
async def collect_coins(current_user: User = Depends(get_current_user)):
    """Collect coins for gamification (demo: increments user's coin balance)."""
    user_id = str(current_user.id)
    coins_to_collect = 10  # Demo: fixed coins per collection
    with COIN_LOCK:
        balances = load_coin_balances()
        prev_balance = balances.get(user_id, 0)
        new_balance = prev_balance + coins_to_collect
        balances[user_id] = new_balance
        save_coin_balances(balances)
    return CoinCollectResponse(
        message=f"Collected {coins_to_collect} coins!",
        coins_collected=coins_to_collect,
        total_balance=new_balance
    )

router = APIRouter()

# Pydantic models
class BlockchainTransaction(BaseModel):
    transaction_hash: str
    block_number: int
    from_address: str
    to_address: str
    value: float
    gas_used: int
    status: str
    timestamp: datetime

class SmartContractInfo(BaseModel):
    address: str
    network: str
    abi: List[Dict[str, Any]]
    deployed_at: datetime
    owner: str

class WalletInfo(BaseModel):
    address: str
    balance: float
    transaction_count: int
    is_verified: bool

class ContractCall(BaseModel):
    function_name: str
    parameters: Dict[str, Any]
    gas_limit: Optional[int] = 100000

class TransactionReceipt(BaseModel):
    transaction_hash: str
    status: str
    block_number: Optional[int]
    gas_used: Optional[int]
    effective_gas_price: Optional[int]
    logs: List[Dict[str, Any]] = []

# Mock blockchain functions (in production, these would interact with actual blockchain)
def get_web3_connection():
    """Get Web3 connection (mock for demo)."""
    # In production, this would connect to actual blockchain
    return None

def get_contract_abi():
    """Get smart contract ABI."""
    # Simplified ABI for demo - would load from file in production
    return [
        {
            "name": "createEnergyOffer",
            "type": "function",
            "inputs": [
                {"name": "_amount", "type": "uint256"},
                {"name": "_pricePerUnit", "type": "uint256"},
                {"name": "_seller", "type": "address"}
            ],
            "outputs": [{"name": "", "type": "uint256"}]
        },
        {
            "name": "executeTransaction",
            "type": "function", 
            "inputs": [
                {"name": "_offerId", "type": "uint256"},
                {"name": "_amount", "type": "uint256"}
            ],
            "outputs": [{"name": "", "type": "bool"}]
        }
    ]

async def simulate_blockchain_transaction(
    function_name: str,
    parameters: Dict[str, Any],
    user_address: str
) -> TransactionReceipt:
    """Simulate blockchain transaction (for demo purposes)."""
    
    # Simulate transaction hash
    import hashlib
    import time
    
    tx_data = f"{function_name}:{parameters}:{user_address}:{time.time()}"
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
    
    # Simulate successful transaction
    return TransactionReceipt(
        transaction_hash=f"0x{tx_hash}",
        status="success",
        block_number=12345678,
        gas_used=85000,
        effective_gas_price=20000000000,  # 20 gwei
        logs=[
            {
                "address": settings.SMART_CONTRACT_ADDRESS or "0x123...abc",
                "topics": [f"0x{function_name.encode().hex()}"],
                "data": str(parameters)
            }
        ]
    )

# API Endpoints
@router.get("/info", response_model=SmartContractInfo)
async def get_smart_contract_info():
    """Get smart contract information."""
    
    return SmartContractInfo(
        address=settings.SMART_CONTRACT_ADDRESS or "0x742d35Cc6676C4d5C4B6B8C7E5DD2E1a8d1A3B2c",
        network=settings.BLOCKCHAIN_NETWORK,
        abi=get_contract_abi(),
        deployed_at=datetime(2024, 1, 1, 12, 0, 0),  # Demo deployment date
        owner="0x8ba1f109551bD432803012645Hac136c91BCF2F5"
    )

@router.get("/wallet/{address}", response_model=WalletInfo)
async def get_wallet_info(
    address: str,
    current_user: User = Depends(get_current_user)
):
    """Get wallet information."""
    
    # Validate address format (basic check)
    if not address.startswith("0x") or len(address) != 42:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid wallet address format"
        )
    
    # In production, this would query actual blockchain
    # For demo, return simulated data
    return WalletInfo(
        address=address,
        balance=2.5,  # ETH balance
        transaction_count=156,
        is_verified=address == current_user.wallet_address
    )

@router.get("/transactions/{address}", response_model=List[BlockchainTransaction])
async def get_wallet_transactions(
    address: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get wallet transaction history."""
    
    if not address.startswith("0x") or len(address) != 42:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid wallet address format"
        )
    
    # In production, this would query blockchain for actual transactions
    # For demo, return simulated transactions
    transactions = []
    for i in range(min(limit, 10)):  # Limit demo data
        transactions.append(BlockchainTransaction(
            transaction_hash=f"0x{hex(i)[2:].zfill(64)}",
            block_number=12345600 + i,
            from_address=address if i % 2 == 0 else "0x" + "1" * 40,
            to_address="0x" + "2" * 40 if i % 2 == 0 else address,
            value=round(0.1 + i * 0.05, 3),
            gas_used=21000 + i * 1000,
            status="success",
            timestamp=datetime.utcnow()
        ))
    
    return transactions

@router.post("/contract/call", response_model=TransactionReceipt)
async def call_smart_contract(
    contract_call: ContractCall,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute smart contract function."""
    
    if not current_user.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a connected wallet address"
        )
    
    # Validate function name
    valid_functions = ["createEnergyOffer", "executeTransaction", "cancelOffer", "updateUserProfile"]
    if contract_call.function_name not in valid_functions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid function name. Must be one of: {', '.join(valid_functions)}"
        )
    
    # Simulate contract interaction
    try:
        receipt = await simulate_blockchain_transaction(
            contract_call.function_name,
            contract_call.parameters,
            current_user.wallet_address
        )
        
        # For energy offers, create corresponding database record
        if contract_call.function_name == "createEnergyOffer":
            # This would be handled by blockchain event listeners in production
            pass
        
        return receipt
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Contract call failed: {str(e)}"
        )

@router.post("/energy-offer")
async def create_blockchain_energy_offer(
    amount: float,
    price_per_unit: float,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create energy offer on blockchain."""
    
    if not current_user.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a connected wallet address"
        )
    
    if amount <= 0 or price_per_unit <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount and price must be positive"
        )
    
    if amount > current_user.current_energy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot offer more energy than currently available"
        )
    
    # Simulate blockchain transaction
    contract_call = ContractCall(
        function_name="createEnergyOffer",
        parameters={
            "amount": int(amount * 1000),  # Convert to wei-like units
            "pricePerUnit": int(price_per_unit * 1000),
            "seller": current_user.wallet_address
        }
    )
    
    receipt = await simulate_blockchain_transaction(
        contract_call.function_name,
        contract_call.parameters,
        current_user.wallet_address
    )
    
    return {
        "message": "Energy offer created on blockchain",
        "transaction_hash": receipt.transaction_hash,
        "offer_details": {
            "amount": amount,
            "price_per_unit": price_per_unit,
            "total_value": amount * price_per_unit,
            "seller": current_user.wallet_address
        }
    }

@router.post("/execute-trade")
async def execute_blockchain_trade(
    offer_id: int,
    amount: float,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute energy trade on blockchain."""
    
    if not current_user.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have a connected wallet address"
        )
    
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trade amount must be positive"
        )
    
    # In production, would verify offer exists on blockchain
    # For demo, simulate the transaction
    
    contract_call = ContractCall(
        function_name="executeTransaction",
        parameters={
            "offerId": offer_id,
            "amount": int(amount * 1000)  # Convert to wei-like units
        }
    )
    
    receipt = await simulate_blockchain_transaction(
        contract_call.function_name,
        contract_call.parameters,
        current_user.wallet_address
    )
    
    return {
        "message": "Trade executed on blockchain",
        "transaction_hash": receipt.transaction_hash,
        "trade_details": {
            "offer_id": offer_id,
            "amount": amount,
            "buyer": current_user.wallet_address
        }
    }

@router.get("/gas-estimates")
async def get_gas_estimates():
    """Get current gas price estimates."""
    
    # In production, this would query actual gas prices
    # For demo, return simulated estimates
    return {
        "network": settings.BLOCKCHAIN_NETWORK,
        "gas_prices": {
            "slow": {
                "gwei": 10,
                "usd": 0.50,
                "estimated_time": "5-10 minutes"
            },
            "standard": {
                "gwei": 20,
                "usd": 1.00,
                "estimated_time": "2-5 minutes"
            },
            "fast": {
                "gwei": 35,
                "usd": 1.75,
                "estimated_time": "30 seconds - 2 minutes"
            }
        },
        "updated_at": datetime.utcnow()
    }

@router.get("/network-stats")
async def get_network_stats():
    """Get blockchain network statistics."""
    
    # In production, this would query actual network stats
    # For demo, return simulated data
    return {
        "network": settings.BLOCKCHAIN_NETWORK,
        "latest_block": 18500000,
        "block_time": "12 seconds",
        "pending_transactions": 120000,
        "network_hashrate": "400 TH/s",
        "total_addresses": 245000000,
        "powershare_transactions_today": 1247,
        "total_energy_traded": 45678.9,
        "updated_at": datetime.utcnow()
    }

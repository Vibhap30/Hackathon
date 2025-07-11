# PowerShare Platform - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Backend Documentation](#backend-documentation)
6. [Frontend Documentation](#frontend-documentation)
7. [Microservices Documentation](#microservices-documentation)
8. [AI Agents Documentation](#ai-agents-documentation)
9. [Blockchain Integration](#blockchain-integration)
10. [Database Schema](#database-schema)
11. [API Documentation](#api-documentation)
12. [Configuration](#configuration)
13. [Deployment](#deployment)
14. [Development Guide](#development-guide)
15. [Testing](#testing)
16. [Security](#security)
17. [Performance](#performance)
18. [Troubleshooting](#troubleshooting)

---

## Overview

PowerShare is a revolutionary decentralized energy trading platform that enables peer-to-peer energy trading within communities. The platform leverages AI agents, blockchain technology, and the Beckn Protocol to create a comprehensive energy trading ecosystem.

### Key Features
- **Peer-to-peer energy trading** with real-time matching
- **AI-powered optimization** for energy consumption and trading
- **Community-based energy sharing** with local trading
- **Blockchain-secured transactions** with smart contracts
- **IoT device integration** for real-time energy monitoring
- **Beckn Protocol integration** for interoperability
- **Real-time analytics** and reporting
- **Multi-channel notifications** (email, SMS, push)

### Target Users
- **Prosumers**: Users who both produce and consume energy
- **Consumers**: Energy buyers looking for renewable sources
- **Communities**: Local energy trading groups
- **Utilities**: Energy providers and grid operators

---

## Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                     PowerShare Platform                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Frontend  │    │   Backend   │    │ AI Agents   │         │
│  │   (React)   │◄──►│  (FastAPI)  │◄──►│(LangGraph)  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                    │                   │             │
│         └────────────────────┼───────────────────┘             │
│                              │                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Microservices                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐   │   │
│  │  │Trading  │ │   IoT   │ │Analytics│ │Notifications│   │   │
│  │  │Service  │ │Service  │ │Service  │ │   Service   │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                Infrastructure                          │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐   │   │
│  │  │PostgreSQL│ │  Redis  │ │Blockchain│ │    MQTT     │   │   │
│  │  │Database │ │  Cache  │ │(Ethereum)│ │   Broker    │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interactions
- **Frontend** communicates with Backend via REST APIs and WebSockets
- **Backend** coordinates with all microservices
- **AI Agents** provide intelligent recommendations and automation
- **Microservices** handle specialized functions (trading, IoT, analytics, notifications)
- **Blockchain** ensures secure and transparent transactions
- **Database** stores all application data with Redis for caching

---

## Technology Stack

### Backend Technologies
- **FastAPI** 0.104.1 - High-performance Python web framework
- **PostgreSQL** - Primary database with TimescaleDB for time-series data
- **Redis** 5.0.1 - Caching and real-time features
- **SQLAlchemy** 2.0.23 - ORM for database operations
- **Celery** 5.3.4 - Background task processing
- **Pydantic** 2.5.0 - Data validation and serialization

### Frontend Technologies
- **React** 18.2.0 - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** 5.0.0 - Fast build tool and dev server
- **Tailwind CSS** 3.3.5 - Utility-first styling
- **React Query** 5.8.4 - Data fetching and state management
- **Socket.IO** 4.7.4 - Real-time communication
- **Recharts** 2.8.0 - Data visualization

### AI & ML
- **LangGraph** 0.0.19 - Agentic AI workflows and orchestration
- **LangChain** 0.0.340 - LLM integration and tool calling
- **OpenAI** 1.3.8 - GPT-4 integration
- **Pandas** 2.1.4 - Data processing
- **NumPy** 1.24.3 - Numerical computing
- **Scikit-learn** 1.3.2 - Machine learning

### Blockchain
- **Ethereum/Polygon** - Smart contract platform
- **Solidity** ^0.8.19 - Smart contract language
- **Web3.py** 6.13.0 - Blockchain integration
- **OpenZeppelin** - Smart contract libraries

### Protocol Integration
- **Beckn Protocol** - Interoperable network discovery
- **MQTT** 1.6.1 - IoT device communication
- **HTTP/WebSocket** - API communication

### DevOps & Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy and load balancing
- **Prometheus** - Monitoring and metrics
- **Grafana** - Data visualization and dashboards

---

## Project Structure

```
powershare-platform/
├── README.md                     # Project overview and setup
├── DOCUMENTATION.md             # This comprehensive documentation
├── .env.template               # Environment variables template
├── docker-compose.yml          # Docker services configuration
├── 
├── backend/                    # FastAPI backend application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # FastAPI application entry point
│       ├── core/              # Core configurations
│       │   ├── config.py      # Application settings
│       │   └── database.py    # Database configuration
│       ├── models/            # SQLAlchemy models
│       │   ├── __init__.py
│       │   ├── user.py        # User model
│       │   ├── energy_transaction.py  # Energy transaction models
│       │   ├── iot_device.py  # IoT device models
│       │   └── community.py   # Community models
│       ├── api/               # API endpoints
│       │   └── api_v1/
│       │       ├── api.py     # API router
│       │       └── endpoints/ # Individual endpoint files
│       │           ├── auth.py
│       │           ├── users.py
│       │           ├── energy_trading.py
│       │           ├── iot_devices.py
│       │           ├── communities.py
│       │           ├── ai_agents.py
│       │           ├── blockchain.py
│       │           ├── beckn_protocol.py
│       │           └── analytics.py
│       └── services/          # Business logic services
│           └── websocket_manager.py
│
├── frontend/                  # React frontend application
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── main.tsx          # Application entry point
│       ├── App.tsx           # Main App component
│       ├── components/       # Reusable components
│       │   ├── Navbar.tsx
│       │   └── Footer.tsx
│       ├── pages/            # Page components
│       │   ├── HomePage.tsx
│       │   ├── Dashboard.tsx
│       │   ├── EnergyMarketplace.tsx
│       │   ├── Community.tsx
│       │   ├── Analytics.tsx
│       │   ├── AIAssistant.tsx
│       │   └── Settings.tsx
│       └── services/         # API and WebSocket services
│           ├── api.ts
│           └── websocket.tsx
│
├── microservices/            # Microservices architecture
│   ├── trading/             # Trading microservice
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── iot/                 # IoT microservice
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── analytics/           # Analytics microservice
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── notifications/       # Notifications microservice
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
│
├── ai-agents/               # AI agents service
│   ├── main.py             # AI agents FastAPI service
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── agents/
│   │   └── energy_trading_agent.py
│   ├── tools/
│   │   └── platform_tools.py
│   └── workflows/
│       └── energy_optimization.py
│
├── blockchain/              # Blockchain contracts
│   └── contracts/
│       └── PowerShareEnergyTrading.sol
│
├── infrastructure/          # Infrastructure as Code
│   ├── kubernetes/         # Kubernetes manifests
│   ├── helm/              # Helm charts
│   └── terraform/         # Terraform configurations
│
└── memory-bank/            # Project memory and documentation
    ├── activeContext.md
    ├── architect.md
    ├── decisionLog.md
    ├── productContext.md
    ├── progress.md
    ├── projectBrief.md
    └── systemPatterns.md
```

---

## Backend Documentation

### FastAPI Application Structure

#### Main Application (`app/main.py`)
The main FastAPI application entry point that:
- Configures structured logging with `structlog`
- Sets up CORS middleware for cross-origin requests
- Includes GZip middleware for response compression
- Manages application lifespan (startup/shutdown)
- Implements WebSocket connections for real-time communication
- Includes health check endpoints

#### Core Configuration (`app/core/config.py`)
Application settings managed with Pydantic Settings:
```python
class Settings(BaseSettings):
    APP_NAME: str = "PowerShare"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    DATABASE_URL: str = "postgresql://..."
    REDIS_URL: str = "redis://..."
    # ... other configuration options
```

#### Database Configuration (`app/core/database.py`)
- SQLAlchemy setup with async support
- Connection pooling configuration
- Database session management
- Migration support with Alembic

### Data Models

#### User Model (`app/models/user.py`)
```python
class User(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    user_type = Column(SQLEnum(UserType))
    energy_capacity = Column(Float)
    current_energy = Column(Float)
    reputation_score = Column(Float)
    # ... additional fields
```

#### Energy Transaction Model (`app/models/energy_transaction.py`)
```python
class EnergyTransaction(Base):
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("users.id"))
    buyer_id = Column(Integer, ForeignKey("users.id"))
    energy_amount = Column(Float)
    price_per_unit = Column(Float)
    transaction_status = Column(SQLEnum(TransactionStatus))
    # ... additional fields
```

#### IoT Device Model (`app/models/iot_device.py`)
```python
class IoTDevice(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_name = Column(String)
    device_type = Column(SQLEnum(DeviceType))
    energy_capacity = Column(Float)
    current_energy = Column(Float)
    # ... additional fields
```

#### Community Model (`app/models/community.py`)
```python
class Community(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    community_type = Column(SQLEnum(CommunityType))
    creator_id = Column(Integer, ForeignKey("users.id"))
    # ... additional fields
```

### API Endpoints

#### Authentication (`app/api/api_v1/endpoints/auth.py`)
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `POST /auth/refresh` - Token refresh
- `GET /auth/me` - Current user information

#### Users (`app/api/api_v1/endpoints/users.py`)
- `GET /users/` - List all users
- `GET /users/me` - Current user profile
- `PUT /users/me` - Update user profile
- `GET /users/{user_id}` - Get user by ID
- `GET /users/me/stats` - User statistics

#### Energy Trading (`app/api/api_v1/endpoints/energy_trading.py`)
- `GET /energy-trading/transactions` - List transactions
- `POST /energy-trading/transactions` - Create transaction
- `GET /energy-trading/offers` - List energy offers
- `POST /energy-trading/offers` - Create energy offer
- `GET /energy-trading/market-stats` - Market statistics

#### IoT Devices (`app/api/api_v1/endpoints/iot_devices.py`)
- `GET /iot-devices/` - List user's IoT devices
- `POST /iot-devices/` - Register new IoT device
- `GET /iot-devices/{device_id}` - Get device details
- `PUT /iot-devices/{device_id}` - Update device
- `DELETE /iot-devices/{device_id}` - Delete device

#### Communities (`app/api/api_v1/endpoints/communities.py`)
- `GET /communities/` - List all communities
- `POST /communities/` - Create new community
- `GET /communities/{community_id}` - Get community details
- `PUT /communities/{community_id}` - Update community
- `POST /communities/{community_id}/join` - Join community

#### AI Agents (`app/api/api_v1/endpoints/ai_agents.py`)
- `POST /ai-agents/process` - Process AI agent request
- `GET /ai-agents/recommendations` - Get AI recommendations
- `POST /ai-agents/optimize` - Optimize energy usage

#### Blockchain (`app/api/api_v1/endpoints/blockchain.py`)
- `GET /blockchain/wallet` - Get wallet information
- `POST /blockchain/deploy-contract` - Deploy smart contract
- `POST /blockchain/execute-transaction` - Execute blockchain transaction

#### Beckn Protocol (`app/api/api_v1/endpoints/beckn_protocol.py`)
- `POST /beckn/search` - Search for energy providers
- `POST /beckn/select` - Select energy provider
- `POST /beckn/confirm` - Confirm energy transaction

#### Analytics (`app/api/api_v1/endpoints/analytics.py`)
- `GET /analytics/market` - Market analytics
- `GET /analytics/user/{user_id}` - User analytics
- `GET /analytics/community/{community_id}` - Community analytics

### WebSocket Service (`app/services/websocket_manager.py`)
Real-time communication manager that handles:
- WebSocket connection management
- Client authentication and authorization
- Message broadcasting
- Real-time energy trading updates
- Live market data streaming

---

## Frontend Documentation

### React Application Structure

#### Main Application (`src/App.tsx`)
The root React component that:
- Provides WebSocket context to all components
- Manages global navigation with React Router
- Implements motion animations with Framer Motion
- Handles global layout (Navbar, Footer, routing)

#### Entry Point (`src/main.tsx`)
Application bootstrap that:
- Configures React Query for API state management
- Sets up routing with React Router
- Provides toast notifications with react-hot-toast
- Enables React Query DevTools for development

### Components

#### Navigation (`src/components/Navbar.tsx`)
Main navigation component featuring:
- Responsive design with mobile menu
- User authentication state
- Real-time notifications
- Quick access to all major sections

#### Footer (`src/components/Footer.tsx`)
Simple footer component with:
- Copyright information
- Platform branding
- Legal links

### Pages

#### Home Page (`src/pages/HomePage.tsx`)
Landing page with:
- Hero section introducing the platform
- Feature highlights
- Getting started guide
- Community statistics

#### Dashboard (`src/pages/Dashboard.tsx`)
User dashboard showing:
- Energy production/consumption charts
- Current energy balance
- Recent transactions
- Market overview
- Quick actions (buy/sell energy)

#### Energy Marketplace (`src/pages/EnergyMarketplace.tsx`)
Trading interface with:
- Live energy offers/requests
- Interactive trading forms
- Market depth visualization
- Order book display
- Transaction history

#### Community (`src/pages/Community.tsx`)
Community management with:
- Community discovery
- Join/create communities
- Member management
- Community energy sharing
- Local trading features

#### Analytics (`src/pages/Analytics.tsx`)
Comprehensive analytics dashboard:
- Market trend analysis
- User performance metrics
- Community statistics
- Predictive analytics
- Export capabilities

#### AI Assistant (`src/pages/AIAssistant.tsx`)
AI-powered assistant interface:
- Energy optimization recommendations
- Trading strategy suggestions
- Real-time market analysis
- Automated trading configuration
- Performance insights

#### Settings (`src/pages/Settings.tsx`)
User preferences and configuration:
- Account settings
- Notification preferences
- Trading parameters
- Security settings
- Privacy controls

### Services

#### API Service (`src/services/api.ts`)
Centralized API client using Axios that provides:
- Authentication management
- Request/response interceptors
- Error handling
- TypeScript interfaces
- Methods for all backend endpoints

#### WebSocket Service (`src/services/websocket.tsx`)
Real-time communication service:
- WebSocket connection management
- Event handling for real-time updates
- Connection state management
- Automatic reconnection
- Message broadcasting

---

## Microservices Documentation

### Trading Microservice (`microservices/trading/main.py`)

#### Purpose
Handles peer-to-peer energy trading operations, order matching, and trade execution.

#### Key Features
- **Order Management**: Create, modify, and cancel energy orders
- **Order Matching**: Automatic matching of buy/sell orders
- **Trade Execution**: Secure transaction processing
- **Market Data**: Real-time market statistics
- **Price Discovery**: Dynamic pricing based on supply/demand

#### API Endpoints
- `POST /orders` - Create new energy order
- `GET /orders` - List all orders
- `GET /orders/{order_id}` - Get order details
- `DELETE /orders/{order_id}` - Cancel order
- `GET /orderbook` - Get current order book
- `GET /trades` - List completed trades
- `GET /market-data` - Get market statistics

#### Data Models
```python
class EnergyOrder(BaseModel):
    user_id: int
    order_type: OrderType  # BUY or SELL
    energy_amount: float
    price_per_unit: float
    location: Optional[str]
    renewable_source: bool
    expires_at: datetime
```

### IoT Microservice (`microservices/iot/main.py`)

#### Purpose
Manages IoT device integration, real-time data collection, and device monitoring.

#### Key Features
- **Device Registration**: Register and manage IoT devices
- **Real-time Data**: Collect energy production/consumption data
- **Device Monitoring**: Track device health and performance
- **Alert System**: Automated alerts for device issues
- **Data Analytics**: Historical data analysis

#### API Endpoints
- `POST /readings` - Submit device readings
- `POST /readings/batch` - Batch upload readings
- `GET /devices/{device_id}/readings` - Get device readings
- `GET /devices/{device_id}/latest` - Get latest reading
- `GET /devices/{device_id}/statistics` - Device statistics
- `POST /devices/{device_id}/alerts` - Configure alerts

#### Data Models
```python
class DeviceReading(BaseModel):
    device_id: str
    energy_production: float
    energy_consumption: float
    temperature: Optional[float]
    humidity: Optional[float]
    battery_level: Optional[float]
    timestamp: datetime
```

### Analytics Microservice (`microservices/analytics/main.py`)

#### Purpose
Provides data analytics, reporting, and business intelligence for the platform.

#### Key Features
- **Market Analytics**: Trading volume, price trends, market efficiency
- **User Analytics**: Individual user performance and insights
- **Community Analytics**: Community-level energy sharing metrics
- **Predictive Analytics**: Machine learning-based predictions
- **Report Generation**: Automated report generation

#### API Endpoints
- `GET /market` - Market analytics
- `GET /price-history` - Historical price data
- `GET /volume-history` - Trading volume history
- `GET /user/{user_id}` - User analytics
- `GET /community/{community_id}` - Community analytics
- `GET /platform` - Platform-wide analytics
- `GET /predictive` - Predictive analytics

#### Data Models
```python
class MarketAnalytics(BaseModel):
    total_volume: float
    average_price: float
    price_trend: str
    volume_trend: str
    peak_hours: List[int]
    active_traders: int
    price_volatility: float
    market_efficiency: float
```

### Notifications Microservice (`microservices/notifications/main.py`)

#### Purpose
Handles multi-channel notifications including email, SMS, and push notifications.

#### Key Features
- **Email Notifications**: HTML and text email support
- **SMS Notifications**: Twilio integration for SMS
- **Push Notifications**: Firebase for mobile push notifications
- **Template Management**: Customizable notification templates
- **Delivery Tracking**: Track notification delivery status

#### API Endpoints
- `POST /send` - Send notification
- `POST /send/email` - Send email notification
- `POST /send/sms` - Send SMS notification
- `POST /send/push` - Send push notification
- `GET /templates` - List notification templates
- `POST /templates` - Create notification template

#### Data Models
```python
class NotificationRequest(BaseModel):
    recipient: str
    type: str  # email, sms, push
    template: str
    data: Dict[str, Any]
    priority: str = "normal"
    scheduled_at: Optional[datetime] = None
```

---

## AI Agents Documentation

### AI Agents Service (`ai-agents/main.py`)

#### Purpose
Provides AI-powered energy trading optimization, market analysis, and automated decision-making.

#### Key Features
- **Energy Trading Agent**: Automated trading based on market conditions
- **Optimization Workflows**: Energy usage optimization recommendations
- **Market Analysis**: Real-time market trend analysis
- **Predictive Analytics**: Machine learning-based predictions
- **Automation**: Automated trading and energy management

#### Architecture
Built on **LangGraph** for agentic workflows:
- **Agents**: Specialized AI agents for different tasks
- **Tools**: Platform integration tools for data access
- **Workflows**: Multi-step optimization processes
- **Memory**: Conversation and decision history

#### API Endpoints
- `POST /api/v1/agents/energy-trading/process` - Process trading request
- `GET /api/v1/agents/energy-trading/recommendations/{user_id}` - Get recommendations
- `POST /api/v1/agents/session-history` - Manage conversation history
- `GET /api/v1/agents/market-analysis` - Get market analysis
- `GET /api/v1/agents/status` - Get agents status

#### Components

##### Energy Trading Agent (`ai-agents/agents/energy_trading_agent.py`)
Intelligent trading agent that:
- Analyzes market conditions
- Provides trading recommendations
- Executes automated trades
- Manages risk and portfolio
- Learns from historical data

##### Platform Tools (`ai-agents/tools/platform_tools.py`)
Integration tools for:
- User data access
- Market data retrieval
- Trading execution
- IoT device interaction
- Analytics queries

##### Energy Optimization Workflow (`ai-agents/workflows/energy_optimization.py`)
Multi-step optimization process:
1. **Data Collection**: Gather user energy data
2. **Analysis**: Analyze consumption patterns
3. **Optimization**: Generate optimization recommendations
4. **Action Planning**: Create actionable items
5. **Execution**: Implement optimizations

---

## Blockchain Integration

### Smart Contract (`blockchain/contracts/PowerShareEnergyTrading.sol`)

#### Purpose
Ethereum smart contract for secure, transparent energy trading transactions.

#### Key Features
- **Decentralized Trading**: Peer-to-peer energy transactions
- **Escrow System**: Secure payment handling
- **Reputation System**: User reputation tracking
- **Automated Settlement**: Smart contract-based settlements
- **Transparency**: All transactions on blockchain

#### Contract Structure
```solidity
contract PowerShareEnergyTrading {
    // State variables
    mapping(address => User) public users;
    mapping(uint256 => EnergyOffer) public offers;
    mapping(uint256 => EnergyTransaction) public transactions;
    
    // Events
    event OfferCreated(uint256 offerId, address seller);
    event TransactionExecuted(uint256 transactionId);
    event PaymentReleased(uint256 transactionId, uint256 amount);
    
    // Functions
    function createOffer(...) external;
    function acceptOffer(...) external;
    function confirmDelivery(...) external;
    function disputeTransaction(...) external;
}
```

#### Integration Points
- **Backend Integration**: Web3.py for contract interaction
- **Frontend Integration**: Ethers.js for web3 functionality
- **Payment Processing**: Cryptocurrency and fiat integration
- **Energy Verification**: IoT device data verification

---

## Database Schema

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    user_type user_type_enum NOT NULL,
    phone VARCHAR(20),
    location VARCHAR(255),
    wallet_address VARCHAR(42),
    energy_capacity FLOAT DEFAULT 0,
    current_energy FLOAT DEFAULT 0,
    reputation_score FLOAT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Energy Transactions Table
```sql
CREATE TABLE energy_transactions (
    id SERIAL PRIMARY KEY,
    seller_id INTEGER REFERENCES users(id),
    buyer_id INTEGER REFERENCES users(id),
    energy_amount FLOAT NOT NULL,
    price_per_unit FLOAT NOT NULL,
    total_amount FLOAT NOT NULL,
    energy_type energy_type_enum NOT NULL,
    transaction_status transaction_status_enum NOT NULL,
    delivery_time_start TIMESTAMP,
    delivery_time_end TIMESTAMP,
    blockchain_tx_hash VARCHAR(66),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### IoT Devices Table
```sql
CREATE TABLE iot_devices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    device_name VARCHAR(255) NOT NULL,
    device_type device_type_enum NOT NULL,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    energy_capacity FLOAT,
    current_energy FLOAT DEFAULT 0,
    location VARCHAR(255),
    device_status device_status_enum DEFAULT 'active',
    last_reading_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Communities Table
```sql
CREATE TABLE communities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    community_type community_type_enum NOT NULL,
    creator_id INTEGER REFERENCES users(id),
    location VARCHAR(255),
    max_members INTEGER,
    total_energy_capacity FLOAT DEFAULT 0,
    total_current_energy FLOAT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Indexes
```sql
-- Performance indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_energy_transactions_seller ON energy_transactions(seller_id);
CREATE INDEX idx_energy_transactions_buyer ON energy_transactions(buyer_id);
CREATE INDEX idx_energy_transactions_status ON energy_transactions(transaction_status);
CREATE INDEX idx_iot_devices_user ON iot_devices(user_id);
CREATE INDEX idx_iot_devices_type ON iot_devices(device_type);
CREATE INDEX idx_communities_creator ON communities(creator_id);
```

---

## API Documentation

### Authentication Flow
```mermaid
sequenceDiagram
    participant Client
    participant Backend
    participant Database
    
    Client->>Backend: POST /auth/register
    Backend->>Database: Create user record
    Database-->>Backend: User created
    Backend-->>Client: User registration successful
    
    Client->>Backend: POST /auth/login
    Backend->>Database: Validate credentials
    Database-->>Backend: User validated
    Backend-->>Client: JWT token + refresh token
    
    Client->>Backend: API request with JWT
    Backend->>Backend: Validate JWT
    Backend-->>Client: API response
```

### Trading Flow
```mermaid
sequenceDiagram
    participant Seller
    participant Backend
    participant TradingService
    participant Blockchain
    participant Buyer
    
    Seller->>Backend: POST /energy-trading/offers
    Backend->>TradingService: Create energy offer
    TradingService->>Blockchain: Record offer on blockchain
    TradingService-->>Backend: Offer created
    Backend-->>Seller: Offer confirmation
    
    Buyer->>Backend: POST /energy-trading/transactions
    Backend->>TradingService: Match with offers
    TradingService->>Blockchain: Execute smart contract
    Blockchain-->>TradingService: Transaction confirmed
    TradingService-->>Backend: Transaction successful
    Backend-->>Buyer: Transaction confirmation
    Backend-->>Seller: Sale notification
```

### Error Handling
All APIs follow consistent error response format:
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "field": "energy_amount",
            "issue": "Must be greater than 0"
        }
    }
}
```

### Rate Limiting
API endpoints are rate-limited:
- **Authentication**: 5 requests per minute
- **Trading**: 100 requests per minute
- **Data queries**: 1000 requests per minute
- **WebSocket**: 10 connections per user

---

## Configuration

### Environment Variables

#### Core Configuration
```bash
# Application
APP_NAME=PowerShare
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/powershare
REDIS_URL=redis://localhost:6379

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
ALGORITHM=HS256
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

#### External Services
```bash
# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Twilio (SMS)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Firebase (Push notifications)
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json

# Blockchain
ETHEREUM_RPC_URL=http://localhost:8545
PRIVATE_KEY=your-ethereum-private-key
CONTRACT_ADDRESS=your-deployed-contract-address

# Beckn Protocol
BECKN_GATEWAY_URL=https://gateway.beckn.org
BECKN_PARTICIPANT_ID=powershare-energy-platform
BECKN_PRIVATE_KEY=your-beckn-private-key
```

#### Microservices URLs
```bash
TRADING_SERVICE_URL=http://localhost:8001
IOT_SERVICE_URL=http://localhost:8002
ANALYTICS_SERVICE_URL=http://localhost:8003
NOTIFICATIONS_SERVICE_URL=http://localhost:8004
AI_AGENTS_URL=http://localhost:8005
```

#### Frontend Configuration
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

### Docker Compose Configuration
The `docker-compose.yml` file defines all services:
- **postgres**: TimescaleDB for time-series data
- **redis**: Caching and session storage
- **backend**: Main FastAPI application
- **frontend**: React application
- **ai-agents**: AI agents service
- **trading-service**: Trading microservice
- **iot-service**: IoT microservice
- **analytics-service**: Analytics microservice
- **notifications-service**: Notifications microservice
- **mosquitto**: MQTT broker for IoT
- **ganache**: Ethereum development blockchain
- **nginx**: Reverse proxy
- **prometheus**: Monitoring
- **grafana**: Dashboards

---

## Deployment

### Local Development

#### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL (if not using Docker)
- Redis (if not using Docker)

#### Quick Start
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd powershare-platform
   ```

2. **Setup environment**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Or run services individually**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Frontend
   cd frontend
   npm install
   npm run dev
   ```

#### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090

### Production Deployment

#### Kubernetes Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: powershare-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: powershare-backend
  template:
    metadata:
      labels:
        app: powershare-backend
    spec:
      containers:
      - name: backend
        image: powershare/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: powershare-secrets
              key: database-url
```

#### Helm Chart
```yaml
# values.yaml
replicaCount: 3

image:
  repository: powershare/backend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80
  targetPort: 8000

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: api.powershare.com
      paths:
        - path: /
          pathType: Prefix
```

#### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build and push Docker images
      run: |
        docker build -t powershare/backend:${{ github.sha }} ./backend
        docker push powershare/backend:${{ github.sha }}
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/powershare-backend backend=powershare/backend:${{ github.sha }}
```

---

## Development Guide

### Getting Started

#### Backend Development
1. **Setup virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database setup**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Create test data
   python scripts/seed_data.py
   ```

3. **Run development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Development
1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

### Code Style and Standards

#### Python (Backend)
- **PEP 8** compliance
- **Type hints** for all functions
- **Docstrings** for all public functions
- **Black** for code formatting
- **isort** for import sorting

#### TypeScript (Frontend)
- **ESLint** for linting
- **Prettier** for code formatting
- **Strict TypeScript** configuration
- **Component documentation**

#### Git Workflow
- **Feature branches** for all development
- **Pull requests** for code review
- **Conventional commits** for commit messages
- **Automated testing** on PR

### Database Migrations

#### Creating Migrations
```bash
# Auto-generate migration
alembic revision --autogenerate -m "Add user energy tracking"

# Create empty migration
alembic revision -m "Custom migration"
```

#### Running Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current
```

### API Testing

#### Using pytest
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_energy_trading.py
```

#### Test Examples
```python
def test_create_energy_offer():
    response = client.post(
        "/api/v1/energy-trading/offers",
        json={
            "energy_amount": 50.0,
            "price_per_unit": 0.25,
            "renewable_source": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["energy_amount"] == 50.0
```

---

## Testing

### Backend Testing

#### Unit Tests
```python
# test_energy_trading.py
import pytest
from app.models.energy_transaction import EnergyTransaction
from app.services.trading_service import TradingService

@pytest.fixture
def trading_service():
    return TradingService()

def test_create_energy_offer(trading_service):
    offer = trading_service.create_offer(
        user_id=1,
        energy_amount=100.0,
        price_per_unit=0.25
    )
    assert offer.energy_amount == 100.0
    assert offer.price_per_unit == 0.25
```

#### Integration Tests
```python
# test_api_integration.py
def test_energy_trading_flow(client, db_session):
    # Create user
    user = create_test_user()
    
    # Create energy offer
    offer_response = client.post(
        "/api/v1/energy-trading/offers",
        json={"energy_amount": 50.0, "price_per_unit": 0.25},
        headers=auth_headers(user)
    )
    assert offer_response.status_code == 201
    
    # Create transaction
    transaction_response = client.post(
        "/api/v1/energy-trading/transactions",
        json={"offer_id": offer_response.json()["id"]},
        headers=auth_headers(user)
    )
    assert transaction_response.status_code == 201
```

### Frontend Testing

#### Component Tests
```typescript
// EnergyMarketplace.test.tsx
import { render, screen } from '@testing-library/react';
import { EnergyMarketplace } from './EnergyMarketplace';

describe('EnergyMarketplace', () => {
  it('renders energy offers', () => {
    render(<EnergyMarketplace />);
    expect(screen.getByText('Energy Offers')).toBeInTheDocument();
  });
  
  it('handles offer creation', async () => {
    render(<EnergyMarketplace />);
    // Test offer creation flow
  });
});
```

#### E2E Tests
```typescript
// e2e/energy-trading.spec.ts
import { test, expect } from '@playwright/test';

test('complete energy trading flow', async ({ page }) => {
  await page.goto('/marketplace');
  
  // Create energy offer
  await page.fill('[data-testid="energy-amount"]', '50');
  await page.fill('[data-testid="price-per-unit"]', '0.25');
  await page.click('[data-testid="create-offer"]');
  
  // Verify offer creation
  await expect(page.locator('[data-testid="offer-created"]')).toBeVisible();
});
```

### Performance Testing

#### Load Testing
```python
# locust_test.py
from locust import HttpUser, task, between

class PowerShareUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def view_marketplace(self):
        self.client.get("/api/v1/energy-trading/offers", headers=self.headers)
    
    @task(1)
    def create_offer(self):
        self.client.post("/api/v1/energy-trading/offers", json={
            "energy_amount": 50.0,
            "price_per_unit": 0.25
        }, headers=self.headers)
```

---

## Security

### Authentication & Authorization

#### JWT Implementation
- **Access tokens**: Short-lived (15 minutes)
- **Refresh tokens**: Long-lived (7 days)
- **Secure storage**: HttpOnly cookies for web
- **Token rotation**: Automatic refresh token rotation

#### Role-Based Access Control
```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    PROSUMER = "prosumer"
    CONSUMER = "consumer"
    UTILITY = "utility"

@router.get("/admin/users")
async def get_all_users(
    current_user: User = Depends(get_current_user),
    required_role: UserRole = UserRole.ADMIN
):
    if current_user.role != required_role:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    # ... implementation
```

### Data Protection

#### Encryption
- **At rest**: Database encryption with AES-256
- **In transit**: TLS 1.3 for all communications
- **Sensitive data**: Additional encryption for PII

#### Privacy Controls
- **Data anonymization**: Remove PII from analytics
- **Consent management**: User control over data sharing
- **Right to deletion**: GDPR compliance

### Security Headers
```python
# Security middleware
app.add_middleware(
    SecurityHeadersMiddleware,
    csp="default-src 'self'",
    hsts=True,
    xframe_options="DENY",
    xss_protection=True,
    content_type_options=True
)
```

### Blockchain Security

#### Smart Contract Security
- **Reentrancy protection**: OpenZeppelin ReentrancyGuard
- **Access control**: Role-based contract permissions
- **Upgrade patterns**: Proxy contracts for upgradability
- **Audit trails**: All transactions logged

#### Wallet Security
- **Hardware wallet support**: Ledger, Trezor integration
- **Multi-signature**: Community wallet protection
- **Private key management**: Never store private keys

---

## Performance

### Backend Optimization

#### Database Optimization
```python
# Efficient queries with indexes
@router.get("/energy-trading/offers")
async def get_energy_offers(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    query = select(EnergyOffer).options(
        selectinload(EnergyOffer.seller)
    ).limit(limit).offset(offset)
    return await db.execute(query)
```

#### Caching Strategy
```python
# Redis caching for frequently accessed data
@cache(expire=300)  # 5 minutes
async def get_market_stats():
    # Expensive calculation
    return market_statistics
```

#### Async Processing
```python
# Background tasks for heavy operations
@router.post("/analytics/generate-report")
async def generate_report(
    background_tasks: BackgroundTasks,
    user_id: int
):
    background_tasks.add_task(generate_user_report, user_id)
    return {"message": "Report generation started"}
```

### Frontend Optimization

#### Code Splitting
```typescript
// Lazy loading for pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const EnergyMarketplace = lazy(() => import('./pages/EnergyMarketplace'));

// Route-based code splitting
<Route path="/dashboard" element={<Suspense fallback={<Loading />}><Dashboard /></Suspense>} />
```

#### State Management
```typescript
// React Query for efficient API state
const { data: energyOffers, isLoading } = useQuery({
  queryKey: ['energyOffers'],
  queryFn: () => apiService.getEnergyOffers(),
  staleTime: 5 * 60 * 1000, // 5 minutes
});
```

#### Bundle Optimization
```javascript
// Vite configuration
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts'],
          utils: ['date-fns', 'axios']
        }
      }
    }
  }
});
```

### Monitoring & Observability

#### Prometheus Metrics
```python
# Custom metrics
from prometheus_client import Counter, Histogram

energy_trades_counter = Counter('energy_trades_total', 'Total energy trades')
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration')

@api_request_duration.time()
def process_energy_trade():
    energy_trades_counter.inc()
    # Process trade
```

#### Grafana Dashboards
- **System metrics**: CPU, memory, disk usage
- **Application metrics**: Request rates, error rates
- **Business metrics**: Trading volume, user growth
- **Alert rules**: Automated alerting for issues

---

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connection
psql -h localhost -U postgres -d powershare

# Check logs
docker logs powershare-postgres

# Reset database
docker-compose down -v
docker-compose up postgres
```

#### Redis Connection Issues
```bash
# Check Redis connection
redis-cli ping

# Check Redis logs
docker logs powershare-redis

# Clear Redis cache
redis-cli flushall
```

#### API Issues
```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Check API logs
docker logs powershare-backend

# Debug mode
DEBUG=true uvicorn app.main:app --reload
```

#### Frontend Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run type-check
```

### Debugging

#### Backend Debugging
```python
# Add logging
import logging
logger = logging.getLogger(__name__)

async def debug_energy_trading():
    logger.info("Processing energy trade")
    logger.debug(f"Trade data: {trade_data}")
    # Debug implementation
```

#### Frontend Debugging
```typescript
// React Query DevTools
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Add to App component
<ReactQueryDevtools initialIsOpen={false} />
```

### Performance Issues

#### Slow API Responses
1. **Check database queries**: Use EXPLAIN ANALYZE
2. **Add database indexes**: For frequently queried columns
3. **Implement caching**: Redis for repeated queries
4. **Optimize serialization**: Use efficient data structures

#### High Memory Usage
1. **Check for memory leaks**: Use profiling tools
2. **Optimize database connections**: Connection pooling
3. **Clear caches**: Regular cache cleanup
4. **Monitor containers**: Docker stats

#### Frontend Performance
1. **Bundle analysis**: Use webpack-bundle-analyzer
2. **Lazy loading**: Implement code splitting
3. **Optimize images**: Use WebP format
4. **Minimize re-renders**: Use React.memo

---

## Appendix

### Useful Commands

#### Docker Commands
```bash
# Build and start all services
docker-compose up --build

# Start specific service
docker-compose up postgres redis

# View logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash

# Remove all containers and volumes
docker-compose down -v
```

#### Database Commands
```bash
# Connect to database
psql -h localhost -U postgres -d powershare

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Seed test data
python scripts/seed_data.py
```

#### API Testing Commands
```bash
# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Test energy offer creation
curl -X POST http://localhost:8000/api/v1/energy-trading/offers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"energy_amount": 50.0, "price_per_unit": 0.25}'
```

### Environment Setup Scripts

#### Backend Setup
```bash
#!/bin/bash
# setup-backend.sh

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
#!/bin/bash
# setup-frontend.sh

# Install dependencies
npm install

# Start development server
npm run dev
```

### Configuration Templates

#### Production Environment
```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@prod-db:5432/powershare
REDIS_URL=redis://prod-redis:6379
SECRET_KEY=your-production-secret-key
BACKEND_CORS_ORIGINS=["https://powershare.com"]
```

#### Development Environment
```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/powershare
REDIS_URL=redis://localhost:6379
SECRET_KEY=development-secret-key
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

---

## Contributing

### Development Workflow
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes and test**
4. **Submit pull request**

### Code Review Process
- All code changes require review
- Automated tests must pass
- Code coverage must be maintained
- Documentation must be updated

### Release Process
1. **Update version numbers**
2. **Create release notes**
3. **Tag release**: `git tag v1.0.0`
4. **Deploy to staging**
5. **Deploy to production**

---

*This documentation is maintained by the PowerShare development team. For questions or updates, please contact the maintainers.*

---

**Last Updated**: July 4, 2025
**Version**: 1.0.0
**Maintainers**: PowerShare Development Team

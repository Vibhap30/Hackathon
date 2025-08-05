# PowerShare - Community Energy Trading Platform

A revolutionary decentralized energy trading ecosystem powered by AI agents, blockchain technology, and the Beckn Protocol.

## 🚀 Technology Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **PostgreSQL** - Primary database with TimescaleDB for time-series data
- **Redis** - Caching and real-time features
- **Celery** - Background task processing

### Frontend
- **React 18** - Modern UI with TypeScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **React Query** - Data fetching and state management
- **Socket.IO** - Real-time communication

### AI & ML
- **LangGraph** - Agentic AI workflows and orchestration
- **LangChain** - LLM integration and tool calling
- **OpenAI GPT-4** - Natural language processing
- **Pandas/NumPy** - Data processing and analytics

### Blockchain
- **Ethereum/Polygon** - Smart contracts for energy trading
- **Solidity** - Smart contract development
- **Web3.py** - Blockchain integration
- **IPFS** - Decentralized storage

### Protocol Integration
- **Beckn Protocol** - Interoperable network discovery and transactions
- **MQTT** - IoT device communication
- **REST & GraphQL** - API interfaces

### Cloud-Native & DevOps
- **Docker** - Containerization
- **Kubernetes** - Container orchestration
- **Helm** - Kubernetes package manager
- **GitHub Actions** - CI/CD pipeline
- **Prometheus/Grafana** - Monitoring and observability

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │   AI Agents     │
│   (Web App)     │◄──►│   (Core API)    │◄──►│  (LangGraph)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Microservices │    │   Blockchain    │    │ Beckn Protocol  │
│   (Trading/IoT) │◄──►│  (Smart Contracts)│◄──►│   (Discovery)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
powershare-platform/
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── api/            # API routes and endpoints
│   │   ├── core/           # Core configuration and settings
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic services
│   │   └── utils/          # Utility functions
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── ai-agents/              # LangGraph AI agents
│   ├── agents/             # Individual agent implementations
│   ├── workflows/          # LangGraph workflows
│   ├── tools/              # Custom tools for agents
│   └── config/             # Agent configurations
├── blockchain/             # Smart contracts and blockchain integration
│   ├── contracts/          # Solidity smart contracts
│   ├── scripts/            # Deployment scripts
│   ├── tests/              # Contract tests
│   └── integration/        # Blockchain integration code
├── microservices/          # Individual microservices
│   ├── trading-service/    # Energy trading logic
│   ├── iot-service/        # IoT device management
│   ├── notification-service/ # Real-time notifications
│   └── analytics-service/  # Data analytics and reporting
├── infrastructure/         # Cloud-native infrastructure
│   ├── kubernetes/         # K8s deployment manifests
│   ├── docker/             # Docker configurations
│   ├── helm/               # Helm charts
│   └── monitoring/         # Observability stack
└── docs/                   # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd powershare-platform
```

2. **Start infrastructure services**
```bash
docker-compose up -d postgres redis
```

3. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

5. **AI Agents Setup**
```bash
cd ai-agents
pip install -r requirements.txt
python -m agents.main
```

### Docker Development

```bash
# Build and run all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🚀 Quick Setup & Deployment

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- Node.js 18+ (for development)

### 1. Environment Setup
```bash
# Copy environment template
cp .env.template .env

# Edit .env with your configuration
# Required: OPENAI_API_KEY=your-openai-api-key-here
```

### 2. Start the Platform
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 3. Access Services
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **AI Agents**: http://localhost:8005/docs
- **Grafana**: http://localhost:3001 (admin/admin)

### 4. Development Mode
```bash
# Backend development
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend development
cd frontend  
npm install
npm run dev

# AI Agents development
cd ai-agents
pip install -r requirements.txt
python main.py
```

## 🤖 AI Features Highlights

### Energy Trading Agent
- **Smart Market Analysis**: Real-time price predictions and market trends
- **Automated Trading**: AI-powered buy/sell recommendations
- **Risk Assessment**: Portfolio optimization and risk management
- **Weather Integration**: Solar/wind production forecasting

### Energy Optimization Workflow
- **Usage Pattern Analysis**: Historical consumption insights
- **Community Matching**: AI-driven community recommendations
- **Cost Optimization**: Personalized savings strategies
- **Carbon Footprint**: Sustainability impact tracking

### LangGraph Integration
- **Multi-Step Workflows**: Complex reasoning chains
- **Tool Integration**: External APIs and data sources
- **State Management**: Persistent conversation memory
- **Human-in-the-Loop**: Interactive decision making

## 📊 Platform Capabilities

- ✅ **Full-Stack Architecture**: React frontend + FastAPI backend
- ✅ **AI-Powered Insights**: LangGraph agents for optimization
- ✅ **Microservices**: Trading, IoT, Analytics, Notifications
- ✅ **Real-Time Features**: WebSocket connections and live updates
- ✅ **Blockchain Integration**: Smart contracts and wallet connection
- ✅ **Community Features**: Local energy networks and social trading
- ✅ **IoT Integration**: Device monitoring and control
- ✅ **Analytics Dashboard**: Rich visualizations and reporting
- ✅ **Mobile-Responsive**: Works on all devices
- ✅ **Production-Ready**: Docker, monitoring, and scaling support

---

**Built for the SURE Hackathon** - Demonstrating the future of decentralized energy trading with AI and blockchain technology.

## 🔧 Configuration

### Environment Variables

Create `.env` files in each service directory:

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:pass@localhost/powershare
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
BLOCKCHAIN_RPC_URL=your-blockchain-rpc
```

**Frontend (.env)**
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_BLOCKCHAIN_NETWORK=polygon-mumbai
```

## 📚 API Documentation

- **REST API**: http://localhost:8000/docs (Swagger)
- **GraphQL**: http://localhost:8000/graphql (GraphiQL)
- **WebSocket**: ws://localhost:8000/ws

## 🧪 Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚀 Deployment

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/

# Install with Helm
helm install powershare infrastructure/helm/powershare
```

### Cloud Deployment

The platform supports deployment on:
- **AWS EKS** - Elastic Kubernetes Service
- **Azure AKS** - Azure Kubernetes Service  
- **Google GKE** - Google Kubernetes Engine

## 🔐 Security

- JWT-based authentication
- OAuth2 integration
- End-to-end encryption
- Smart contract security audits
- Regular security scanning

## 📊 Monitoring

- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger
- **Alerts**: AlertManager

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@powershare.energy

---

**PowerShare** - Empowering communities through decentralized energy trading 🌱⚡


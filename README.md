# 📊 Crypto Monitoring & Analysis System

AI-powered backend for cryptocurrency monitoring and analysis with real-time alerts, fundamental analysis, portfolio management, and backtesting capabilities.

## 🚀 Features

- **Real-time Price Monitoring**: WebSocket-based price tracking with custom alerts
- **Fundamental Analysis**: On-chain metrics, sentiment analysis, and comprehensive reports
- **Technical Analysis**: Custom indicators, pattern recognition, and charting
- **Portfolio Management**: Multi-portfolio tracking with risk monitoring and rebalancing
- **Backtesting Engine**: Strategy validation with performance metrics
- **Content Aggregation**: Daily market digests and personalized news
- **Community Platform**: Discussion forums and insight sharing

## 🧰 Tech Stack

- **Backend**: Python 3.11 + FastAPI
- **Package Manager**: uv
- **AI Framework**: LangChain v1 (ReAct agents)
- **LLM**: OpenAI GPT-4 / Anthropic Claude
- **Database**: PostgreSQL + TimescaleDB
- **Cache**: Redis (Pub/Sub + caching)
- **Task Queue**: Celery + Redis broker
- **Analysis**: pandas, TA-Lib, pandas-ta
- **NLP**: transformers (HuggingFace)

## 📦 Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- uv package manager

### Setup

```bash
# Clone repository
git clone <repository-url>
cd crypto-monitoring-system/backend

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/seed_data.py

# Run migrations
alembic upgrade head
```

## 🏃 Running the Application

### Development

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A app.tasks.celery_app beat --loglevel=info
```

### Docker

```bash
docker-compose up -d
```

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Setup Guide](docs/SETUP.md)
- [Deployment](docs/DEPLOYMENT.md)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run load tests
locust -f tests/load_tests/locustfile.py
```

## 📊 API Endpoints

- `POST /api/alerts` - Create price alerts
- `GET /api/alerts/{userId}` - Get user alerts
- `POST /api/analysis/fundamental` - Generate fundamental analysis
- `POST /api/analysis/technical` - Generate technical analysis
- `POST /api/portfolios` - Create portfolio
- `GET /api/portfolios/{portfolioId}/analysis` - Portfolio analysis
- `POST /api/backtest/strategy` - Run strategy backtest

See [API.md](docs/API.md) for complete documentation.

## 🔧 Configuration

Key environment variables:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/crypto_db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_openai_key
COINGECKO_API_KEY=your_coingecko_key
COINMARKETCAP_API_KEY=your_cmc_key
```

## 📈 Performance Targets

- Alert delivery latency: < 500ms
- WebSocket connections: 10,000+
- Report generation: < 30s
- API response (p95): < 200ms
- System uptime: 99.9%

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

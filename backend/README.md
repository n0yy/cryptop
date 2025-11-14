# 📊 Crypto Monitoring & Analysis System - Backend

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
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Initialize database
python scripts/seed_data.py

# Run migrations
alembic upgrade head
```

## 🏃 Running the Application

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# Start Celery beat
celery -A app.tasks.celery_app beat --loglevel=info
```

## 🧪 Testing

```bash
pytest
pytest --cov=app --cov-report=html
```

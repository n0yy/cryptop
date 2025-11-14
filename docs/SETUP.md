# Setup Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional)

## Local Development Setup

### 1. Install uv Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup

```bash
cd crypto-monitoring-system/backend

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
DATABASE_URL=postgresql://crypto_user:crypto_pass@localhost:5432/crypto_db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_openai_key
COINGECKO_API_KEY=your_coingecko_key
```

### 4. Initialize Database

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Seed initial data (optional)
python scripts/seed_data.py
```

### 5. Run Application

```bash
# Terminal 1: Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 3: Start Celery beat
celery -A app.tasks.celery_app beat --loglevel=info

# Terminal 4: Start Flower (optional)
celery -A app.tasks.celery_app flower --port=5555
```

## Docker Setup

### Quick Start

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (TimescaleDB)
- Redis
- FastAPI application
- Celery worker
- Celery beat
- Flower monitoring

### Access Services

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Flower: http://localhost:5555

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_alerts/test_engine.py

# Run load tests
locust -f tests/load_tests/locustfile.py
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
psql postgresql://crypto_user:crypto_pass@localhost:5432/crypto_db
```

### Redis Connection Issues

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli ping
```

### Celery Issues

```bash
# Check Celery worker status
celery -A app.tasks.celery_app inspect active

# Purge all tasks
celery -A app.tasks.celery_app purge
```

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

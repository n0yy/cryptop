# Architecture Documentation

## System Overview

The Crypto Monitoring & Analysis System is a microservices-based backend built with FastAPI, LangChain, and PostgreSQL.

## Architecture Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌──────────┐      ┌─────────────┐ │
│  │   API    │      │  WebSocket  │ │
│  │ Endpoints│      │   Server    │ │
│  └────┬─────┘      └──────┬──────┘ │
└───────┼────────────────────┼────────┘
        │                    │
        ▼                    ▼
┌──────────────┐    ┌────────────────┐
│   Services   │    │   Connection   │
│    Layer     │    │    Manager     │
└──────┬───────┘    └────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│        Business Logic Layer         │
│  ┌──────┐  ┌──────┐  ┌──────────┐  │
│  │Alert │  │Port- │  │Analysis  │  │
│  │Engine│  │folio │  │ Agents   │  │
│  └──────┘  └──────┘  └──────────┘  │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│         Data Layer                  │
│  ┌──────────┐      ┌─────────────┐ │
│  │PostgreSQL│      │    Redis    │ │
│  │TimescaleDB│     │  Cache/Queue│ │
│  └──────────┘      └─────────────┘ │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│      External Integrations          │
│  CoinGecko | CMC | Twitter | Twilio│
└─────────────────────────────────────┘
```

## Component Details

### 1. API Layer

**FastAPI Application**
- RESTful API endpoints
- WebSocket connections
- Request validation with Pydantic
- Authentication & authorization
- Rate limiting

**Key Routes:**
- `/api/alerts` - Alert management
- `/api/analysis` - Analysis endpoints
- `/api/portfolios` - Portfolio management
- `/api/backtest` - Backtesting
- `/ws/alerts` - WebSocket alerts

### 2. Service Layer

**Alert Service**
- CRUD operations for alerts
- Alert validation
- User alert management

**Analysis Service**
- Fundamental analysis orchestration
- Technical analysis coordination
- Result caching

**Portfolio Service**
- Portfolio CRUD
- Position management
- Performance tracking

**Backtest Service**
- Strategy execution
- Performance metrics
- Result storage

### 3. Business Logic Layer

**Alert Engine**
- Continuous alert monitoring
- Condition evaluation
- Trigger management

**Portfolio Manager**
- Risk calculation
- Allocation analysis
- Rebalancing recommendations

**LangChain Agents**
- Crypto analysis agent
- Multi-tool orchestration
- Conversational memory

**Analysis Modules**
- Fundamental analyzer
- Technical analyzer
- Sentiment analyzer

### 4. Data Layer

**PostgreSQL + TimescaleDB**
- User data
- Alerts
- Portfolios & positions
- Reports
- Time-series price data

**Redis**
- Caching layer
- Pub/Sub messaging
- Celery broker
- Session storage

### 5. Task Queue

**Celery Workers**
- Alert checking (every 5s)
- Report generation
- Daily digests
- Data cleanup

**Celery Beat**
- Scheduled task execution
- Cron-based triggers

### 6. External Integrations

**Data Sources**
- CoinGecko: Market data
- CoinMarketCap: Rankings & quotes
- Etherscan: On-chain data

**Notifications**
- Twilio: SMS alerts
- SendGrid: Email notifications
- Discord: Webhook notifications

**AI/ML**
- OpenAI: GPT-4 for analysis
- Anthropic: Claude for insights
- HuggingFace: Sentiment analysis

## Data Flow

### Alert Flow

```
1. User creates alert → API
2. Alert stored in PostgreSQL
3. Celery beat triggers check (every 5s)
4. Alert engine evaluates conditions
5. If triggered → Notifier sends via channels
6. WebSocket broadcasts to connected clients
7. Alert status updated in database
```

### Analysis Flow

```
1. User requests analysis → API
2. Check Redis cache
3. If miss → LangChain agent orchestrates
4. Agent uses tools (CoinGecko, Technical, etc.)
5. Results aggregated and analyzed
6. Response cached in Redis
7. Return to user
```

### Portfolio Flow

```
1. User creates portfolio → API
2. Portfolio stored in PostgreSQL
3. User adds positions
4. Portfolio manager calculates metrics
5. Risk analysis performed
6. Rebalancing recommendations generated
7. Results returned to user
```

## Scalability Considerations

### Horizontal Scaling

- **API Servers**: Multiple FastAPI instances behind load balancer
- **Celery Workers**: Scale workers based on queue depth
- **WebSocket**: Redis Pub/Sub for message broadcasting

### Vertical Scaling

- **Database**: PostgreSQL read replicas
- **Cache**: Redis cluster for high availability
- **TimescaleDB**: Automatic data compression

### Performance Optimization

- **Caching Strategy**: Multi-level caching (Redis + in-memory)
- **Database Indexing**: Optimized queries with proper indexes
- **Connection Pooling**: Async database connections
- **Rate Limiting**: Protect against abuse

## Security

- JWT-based authentication
- API key management
- Rate limiting per user/IP
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- Environment variable secrets

## Monitoring & Observability

- **Logging**: Structured logging with Loguru
- **Metrics**: Prometheus metrics
- **Tracing**: Sentry error tracking
- **Health Checks**: `/health` endpoint
- **Celery Monitoring**: Flower dashboard

## Deployment Architecture

```
┌─────────────────────────────────────┐
│         Load Balancer (Nginx)       │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│  FastAPI 1  │  │  FastAPI 2  │
└──────┬──────┘  └──────┬───────┘
       │                │
       └────────┬───────┘
                ▼
       ┌────────────────┐
       │   PostgreSQL   │
       │  (Primary +    │
       │   Replicas)    │
       └────────────────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
┌─────────────┐  ┌──────────────┐
│    Redis    │  │    Celery    │
│   Cluster   │  │   Workers    │
└─────────────┘  └──────────────┘
```

## Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI |
| Language | Python 3.11 |
| Database | PostgreSQL + TimescaleDB |
| Cache | Redis |
| Task Queue | Celery |
| AI Framework | LangChain |
| LLM | OpenAI GPT-4 / Anthropic Claude |
| WebSocket | FastAPI WebSocket |
| ORM | SQLAlchemy (async) |
| Validation | Pydantic |
| Testing | pytest |
| Containerization | Docker |
| Orchestration | Docker Compose |

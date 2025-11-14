# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Alerts

#### Create Alert
```http
POST /api/alerts
Content-Type: application/json

{
  "userId": 1,
  "symbol": "BTC-USD",
  "condition": "PRICE_ABOVE",
  "threshold": 50000,
  "channels": ["EMAIL", "DISCORD"]
}
```

#### Get User Alerts
```http
GET /api/alerts/{userId}?status=ACTIVE&symbol=BTC-USD
```

### Analysis

#### Fundamental Analysis
```http
POST /api/analysis/fundamental
Content-Type: application/json

{
  "symbol": "BTC-USD",
  "sources": ["COINGECKO", "COINMARKETCAP"],
  "includeOnChain": true,
  "includeSentiment": true,
  "timeframe": "30d"
}
```

#### Technical Analysis
```http
POST /api/analysis/technical
Content-Type: application/json

{
  "symbol": "ETH-USD",
  "indicators": ["RSI", "MACD", "BOLLINGER_BANDS"],
  "timeframes": ["1h", "4h", "1d"],
  "period": "90d"
}
```

### Portfolio

#### Create Portfolio
```http
POST /api/portfolios
Content-Type: application/json

{
  "userId": 1,
  "name": "Conservative Portfolio",
  "riskProfile": "LOW",
  "targetAllocations": {
    "BTC-USD": 0.60,
    "ETH-USD": 0.30,
    "USDT": 0.10
  }
}
```

#### Add Position
```http
POST /api/portfolios/{portfolioId}/positions
Content-Type: application/json

{
  "symbol": "BTC-USD",
  "quantity": 0.5,
  "entryPrice": 48000,
  "entryDate": "2025-11-01T10:00:00Z"
}
```

#### Get Portfolio Analysis
```http
GET /api/portfolios/{portfolioId}/analysis
```

### Backtesting

#### Run Backtest
```http
POST /api/backtest/strategy
Content-Type: application/json

{
  "strategyName": "RSI Mean Reversion",
  "symbol": "BTC-USD",
  "period": "1y",
  "parameters": {
    "rsiPeriod": 14,
    "buyThreshold": 30,
    "sellThreshold": 70
  },
  "initialCapital": 10000
}
```

### Content

#### Get Daily Digest
```http
GET /api/content/daily-digest/{userId}
```

#### Get Crypto News
```http
GET /api/content/news?limit=10
```

### WebSocket

#### Connect to Alerts
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/alerts/1');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    symbols: ['BTC-USD', 'ETH-USD']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Alert:', data);
};
```

## Response Format

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2025-11-13T12:00:00Z"
}
```

### Error Response
```json
{
  "status": "error",
  "code": "INVALID_SYMBOL",
  "message": "Symbol BTC-INVALID not found",
  "timestamp": "2025-11-13T12:01:00Z"
}
```

## Rate Limiting

- 60 requests per minute per IP
- 1000 requests per hour per user

## Error Codes

- `INVALID_SYMBOL` - Invalid cryptocurrency symbol
- `INSUFFICIENT_DATA` - Not enough historical data
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `UNAUTHORIZED` - Invalid or missing authentication
- `INTERNAL_SERVER_ERROR` - Server error

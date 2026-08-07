# Massive API Documentation (formerly Polygon.io)

Massive (formerly known as Polygon.io) is a financial data platform that provides real-time and historical market data for stocks, options, forex, and crypto. This document focuses on the Python API for retrieving real-time and end-of-day (EOD) stock prices.

## Prerequisites
To interact with the Massive API, use the official Python client:
```bash
pip install polygon-api-client
```
Ensure that you have your Massive API key available.

## End-of-Day (EOD) Prices
To retrieve daily Open, High, Low, Close (OHLC) data for a given ticker or multiple tickers, use the REST Client's aggregations or daily open/close endpoints.

### Fetching Daily Aggregates
```python
from polygon import RESTClient

client = RESTClient("YOUR_MASSIVE_API_KEY")

# Fetch daily aggregates for a ticker
aggs = client.get_aggs(
    ticker="AAPL",
    multiplier=1,
    timespan="day",
    from_="2023-01-01",
    to="2023-01-31"
)

for bar in aggs:
    print(f"Date: {bar.timestamp}, Close: {bar.close}, Open: {bar.open}")
```

### Fetching a Specific Day's Open/Close
```python
data = client.get_daily_open_close(ticker="AAPL", date="2023-01-05")
print(f"Open: {data.open}, Close: {data.close}")
```

## Real-Time Prices
For real-time streaming data, Massive utilizes WebSockets.

```python
from polygon import WebSocketClient
from polygon.websocket.models import Market

# Initialize WebSocket Client
ws = WebSocketClient(api_key="YOUR_MASSIVE_API_KEY", market=Market.Stocks)

def handle_message(msg):
    # msg is a list of real-time events
    for event in msg:
        print(f"Real-time event: {event}")

# Subscribe to trades for a specific ticker
ws.subscribe("T.AAPL")

# Run the WebSocket client loop
ws.run(handle_message)
```

## Considerations
* **Rate Limits**: The free tier is typically restricted to 5 API calls per minute.
* **Data Freshness**: Depending on your subscription plan, real-time data might be delayed (e.g., by 15 minutes) or fully real-time.

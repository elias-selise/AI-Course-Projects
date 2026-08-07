# Market Interface Design

To abstract the market data provider and allow seamless local development, we will use a unified Python API (`MarketClient`). This client will automatically use the Massive API if the `MASSIVE_API_KEY` environment variable is set. Otherwise, it will fall back to a simulated market environment.

## Unified Interface: `MarketClientBase`
All market clients must implement a common interface.

```python
from abc import ABC, abstractmethod
from typing import List, Callable, Dict, Any

class MarketClientBase(ABC):
    @abstractmethod
    def get_eod_prices(self, tickers: List[str], start_date: str, end_date: str) -> Dict[str, Any]:
        """Fetch End-of-Day prices for a list of tickers over a date range."""
        pass

    @abstractmethod
    def subscribe_realtime(self, tickers: List[str], callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to real-time price updates for the given tickers."""
        pass
        
    @abstractmethod
    def disconnect(self):
        """Disconnect from any real-time streams."""
        pass
```

## Implementations

### 1. `MassiveMarketClient`
This implementation wraps the `polygon-api-client`.
*   `get_eod_prices`: Calls `RESTClient.get_aggs` or `get_daily_open_close`.
*   `subscribe_realtime`: Utilizes the `WebSocketClient` and registers the provided callback.

### 2. `SimulatedMarketClient`
This implementation uses local algorithms to generate realistic mock market data (see `MARKET_SIMULATOR.md`).

## Factory Pattern
A factory method handles the instantiation logic based on the environment variable.

```python
import os

def get_market_client() -> MarketClientBase:
    api_key = os.environ.get("MASSIVE_API_KEY")
    if api_key:
        return MassiveMarketClient(api_key=api_key)
    else:
        return SimulatedMarketClient()
```

## Example Usage
```python
client = get_market_client()

# 1. Fetch EOD Prices
eod_data = client.get_eod_prices(["AAPL", "GOOG"], "2023-01-01", "2023-01-31")
print(eod_data)

# 2. Subscribe to Real-Time Updates
def on_price_update(data):
    print(f"Price Update: {data['ticker']} @ {data['price']}")

client.subscribe_realtime(["AAPL"], on_price_update)
```

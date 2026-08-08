# Market Simulator Design

When the `MASSIVE_API_KEY` is not present, the application will use the `SimulatedMarketClient`. This simulator generates realistic stock price movements to facilitate local development and testing without incurring API usage costs or requiring internet access.

## Simulation Approach
To model stock prices, we will use **Geometric Brownian Motion (GBM)**, a standard mathematical model for simulating stock price behavior.

### Key Parameters per Ticker
*   **Initial Price ($S_0$)**: A base starting price (e.g., $150.00).
*   **Drift ($\mu$)**: The expected return (trend).
*   **Volatility ($\sigma$)**: The standard deviation of the returns, controlling how wildly the price swings.

## Code Structure

### 1. The Price Generator
A utility class/function that generates the next price based on the current price and a time delta.

```python
import math
import random

class GBMPriceGenerator:
    def __init__(self, initial_price: float, drift: float, volatility: float):
        self.current_price = initial_price
        self.drift = drift
        self.volatility = volatility
        
    def get_next_price(self, dt: float = 1/252) -> float:
        # standard GBM formula
        shock = random.gauss(0, 1)
        drift_component = (self.drift - 0.5 * self.volatility ** 2) * dt
        volatility_component = self.volatility * math.sqrt(dt) * shock
        
        self.current_price *= math.exp(drift_component + volatility_component)
        return self.current_price
```

### 2. EOD Data Simulation
For `get_eod_prices(tickers, start_date, end_date)`, the simulator will:
1. Identify the number of trading days between `start_date` and `end_date`.
2. For each day and ticker, compute a simulated Open, High, Low, and Close by invoking the price generator in a loop (e.g., simulating 390 minutes of trading per day) to find intraday extremes.

### 3. Real-Time Data Simulation
For `subscribe_realtime(tickers, callback)`, the simulator will use a background thread to mimic real-time WebSocket events.

```python
import threading
import time

class SimulatedMarketClient(MarketClientBase):
    def __init__(self):
        self.generators = {
            "AAPL": GBMPriceGenerator(150.0, 0.05, 0.2),
            "GOOG": GBMPriceGenerator(2800.0, 0.07, 0.25)
        }
        self.running = False
        self.thread = None
        
    def subscribe_realtime(self, tickers: List[str], callback: Callable[[Dict[str, Any]], None]):
        self.running = True
        self.thread = threading.Thread(target=self._simulate_stream, args=(tickers, callback))
        self.thread.start()
        
    def _simulate_stream(self, tickers: List[str], callback: Callable[[Dict[str, Any]], None]):
        while self.running:
            for ticker in tickers:
                if ticker not in self.generators:
                    self.generators[ticker] = GBMPriceGenerator(100.0, 0.05, 0.2)
                
                new_price = self.generators[ticker].get_next_price(dt=1/(252*390))
                callback({"ticker": ticker, "price": new_price, "timestamp": time.time()})
                
            time.sleep(1) # Emit an event every second

    def disconnect(self):
        self.running = False
        if self.thread:
            self.thread.join()
```

## Reproducibility
For testing purposes, the simulator should allow seeding the random number generator (`random.seed()`). This ensures that unit tests always receive the same sequence of "random" prices.

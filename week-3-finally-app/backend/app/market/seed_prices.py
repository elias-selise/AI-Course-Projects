"""Seed prices and parameters for market data simulator."""

SEED_PRICES = {
    "AAPL": 190.0,
    "GOOGL": 175.0,
    "MSFT": 420.0,
    "AMZN": 180.0,
    "TSLA": 220.0,
    "NVDA": 120.0,
    "META": 500.0,
    "JPM": 200.0,
    "V": 270.0,
    "NFLX": 650.0,
}

# Per-ticker parameters: (drift mu, volatility sigma)
GBM_PARAMS = {
    "AAPL": (0.05, 0.20),
    "GOOGL": (0.05, 0.22),
    "MSFT": (0.06, 0.18),
    "AMZN": (0.05, 0.25),
    "TSLA": (0.08, 0.45),
    "NVDA": (0.10, 0.40),
    "META": (0.07, 0.30),
    "JPM": (0.04, 0.15),
    "V": (0.04, 0.16),
    "NFLX": (0.06, 0.28),
}

# Sector groups for correlation matrix
CORRELATION_GROUPS = {
    "TECH": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META"],
    "FINANCE": ["JPM", "V"],
    "MEDIA": ["NFLX"],
}

SAME_GROUP_CORR = 0.6
CROSS_GROUP_CORR = 0.3

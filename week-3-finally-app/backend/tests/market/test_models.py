from app.market.models import PriceUpdate


def test_price_update_creation():
    update = PriceUpdate(
        ticker="AAPL",
        price=190.5,
        previous_price=190.0,
        timestamp="2026-08-08T12:00:00Z",
        change=0.5,
        direction="up",
    )
    assert update.ticker == "AAPL"
    assert update.price == 190.5
    assert update.previous_price == 190.0
    assert update.change == 0.5
    assert update.direction == "up"


def test_price_update_to_dict():
    update = PriceUpdate(
        ticker="GOOGL",
        price=175.0,
        previous_price=176.0,
        timestamp="2026-08-08T12:00:00Z",
        change=-1.0,
        direction="down",
    )
    d = update.to_dict()
    assert d["ticker"] == "GOOGL"
    assert d["price"] == 175.0
    assert d["direction"] == "down"


def test_price_update_to_json():
    update = PriceUpdate(
        ticker="MSFT",
        price=420.0,
        previous_price=420.0,
        timestamp="2026-08-08T12:00:00Z",
        change=0.0,
        direction="flat",
    )
    json_str = update.to_json()
    assert '"ticker": "MSFT"' in json_str
    assert '"direction": "flat"' in json_str

def test_get_initial_portfolio(client):
    response = client.get("/api/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert data["cash_balance"] == 10000.0
    assert data["positions"] == []
    assert data["total_portfolio_value"] == 10000.0
    assert data["total_unrealized_pnl"] == 0.0


def test_buy_trade_execution(client):
    trade_payload = {"ticker": "AAPL", "quantity": 10, "side": "buy"}
    response = client.post("/api/portfolio/trade", json=trade_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["trade"]["ticker"] == "AAPL"
    assert data["trade"]["side"] == "buy"
    assert data["trade"]["quantity"] == 10
    assert data["cash_balance"] < 10000.0

    # Verify portfolio state
    p_response = client.get("/api/portfolio")
    p_data = p_response.json()
    assert len(p_data["positions"]) == 1
    assert p_data["positions"][0]["ticker"] == "AAPL"
    assert p_data["positions"][0]["quantity"] == 10


def test_sell_trade_execution(client):
    # Buy 10 AAPL first
    client.post("/api/portfolio/trade", json={"ticker": "AAPL", "quantity": 10, "side": "buy"})

    # Partial sell 4 AAPL
    sell_res = client.post("/api/portfolio/trade", json={"ticker": "AAPL", "quantity": 4, "side": "sell"})
    assert sell_res.status_code == 200
    s_data = sell_res.json()
    assert s_data["success"] is True

    p_data = client.get("/api/portfolio").json()
    assert len(p_data["positions"]) == 1
    assert p_data["positions"][0]["quantity"] == 6

    # Sell remaining 6 AAPL
    sell_all = client.post("/api/portfolio/trade", json={"ticker": "AAPL", "quantity": 6, "side": "sell"})
    assert sell_all.status_code == 200

    p_data_after = client.get("/api/portfolio").json()
    assert len(p_data_after["positions"]) == 0


def test_fractional_shares_trade(client):
    trade_payload = {"ticker": "GOOGL", "quantity": 2.5, "side": "buy"}
    response = client.post("/api/portfolio/trade", json=trade_payload)
    assert response.status_code == 200
    p_data = client.get("/api/portfolio").json()
    assert p_data["positions"][0]["quantity"] == 2.5


def test_trade_validation_errors(client):
    # Quantity <= 0
    res = client.post("/api/portfolio/trade", json={"ticker": "AAPL", "quantity": 0, "side": "buy"})
    assert res.status_code == 422 or res.status_code == 400

    # Invalid side
    res = client.post("/api/portfolio/trade", json={"ticker": "AAPL", "quantity": 5, "side": "hold"})
    assert res.status_code == 422 or res.status_code == 400

    # Insufficient cash
    res = client.post("/api/portfolio/trade", json={"ticker": "AAPL", "quantity": 100000, "side": "buy"})
    assert res.status_code == 400
    assert "Insufficient cash" in res.json()["detail"]

    # Sell not owned
    res = client.post("/api/portfolio/trade", json={"ticker": "NVDA", "quantity": 5, "side": "sell"})
    assert res.status_code == 400
    assert "Insufficient shares owned" in res.json()["detail"]


def test_portfolio_history(client):
    response = client.get("/api/portfolio/history")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) >= 1
    assert "total_value" in history[0]
    assert "recorded_at" in history[0]

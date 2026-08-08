def test_chat_mock_mode_general(client):
    response = client.post("/api/chat", json={"message": "What is my current portfolio value?"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "chat_message_id" in data
    assert isinstance(data["trades_executed"], list)
    assert isinstance(data["watchlist_changes"], list)


def test_chat_mock_trade_execution(client):
    response = client.post("/api/chat", json={"message": "Please buy 5 AAPL for me"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["trades_executed"]) == 1
    assert data["trades_executed"][0]["success"] is True

    # Check portfolio updated
    portfolio = client.get("/api/portfolio").json()
    assert len(portfolio["positions"]) == 1
    assert portfolio["positions"][0]["ticker"] == "AAPL"
    assert portfolio["positions"][0]["quantity"] == 5


def test_chat_mock_watchlist_action(client):
    response = client.post("/api/chat", json={"message": "Please add TSLA to watchlist"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["watchlist_changes"]) == 1

    wl = client.get("/api/watchlist").json()
    tickers = [item["ticker"] for item in wl]
    assert "TSLA" in tickers

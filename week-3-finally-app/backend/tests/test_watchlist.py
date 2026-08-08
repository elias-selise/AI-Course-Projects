def test_get_watchlist(client):
    response = client.get("/api/watchlist")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    tickers = [item["ticker"] for item in data]
    assert "AAPL" in tickers
    assert "GOOGL" in tickers
    assert len(tickers) == 10


def test_add_watchlist_ticker(client):
    response = client.post("/api/watchlist", json={"ticker": "AMD"})
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AMD"

    wl = client.get("/api/watchlist").json()
    tickers = [item["ticker"] for item in wl]
    assert "AMD" in tickers


def test_remove_watchlist_ticker(client):
    delete_res = client.delete("/api/watchlist/AAPL")
    assert delete_res.status_code == 200
    assert delete_res.json()["success"] is True

    wl = client.get("/api/watchlist").json()
    tickers = [item["ticker"] for item in wl]
    assert "AAPL" not in tickers


def test_remove_nonexistent_ticker(client):
    delete_res = client.delete("/api/watchlist/NONEXISTENT")
    assert delete_res.status_code == 404

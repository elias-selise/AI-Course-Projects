def test_nonexistent_api_route(client):
    response = client.get("/api/nonexistent")
    assert response.status_code == 404

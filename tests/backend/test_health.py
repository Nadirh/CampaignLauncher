from httpx import AsyncClient


async def test_health_returns_200(client: AsyncClient) -> None:
    response = await client.get("/api/health")
    assert response.status_code == 200


async def test_health_returns_correct_body(client: AsyncClient) -> None:
    response = await client.get("/api/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "campaign-launcher-api"

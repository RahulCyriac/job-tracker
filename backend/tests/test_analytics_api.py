import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.db.session import get_db
from httpx import ASGITransport, AsyncClient
@pytest.fixture
async def async_client(db_session:AsyncSession):
    app.dependency_overrides[get_db] = lambda : db_session

    async with AsyncClient(
        transport = ASGITransport(app = app),base_url = "http://test"

    ) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_analytics_response_empty_database(async_client:AsyncClient):
    payload = {
        "total_applications":"0",
        "ghosted_count":"0",
        "active_count":"0", 
        "responded_count":"0",
        "median_response_time_days":None,
        "sources":"",
        "funnel":{"applied":"0",
            "screening":"0",
            "interviewing":"0",
            "offer":"0",
            "rejected":"0",
            "ghosted":"0"}
    }

    res = await async_client.get("/api/v1/analytics/")
    assert res.status_code == 200
    data = res.json()
    assert data["total_applications"] == 0
    assert data["median_response_time_days"] is None

@pytest.mark.asyncio
async def test_analytics_response_non_empty_database(async_client:AsyncClient):

    payload = {
            "company_name":"Google",
            "role_title": "Backend Dev",
            "source":"other",
            "location_type":"remote",
              }
    await async_client.post("/api/v1/applications/",json = payload)
    res = await async_client.get("/api/v1/analytics/")
    assert res.status_code == 200
    data = res.json()
    assert data["total_applications"] == 1
    assert data["active_count"] == 1
    assert data["sources"]["other"]["total"] == 1




        
    

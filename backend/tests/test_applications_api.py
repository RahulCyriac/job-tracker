import uuid
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.main import app
from datetime import datetime,timezone,timedelta

@pytest.fixture
async def async_client(db_session: AsyncSession):
  # Override FastAPI get_db dependency to use our in-memory test database
  app.dependency_overrides[get_db] = lambda: db_session

  async with AsyncClient(
      transport=ASGITransport(app=app), base_url="http://test"
  ) as client:
    yield client

  app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_and_get_application(async_client: AsyncClient):
  # 1. Test POST /api/v1/applications/
  payload = {
      "company_name": "Netflix",
      "role_title": "Platform Engineer",
      "source": "linkedin",
      "location_type": "remote",
  }
  res = await async_client.post("/api/v1/applications/", json=payload)
  assert res.status_code in (200, 201)
  data = res.json()
  assert data["company_name"] == "Netflix"
  assert data["current_status"] == "APPLIED"
  assert len(data["events"]) == 1

  app_id = data["id"]

  # 2. Test GET /api/v1/applications/{id}
  get_res = await async_client.get(f"/api/v1/applications/{app_id}")
  assert get_res.status_code == 200
  assert get_res.json()["id"] == app_id


@pytest.mark.asyncio
async def test_update_status_api(async_client: AsyncClient):
  # Create application
  res = await async_client.post(
      "/api/v1/applications/",
      json={"company_name": "Meta", "role_title": "Systems Engineer"},
  )
  app_id = res.json()["id"]

  # Patch Status to SCREENING
  patch_res = await async_client.patch(
      f"/api/v1/applications/{app_id}/status",
      json={"to_status": "SCREENING", "note": "Recruiter call scheduled"},
  )
  assert patch_res.status_code == 200
  data = patch_res.json()
  assert data["current_status"] == "SCREENING"
  assert data["date_first_response"] is not None
  assert len(data["events"]) == 2


@pytest.mark.asyncio
async def test_get_nonexistent_application_returns_404(
    async_client: AsyncClient,
):
  random_uuid = str(uuid.uuid4())
  res = await async_client.get(f"/api/v1/applications/{random_uuid}")
  assert res.status_code == 404

@pytest.mark.asyncio
async def  test_api_detect_ghosted(async_client:  AsyncClient,db_session: AsyncSession):
  today = datetime.now(timezone.utc).date()
  twenty_days_ago = (today - timedelta(days=20)).isoformat()
  ten_days_ago = (today - timedelta(days=10)).isoformat()
  payload = {
            "company_name": "Netflix",
            "role_title": "Platform Engineer",
            "source": "linkedin",
            "location_type": "remote",
            "date_applied" : twenty_days_ago,
            }
  await async_client.post("/api/v1/applications/",json= payload)
  res = await async_client.post("/api/v1/applications/detect-ghosted?days_threshold=14")
  data = res.json()
  print(data)
  assert len(data) == 1
  assert data[0]["company_name"] == "Netflix"
  assert data[0]["current_status"] == "GHOSTED"
  assert len(data[0]["events"]) == 2
  



  payload = {
              "company_name": "Amazon",
              "role_title": "Platform Engineer",
              "source": "linkedin",
              "location_type": "remote",
              "date_applied" : ten_days_ago,
              }
  create_res = await async_client.post("/api/v1/applications/",json= payload)
  amazon_id = create_res.json()["id"]
  res = await async_client.post("/api/v1/applications/detect-ghosted?days_threshold=14")
  data = res.json()
  assert data == []

  get_res = await async_client.get(f"/api/v1/applications/{amazon_id}")
  assert get_res.json()["current_status"] == "APPLIED"
  assert len(get_res.json()["events"]) == 1
    
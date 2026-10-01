from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.db.session import get_db
from app.main import app as fastapi_app
from app.schemas.user import UserCreate
from app.services.user import UserService


@pytest.fixture
async def multi_tenant_client(db_session: AsyncSession):
    """Client for testing multi-tenancy without fixed user dependency overrides."""
    fastapi_app.dependency_overrides[get_db] = lambda: db_session
    # Note: We do NOT override get_current_user here so real Bearer tokens are validated!
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as client:
        yield client
    fastapi_app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_tenant_application_isolation(
    multi_tenant_client: AsyncClient, db_session: AsyncSession
):
    # 1. Register User Alice and User Bob
    alice = await UserService.create_user(
        db_session, user_in=UserCreate(email="alice@tenant.com", password="alicepassword123")
    )
    bob = await UserService.create_user(
        db_session, user_in=UserCreate(email="bob@tenant.com", password="bobpassword123")
    )

    alice_token = create_access_token(data={"sub": str(alice.id)})
    bob_token = create_access_token(data={"sub": str(bob.id)})

    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # 2. Alice creates two applications
    await multi_tenant_client.post(
        "/api/v1/applications/",
        json={"company_name": "AliceCorp", "role_title": "Backend Dev"},
        headers=alice_headers,
    )
    await multi_tenant_client.post(
        "/api/v1/applications/",
        json={"company_name": "AliceAI", "role_title": "ML Engineer"},
        headers=alice_headers,
    )

    # 3. Bob creates one application
    bob_app_res = await multi_tenant_client.post(
        "/api/v1/applications/",
        json={"company_name": "BobLogistics", "role_title": "DevOps Engineer"},
        headers=bob_headers,
    )
    assert bob_app_res.status_code == 201
    bob_app_id = bob_app_res.json()["id"]

    # 4. Verify Alice only sees her 2 applications
    alice_list_res = await multi_tenant_client.get(
        "/api/v1/applications/", headers=alice_headers
    )
    assert alice_list_res.status_code == 200
    alice_apps = alice_list_res.json()
    assert len(alice_apps) == 2
    assert all(a["company_name"] in ["AliceCorp", "AliceAI"] for a in alice_apps)

    # 5. Verify Bob only sees his 1 application
    bob_list_res = await multi_tenant_client.get(
        "/api/v1/applications/", headers=bob_headers
    )
    assert bob_list_res.status_code == 200
    bob_apps = bob_list_res.json()
    assert len(bob_apps) == 1
    assert bob_apps[0]["company_name"] == "BobLogistics"

    # 6. IDOR TEST: Alice attempts to GET Bob's application directly
    idor_get_res = await multi_tenant_client.get(
        f"/api/v1/applications/{bob_app_id}", headers=alice_headers
    )
    assert idor_get_res.status_code == 404
    assert idor_get_res.json()["detail"] == "Application not found"

    # 7. IDOR TEST: Alice attempts to PATCH Bob's application status
    idor_patch_res = await multi_tenant_client.patch(
        f"/api/v1/applications/{bob_app_id}/status",
        json={"to_status": "OFFER"},
        headers=alice_headers,
    )
    assert idor_patch_res.status_code == 404

    # 8. IDOR TEST: Alice attempts to DELETE Bob's application
    idor_del_res = await multi_tenant_client.delete(
        f"/api/v1/applications/{bob_app_id}", headers=alice_headers
    )
    assert idor_del_res.status_code == 404

    # 9. Verify Bob's application is STILL intact and untouched
    bob_verify_res = await multi_tenant_client.get(
        f"/api/v1/applications/{bob_app_id}", headers=bob_headers
    )
    assert bob_verify_res.status_code == 200
    assert bob_verify_res.json()["current_status"] == "APPLIED"

    # 10. Analytics Isolation: Verify Alice's metrics count = 2, Bob's = 1
    alice_analytics = await multi_tenant_client.get(
        "/api/v1/analytics/", headers=alice_headers
    )
    assert alice_analytics.status_code == 200
    assert alice_analytics.json()["total_applications"] == 2

    bob_analytics = await multi_tenant_client.get(
        "/api/v1/analytics/", headers=bob_headers
    )
    assert bob_analytics.status_code == 200
    assert bob_analytics.json()["total_applications"] == 1

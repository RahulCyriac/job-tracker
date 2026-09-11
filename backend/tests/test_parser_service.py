import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.job_parser import JobParserService
@pytest.mark.asyncio
async def test_parse_full_posting_with_k_salary(
    db_session:AsyncSession,
):
    text = "Google is hiring a Senior Backend Engineer (Remote). Salary: $140k - $180k. Apply at: https://careers.google.com/jobs/1"
    res = await JobParserService.parse(text)
    assert res.company_name == "Google"
    assert res.role_title == "Senior Backend Engineer"
    assert res.location_type == "remote"
    assert res.salary_range_min == 140000
    assert res.salary_range_max == 180000
    assert res.job_url == "https://careers.google.com/jobs/1"

@pytest.mark.asyncio
async def test_parse_posting_with_lakhs_and_hybrid(
        db_session:AsyncSession,
        ):
    text = "Frontend Developer at Swiggy (Hybrid). Compensation: ₹12l to ₹18l per annum."
    res = await JobParserService.parse(text)
    assert res.company_name == "Swiggy"
    assert res.role_title == "Frontend Developer"
    assert res.location_type == "hybrid"
    assert res.salary_range_min == 1200000
    assert res.salary_range_max == 1800000

@pytest.mark.asyncio
async def test_parse_minimal_posting(
    db_session:AsyncSession,
                                     ):

    text = "Software Engineer at Uber. Requirements: Python, FastAPI."
    res = await JobParserService.parse(text)
    assert res.company_name == "Uber"
    assert res.role_title == "Software Engineer"
    assert res.salary_range_min is None
    assert res.salary_range_max is None
    assert res.job_url is None
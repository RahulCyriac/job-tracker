from pydantic import BaseModel, ConfigDict

class JobParseRequest(BaseModel):
    text: str
    url: str | None = None

class JobParseResponse(BaseModel):
    company_name: str | None = None
    role_title: str | None = None
    location_type: str | None = None
    salary_range_min: int | None = None
    salary_range_max: int | None = None
    job_url: str | None = None
    raw_posting_text: str
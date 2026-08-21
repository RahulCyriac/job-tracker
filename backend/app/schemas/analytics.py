from pydantic import BaseModel,ConfigDict

class SourceMetric(BaseModel):
    total:int
    responded:int
    response_rate_pct:float 

class FunnelMetric(BaseModel):
    applied:int 
    screening:int
    interviewing:int 
    offer:int 
    rejected:int 
    ghosted:int

class AnalyticsResponse(BaseModel):
    total_applications:int
    ghosted_count:int 
    active_count:int 
    responded_count:int 
    median_response_time_days:float | None 
    sources:dict[str,SourceMetric]
    funnel:FunnelMetric
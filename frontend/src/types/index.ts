
export type StatusType =
  | 'APPLIED'
  | 'SCREENING'
  | 'INTERVIEWING'
  | 'OFFER'
  | 'REJECTED'
  | 'GHOSTED';

export interface StatusEvent {
  id: string;
  application_id: string;
  from_status: string | null;
  to_status: string;
  timestamp: string;
  note: string | null;
}

export interface Application {
  id: string;
  company_name: string;
  role_title: string;
  job_url: string | null;
  raw_posting_text: string | null;
  source: string | null;
  current_status: StatusType;
  date_applied: string;
  date_first_response: string | null;
  salary_range_min: number | null;
  salary_range_max: number | null;
  location_type: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  events: StatusEvent[];
}

export interface ApplicationCreate {
  company_name: string;
  role_title: string;
  job_url?: string;
  source?: string;
  location_type?: string;
  salary_range_min?: number;
  salary_range_max?: number;
  notes?: string;
  date_applied?: string;
}

export interface AnalyticsResponse{
  total_applications: number;
  ghosted_count: number;
  active_count: number;
  responded_count:number ;
  median_response_time_days?:number; 
  sources:{[key:string]:SourceMetric};
  funnel:FunnelMetric;
  }

export interface SourceMetric{
  total:number;
  responded:number;
  response_rate_pct:number
}

export interface FunnelMetric{
  applied:number; 
  screening:number;
  interviewing:number;
  offer:number;
  rejected:number ;
  ghosted:number;
}
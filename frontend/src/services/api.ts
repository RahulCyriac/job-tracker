import { Application, ApplicationCreate, StatusType } from '@/types';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function createApplication(
  data: ApplicationCreate
): Promise<Application> {
  const res = await fetch(`${API_BASE_URL}/applications/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create application');
  return res.json();
}

export async function getApplications(): Promise<Application[]> {
  const res = await fetch(`${API_BASE_URL}/applications/`, {
    cache: 'no-store',
  });
  if (!res.ok) throw new Error('Failed to fetch applications');
  return res.json();
}

export async function updateApplicationStatus(
  id: string,
  toStatus: StatusType,
  note?: string
): Promise<Application> {
  const res = await fetch(`${API_BASE_URL}/applications/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ to_status: toStatus, note }),
  });
  if (!res.ok) throw new Error('Failed to update status');
  return res.json();
}

export async function detectGhostedApplications(
  daysThreshold = 14
): Promise<Application[]> {
  const res = await fetch(
    `${API_BASE_URL}/applications/detect-ghosted?days_threshold=${daysThreshold}`,
    {
      method: 'POST',
    }
  );
  if (!res.ok) throw new Error('Failed to run ghost detection');
  return res.json();
}

export async function deleteApplication(id: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/applications/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete application');
}
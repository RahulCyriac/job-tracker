'use client';

import React from 'react';
import { Application, StatusType } from '@/types';

interface ApplicationCardProps {
  application: Application;
  onStatusChange: (id: string, newStatus: StatusType) => void;
  onDelete: (id: string) => void;
}

export const ApplicationCard: React.FC<ApplicationCardProps> = ({
  application,
  onStatusChange,
  onDelete,
}) => {
  const getDaysAgo = (dateStr: string) => {
    const applied = new Date(dateStr);
    const today = new Date();
    const diffTime = Math.abs(today.getTime() - applied.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    return diffDays === 0
      ? 'Today'
      : `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  return (
    <div className="app-card">
      <div className="card-top">
        <div>
          <h3 className="company-name">{application.company_name}</h3>
          <p className="role-title">{application.role_title}</p>
        </div>
        {application.location_type && (
          <span className="tag" style={{ textTransform: 'capitalize' }}>
            {application.location_type}
          </span>
        )}
      </div>

      <div className="card-meta">
        {application.source && (
          <span className="tag">🏷️ {application.source}</span>
        )}

        {(application.salary_range_min || application.salary_range_max) && (
          <span className="tag">
            💰 $
            {application.salary_range_min?.toLocaleString() ||
              application.salary_range_max?.toLocaleString()}
            {application.salary_range_min && application.salary_range_max
              ? ` - $${application.salary_range_max.toLocaleString()}`
              : ''}
          </span>
        )}
      </div>

      {application.notes && (
        <p
          style={{
            fontSize: '0.75rem',
            color: 'var(--text-subtle)',
            fontStyle: 'italic',
          }}
        >
          &quot;{application.notes}&quot;
        </p>
      )}

      <div className="card-footer">
        <span className="days-badge">
          📅 {getDaysAgo(application.date_applied)}
        </span>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <select
            className="status-select"
            value={application.current_status}
            onChange={(e) =>
              onStatusChange(application.id, e.target.value as StatusType)
            }
          >
            <option value="APPLIED">Applied</option>
            <option value="SCREENING">Screening</option>
            <option value="INTERVIEWING">Interviewing</option>
            <option value="OFFER">Offer</option>
            <option value="REJECTED">Rejected</option>
            <option value="GHOSTED">Ghosted</option>
          </select>

          <button
            onClick={() => onDelete(application.id)}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              fontSize: '0.85rem',
              opacity: 0.6,
            }}
            title="Delete Application"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
};
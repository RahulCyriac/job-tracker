'use client';

import React, { useEffect, useState } from 'react';
import { AnalyticsResponse } from '@/types';
import { getAnalytics } from '@/services/api';

interface AnalyticsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AnalyticsModal: React.FC<AnalyticsModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch analytics whenever modal opens
  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      getAnalytics()
        .then((res) => setData(res))
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content"
        style={{ maxWidth: '680px' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="modal-header">
          <div>
            <h2 className="modal-title">📊 Pipeline Analytics & Insights</h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Outlier-Resilient Survival Metrics
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: '1.2rem',
              cursor: 'pointer',
            }}
          >
            ✕
          </button>
        </div>

        {loading || !data ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            <p>⏳ Computing statistical metrics...</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* 1. The 4 Top Stat Summary Cards */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '0.75rem',
              }}
            >
              <div
                style={{
                  background: 'var(--bg-input)',
                  padding: '0.85rem',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center',
                }}
              >
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Tracked</p>
                <p style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>{data.total_applications}</p>
              </div>

              <div
                style={{
                  background: 'var(--bg-input)',
                  padding: '0.85rem',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center',
                }}
              >
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Median Response</p>
                <p style={{ fontSize: '1.4rem', fontWeight: 'bold', color: 'var(--status-applied)' }}>
                  {data.median_response_time_days !== null
                    ? `${data.median_response_time_days}d`
                    : 'N/A'}
                </p>
              </div>

              <div
                style={{
                  background: 'var(--bg-input)',
                  padding: '0.85rem',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center',
                }}
              >
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Ghosted Rate</p>
                <p style={{ fontSize: '1.4rem', fontWeight: 'bold', color: 'var(--status-ghosted)' }}>
                  {data.total_applications > 0
                    ? `${((data.ghosted_count / data.total_applications) * 100).toFixed(1)}%`
                    : '0%'}
                </p>
              </div>

              <div
                style={{
                  background: 'var(--bg-input)',
                  padding: '0.85rem',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center',
                }}
              >
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Active In-Flight</p>
                <p style={{ fontSize: '1.4rem', fontWeight: 'bold', color: 'var(--status-interviewing)' }}>
                  {data.active_count}
                </p>
              </div>
            </div>

            {/* 2. Source Breakdown (ROI) */}
            <div
              style={{
                background: 'var(--bg-input)',
                padding: '1rem',
                borderRadius: 'var(--radius-md)',
              }}
            >
              <h3 style={{ fontSize: '0.9rem', marginBottom: '0.75rem', color: '#fff' }}>
                🏷️ Response Rate by Source
              </h3>
              {Object.keys(data.sources).length === 0 ? (
                <p style={{ fontSize: '0.8rem', color: 'var(--text-subtle)' }}>No source data yet</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {Object.entries(data.sources).map(([src, metric]) => (
                    <div key={src} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ textTransform: 'capitalize', fontSize: '0.85rem' }}>{src}</span>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {metric.responded} / {metric.total} responded ({metric.response_rate_pct}%)
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 3. Funnel Stages Breakdown */}
            <div
              style={{
                background: 'var(--bg-input)',
                padding: '1rem',
                borderRadius: 'var(--radius-md)',
              }}
            >
              <h3 style={{ fontSize: '0.9rem', marginBottom: '0.75rem', color: '#fff' }}>
                🔄 Stage-by-Stage Funnel Status
              </h3>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(6, 1fr)',
                  gap: '0.5rem',
                  textAlign: 'center',
                }}
              >
                <div>
                  <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Applied</p>
                  <p style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{data.funnel.applied}</p>
                </div>
                <div>
                  <p style={{ fontSize: '0.7rem', color: 'var(--status-screening)' }}>Screening</p>
                  <p style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{data.funnel.screening}</p>
                </div>
                <div>
                  <p style={{ fontSize: '0.7rem', color: 'var(--status-interviewing)' }}>Interview</p>
                  <p style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{data.funnel.interviewing}</p>
                </div>
                <div>
                  <p style={{ fontSize: '0.7rem', color: 'var(--status-offer)' }}>Offer 🎉</p>
                  <p style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{data.funnel.offer}</p>
                </div>
                <div>
                  <p style={{ fontSize: '0.7rem', color: 'var(--status-rejected)' }}>Rejected</p>
                  <p style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{data.funnel.rejected}</p>
                </div>
                <div>
                  <p style={{ fontSize: '0.7rem', color: 'var(--status-ghosted)' }}>Ghosted</p>
                  <p style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{data.funnel.ghosted}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
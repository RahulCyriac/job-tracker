'use client';

import React from 'react';

interface NavbarProps {
  onOpenAddModal: () => void;
  onDetectGhosted: () => void;
  onOpenAnalyticsModal: () => void;
  isDetecting: boolean;
  totalApplications: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenAddModal,
  onDetectGhosted,
  onOpenAnalyticsModal,
  isDetecting,
  totalApplications,
}) => {
  return (
    <header className="navbar">
      <div className="nav-brand">
        <span style={{ fontSize: '1.5rem' }}>🎯</span>
        <div>
          <h1>Job Application Tracker</h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Event-Sourced Analytics Platform
          </p>
        </div>
      </div>

      <div className="nav-actions">
        <span
          className="tag"
          style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
        >
          Total Tracked: <strong>{totalApplications}</strong>
        </span>

        <button
          className="btn btn-secondary"
          onClick={onDetectGhosted}
          disabled={isDetecting}
        >
          {isDetecting ? '⚙️ Scanning...' : '👻 Auto-Detect Ghosted'}
        </button>

        <button className="btn btn-primary" onClick={onOpenAddModal}>
          + Add Application
        </button>


        <button className="btn btn-secondary" onClick = {onOpenAnalyticsModal}> 
          Analytics
        </button>
      </div>
    </header>
  );
};
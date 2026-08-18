'use client';

import React, { useEffect, useState } from 'react';
import { Application, ApplicationCreate, StatusType } from '@/types';
import {
  getApplications,
  createApplication,
  updateApplicationStatus,
  deleteApplication,
  detectGhostedApplications,
} from '@/services/api';
import { Navbar } from '@/components/Navbar';
import { ApplicationCard } from '@/components/ApplicationCard';
import { AddApplicationModal } from '@/components/AddApplicationModal';

const COLUMNS: {
  key: StatusType;
  label: string;
  icon: string;
  color: string;
}[] = [
  { key: 'APPLIED', label: 'Applied', icon: '📬', color: 'var(--status-applied)' },
  { key: 'SCREENING', label: 'Screening', icon: '📞', color: 'var(--status-screening)' },
  { key: 'INTERVIEWING', label: 'Interviewing', icon: '💼', color: 'var(--status-interviewing)' },
  { key: 'OFFER', label: 'Offer', icon: '🎉', color: 'var(--status-offer)' },
  { key: 'REJECTED', label: 'Rejected', icon: '❌', color: 'var(--status-rejected)' },
  { key: 'GHOSTED', label: 'Ghosted', icon: '👻', color: 'var(--status-ghosted)' },
];

export default function KanbanPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await getApplications();
      setApplications(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (formData: ApplicationCreate) => {
    const newApp = await createApplication(formData);
    setApplications((prev) => [newApp, ...prev]);
  };

  const handleStatusChange = async (id: string, newStatus: StatusType) => {
    try {
      const updated = await updateApplicationStatus(id, newStatus);
      setApplications((prev) =>
        prev.map((app) => (app.id === id ? updated : app))
      );
    } catch (err) {
      console.error(err);
      alert('Failed to update status.');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this application?')) return;
    try {
      await deleteApplication(id);
      setApplications((prev) => prev.filter((app) => app.id !== id));
    } catch (err) {
      console.error(err);
      alert('Failed to delete application.');
    }
  };

  const handleDetectGhosted = async () => {
    try {
      setIsDetecting(true);
      const ghosted = await detectGhostedApplications(14);
      if (ghosted.length > 0) {
        alert(`👻 Auto-detected ${ghosted.length} application(s) as ghosted!`);
        await loadData();
      } else {
        alert('✨ No inactive applications found to ghost.');
      }
    } catch (err) {
      console.error(err);
      alert('Failed to run ghost detection.');
    } finally {
      setIsDetecting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar
        onOpenAddModal={() => setIsModalOpen(true)}
        onDetectGhosted={handleDetectGhosted}
        isDetecting={isDetecting}
        totalApplications={applications.length}
      />

      <main className="kanban-container">
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
            <p style={{ fontSize: '1.2rem' }}>⏳ Loading your applications from database...</p>
          </div>
        ) : (
          <div className="kanban-grid">
            {COLUMNS.map((col) => {
              const columnCards = applications.filter(
                (app) => app.current_status === col.key
              );

              return (
                <div key={col.key} className="kanban-column">
                  <div className="column-header">
                    <div className="column-title-wrap">
                      <span>{col.icon}</span>
                      <span className="column-title" style={{ color: col.color }}>
                        {col.label}
                      </span>
                    </div>
                    <span className="column-badge">{columnCards.length}</span>
                  </div>

                  <div className="column-cards">
                    {columnCards.length === 0 ? (
                      <p
                        style={{
                          fontSize: '0.75rem',
                          color: 'var(--text-subtle)',
                          textAlign: 'center',
                          marginTop: '1.5rem',
                        }}
                      >
                        No applications
                      </p>
                    ) : (
                      columnCards.map((app) => (
                        <ApplicationCard
                          key={app.id}
                          application={app}
                          onStatusChange={handleStatusChange}
                          onDelete={handleDelete}
                        />
                      ))
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      <AddApplicationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreate}
      />
    </div>
  );
}
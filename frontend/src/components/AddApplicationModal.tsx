'use client';

import React, { useState } from 'react';
import { ApplicationCreate } from '@/types';

interface AddModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ApplicationCreate) => Promise<void>;
}

export const AddApplicationModal: React.FC<AddModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [companyName, setCompanyName] = useState('');
  const [roleTitle, setRoleTitle] = useState('');
  const [source, setSource] = useState('linkedin');
  const [locationType, setLocationType] = useState('remote');
  const [salaryMin, setSalaryMin] = useState('');
  const [salaryMax, setSalaryMax] = useState('');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName || !roleTitle) return;

    setIsSubmitting(true);
    try {
      await onSubmit({
        company_name: companyName,
        role_title: roleTitle,
        source: source || undefined,
        location_type: locationType || undefined,
        salary_range_min: salaryMin ? parseInt(salaryMin) : undefined,
        salary_range_max: salaryMax ? parseInt(salaryMax) : undefined,
        notes: notes || undefined,
      });

      setCompanyName('');
      setRoleTitle('');
      setSalaryMin('');
      setSalaryMax('');
      setNotes('');
      onClose();
    } catch (err) {
      console.error(err);
      alert('Failed to save application.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">✨ Add Job Application</h2>
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

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Company Name *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Google, Netflix, Stripe"
              required
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Role Title *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Backend Software Engineer"
              required
              value={roleTitle}
              onChange={(e) => setRoleTitle(e.target.value)}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Source</label>
              <select
                className="form-input"
                value={source}
                onChange={(e) => setSource(e.target.value)}
              >
                <option value="linkedin">LinkedIn</option>
                <option value="referral">Referral</option>
                <option value="naukri">Naukri</option>
                <option value="company_site">Company Website</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Location Type</label>
              <select
                className="form-input"
                value={locationType}
                onChange={(e) => setLocationType(e.target.value)}
              >
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">On-Site</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Min Salary ($)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 120000"
                value={salaryMin}
                onChange={(e) => setSalaryMin(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Max Salary ($)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 160000"
                value={salaryMax}
                onChange={(e) => setSalaryMax(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Notes / Referral Info</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Referred by senior engineer"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Save Application'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
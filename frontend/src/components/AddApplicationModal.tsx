'use client';

import React, { useState } from 'react';
import { ApplicationCreate } from '@/types';
import { parseJob } from '@/services/api';

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

  // Auto-Fill Text Parser State
  const [pasteText, setPasteText] = useState('');
  const [isParsing, setIsParsing] = useState(false);
  const [showPasteBox, setShowPasteBox] = useState(false);

  if (!isOpen) return null;

  const handleAutoFill = async () => {
    if (!pasteText.trim()) return;
    setIsParsing(true);
    try {
      const parsed = await parseJob({ text: pasteText });
      if (parsed.company_name) setCompanyName(parsed.company_name);
      if (parsed.role_title) setRoleTitle(parsed.role_title);
      if (
        parsed.location_type &&
        ['remote', 'hybrid', 'onsite'].includes(parsed.location_type.toLowerCase())
      ) {
        setLocationType(parsed.location_type.toLowerCase());
      }
      if (parsed.salary_range_min != null) {
        setSalaryMin(parsed.salary_range_min.toString());
      }
      if (parsed.salary_range_max != null) {
        setSalaryMax(parsed.salary_range_max.toString());
      }
      if (parsed.job_url) {
        setNotes((prev) =>
          prev ? `${prev} | Link: ${parsed.job_url}` : `Link: ${parsed.job_url}`
        );
      }
      setShowPasteBox(false);
    } catch (err) {
      console.error(err);
      alert('Failed to parse job description. Please check your backend connection.');
    } finally {
      setIsParsing(false);
    }
  };

  const handleClose = () => {
    setPasteText('');
    setShowPasteBox(false);
    onClose();
  };

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
      setPasteText('');
      setShowPasteBox(false);
      onClose();
    } catch (err) {
      console.error(err);
      alert('Failed to save application.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">✨ Add Job Application</h2>
          <button
            onClick={handleClose}
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

        {/* Auto-Fill Parser Banner / Dropdown */}
        <div style={{ marginBottom: '1.25rem' }}>
          {!showPasteBox ? (
            <button
              type="button"
              onClick={() => setShowPasteBox(true)}
              className="btn btn-secondary"
              style={{
                width: '100%',
                justifyContent: 'center',
                background: 'rgba(56, 189, 248, 0.08)',
                borderColor: 'rgba(56, 189, 248, 0.3)',
                color: '#38bdf8',
                fontSize: '0.85rem',
              }}
            >
              📋 Auto-Fill with Job Description (LinkedIn / Indeed)
            </button>
          ) : (
            <div
              style={{
                background: 'var(--bg-card)',
                padding: '1rem',
                borderRadius: 'var(--radius-md)',
                border: '1px solid rgba(56, 189, 248, 0.35)',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.6rem',
              }}
            >
              <label
                className="form-label"
                style={{ color: '#38bdf8', fontWeight: 600 }}
              >
                Paste raw posting from LinkedIn / Indeed / Naukri:
              </label>
              <textarea
                className="form-input"
                rows={4}
                placeholder="e.g. 'Google is hiring a Senior Backend Engineer (Remote). Salary: $140k - $180k. Requirements: Python, FastAPI...'"
                value={pasteText}
                onChange={(e) => setPasteText(e.target.value)}
                style={{ width: '100%', resize: 'vertical', fontSize: '0.85rem' }}
              />
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'flex-end',
                  gap: '0.5rem',
                  marginTop: '0.25rem',
                }}
              >
                <button
                  type="button"
                  onClick={() => setShowPasteBox(false)}
                  className="btn btn-secondary"
                  style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleAutoFill}
                  disabled={isParsing || !pasteText.trim()}
                  className="btn btn-primary"
                  style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
                >
                  {isParsing ? '⏳ Parsing...' : '⚡ Auto-Fill Form'}
                </button>
              </div>
            </div>
          )}
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
              onClick={handleClose}
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
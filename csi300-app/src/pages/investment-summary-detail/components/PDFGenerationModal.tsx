/**
 * @fileoverview PDF Generation Progress Modal
 * @module pages/investment-summary-detail/components/PDFGenerationModal
 *
 * Modal component showing real-time PDF generation progress with
 * animated stages and download capability.
 */

import React, { useEffect, useState } from 'react';
import {
  FileText,
  BarChart3,
  FileCode,
  Upload,
  CheckCircle2,
  XCircle,
  Download,
  X,
  Loader2,
} from 'lucide-react';
import { PDFTask } from '@shared/api/generated';

// PDFTaskStatusEnum is now PDFTask.status
const PDFTaskStatusEnum = PDFTask.status;

// ==========================================
// Types
// ==========================================

export interface PDFGenerationModalProps {
  /** Whether modal is visible */
  isOpen: boolean;
  /** Current status */
  status: PDFTask.status | null;
  /** Human-readable status */
  statusDisplay: string;
  /** Progress percentage (0-100) */
  progress: number;
  /** Error message if failed */
  errorMessage: string | null;
  /** Download URL when completed */
  downloadUrl: string | null;
  /** Company name for display */
  companyName?: string;
  /** Close modal handler */
  onClose: () => void;
  /** Retry handler */
  onRetry?: () => void;
}

// ==========================================
// Stage Configuration
// ==========================================

interface Stage {
  id: PDFTaskStatusEnum;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  description: string;
}

const STAGES: Stage[] = [
  {
    id: PDFTaskStatusEnum.PENDING,
    label: 'Preparing',
    icon: FileText,
    description: 'Preparing company data...',
  },
  {
    id: PDFTaskStatusEnum.PROCESSING,
    label: 'Processing',
    icon: FileText,
    description: 'Processing financial data...',
  },
  {
    id: PDFTaskStatusEnum.GENERATING_CHARTS,
    label: 'Charts',
    icon: BarChart3,
    description: 'Generating financial charts...',
  },
  {
    id: PDFTaskStatusEnum.COMPILING,
    label: 'Compiling',
    icon: FileCode,
    description: 'Compiling LaTeX report...',
  },
  {
    id: PDFTaskStatusEnum.UPLOADING,
    label: 'Uploading',
    icon: Upload,
    description: 'Uploading to cloud storage...',
  },
  {
    id: PDFTaskStatusEnum.COMPLETED,
    label: 'Complete',
    icon: CheckCircle2,
    description: 'Report ready for download',
  },
];

// Get stage index for a status
function getStageIndex(status: PDFTaskStatusEnum | null): number {
  if (!status) return -1;
  const index = STAGES.findIndex((s) => s.id === status);
  return index >= 0 ? index : -1;
}

// ==========================================
// Component
// ==========================================

export function PDFGenerationModal({
  isOpen,
  status,
  statusDisplay,
  progress,
  errorMessage,
  downloadUrl,
  companyName,
  onClose,
  onRetry,
}: PDFGenerationModalProps) {
  const [animatedProgress, setAnimatedProgress] = useState(0);

  // Animate progress bar
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedProgress(progress);
    }, 100);
    return () => clearTimeout(timer);
  }, [progress]);

  if (!isOpen) return null;

  const currentStageIndex = getStageIndex(status);
  const isCompleted = status === PDFTaskStatusEnum.COMPLETED;
  const isFailed = status === PDFTaskStatusEnum.FAILED;

  // Handle download
  const handleDownload = () => {
    if (downloadUrl) {
      window.open(downloadUrl, '_blank');
    }
  };

  return (
    <div className="pdf-modal-overlay" onClick={onClose}>
      <div className="pdf-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="pdf-modal-header">
          <div className="pdf-modal-title">
            <FileText size={20} />
            <span>Generating PDF Report</span>
          </div>
          <button className="pdf-modal-close" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="pdf-modal-content">
          {/* Company Name */}
          {companyName && (
            <div className="pdf-modal-company">{companyName}</div>
          )}

          {/* Progress Bar */}
          <div className="pdf-progress-container">
            <div className="pdf-progress-bar">
              <div
                className="pdf-progress-fill"
                style={{ width: `${animatedProgress}%` }}
              />
            </div>
            <div className="pdf-progress-text">{Math.round(animatedProgress)}%</div>
          </div>

          {/* Status Display */}
          <div className="pdf-status-display">
            {isFailed ? (
              <XCircle size={20} className="pdf-status-icon error" />
            ) : isCompleted ? (
              <CheckCircle2 size={20} className="pdf-status-icon success" />
            ) : (
              <Loader2 size={20} className="pdf-status-icon loading" />
            )}
            <span className={`pdf-status-text ${isFailed ? 'error' : ''}`}>
              {statusDisplay || 'Starting...'}
            </span>
          </div>

          {/* Stage Indicators */}
          <div className="pdf-stages">
            {STAGES.slice(0, -1).map((stage, index) => {
              const Icon = stage.icon;
              const isActive = index === currentStageIndex;
              const isComplete = index < currentStageIndex || isCompleted;
              const isPending = index > currentStageIndex && !isFailed;

              return (
                <div
                  key={stage.id}
                  className={`pdf-stage ${isActive ? 'active' : ''} ${isComplete ? 'complete' : ''} ${isPending ? 'pending' : ''}`}
                >
                  <div className="pdf-stage-icon">
                    {isComplete ? (
                      <CheckCircle2 size={16} />
                    ) : (
                      <Icon size={16} />
                    )}
                  </div>
                  <div className="pdf-stage-label">{stage.label}</div>
                </div>
              );
            })}
          </div>

          {/* Error Message */}
          {isFailed && errorMessage && (
            <div className="pdf-error-message">
              <XCircle size={16} />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pdf-modal-footer">
          {isCompleted && downloadUrl ? (
            <button className="pdf-btn primary" onClick={handleDownload}>
              <Download size={16} />
              Download PDF
            </button>
          ) : isFailed && onRetry ? (
            <button className="pdf-btn primary" onClick={onRetry}>
              Retry
            </button>
          ) : null}
          <button className="pdf-btn secondary" onClick={onClose}>
            {isCompleted || isFailed ? 'Close' : 'Cancel'}
          </button>
        </div>
      </div>

      {/* Styles */}
      <style>{`
        .pdf-modal-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(4px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          animation: fadeIn 0.2s ease;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .pdf-modal {
          background: var(--color-surface, #1a1a2e);
          border: 1px solid var(--color-border, rgba(255, 255, 255, 0.1));
          border-radius: 12px;
          width: 90%;
          max-width: 480px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
          animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .pdf-modal-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px 20px;
          border-bottom: 1px solid var(--color-border, rgba(255, 255, 255, 0.1));
        }

        .pdf-modal-title {
          display: flex;
          align-items: center;
          gap: 10px;
          font-weight: 600;
          color: var(--color-text, #fff);
        }

        .pdf-modal-close {
          background: transparent;
          border: none;
          color: var(--color-text-muted, rgba(255, 255, 255, 0.5));
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
          transition: all 0.2s;
        }

        .pdf-modal-close:hover {
          background: rgba(255, 255, 255, 0.1);
          color: var(--color-text, #fff);
        }

        .pdf-modal-content {
          padding: 24px 20px;
        }

        .pdf-modal-company {
          font-size: 1.1rem;
          font-weight: 600;
          color: var(--color-text, #fff);
          margin-bottom: 20px;
          text-align: center;
        }

        .pdf-progress-container {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
        }

        .pdf-progress-bar {
          flex: 1;
          height: 8px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 4px;
          overflow: hidden;
        }

        .pdf-progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--color-primary, #6366f1), var(--color-accent, #8b5cf6));
          border-radius: 4px;
          transition: width 0.5s ease;
        }

        .pdf-progress-text {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--color-text-muted, rgba(255, 255, 255, 0.7));
          min-width: 40px;
          text-align: right;
        }

        .pdf-status-display {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          margin-bottom: 24px;
        }

        .pdf-status-icon {
          color: var(--color-primary, #6366f1);
        }

        .pdf-status-icon.loading {
          animation: spin 1s linear infinite;
        }

        .pdf-status-icon.success {
          color: var(--color-success, #22c55e);
        }

        .pdf-status-icon.error {
          color: var(--color-danger, #ef4444);
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .pdf-status-text {
          font-size: 0.9rem;
          color: var(--color-text-muted, rgba(255, 255, 255, 0.7));
        }

        .pdf-status-text.error {
          color: var(--color-danger, #ef4444);
        }

        .pdf-stages {
          display: flex;
          justify-content: space-between;
          gap: 8px;
        }

        .pdf-stage {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
          opacity: 0.4;
          transition: all 0.3s ease;
        }

        .pdf-stage.active {
          opacity: 1;
        }

        .pdf-stage.complete {
          opacity: 0.8;
        }

        .pdf-stage-icon {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.05);
          color: var(--color-text-muted, rgba(255, 255, 255, 0.5));
          transition: all 0.3s ease;
        }

        .pdf-stage.active .pdf-stage-icon {
          background: var(--color-primary, #6366f1);
          color: white;
          box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
        }

        .pdf-stage.complete .pdf-stage-icon {
          background: var(--color-success, #22c55e);
          color: white;
        }

        .pdf-stage-label {
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: var(--color-text-muted, rgba(255, 255, 255, 0.5));
        }

        .pdf-stage.active .pdf-stage-label {
          color: var(--color-text, #fff);
        }

        .pdf-error-message {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 16px;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 8px;
          margin-top: 16px;
          color: var(--color-danger, #ef4444);
          font-size: 0.875rem;
        }

        .pdf-modal-footer {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          padding: 16px 20px;
          border-top: 1px solid var(--color-border, rgba(255, 255, 255, 0.1));
        }

        .pdf-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 20px;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          border: none;
        }

        .pdf-btn.primary {
          background: linear-gradient(135deg, var(--color-primary, #6366f1), var(--color-accent, #8b5cf6));
          color: white;
        }

        .pdf-btn.primary:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        }

        .pdf-btn.secondary {
          background: rgba(255, 255, 255, 0.1);
          color: var(--color-text-muted, rgba(255, 255, 255, 0.7));
        }

        .pdf-btn.secondary:hover {
          background: rgba(255, 255, 255, 0.15);
          color: var(--color-text, #fff);
        }
      `}</style>
    </div>
  );
}

export default PDFGenerationModal;


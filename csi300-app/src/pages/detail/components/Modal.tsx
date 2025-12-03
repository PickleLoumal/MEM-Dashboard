import React, { useEffect } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay active" onClick={onClose} style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(15, 23, 42, 0.4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        opacity: 1,
        visibility: 'visible',
        transition: 'opacity 0.18s ease, visibility 0.18s ease'
    }}>
      <div className="modal-content" onClick={e => e.stopPropagation()} style={{
          background: 'var(--app-surface)',
          borderRadius: 'var(--app-radius-lg)',
          padding: '24px',
          maxWidth: '720px',
          maxHeight: '80vh',
          overflowY: 'auto',
          margin: '20px',
          width: '90%',
          boxShadow: 'var(--app-shadow-soft)'
      }}>
        <div className="modal-header" style={{
            marginBottom: '20px',
            paddingBottom: '16px',
            borderBottom: '1px solid var(--app-border)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
        }}>
          <h2 className="modal-title" style={{
              fontSize: '20px',
              fontWeight: 600,
              color: 'var(--app-heading)',
              margin: 0
          }}>
            {title}
          </h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: 'var(--app-text-muted)' }}>&times;</button>
        </div>
        <div className="modal-body" style={{
            color: 'var(--app-text)',
            lineHeight: '1.6'
        }}>
          {children}
        </div>
      </div>
    </div>
  );
}


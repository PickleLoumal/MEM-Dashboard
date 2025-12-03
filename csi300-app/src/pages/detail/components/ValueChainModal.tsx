import React from 'react';
import { Modal } from './Modal';
import { CompanyDetail } from '../types';
import { getImSectorDisplay, formatNumber } from '../utils';

interface ValueChainModalProps {
  isOpen: boolean;
  onClose: () => void;
  company: CompanyDetail | null;
}

export function ValueChainModal({ isOpen, onClose, company }: ValueChainModalProps) {
  if (!company) return null;

  const imSector = getImSectorDisplay(company);
  const marketCap = company.market_cap_usd ? `$${formatNumber(company.market_cap_usd, 0)}M` : 'N/A';
  const peRatio = company.pe_ratio_trailing ? formatNumber(company.pe_ratio_trailing, 2) : 'N/A';
  const companyName = company.name || 'Unknown Company';

  const isMoutai = companyName.includes('Kweichow Moutai') || companyName.includes('茅台');

  const handleViewDetail = () => {
    let targetIndustry = 'energy';
    if (imSector) {
        const sectorLower = imSector.toLowerCase();
        if (sectorLower.includes('energy')) {
            targetIndustry = 'energy';
        } else if (sectorLower.includes('supporting') && sectorLower.includes('technolog')) {
            targetIndustry = 'supporting-technology';
        } else if (sectorLower.includes('technology') || sectorLower.includes('tech')) {
            targetIndustry = 'supporting-technology';
        }
    }
    window.location.href = `/legacy/value-chain/${targetIndustry}/detail.html?company=${encodeURIComponent(companyName)}&id=${company.id}`;
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Value Chain Analysis">
      <div className="modal-section" style={{ marginBottom: '16px' }}>
        <ModalRow label="Company" value={companyName} />
        <ModalRow label="Industry Matrix Sector" value={imSector} />
        <ModalRow label="Market Cap" value={marketCap} />
        <ModalRow label="P/E Ratio" value={peRatio} />
      </div>

      {isMoutai ? (
        <MoutaiContent />
      ) : (
        <GenericContent imSector={imSector} companyName={companyName} />
      )}

      <div style={{ marginTop: '24px', textAlign: 'center' }}>
        <button 
          className="button button-secondary" 
          onClick={handleViewDetail}
          style={{
            background: 'var(--app-surface-muted)',
            color: 'var(--app-heading)',
            border: '1px solid var(--app-border)',
            padding: '8px 16px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 600
          }}
        >
          View Detail
        </button>
      </div>
    </Modal>
  );
}

function ModalRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1.1fr) minmax(0, 1fr)',
        gap: '12px',
        marginBottom: '8px',
        fontSize: '14px',
        alignItems: 'baseline'
    }}>
      <span style={{ color: 'var(--app-text-muted)', fontWeight: 500 }}>{label}</span>
      <span style={{ color: 'var(--app-heading)', fontWeight: 600, textAlign: 'right' }}>{value}</span>
    </div>
  );
}

function ModalBreakdown({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="modal-breakdown" style={{
        margin: '16px 0',
        padding: '12px 0',
        borderTop: '1px solid #eaecf0',
        borderBottom: '1px solid #eaecf0'
    }}>
      <h4 style={{ color: '#1f2937', margin: '0 0 12px 0', fontSize: '16px' }}>{title}</h4>
      {children}
    </div>
  );
}

function ModalSubItem({ label, value }: { label: string; value: string }) {
  return (
    <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1.1fr) minmax(0, 1fr)',
        gap: '12px',
        alignItems: 'baseline',
        marginBottom: '8px'
    }}>
      <span style={{ color: 'var(--app-text-muted)', fontWeight: 500, fontSize: '13px' }}>{label}</span>
      <span style={{ color: 'var(--app-heading)', fontWeight: 600, fontSize: '13px', textAlign: 'right' }}>{value}</span>
    </div>
  );
}

function ModalDescription({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
        color: 'var(--app-text)',
        background: 'var(--app-surface-muted)',
        borderRadius: 'var(--app-radius-md)',
        padding: '12px',
        marginTop: '12px',
        fontSize: '14px'
    }}>
      {children}
    </div>
  );
}

function MoutaiContent() {
  return (
    <>
      <ModalBreakdown title="Primary Value Chain Activities">
        <ModalSubItem label="Inbound Logistics" value="Premium sorghum sourcing from local farms" />
        <ModalSubItem label="Operations" value="Traditional fermentation & distillation processes" />
        <ModalSubItem label="Outbound Logistics" value="Controlled distribution network nationwide" />
        <ModalSubItem label="Marketing & Sales" value="Premium brand positioning & cultural heritage" />
        <ModalSubItem label="Service" value="Customer education & brand experience" />
      </ModalBreakdown>

      <ModalBreakdown title="Support Activities">
        <ModalSubItem label="Technology Development" value="Traditional brewing technology & quality control" />
        <ModalSubItem label="Human Resources" value="Master distillers & skilled craftsmen" />
        <ModalSubItem label="Procurement" value="Long-term supplier relationships" />
        <ModalSubItem label="Infrastructure" value="Corporate governance & financial management" />
      </ModalBreakdown>

      <ModalDescription>
        <strong>Value Chain Summary:</strong> Kweichow Moutai's integrated value chain leverages traditional 
        craftsmanship, premium raw materials, and controlled distribution to maintain market leadership. 
        The company's value creation spans from specialized sorghum sourcing through heritage-based production 
        to premium brand positioning, delivering exceptional margins and customer loyalty.
      </ModalDescription>
    </>
  );
}

function GenericContent({ imSector, companyName }: { imSector: string; companyName: string }) {
  return (
    <>
      <ModalBreakdown title="Value Chain Stages">
        <ModalSubItem label="Upstream Activities" value="Raw material sourcing and supplier relationships" />
        <ModalSubItem label="Core Operations" value="Production processes and operational efficiency" />
        <ModalSubItem label="Midstream Processing" value="Value-added processing and quality control" />
        <ModalSubItem label="Downstream Distribution" value="Market channels and customer delivery" />
        <ModalSubItem label="End Customer Markets" value="Final consumption and customer satisfaction" />
      </ModalBreakdown>

      <ModalDescription>
        <strong>Value Chain Summary:</strong> Comprehensive analysis of {companyName}'s value creation process 
        from upstream activities to end customer delivery. This summary provides an overview of key operational 
        stages, competitive positioning, and strategic value drivers within the {imSector} sector.
      </ModalDescription>
    </>
  );
}


import React, { useEffect, useState } from 'react';
import { Modal } from './Modal';
import { CompanyDetail, PeerComparisonData } from '../types';
import { fetchPeersComparison } from '../api';
import { getImSectorDisplay } from '../utils';

interface PeersComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  company: CompanyDetail | null;
}

export function PeersComparisonModal({ isOpen, onClose, company }: PeersComparisonModalProps) {
  const [data, setData] = useState<PeerComparisonData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && company) {
      loadData();
    }
  }, [isOpen, company]);

  const loadData = async () => {
    if (!company) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchPeersComparison(String(company.id));
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load comparison data');
    } finally {
      setLoading(false);
    }
  };

  const getMarketPosition = (percentile: number) => {
    if (percentile >= 75) return 'Market Leader';
    if (percentile >= 50) return 'Mid-Tier';
    if (percentile >= 25) return 'Competitor';
    return 'Follower';
  };

  const getRankSuffix = (rank: number) => {
    if (rank % 100 >= 11 && rank % 100 <= 13) return 'th';
    switch (rank % 10) {
      case 1: return 'st';
      case 2: return 'nd';
      case 3: return 'rd';
      default: return 'th';
    }
  };

  if (!company) return null;

  const imSector = data ? (data.industry || data.im_sector || getImSectorDisplay(company)) : getImSectorDisplay(company);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Industry Matrix Sector Peers Comparison">
      <div className="modal-section">
        <div className="modal-row" style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.1fr) minmax(0, 1fr)', gap: '12px', marginBottom: '8px', fontSize: '14px', alignItems: 'baseline' }}>
          <span className="modal-label" style={{ color: 'var(--app-text-muted)', fontWeight: 500 }}>Company</span>
          <span className="modal-value" style={{ color: 'var(--app-heading)', fontWeight: 600, textAlign: 'right' }}>{company.name || 'Unknown Company'}</span>
        </div>
        <div className="modal-row" style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.1fr) minmax(0, 1fr)', gap: '12px', marginBottom: '8px', fontSize: '14px', alignItems: 'baseline' }}>
          <span className="modal-label" style={{ color: 'var(--app-text-muted)', fontWeight: 500 }}>Industry Matrix Sector</span>
          <span className="modal-value" style={{ color: 'var(--app-heading)', fontWeight: 600, textAlign: 'right' }}>{imSector}</span>
        </div>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <div style={{ display: 'inline-block', width: '20px', height: '20px', border: '2px solid #f3f3f3', borderTop: '2px solid #3498db', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
          <p style={{ marginTop: '10px', color: '#666' }}>Loading IM sector peers comparison...</p>
          <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
        </div>
      )}

      {error && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#dc3545' }}>
          <h3>Unable to Load Comparison Data</h3>
          <p style={{ margin: '15px 0', color: '#666' }}>{error}</p>
          <button onClick={loadData} style={{ padding: '10px 20px', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && data && (
        <>
          {/* Peer ranking visualization with percentile indicator */}
          {(() => {
            const currentRank = data.target_company.rank;
            const totalCompanies = data.total_companies_in_industry;
            const percentileBeat = Math.round(((totalCompanies - currentRank) / (totalCompanies - 1)) * 100);

            let rankColor = '#e74c3c';
            if (percentileBeat >= 75) rankColor = '#27ae60';
            else if (percentileBeat >= 50) rankColor = '#f39c12';
            else if (percentileBeat >= 25) rankColor = '#f1c40f';

            return (
              <div style={{ marginTop: '20px', padding: '15px 0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ background: rankColor, color: 'white', padding: '4px 10px', borderRadius: '4px', fontWeight: 600, fontSize: '13px' }}>
                      #{currentRank} / {totalCompanies}
                    </div>
                    <div>
                      <span style={{ fontWeight: 600, color: '#2c3e50', fontSize: '14px' }}>Industry Matrix Sector Ranking</span>
                      <span style={{ fontSize: '12px', color: '#6c757d', marginLeft: '8px' }}>{getMarketPosition(percentileBeat)} Position</span>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '11px', color: '#6c757d', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Percentile</span>
                    <div style={{ fontSize: '14px', fontWeight: 600, color: rankColor }}>
                      {percentileBeat === 100 ? 'Market Leader' : percentileBeat === 0 ? 'Last Position' : percentileBeat < 50 ? `Bottom ${percentileBeat}%` : `Top ${100 - percentileBeat}%`}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'end', height: '35px', width: '100%' }}>
                  {Array.from({length: totalCompanies}, (_, index) => {
                    const rank = totalCompanies - index;
                    const isCurrentCompany = rank === currentRank;
                    const distanceFromCurrent = Math.abs(rank - currentRank);

                    let barHeight = 8;
                    if (isCurrentCompany) barHeight = 35;
                    else if (distanceFromCurrent === 1) barHeight = 22;
                    else if (distanceFromCurrent === 2) barHeight = 14;

                    let barColor = '#e0e0e0';
                    if (isCurrentCompany) barColor = rankColor;
                    else if (distanceFromCurrent === 1) barColor = `${rankColor}80`;
                    else if (distanceFromCurrent === 2) barColor = `${rankColor}40`;

                    const barWidth = `calc((100% - ${(totalCompanies - 1) * 2}px) / ${totalCompanies})`;

                    return (
                      <div key={rank} style={{
                        width: barWidth,
                        height: `${barHeight}px`,
                        background: barColor,
                        borderRadius: isCurrentCompany ? '4px' : '2px',
                        marginRight: index < totalCompanies - 1 ? '2px' : '0',
                        transition: 'all 0.4s ease',
                        boxShadow: isCurrentCompany ? '0 2px 12px rgba(0,0,0,0.15)' : 'none'
                      }}></div>
                    );
                  })}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '11px', color: '#95a5a6', fontWeight: 500 }}>
                  <span>Followers</span>
                  <span>Mid-Tier</span>
                  <span>Market Leader</span>
                </div>
              </div>
            );
          })()}

          <div style={{ marginTop: '20px' }}>
             <div style={{ display: 'grid', gridTemplateColumns: '1fr 90px 80px 80px 90px', gap: '15px', padding: '10px 0', borderBottom: '1px solid rgba(0,0,0,0.08)', fontWeight: 600, color: '#495057', fontSize: '12px', alignItems: 'center' }}>
                <div>Company</div>
                <div style={{ textAlign: 'right' }}>Market Cap</div>
                <div style={{ textAlign: 'right' }}>P/E Ratio</div>
                <div style={{ textAlign: 'right' }}>ROE (%)</div>
                <div style={{ textAlign: 'right' }}>OM (% TTM)</div>
             </div>
             {data.comparison_data.map((item, index) => {
               const isCurrentCompany = item.is_current_company;
               const rank = item.rank;
               let rankBadge = null;

               if (isCurrentCompany) {
                   rankBadge = <span style={{ background: '#666', color: 'white', fontSize: '10px', fontWeight: 600, padding: '3px 8px', borderRadius: '3px', lineHeight: 1, marginRight: '8px' }}>{rank}{getRankSuffix(rank)}</span>;
               } else if (rank <= 3) {
                   const colors = ['#e74c3c', '#f39c12', '#27ae60'];
                   const rankings = ['1st', '2nd', '3rd'];
                   rankBadge = <span style={{ background: colors[rank-1], color: 'white', fontSize: '10px', fontWeight: 600, padding: '3px 8px', borderRadius: '3px', lineHeight: 1, marginRight: '8px' }}>{rankings[rank-1]}</span>;
               }

               return (
                 <div key={index} style={{ padding: '15px 0', borderBottom: '1px solid rgba(0,0,0,0.08)' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 90px 80px 80px 90px', gap: '15px', alignItems: 'center', marginBottom: '8px' }}>
                        <strong style={{ color: '#2c3e50', fontSize: '14px' }}>{item.name}</strong>
                        <span style={{ textAlign: 'right', fontWeight: 500, color: '#2c3e50', fontSize: '13px' }}>{item.market_cap_display || '-'}</span>
                        <span style={{ textAlign: 'right', fontWeight: 500, color: '#2c3e50', fontSize: '13px' }}>{item.pe_ratio_display || '-'}</span>
                        <span style={{ textAlign: 'right', fontWeight: 500, color: '#2c3e50', fontSize: '13px' }}>{item.roe_display || '-'}</span>
                        <span style={{ textAlign: 'right', fontWeight: 500, color: '#2c3e50', fontSize: '13px' }}>{item.operating_margin_display || '-'}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {rankBadge}
                        <span style={{ color: '#7f8c8d', fontWeight: 500, fontSize: '13px' }}>{item.ticker}</span>
                        {isCurrentCompany && <span style={{ color: '#2196f3', fontSize: '11px', fontWeight: 600, marginLeft: '10px', display: 'flex', alignItems: 'center' }}><span style={{ display: 'inline-block', width: '6px', height: '6px', background: '#2196f3', borderRadius: '50%', marginRight: '6px', boxShadow: '0 0 8px rgba(33, 150, 243, 0.4), 0 0 3px rgba(33, 150, 243, 0.6)' }}></span>Current Company</span>}
                    </div>
                 </div>
               );
             })}
          </div>
        </>
      )}
    </Modal>
  );
}


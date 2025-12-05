import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../../csi300-app/src/pages/investment-summary-detail/App';
import * as api from '../../csi300-app/src/pages/investment-summary-detail/api';

// Mock API
vi.mock('../../csi300-app/src/pages/investment-summary-detail/api', () => ({
  fetchInvestmentSummary: vi.fn(),
  generateInvestmentSummary: vi.fn(),
}));

// Mock URLSearchParams
const mockParams = new URLSearchParams();
Object.defineProperty(window, 'location', {
  value: {
    search: mockParams.toString(),
    href: '',
  },
  writable: true,
});

describe('Investment Summary Detail App', () => {
  const mockSummaryData = {
    company_name: 'Test Company',
    report_date: '2024-01-01',
    stock_price_previous_close: 100,
    market_cap_display: '100B',
    recommended_action: 'Buy',
    industry: 'Tech',
    business_overview: 'Overview content',
    business_performance: 'Performance content',
    industry_context: 'Industry context',
    financial_stability: 'Stability content',
    key_financials_valuation: 'Financials content',
    big_trends_events: 'Trends content',
    customer_segments: 'Segments content',
    competitive_landscape: 'Landscape content',
    risks_anomalies: 'Risks content',
    forecast_outlook: 'Outlook content',
    investment_firms_views: 'Views content',
    recommended_action_detail: 'Action detail',
    industry_ratio_analysis: 'Ratio analysis',
    key_takeaways: 'Takeaways content',
    sources: 'Sources content'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Set URL params
    window.location.search = '?id=1';
  });

  it('renders loading state initially', () => {
    (api.fetchInvestmentSummary as any).mockReturnValue(new Promise(() => {})); // Pending promise
    render(<App />);
    // 根据 App.tsx 实现，loading 时显示 spinner
    // 这里假设 spinner 有 loading class 或可以被查询到
    // 由于 App.tsx 用了 <div className="loading-spinner">，我们可以通过 container 查询
    const { container } = render(<App />);
    expect(container.querySelector('.loading-spinner')).toBeInTheDocument();
  });

  it('renders summary data after load', async () => {
    (api.fetchInvestmentSummary as any).mockResolvedValue(mockSummaryData);
    
    render(<App />);
    
    await waitFor(() => {
      // 页面上可能有多个地方显示公司名称（导航栏、标题等）
      const companyElements = screen.getAllByText('Test Company');
      expect(companyElements.length).toBeGreaterThan(0);
      
      // 检查主标题 (H1)
      expect(screen.getByRole('heading', { name: 'Investment Summary', level: 1 })).toBeInTheDocument();
      
      // 检查具体内容
      expect(screen.getByText('Overview content')).toBeInTheDocument();
    });
  });

  it('handles regeneration click', async () => {
    (api.fetchInvestmentSummary as any).mockResolvedValue(mockSummaryData);
    (api.generateInvestmentSummary as any).mockResolvedValue({
      status: 'success',
      message: 'Updated',
      data: { company_id: 1 }
    });

    render(<App />);
    
    // 等待加载完成
    await waitFor(() => screen.getByText('Regenerate'));
    
    const btn = screen.getByText('Regenerate');
    fireEvent.click(btn);
    
    // 验证 loading 状态
    expect(btn).toBeDisabled();
    expect(screen.getByText(/Regenerating/i)).toBeInTheDocument();
    
    // 验证 API 调用
    await waitFor(() => {
      expect(api.generateInvestmentSummary).toHaveBeenCalledWith('1');
      // 重新获取数据
      expect(api.fetchInvestmentSummary).toHaveBeenCalledTimes(2); 
    });
  });

  it('handles regeneration error', async () => {
    (api.fetchInvestmentSummary as any).mockResolvedValue(mockSummaryData);
    (api.generateInvestmentSummary as any).mockResolvedValue({
      status: 'error',
      message: 'Generation Failed'
    });

    render(<App />);
    
    await waitFor(() => screen.getByText('Regenerate'));
    
    fireEvent.click(screen.getByText('Regenerate'));
    
    await waitFor(() => {
      expect(screen.getByText(/Generation Failed/i)).toBeInTheDocument();
    });
  });
});

import React from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { SectionHeader } from './ui';
import {
  TrendingUp,
  Building2,
  DollarSign,
  Zap,
  Users,
  Swords,
  AlertTriangle,
  LineChart,
  Building,
  Scale,
  Ship,
  Lightbulb
} from 'lucide-react';

interface SummarySectionProps {
  title: string;
  content: string | undefined;
  id?: string;
}

// Map section IDs to icons
const sectionIcons: Record<string, React.ElementType> = {
  businessPerformance: TrendingUp,
  industryContext: Building2,
  financialStability: DollarSign,
  keyFinancialsValuation: Scale,
  bigTrendsEvents: Zap,
  customerSegments: Users,
  competitiveLandscape: Swords,
  risksAnomalies: AlertTriangle,
  forecastOutlook: LineChart,
  investmentFirmsViews: Building,
  industryRatioAnalysis: Scale,
  tariffsSupplyChainRisks: Ship,
  keyTakeaways: Lightbulb,
  recommendedActionDetail: TrendingUp,
};

/**
 * 清理 markdown 内容：
 * 1. 移除 JSON 代码块（如 ```business_overview_data ... ```）
 * 2. 移除裸露的 JSON 对象（{ ... } 多行块）
 * 3. 移除与卡片标题重复的 markdown 标题
 * 4. 移除开头的标题行
 */
function cleanMarkdownContent(content: string, sectionTitle: string): string {
  if (!content) return content;

  let cleaned = content;

  // 1. 移除所有代码块（```...```），包括 business_overview_data 等
  cleaned = cleaned.replace(/```[\s\S]*?```/g, '');

  // 2. 移除裸露的 JSON 对象
  cleaned = removeJsonBlocks(cleaned);

  // 3. 移除开头的 markdown 标题（# 开头的行）
  cleaned = cleaned.replace(/^#+\s+[^\n]+\n?/m, '');

  // 4. 移除与 section title 重复的单独一行
  const escapedTitle = sectionTitle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const titlePattern = new RegExp(`^${escapedTitle}[:\\s]*\n`, 'im');
  cleaned = cleaned.replace(titlePattern, '');

  // 5. 清理多余的空行（超过2个连续空行变成1个）
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n');

  // 6. 移除开头的空行
  cleaned = cleaned.replace(/^\s*\n+/, '');

  return cleaned;
}

/**
 * 移除文本中的 JSON 块（支持嵌套的 { } 结构）
 */
function removeJsonBlocks(text: string): string {
  let result = '';
  let i = 0;

  while (i < text.length) {
    // 检测是否是 JSON 块的开始: { 后面跟着换行和 "
    if (text[i] === '{') {
      // 检查是否看起来像 JSON（后面有 "key": 结构）
      const lookAhead = text.slice(i, i + 50);
      if (/^\{\s*\n?\s*"[^"]+"\s*:/.test(lookAhead)) {
        // 找到匹配的闭合 }
        let braceCount = 1;
        let j = i + 1;
        while (j < text.length && braceCount > 0) {
          if (text[j] === '{') braceCount++;
          if (text[j] === '}') braceCount--;
          j++;
        }
        // 跳过整个 JSON 块
        i = j;
        continue;
      }
    }
    result += text[i];
    i++;
  }

  return result;
}

export const SummarySection: React.FC<SummarySectionProps> = ({ title, content, id }) => {
  if (!content) return null;

  // 清理内容
  const cleanedContent = cleanMarkdownContent(content, title);

  // Get icon for this section
  const Icon = id ? sectionIcons[id] : undefined;

  return (
    <section className="doc-section" id={id}>
      <SectionHeader title={title} icon={Icon} />
      <div className="doc-section-content doc-prose">
        <Markdown remarkPlugins={[remarkGfm]}>{cleanedContent}</Markdown>
      </div>
    </section>
  );
};

# Value Chain Analysis Framework

## 概述

价值链分析框架为不同行业提供专业的价值链分析工具和可视化界面。每个行业都有其独特的价值创造过程，我们的分析框架针对各行业特点提供定制化的分析模板。

## 文件结构

```
value-chain/
├── index.html              # 主页面 - 行业选择界面
├── README.md              # 本文档
├── assets/                # 共享资源
│   └── value-chain.css    # 统一样式文件
└── energy/                # 能源行业
    └── detail.html        # 能源行业价值链详细分析
```

## 当前可用行业

### ✅ 能源行业 (Energy)
- **状态**: 已完成
- **文件**: `energy/detail.html`
- **覆盖范围**: 
  - 上游：勘探与生产
  - 中游：加工与运输
  - 下游：炼制与分销
  - 终端客户与市场

### 🚧 计划中的行业

1. **科技行业 (Technology)**
   - 软件、硬件、半导体
   - R&D → 设计 → 制造 → 分销

2. **金融服务 (Financial Services)**
   - 银行、保险、投资
   - 客户获取 → 产品开发 → 风险管理 → 服务交付

3. **医疗健康 (Healthcare)**
   - 制药、医疗设备
   - 研发 → 临床试验 → 制造 → 分销

4. **消费品 (Consumer Goods)**
   - 快消品、零售、电商
   - 产品开发 → 制造 → 营销 → 零售

5. **材料制造 (Materials)**
   - 化工、金属、建筑材料
   - 原材料采购 → 加工 → 制造 → 分销

## 使用方法

### 1. 访问主页面
```
http://localhost:8082/value-chain/
```

### 2. 选择行业
点击相应的行业卡片进入详细分析页面

### 3. 查看详细分析
每个行业的详细页面包含：
- 行业概述
- 价值链各阶段详细分析
- 关键成功因素
- 风险评估
- 市场趋势

## 技术实现

### 前端技术栈
- **HTML5**: 语义化结构
- **Tailwind CSS**: 响应式设计框架
- **MEM Dashboard CSS**: 统一的设计系统
- **Vanilla JavaScript**: 交互逻辑
- **SVG Icons**: 矢量图标

### 设计原则
- **响应式设计**: 适配桌面、平板、手机
- **一致性**: 与 MEM Dashboard 保持完全一致的设计语言
- **可扩展性**: 易于添加新行业
- **用户体验**: 直观的导航和交互
- **样式统一**: 使用共享的 value-chain.css 样式文件

## 开发指南

### 添加新行业

1. **创建行业文件夹**
   ```bash
   mkdir value-chain/[industry-name]
   ```

2. **复制模板文件**
   ```bash
   cp value-chain/energy/detail.html value-chain/[industry-name]/detail.html
   ```

3. **更新主页面**
   在 `index.html` 中添加新的行业卡片

4. **自定义内容**
   - 更新行业特定的价值链阶段
   - 修改颜色主题
   - 添加行业特定的分析内容

### 样式定制

#### 使用统一样式系统

所有页面都应该引入统一的样式文件：

```html
<!-- 基础样式 -->
<link rel="stylesheet" href="../../src/assets/css/base/main.css">
<!-- Value Chain 专用样式 -->
<link rel="stylesheet" href="assets/value-chain.css">
```

#### 行业特定颜色主题

每个行业可以有自己的颜色主题：

```css
.value-chain-industry-[name] .value-chain-industry-header {
    background: linear-gradient(135deg, #color1 0%, #color2 100%);
    color: white;
}
```

#### 可用的样式类

- `.value-chain-header`: 页面头部
- `.value-chain-container`: 内容容器
- `.value-chain-industry-card`: 行业卡片
- `.value-chain-stage-card`: 价值链阶段卡片
- `.value-chain-sub-item`: 子项目
- `.value-chain-badge`: 状态徽章

### 导航更新

确保所有页面的导航链接正确：
- 返回主页面: `../index.html`
- 返回 CSI300: `../../`

## 集成说明

### 与 CSI300 主应用集成

价值链分析通过以下方式与主应用集成：

1. **公司详情页调用**
   ```javascript
   window.app.openValueChainDetail(industry)
   ```

2. **路径映射**
   ```javascript
   // 在 detail.html 中
   window.open(`/value-chain/${targetIndustry}/detail.html`, '_blank');
   ```

3. **API 集成**
   - 使用相同的 Django 后端
   - 共享公司数据和行业分类

### 数据流

```
CSI300 公司详情 → 行业识别 → 价值链分析页面 → 行业特定分析
```

## 维护指南

### 定期更新任务

1. **内容更新**
   - 行业趋势分析
   - 市场数据更新
   - 新兴技术影响

2. **功能增强**
   - 新行业添加
   - 交互功能改进
   - 性能优化

3. **设计优化**
   - 用户体验改进
   - 响应式设计调整
   - 视觉效果更新

### 质量检查

- [ ] 所有链接正常工作
- [ ] 响应式设计在各设备正常显示
- [ ] 内容准确性和时效性
- [ ] 性能和加载速度
- [ ] 浏览器兼容性

## 未来规划

### 短期目标 (1-3个月)
- 完成科技行业价值链分析
- 添加金融服务行业
- 改进交互体验

### 中期目标 (3-6个月)
- 完成所有主要行业覆盖
- 添加数据可视化功能
- 集成实时数据更新

### 长期目标 (6-12个月)
- AI 驱动的个性化分析
- 行业对比功能
- 导出和分享功能
- 多语言支持

## 支持与反馈

如有问题或建议，请通过以下方式联系：

- 项目文档: 查看主项目 README
- 技术支持: 参考 STARTUP_GUIDE.md
- 功能请求: 创建 GitHub Issue

# 自动化工具集

本文件夹包含用于金融数据分析和报告生成的自动化工具集。这些工具主要用于每日简报生成、市场数据爬取和取证会计分析。

> **重要提示**: 这些自动化功能将在未来集成到 `csi300-app` 前端应用中，提供统一的用户界面和更好的用户体验。

---

## 📋 功能概览

### 1. Daily Briefing AI Automation (`Daily_Briefing_AI_Automation.py`)

**功能**: 使用 Perplexity AI 生成专业的每日投资简报报告

**主要特性**:
- 从 Google Sheets 读取最新市场数据和新闻
- 调用 Perplexity Sonar Deep Research API 进行深度分析
- 生成详细的 Markdown 格式报告
- 自动转换为格式化的 Word 文档（长版本和快速版本）
- 自动上传到 Google Drive 指定文件夹
- 支持 Markdown 格式转换（标题、列表、表格、代码块等）

**输出文件**:
- `Daily Briefing {日期}_Long Version.docx` - 完整详细版本
- `Daily Briefing {日期}_Quick Version.docx` - 5页快速摘要版本

**配置要求**:
- Perplexity API Key
- Google Sheets 服务账号凭据 (`boxwood-sandbox-483506-u5-d246bd69f7d7.json`)
- Google Drive OAuth 凭据 (`oauth_credentials.json`)

---

### 2. Daily Briefing Data Scraper (`daily_briefing_automation_new.py`)

**功能**: 自动爬取 Briefing.com 网站的市场数据并更新到 Google Sheets

**主要特性**:
- 使用 Selenium 自动化浏览器爬取以下页面:
  - **Page One** → 写入 Google Sheets 单元格 H2
  - **Stock Market Update** → 写入 Google Sheets 单元格 I2
  - **Bond Market Update** → 写入 Google Sheets 单元格 J2
- 支持无头模式运行（headless）
- 自动等待页面加载完成
- 提取关键市场数据（Market Snapshot、Industry Watch、Moving the Market 等）

**配置要求**:
- Google Sheets 服务账号凭据
- Chrome 浏览器和 ChromeDriver
- Briefing.com 账户访问权限

---

### 3. Forensic Accounting Automation (`Forensic_Accounting_Automation.py`)

**功能**: 批量生成上市公司的取证会计分析报告

**主要特性**:
- 从 Excel 文件读取公司列表（格式: `List - {月日}.xlsx`）
- 自动从 Yahoo Finance 获取股价和市值数据
- 使用 Perplexity AI 进行深度取证会计分析
- 检测多种会计欺诈手法:
  - 收入确认技巧（渠道填充、虚假销售等）
  - 费用操纵（资本化费用、Cookie Jar 储备等）
  - 收益管理（大洗澡会计、收益平滑等）
  - 资产负债表操纵（表外融资、资产估值不当等）
  - 现金流操纵
  - 税务和监管规避
- 生成带红绿灯标识（🟢🟡🔴）的风险评估报告
- 自动生成执行报告，包含成功/失败统计

**输入文件格式**:
- Excel 文件: `List - {月日}.xlsx`
  - A列: 公司名称
  - B列: 股票代码
  - F列: 输出文件名

**输出文件**:
- `FA - {文件名}.docx` - 取证会计分析报告
- `FA Execution Report - {日期} - {时间}.docx` - 批量执行报告

**配置要求**:
- Perplexity API Key
- Yahoo Finance 数据访问（免费，无需 API Key）

---

## 🚀 安装和配置

### 1. 安装依赖

```bash
cd automation
pip install -r requirements.txt
```

### 2. 配置 Google Sheets 服务账号

1. 在 Google Cloud Console 创建服务账号
2. 下载 JSON 凭据文件，保存为 `boxwood-sandbox-483506-u5-d246bd69f7d7.json`
3. 确保服务账号有 Google Sheets 和 Google Drive 的访问权限

### 3. 配置 Google Drive OAuth（仅 Daily Briefing AI Automation 需要）

1. 在 Google Cloud Console 创建 OAuth 2.0 凭据
2. 下载客户端凭据，保存为 `oauth_credentials.json`
3. 首次运行时会打开浏览器进行授权，之后会自动保存 token

### 4. 配置 Perplexity API Key

在相应的 Python 脚本中设置 `PERPLEXITY_API_KEY` 变量：

```python
PERPLEXITY_API_KEY = "your-api-key-here"
```

### 5. 配置 Google Sheets ID 和 Drive 文件夹 ID

在脚本中修改以下变量：

```python
SPREADSHEET_ID = "your-spreadsheet-id"
GOOGLE_DRIVE_FOLDER_ID = "your-folder-id"  # 可选
```

---

## 📖 使用方法

### Daily Briefing AI Automation

```bash
python Daily_Briefing_AI_Automation.py
```

**流程**:
1. 读取 Google Sheets 数据
2. 调用 Perplexity API 生成详细报告
3. 转换为 Word 文档（长版本）
4. 生成快速版本（5页摘要）
5. 上传到 Google Drive（如果配置了文件夹 ID）

**输出位置**: `automation/output/{日期}/`

---

### Daily Briefing Data Scraper

```bash
python daily_briefing_automation_new.py
```

**流程**:
1. 认证 Google Sheets
2. 爬取 Page One 并写入 H2
3. 爬取 Stock Market Update 并写入 I2
4. 爬取 Bond Market Update 并写入 J2

**注意事项**:
- 需要稳定的网络连接
- 首次运行可能需要较长时间等待页面加载
- 建议在非交易时间运行以避免数据更新冲突

---

### Forensic Accounting Automation

```bash
python Forensic_Accounting_Automation.py
```

**前置条件**:
1. 准备 Excel 文件，命名格式: `List - {月日}.xlsx`（例如: `List - 0113.xlsx`）
2. 确保 Excel 文件包含以下列:
   - A列: 公司名称
   - B列: 股票代码（Yahoo Finance 格式，如 `0700.HK`, `AAPL`）
   - F列: 输出文件名

**流程**:
1. 读取 Excel 文件获取公司列表
2. 对每家公司在 Yahoo Finance 获取股价和市值
3. 调用 Perplexity API 生成取证会计分析报告
4. 保存 Word 文档到输出目录
5. 生成执行报告

**输出位置**: `automation/output/{日期}/`

**重试机制**:
- 每个公司最多重试 3 次
- 失败的公司会生成错误记录文件

---

## 📁 文件结构

```
automation/
├── README.md                                    # 本文件
├── requirements.txt                             # Python 依赖包
├── Daily_Briefing_AI_Automation.py            # 每日简报 AI 生成工具
├── daily_briefing_automation_new.py           # Briefing.com 数据爬取工具
├── Forensic_Accounting_Automation.py         # 取证会计分析工具
├── boxwood-sandbox-483506-u5-d246bd69f7d7.json # Google 服务账号凭据
├── oauth_credentials.json                      # Google OAuth 凭据
├── oauth_token.pickle                          # OAuth token 缓存（自动生成）
└── output/                                     # 输出目录（自动创建）
    └── {日期}/
        ├── Daily Briefing {日期}_Long Version.docx
        ├── Daily Briefing {日期}_Quick Version.docx
        ├── FA - {公司名}.docx
        └── FA Execution Report - {日期}.docx
```

---

## ⚙️ 技术栈

- **Python 3.x**
- **Selenium** - 网页自动化爬取
- **Perplexity AI API** - 深度研究和分析
- **Google Sheets API** - 数据读写
- **Google Drive API** - 文件上传
- **python-docx** - Word 文档生成
- **yfinance** - 股价数据获取
- **pandas** - Excel 文件处理

---

## 🔒 安全注意事项

1. **API 密钥**: 不要将 API 密钥提交到版本控制系统
2. **凭据文件**: `.json` 和 `.pickle` 文件应添加到 `.gitignore`
3. **OAuth Token**: `oauth_token.pickle` 包含用户授权信息，请妥善保管
4. **服务账号**: 限制服务账号的权限范围，仅授予必要的访问权限

---

## 🐛 故障排除

### ChromeDriver 版本不匹配

```bash
# 检查 Chrome 版本
google-chrome --version

# 下载对应版本的 ChromeDriver
# https://chromedriver.chromium.org/downloads
```

### Google Sheets 认证失败

- 检查服务账号 JSON 文件路径是否正确
- 确认服务账号有 Google Sheets 和 Drive 的访问权限
- 检查网络连接和防火墙设置

### Perplexity API 调用失败

- 检查 API Key 是否有效
- 确认账户有足够的 API 调用额度
- 检查网络连接和超时设置

### Yahoo Finance 数据获取失败

- 检查股票代码格式是否正确（如 `0700.HK` 而不是 `700.HK`）
- 确认网络连接正常
- 某些股票可能暂时无法获取数据

---

## 📝 未来集成计划

> **重要**: 这些自动化功能计划在未来集成到 `csi300-app` 前端应用中。

### 集成目标

1. **统一用户界面**: 通过 Web 界面操作，无需命令行
2. **实时状态监控**: 显示任务执行进度和状态
3. **结果预览**: 在浏览器中直接预览生成的报告
4. **定时任务**: 支持设置定时自动执行
5. **历史记录**: 查看和管理历史生成的报告
6. **权限管理**: 基于用户角色的访问控制

### 技术实现方向

- 后端 API: 将 Python 脚本封装为 Django REST API 端点
- 前端组件: React 组件用于任务配置和执行
- 任务队列: 使用 Celery 处理长时间运行的任务
- 文件存储: 集成 AWS S3 或 Google Cloud Storage
- 通知系统: 任务完成时发送邮件或系统通知

---

## 📞 支持

如有问题或建议，请联系开发团队或提交 Issue。

---

## 📄 许可证

本项目遵循 ALFIE 项目的许可证协议。

# YFinance Real-time Data Testing Suite

## 📁 文件夹概述

`yrealtime` 文件夹包含了所有与 yfinance 实时股票数据集成相关的测试文件、脚本和文档。

## 📋 文件清单

### 🔧 核心测试脚本
- **`test_yfinance_realtime.py`** - 主要的 yfinance 实时数据测试脚本
- **`test_tcl_realtime_update.py`** - TCL Technology (000100.SZ) 实时更新测试
- **`test_tcl_yfinance_only.py`** - 仅测试 yfinance 数据获取功能
- **`test_yfinance_direct.py`** - 直接测试 yfinance 库功能
- **`test_csi300_realtime_integration.py`** - CSI300 实时数据集成测试

### 🐛 调试和检查工具
- **`debug_yfinance_issues.py`** - yfinance 问题诊断和调试工具
- **`check_csi300_data.py`** - 检查 CSI300 数据库数据状态
- **`verify_admin_fix.py`** - 验证 admin 界面修复
- **`simple_csi300_test.py`** - 简化的 CSI300 测试

### 🎯 演示和指南
- **`demo_csi300_realtime.py`** - CSI300 实时数据集成演示
- **`csi300_admin_guide.py`** - CSI300 admin 界面使用指南

### 📚 文档
- **`YFINANCE_REALTIME_README.md`** - yfinance 实时数据集成详细文档
- **`CSI300_YFINANCE_INTEGRATION_SUMMARY.md`** - CSI300 与 yfinance 集成总结

### 🧪 其他测试文件
- **`test_stocks_django.py`** - Django 股票应用测试
- **`test_complete_ai_system.py`** - 完整 AI 系统测试
- **`test_docx_processing.py`** - DOCX 处理测试
- **`realtime_stock_data.json`** - 实时股票数据示例

## 🚀 使用方法

### 基本测试
```bash
cd /Volumes/Pickle\ Samsung\ SSD/MEM\ Dashboard\ 2/yrealtime
python3 test_yfinance_direct.py  # 测试 yfinance 基本功能
```

### TCL Technology 专用测试
```bash
python3 test_tcl_yfinance_only.py    # 测试 TCL Technology 数据获取
python3 test_tcl_realtime_update.py  # 测试 TCL Technology 数据库更新
```

### CSI300 集成测试
```bash
python3 test_csi300_realtime_integration.py  # 测试 CSI300 实时数据集成
python3 check_csi300_data.py                 # 检查 CSI300 数据状态
python3 verify_admin_fix.py                  # 验证 admin 界面修复
```

### 调试工具
```bash
python3 debug_yfinance_issues.py  # 诊断 yfinance 问题
```

### 演示和指南
```bash
python3 demo_csi300_realtime.py   # 查看功能演示
python3 csi300_admin_guide.py     # 查看 admin 使用指南
```

## 🔍 文件用途说明

### 测试脚本
- **test_yfinance_realtime.py** - 综合测试 yfinance 实时数据获取和数据库集成
- **test_tcl_realtime_update.py** - 专门测试 TCL Technology 的完整工作流程
- **test_tcl_yfinance_only.py** - 专注测试 yfinance 数据获取，不涉及数据库
- **test_yfinance_direct.py** - 直接测试 yfinance 库的基本功能

### 调试工具
- **debug_yfinance_issues.py** - 帮助诊断网络、安装和数据获取问题

### 演示脚本
- **demo_csi300_realtime.py** - 展示整个系统的功能和特点

### 文档
- **YFINANCE_REALTIME_README.md** - 完整的技术文档和使用指南
- **CSI300_YFINANCE_INTEGRATION_SUMMARY.md** - 项目总结和下一步计划

## 📊 测试覆盖范围

✅ **数据获取测试**
- yfinance 库安装和基本功能
- 股票信息获取（价格、市值、市盈率等）
- 历史数据获取（52周高低价等）
- 多股票批量处理

✅ **数据库集成测试**
- CSI300 股票代码读取
- 实时数据更新到数据库
- 字段映射验证

✅ **错误处理测试**
- 网络连接问题处理
- 数据获取失败处理
- 备用数据系统

✅ **性能测试**
- 数据缓存机制
- 大批量数据处理
- 并发请求处理

## 🛠️ 环境要求

- Python 3.8+
- Django 4.2+
- yfinance 库（推荐但可选）
- 网络连接（用于真实数据获取）

## 📈 开发状态

- ✅ **核心功能完成** - yfinance 集成和数据库更新
- ✅ **测试覆盖完整** - 各种场景和边缘情况
- ✅ **文档齐全** - 使用指南和技术文档
- 🔄 **持续优化中** - 性能和可靠性改进

## 🎯 下一步计划

1. **真实数据验证** - 在有网络的环境中验证真实数据获取
2. **性能优化** - 添加缓存和批量处理优化
3. **监控集成** - 添加数据质量监控和告警
4. **前端集成** - 将实时数据集成到前端界面

---

*最后更新: 2025年10月17日*

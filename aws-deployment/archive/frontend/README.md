# MEM Dashboard 前端部署指南

## AWS S3 + CloudFront 架构

本文档介绍如何使用 AWS S3 + CloudFront 部署 MEM Dashboard 前端应用。

## 架构概述

```
用户请求
    ↓
CloudFront CDN (全球边缘节点)
    ↓
S3 静态网站托管
    ↓
API 请求 → Application Load Balancer → ECS Fargate (Django API)
```

### 核心优势

1. **全球加速**: CloudFront CDN 提供低延迟访问
2. **高可用性**: 99.99% 可用性保证
3. **成本效益**: 比 EC2/ECS 托管前端更经济
4. **自动扩展**: 无服务器架构，自动应对流量峰值
5. **HTTPS 安全**: 自动 SSL/TLS 证书

## 部署架构

### 前端层 (S3 + CloudFront)
- **S3 Bucket**: 静态文件存储和网站托管
- **CloudFront**: 全球 CDN 分发网络
- **域名**: 可配置自定义域名 (可选)

### 后端层 (已部署)
- **ECS Fargate**: Django API 服务
- **ALB**: 负载均衡器
- **RDS PostgreSQL**: 数据库

## 快速部署

### 前提条件

1. AWS CLI 已安装并配置
2. 后端 ECS 服务正常运行
3. 具备必要的 AWS 权限

### 一键部署

```bash
# 进入前端部署目录
cd aws-deployment/frontend

# 执行部署脚本
./deploy-frontend.sh
```

部署过程将自动完成：
1. 准备静态文件
2. 创建 S3 bucket
3. 上传文件到 S3
4. 创建 CloudFront 分发
5. 配置缓存策略

### 部署输出

```
🎉 Frontend Deployment Complete!
================================

📍 Deployment URLs:
   S3 Website: http://mem-dashboard-frontend-production.s3-website.ap-east-1.amazonaws.com
   CloudFront: https://d1234567890abc.cloudfront.net

📊 Resource Information:
   S3 Bucket: mem-dashboard-frontend-production
   CloudFront Distribution: E1234567890ABC
   Region: ap-east-1
```

## 日常运维

### 快速更新

更新前端文件而无需完整重新部署：

```bash
# 更新所有文件
./update-frontend.sh

# 只更新配置文件
./update-frontend.sh --config

# 只更新 JavaScript 文件
./update-frontend.sh --js

# 更新但跳过缓存清理
./update-frontend.sh --config --no-cache
```

### 版本回滚

```bash
# 查看可用版本
./rollback-frontend.sh --list-versions

# 回滚到上一版本
./rollback-frontend.sh --previous

# 回滚到指定版本
./rollback-frontend.sh --version 2025-08-29-143000
```

## 配置详解

### S3 配置

**Bucket 政策**: 允许公开读取访问
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::bucket-name/*"
        }
    ]
}
```

**网站配置**: 单页应用路由支持
- 索引文档: `index.html`
- 错误文档: `index.html` (SPA 路由)

### CloudFront 配置

**缓存策略**:
- HTML 文件: 24小时 (86400秒)
- JS/CSS 文件: 1年 (31536000秒)
- API 请求: 不缓存

**错误页面**:
- 404/403 → index.html (支持 SPA 路由)

**压缩**: 启用 Gzip 压缩

## 生产环境配置

### API 配置自动更新

部署脚本会自动更新 `config/api_config.js`，将 API 端点从本地开发环境切换到生产环境：

```javascript
// 自动配置为生产环境 ALB 地址
const API_CONFIGS = {
    DJANGO: {
        name: 'Django REST API',
        baseUrl: 'https://your-alb-dns.ap-east-1.elb.amazonaws.com/api',
        status: 'production'
    }
};
```

### HTTPS 和安全性

- CloudFront 自动提供 HTTPS
- 强制 HTTP 重定向到 HTTPS
- 支持 HTTP/2 协议
- 安全头配置

## 成本估算

| 服务 | 配置 | 月度成本 |
|------|------|----------|
| S3 存储 | 1GB 静态文件 | $0.02 |
| S3 请求 | 10万次请求 | $0.04 |
| CloudFront | 100GB 传输 | $8.50 |
| CloudFront 请求 | 100万次请求 | $0.75 |
| **总计** | | **~$9.31/月** |

### 成本优化

1. **合理缓存**: 设置适当的 TTL 减少回源
2. **文件压缩**: 启用 Gzip 减少传输量
3. **区域选择**: 根据用户分布选择价格区域

## 监控和告警

### CloudWatch 指标

- **请求数量**: 监控访问流量
- **错误率**: 4xx/5xx 错误统计
- **缓存命中率**: CloudFront 缓存效率
- **传输量**: 带宽使用统计

### 建议告警

```bash
# 高错误率告警
aws cloudwatch put-metric-alarm \
  --alarm-name "Frontend-High-Error-Rate" \
  --alarm-description "Frontend error rate > 5%" \
  --metric-name "4xxErrorRate" \
  --namespace "AWS/CloudFront" \
  --statistic "Average" \
  --period 300 \
  --threshold 5.0 \
  --comparison-operator "GreaterThanThreshold"
```

## 自定义域名配置 (可选)

### 1. 获取 SSL 证书

```bash
# 必须在 us-east-1 区域申请证书 - CloudFront 全球服务要求
# 注意: 即使您的其他AWS资源在 ap-east-1，CloudFront 证书必须在 us-east-1
aws acm request-certificate \
  --domain-name "dashboard.yourdomain.com" \
  --validation-method "DNS" \
  --region us-east-1
```

## 为什么CloudFront证书必须在us-east-1？

### 技术原因：

1. **CloudFront是全球服务**
   - CloudFront不属于任何特定区域，它是AWS的全球CDN服务
   - 所有CloudFront配置都存储在us-east-1（北弗吉尼亚）

2. **证书分发机制**
   - ACM证书需要分发到全球所有CloudFront边缘节点
   - AWS设计时选择us-east-1作为证书的"主控区域"
   - 只有us-east-1的证书才能被CloudFront识别和使用

3. **架构一致性**
   - 这确保了全球所有CloudFront分发使用相同的证书管理机制
   - 避免了跨区域证书同步的复杂性

### 您的部署架构：

```
证书管理: us-east-1 (ACM) → CloudFront 全球分发 → 用户
后端服务: ap-east-1 (ECS/RDS/ALB) ← CloudFront回源 ← API请求
```

### 实际操作：

1. **证书申请**: 必须在us-east-1
2. **DNS验证**: 在您的域名DNS提供商完成
3. **CloudFront配置**: 引用us-east-1的证书ARN
4. **用户访问**: 全球用户都能使用HTTPS访问

这不会影响您的：
- 后端ECS服务（继续在ap-east-1）
- 数据库RDS（继续在ap-east-1）
- S3存储（继续在ap-east-1）
- API响应速度

只是SSL证书这一个组件需要在us-east-1管理，这是CloudFront的标准要求。

### 2. 配置 DNS

在您的域名解析商添加 CNAME 记录：
```
dashboard.yourdomain.com → d1234567890abc.cloudfront.net
```

### 3. 更新 CloudFront 分发

```bash
# 添加备用域名和 SSL 证书
aws cloudfront update-distribution \
  --id E1234567890ABC \
  --distribution-config file://custom-domain-config.json
```

## 故障排除

### 常见问题

1. **404 错误**
   - 检查 S3 bucket 政策
   - 验证 CloudFront 错误页面配置

2. **API 调用失败**
   - 确认 ALB DNS 名称正确
   - 检查 CORS 配置

3. **缓存问题**
   - 创建 CloudFront 无效化
   - 清除浏览器缓存

### 调试命令

```bash
# 测试 S3 网站访问
curl -I http://bucket-name.s3-website.region.amazonaws.com

# 测试 CloudFront 访问
curl -I https://d1234567890abc.cloudfront.net

# 检查 DNS 解析
nslookup d1234567890abc.cloudfront.net

# 查看 CloudFront 日志
aws logs tail /aws/cloudfront/distribution-id --follow
```

## 安全最佳实践

### 1. Bucket 安全

- 禁用公开写入权限
- 启用 S3 访问日志
- 配置 Bucket 版本控制

### 2. CloudFront 安全

- 启用 AWS WAF (可选)
- 配置地理限制 (如需要)
- 启用实时日志

### 3. 内容安全

- 设置适当的缓存头
- 配置 CSP 安全头
- 定期扫描依赖漏洞

## 备份和恢复

### 自动备份

部署脚本会自动创建备份：
- 备份位置: `s3://bucket-name-backups/`
- 备份格式: `backup-YYYY-MM-DD-HHMMSS/`
- 保留策略: 保留最近 10 个版本

### 灾难恢复

```bash
# 完整环境重建
./deploy-frontend.sh

# 从备份恢复
./rollback-frontend.sh --version 2025-08-29-120000
```

## CI/CD 集成

### GitHub Actions 自动化

创建 `.github/workflows/deploy-frontend.yml`:

```yaml
name: Deploy Frontend to S3+CloudFront

on:
  push:
    branches: [ main ]
    paths: [ 'src/**', 'config/**' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ap-east-1
    
    - name: Deploy frontend
      run: |
        cd aws-deployment/frontend
        ./deploy-frontend.sh
```

## 性能优化

### 1. 文件优化

- 压缩 JavaScript/CSS 文件
- 优化图片大小和格式
- 使用适当的文件命名策略

### 2. 缓存优化

- 静态资源使用长期缓存
- HTML 使用短期缓存
- 使用 ETag 进行条件请求

### 3. CDN 优化

- 选择合适的价格等级
- 配置压缩设置
- 使用 HTTP/2 协议

## 总结

S3 + CloudFront 架构为 MEM Dashboard 前端提供了：

✅ **高性能**: 全球 CDN 加速  
✅ **高可用**: 99.99% SLA 保证  
✅ **低成本**: 按使用量付费  
✅ **易维护**: 自动化部署和运维  
✅ **安全性**: HTTPS 和访问控制  

这个架构方案完美契合您的后端 ECS 部署，形成了一个完整、可靠的全栈云原生解决方案。

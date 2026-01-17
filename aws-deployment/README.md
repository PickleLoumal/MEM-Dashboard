# AWS Deployment Configuration

AWS 部署相关的配置文件和模板。

> **注意**: 实际部署脚本在 `scripts/active/deployment/` 目录下，本目录主要存放参考配置和 CloudFormation 模板。

## 目录结构

```
aws-deployment/
├── cloudformation/          # CloudFormation 基础设施模板
│   ├── vpc-template.json    # VPC 网络架构（含 NAT Gateway）
│   ├── automation-secrets-template.json  # Secrets Manager 模板
│   └── pdf-service-template.json         # PDF 服务资源模板
│
├── ecs/                     # ECS 任务定义参考（实际由部署脚本动态生成）
│   ├── ecs-service.json     # MEM Dashboard 服务配置参考
│   ├── latex-service.json   # LaTeX 服务配置参考
│   ├── latex-service-task-definition.json
│   ├── stocks-data-import-task-definition.json
│   └── yfinance-diagnostic-task-definition.json
│
├── eventbridge/             # EventBridge 定时任务配置
│   └── auto-fetch-targets.json
│
├── config/                  # 环境变量参考
│   └── environment.env
│
├── archive/                 # 已归档的旧文件
│   ├── ecs/                 # 旧的 ECS 任务定义
│   ├── frontend/            # 旧的前端部署配置
│   └── docs/                # 旧文档
│
└── README.md
```

## 实际部署方式

### 后端部署 (ECS)

```bash
# MEM Dashboard 后端
python3 scripts/active/deployment/deploy_to_ecs.py --auto-tag

# LaTeX PDF 服务
python3 scripts/active/deployment/deploy_latex_service.py
```

这些脚本会**动态生成任务定义**，不依赖本目录的 JSON 文件。

### 前端部署 (S3 + CloudFront)

```bash
# CSI300 Dashboard
./scripts/active/deployment/deploy-csi300-frontend-to-aws.sh

# MEM Dashboard
./scripts/active/deployment/deploy-mem-frontend-to-aws.sh
```

## AWS 架构

### 网络架构

```
┌─────────────────────────────────────────────────────────┐
│                    VPC (10.0.0.0/16)                    │
│  ┌─────────────────┐      ┌─────────────────┐          │
│  │  Public Subnet  │      │  Public Subnet  │          │
│  │   10.0.1.0/24   │      │   10.0.2.0/24   │          │
│  │  ┌───────────┐  │      │                 │          │
│  │  │NAT Gateway│  │      │      ALB        │          │
│  │  └─────┬─────┘  │      └─────────────────┘          │
│  └────────┼────────┘                                   │
│           │                                            │
│  ┌────────▼────────┐      ┌─────────────────┐          │
│  │ Private Subnet  │      │ Private Subnet  │          │
│  │   10.0.3.0/24   │      │   10.0.4.0/24   │          │
│  │   (ECS Tasks)   │      │   (ECS Tasks)   │          │
│  └─────────────────┘      └─────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

### 运行的服务

| 服务 | 类型 | 说明 |
|------|------|------|
| `mem-dashboard-service` | ECS Fargate | 主后端 API |
| `alfie-latex-service` | ECS Fargate | PDF 生成服务 |
| `csi300-backend-service` | ECS Fargate | CSI300 后端 |

### 前端

| 前端 | S3 Bucket | CloudFront |
|------|-----------|------------|
| CSI300 Dashboard | `csi300-frontend-ap-east-1-*` | `d3ex2kglhlhbyr.cloudfront.net` |
| MEM Dashboard | `mem-dashboard-frontend-production` | `d1ht73txi7ykd0.cloudfront.net` |

## CloudFormation 模板

### vpc-template.json

定义 VPC 网络架构，包括：
- VPC (10.0.0.0/16)
- 2 个公有子网 + 2 个私有子网
- Internet Gateway
- NAT Gateway（私有子网访问外网）
- 路由表

### automation-secrets-template.json

定义 Secrets Manager 密钥，包括：
- 数据库凭证
- API Keys (FRED, BEA, XAI, Perplexity)

### pdf-service-template.json

定义 PDF 服务资源：
- SQS 队列
- S3 存储桶
- IAM 角色

## 常用 AWS 命令

```bash
# 查看 ECS 服务状态
aws ecs describe-services --cluster mem-dashboard-cluster --services mem-dashboard-service --region ap-east-1

# 查看任务日志
aws logs tail /ecs/mem-dashboard --follow --region ap-east-1

# 强制重新部署
aws ecs update-service --cluster mem-dashboard-cluster --service mem-dashboard-service --force-new-deployment --region ap-east-1

# 连接到运行中的容器
aws ecs execute-command --cluster mem-dashboard-cluster --task <TASK-ARN> --container mem-dashboard-container --interactive --command "/bin/bash" --region ap-east-1
```

## 归档文件

`archive/` 目录包含旧的配置文件，仅供参考：
- 旧版本任务定义 (v19, v20 等)
- 旧的前端部署脚本
- 旧文档

---

**Region**: ap-east-1 (Hong Kong)
**Account**: 952189540759
**Last Updated**: 2026-01-17

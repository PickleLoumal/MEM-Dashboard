# AWS Deployment for MEM Dashboard

This directory contains all configuration files, scripts, and documentation for deploying the MEM Dashboard to Amazon Web Services (AWS).

## Directory Structure

```
MEM Dashboard/
├── Dockerfile                                    # Docker container build configuration
├── .dockerignore                                 # Docker build ignore file
├── requirements.txt                              # Python base dependencies
├── runtime.txt                                   # Python runtime version
│
├── .github/                                      # GitHub Actions CI/CD
│   └── workflows/
│       └── deploy-ecs.yml                        # ECS automated deployment pipeline
│
└── aws-deployment/                               # AWS deployment core directory
    ├── config/                                   # Environment configuration
    │   └── environment.env                       # Environment variables configuration
    │
    ├── ecs/                                      # ECS container service configuration
    │   ├── ecs-task-definition.json              # ECS task definition
    │   └── ecs-service.json                      # ECS service configuration
    │
    ├── scripts/                                  # Automated deployment scripts
    │   ├── setup-infrastructure.sh               # AWS infrastructure creation
    │   ├── deploy-ecs.sh                         # ECS application deployment
    │   ├── rollback.sh                           # Deployment rollback script
    │   ├── logs.sh                               # Log management script
    │   └── validate.sh                           # Deployment validation script
    │
    └── cloudformation/                           # CloudFormation infrastructure templates
        └── vpc-template.json                     # VPC network architecture template

```

## File Functions Overview

### Container Layer
- **Dockerfile** - Multi-stage build for production-grade container images
- **.dockerignore** - Optimizes build size and security

### AWS Infrastructure Layer
- **cloudformation/vpc-template.json** - Network architecture definition
- **scripts/setup-infrastructure.sh** - One-click AWS resource creation

### Container Orchestration Layer
- **ecs-task-definition.json** - Container runtime configuration
- **ecs/ecs-service.json** - Service load balancing configuration

### Automated Operations Layer
- **scripts/deploy-ecs.sh** - Automated deployment
- **scripts/rollback.sh** - Version rollback
- **scripts/logs.sh** - Log management
- **scripts/validate.sh** - Configuration validation

### CI/CD Layer
- **deploy-ecs.yml** - GitHub Actions automation

### Configuration Management Layer
- **config/environment.env** - Unified environment variable management

This architecture implements **Infrastructure as Code (IaC)** and **DevOps best practices**, supporting one-click deployment, auto-scaling, and zero-downtime updates.

## Quick Deployment

### 1. 准备环境

```bash
# 确保已安装 AWS CLI 和 Docker
# 配置 AWS 凭证
aws configure
```

### 2. 一键部署

```bash
# 进入 aws-deployment 目录
cd aws-deployment

# 验证部署配置
./scripts/validate.sh

# 创建 AWS 基础设施
./scripts/setup-infrastructure.sh

# 配置数据库和API密钥 (参考 docs/ECS-Quick-Start.md)

# 部署应用到 ECS
./scripts/deploy-ecs.sh
```

## 📋 部署组件

### 🏗️ AWS 基础设施

- **VPC**: 10.0.0.0/16 专用网络
- **子网**: 2个公有子网 + 2个私有子网 (跨AZ)
- **安全组**: ALB、ECS、RDS 专用安全组
- **负载均衡器**: Application Load Balancer
- **NAT Gateway**: 私有子网互联网访问

### 🐳 容器服务

- **ECS Fargate**: 无服务器容器服务
- **ECR**: 私有容器镜像仓库
- **任务规格**: 0.5 vCPU, 1GB 内存
- **自动扩展**: 1-10 个实例

### 🗄️ 数据存储

- **RDS PostgreSQL**: 托管数据库服务
- **AWS Secrets Manager**: 密钥管理
- **S3**: 备份和静态文件存储

### 📊 监控运维

- **CloudWatch**: 日志和指标监控
- **ALB健康检查**: 应用层健康监控
- **ECS服务发现**: 自动故障恢复

## 💰 成本预估

| 服务 | 配置 | 月度成本 |
|------|------|----------|
| ECS Fargate | 0.5 vCPU, 1GB × 2实例 | $24 |
| ALB | 标准负载均衡器 | $16 |
| RDS | db.t3.micro PostgreSQL | $13 |
| NAT Gateway | 单AZ | $32 |
| CloudWatch | 日志和监控 | $3 |
| **总计** | | **~$88/月** |

### 成本优化选项

- **Fargate Spot**: 节省 70% 计算成本
- **定时停止**: 开发环境节省 60% 成本
- **Reserved Instances**: RDS 节省 40% 成本

## 🔧 常用操作

### 查看部署状态

```bash
# 检查 ECS 服务状态
aws ecs describe-services \
    --cluster mem-dashboard-cluster \
    --services mem-dashboard-service

# 查看应用日志
aws logs tail /ecs/mem-dashboard --follow
```

### 更新应用

```bash
# 重新部署最新代码
./scripts/deploy-ecs.sh

# 或强制重新部署
aws ecs update-service \
    --cluster mem-dashboard-cluster \
    --service mem-dashboard-service \
    --force-new-deployment
```

### 扩展服务

```bash
# 扩展到 3 个实例
aws ecs update-service \
    --cluster mem-dashboard-cluster \
    --service mem-dashboard-service \
    --desired-count 3
```

## 🔒 安全考虑

### 网络安全
- 数据库在私有子网，不可直接访问
- 安全组限制端口和IP访问
- SSL/TLS 加密传输

### 访问控制
- IAM 角色最小权限原则
- AWS Secrets Manager 管理敏感信息
- ECS 任务角色隔离

### 合规性
- 启用 CloudTrail 审计日志
- VPC Flow Logs 网络监控
- 定期安全扫描和更新

## 📚 详细文档

- **[ECS 快速开始](docs/ECS-Quick-Start.md)** - 分步部署指南
- **[ECS 部署详情](docs/ECS-Deployment-README.md)** - 详细配置说明
- **[部署摘要](docs/ECS-Deployment-Summary.md)** - 完整文件清单

## 🛠️ 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 查看服务事件
   aws ecs describe-services --cluster mem-dashboard-cluster --services mem-dashboard-service
   ```

2. **健康检查失败**
   ```bash
   # 检查目标组健康
   aws elbv2 describe-target-health --target-group-arn <TARGET-GROUP-ARN>
   ```

3. **数据库连接失败**
   ```bash
   # 验证密钥配置
   aws secretsmanager get-secret-value --secret-id mem-dashboard/database
   ```

### 调试模式

```bash
# 连接到运行中的容器
aws ecs execute-command \
    --cluster mem-dashboard-cluster \
    --task <TASK-ARN> \
    --container mem-dashboard-container \
    --interactive \
    --command "/bin/bash"
```

## 🔄 CI/CD 集成

项目根目录的 `.github/workflows/deploy-ecs.yml` 提供了自动化部署工作流：

- **触发条件**: push到main分支
- **测试**: 运行Django测试套件
- **构建**: Docker镜像构建和推送
- **部署**: 自动更新ECS服务

## 📞 获取帮助

如果遇到问题：

1. 检查 [故障排除文档](docs/ECS-Quick-Start.md#故障排除)
2. 查看 CloudWatch 日志
3. 验证 AWS 服务状态
4. 检查 IAM 权限配置

---

**维护**: 技术团队  
**版本**: 1.0  
**更新**: 2025年7月1日

## 🛠️ 管理脚本

### 回滚部署

使用 `rollback.sh` 脚本可以快速回滚到之前的版本：

```bash
# 查看可用的版本
./scripts/rollback.sh --list

# 查看当前服务状态
./scripts/rollback.sh --status

# 回滚到上一个版本
./scripts/rollback.sh --previous

# 回滚到指定版本
./scripts/rollback.sh --revision 5
```

### 日志管理

使用 `logs.sh` 脚本管理和查看应用日志：

```bash
# 查看运行中的任务
./scripts/logs.sh tasks

# 实时查看日志 (默认10分钟)
./scripts/logs.sh follow

# 查看最近的日志
./scripts/logs.sh recent 2 100  # 最近2小时，100行

# 搜索错误日志
./scripts/logs.sh errors 24     # 最近24小时的错误

# 搜索特定模式
./scripts/logs.sh search "ConnectionError" 12

# 导出日志到文件
./scripts/logs.sh export debug.log 6  # 导出最近6小时的日志

# 查看日志统计
./scripts/logs.sh stats
```

### 环境配置

所有环境变量都在 `config/environment.env` 中定义：

```bash
# 加载环境变量
source aws-deployment/config/environment.env

# 查看当前配置
echo "Project: $PROJECT_NAME"
echo "Region: $AWS_REGION"
echo "Cluster: $ECS_CLUSTER_NAME"
```

### 部署验证

使用 `validate.sh` 脚本验证部署配置：

```bash
# 完整验证（包括AWS资源检查）
./scripts/validate.sh

# 快速验证（跳过AWS资源检查）
./scripts/validate.sh --quick

# 仅验证配置文件
./scripts/validate.sh --config-only
```

验证脚本会检查：
- AWS CLI 配置和权限
- Docker 环境
- 必需工具（jq, curl）
- 配置文件完整性
- JSON 格式正确性
- 环境变量设置
- 现有 AWS 资源状态

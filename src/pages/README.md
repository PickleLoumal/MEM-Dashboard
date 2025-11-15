# MEM Dashboard - US Economic Indicators Page

## 文件说明

### US.html
美国经济指标的独立页面版本，包含完整的经济数据展示。

**访问地址：**
- S3: http://mem-dashboard-frontend-production.s3-website.ap-east-1.amazonaws.com/src/pages/US.html
- CloudFront: https://d1ht73txi7ykd0.cloudfront.net/src/pages/US.html

### index.html
与 US.html 相同的内容，作为目录默认页面。

**访问地址：**
- S3: http://mem-dashboard-frontend-production.s3-website.ap-east-1.amazonaws.com/src/pages/
- CloudFront: https://d1ht73txi7ykd0.cloudfront.net/src/pages/

## 资源路径

此页面使用相对路径引用资源：
- CSS: `../../src/assets/css/base/main.css`
- JS: `../../src/assets/js/`
- Config: `../../config/api_config.js`

## 部署说明

此目录会通过 `aws-deployment/frontend/deploy-frontend.sh` 脚本自动部署到S3。

部署命令会同步整个 `src/` 目录：
```bash
aws s3 sync "${BUILD_DIR}/src" "s3://${BUCKET_NAME}/src" \
    --cache-control "public, max-age=31536000" \
    --delete
```

## 历史

- 2025-08-29: 从S3恢复此目录（之前在本地被误删）
- 原始创建时间: 2025年8月之前

## 与根目录 index.html 的区别

- **根目录 index.html**: 主入口页面，使用相对路径 `src/` 和 `config/`
- **src/pages/US.html**: 独立的美国经济页面，使用 `../../` 相对路径

两者内容相似但路径引用不同。

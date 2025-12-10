#!/usr/bin/env python
"""
Investment Summary Generator CLI

命令行入口 - 独立脚本运行时使用。
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path


def setup_django():
    """设置 Django 环境"""
    # 计算路径: cli.py -> services -> csi300 -> django_api -> src -> project_root
    PROJECT_ROOT = Path(__file__).resolve().parents[4]
    SRC_DIR = PROJECT_ROOT / "src"
    DJANGO_API_DIR = SRC_DIR / "django_api"

    for path in (str(SRC_DIR), str(DJANGO_API_DIR)):
        if path not in sys.path:
            sys.path.insert(0, path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_api.settings")

    import django

    django.setup()


def main():
    """CLI 主入口"""
    parser = argparse.ArgumentParser(
        description="CSI300 Investment Summary 自动化生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python -m csi300.services.cli                              # 处理所有公司
  python -m csi300.services.cli --company "ZTE Corp"         # 只处理 ZTE Corp
  python -m csi300.services.cli --ticker "000063.SZ"         # 只处理股票代码 000063.SZ
  python -m csi300.services.cli --id 1086                    # 只处理 ID 为 1086 的公司
  python -m csi300.services.cli --company "ZTE" --fuzzy      # 模糊匹配包含 "ZTE" 的公司
        """,
    )
    parser.add_argument("--company", "-c", type=str, help="公司名称 (精确匹配或模糊匹配)")
    parser.add_argument("--ticker", "-t", type=str, help="股票代码 (精确匹配)")
    parser.add_argument("--id", type=int, help="公司数据库 ID")
    parser.add_argument("--fuzzy", "-f", action="store_true", help="启用模糊匹配 (用于 --company)")

    args = parser.parse_args()

    # 设置 Django 环境
    setup_django()

    # 导入 main 函数 (Django 已初始化后)
    from csi300.services.generator import main as async_main

    # 运行
    asyncio.run(
        async_main(
            company_id=args.id, company_name=args.company, ticker=args.ticker, fuzzy=args.fuzzy
        )
    )


if __name__ == "__main__":
    main()

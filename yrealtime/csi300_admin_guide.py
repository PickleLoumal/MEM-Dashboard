#!/usr/bin/env python3
"""
CSI300 Admin Interface Guide

This script helps troubleshoot and fix CSI300 admin interface issues.
"""

def show_admin_fixes():
    """显示 admin 界面修复说明"""
    print("🔧 CSI300 Admin Interface Fixes")
    print("=" * 50)

    print("\n✅ 已修复的问题:")
    print("1. 添加了价格字段到 list_display")
    print("2. 创建了 'Price Information' 字段组")
    print("3. 增强了筛选器和搜索选项")
    print("4. 添加了收益和增长指标")

    print("\n📋 修复后的 admin 配置:")
    print("• list_display: ticker, name, im_sector, price_local_currency, market_cap_local, pe_ratio_trailing, roe_trailing, updated_at")
    print("• 新增 fieldsets: Price Information, Earnings & Growth")
    print("• 增强的 list_filter: im_sector, gics_industry, industry, currency, last_trade_date")
    print("• 增强的 search_fields: ticker, name, naming, im_sector, gics_industry")

    print("\n🚨 如果看不到数据，请检查:")
    print("1. 数据库中是否有 CSI300 数据")
    print("2. 数据是否包含价格和市值信息")
    print("3. Django 服务器是否重启以应用新配置")

def show_data_loading_instructions():
    """显示数据加载说明"""
    print("\n📊 数据加载说明:")
    print("=" * 30)

    print("如果数据库中没有数据或数据不完整，请运行:")
    print("1. python3 src/django_api/manage.py update_market_cap --json-file /path/to/csi300_data.json")
    print("2. 或者从 S3 加载: python3 src/django_api/manage.py update_market_cap --s3-bucket your-bucket")

    print("\n💡 数据文件格式:")
    print("CSI300 数据应该是 JSON 格式，包含公司信息、市值、价格等字段")

    print("\n🔍 检查数据状态:")
    print("运行: python3 check_csi300_data.py")

def show_admin_access_steps():
    """显示 admin 访问步骤"""
    print("\n🌐 Admin 界面访问:")
    print("=" * 25)

    print("1. 启动 Django 服务器:")
    print("   python3 src/django_api/manage.py runserver")

    print("2. 打开浏览器访问:")
    print("   http://localhost:8000/admin/")

    print("3. 登录后导航到:")
    print("   CSI300 > CSI300 companies")

    print("4. 查看修复后的界面:")
    print("   • 列表视图显示价格和市值")
    print("   • 详情页有完整的价格信息分组")
    print("   • 可以使用新的筛选器和搜索")

def main():
    """主函数"""
    show_admin_fixes()
    show_data_loading_instructions()
    show_admin_access_steps()

    print("\n🎯 快速检查:")
    print("运行以下命令检查数据状态:")
    print("  python3 check_csi300_data.py")

    print("\n✨ 修复完成!")
    print("现在应该能在 admin 界面看到所有公司字段包括价格信息了。")

if __name__ == "__main__":
    main()

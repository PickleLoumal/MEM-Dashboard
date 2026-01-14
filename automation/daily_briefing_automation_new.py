"""
Daily Briefing Automation Tool

Scrapes Briefing.com pages and updates Google Sheets:
1. Page One -> H2
2. Stock Market Update -> I2
3. Bond Market Update -> J2

Environment Variables Required:
- GOOGLE_SHEETS_SPREADSHEET_ID: Google Sheets document ID
- GOOGLE_SHEETS_CREDENTIALS_FILE: Service account JSON file name
"""

import os
import re
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from google.oauth2.service_account import Credentials

# Load environment variables from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(env_path)
except ImportError:
    pass

# =============================================================================
# Configuration from Environment Variables
# =============================================================================


def _validate_config():
    """Validate that required environment variables are set."""
    missing = []
    if not os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID"):
        missing.append("GOOGLE_SHEETS_SPREADSHEET_ID")
    if not os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE"):
        missing.append("GOOGLE_SHEETS_CREDENTIALS_FILE")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please set them in your .env file or system environment."
        )


class DailyBriefingAutomation:
    def __init__(self, credentials_file=None):
        """Initialize with configuration from environment variables."""
        # Validate configuration
        _validate_config()

        # URLs for Briefing.com pages
        self.page_one_url = "https://www.briefing.com/page-one"
        self.market_update_url = "https://www.briefing.com/stock-market-update"
        self.bond_update_url = "https://www.briefing.com/bond-market-update"

        # Load from environment variables (required)
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")

        # Resolve credentials file path
        creds_file = credentials_file or os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.isabs(creds_file):
            self.credentials_file = creds_file
        else:
            self.credentials_file = os.path.join(script_dir, creds_file)

        self.client = None
        self.sheet = None
        self.driver = None

    def authenticate_google_sheets(self):
        """认证 Google Sheets"""
        try:
            print("🔐 正在认证 Google Sheets...")

            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=scopes
            )

            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_key(self.spreadsheet_id).sheet1

            print("✅ Google Sheets 认证成功！")
            return True

        except Exception as e:
            print(f"❌ Google Sheets 认证失败: {str(e)}")
            return False

    def init_driver(self):
        """初始化 Chrome 浏览器"""
        if self.driver:
            return

        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        self.driver = webdriver.Chrome(options=chrome_options)

    def close_driver(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def scrape_page_one(self):
        """爬取 Page One 内容"""
        try:
            print(f"\n📰 [1/2] 爬取 Page One...")
            print(f"    URL: {self.page_one_url}")

            self.init_driver()
            self.driver.get(self.page_one_url)

            # 等待页面加载
            print("    ⏳ 等待页面加载...")
            time.sleep(5)

            # 提取内容
            try:
                app_root = self.driver.find_element(By.TAG_NAME, 'briefing-app-root')
                content = app_root.text

                if content and len(content) > 100:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    final_content = f"=== Daily Briefing Page One - {timestamp} ===\n"
                    final_content += f"来源: {self.page_one_url}\n\n"
                    final_content += content[:5000]  # 限制长度避免超出单元格限制

                    print(f"    ✅ 成功爬取，共 {len(content)} 字符")
                    return final_content
                else:
                    print("    ⚠️  内容为空")
                    return None

            except Exception as e:
                print(f"    ❌ 提取内容失败: {str(e)}")
                return None

        except Exception as e:
            print(f"    ❌ 爬取失败: {str(e)}")
            return None

    def scrape_market_update(self):
        """爬取 Stock Market Update 最新文章"""
        try:
            print(f"\n📊 [2/2] 爬取 Stock Market Update...")
            print(f"    URL: {self.market_update_url}")

            self.init_driver()
            self.driver.get(self.market_update_url)

            # 等待页面加载
            print("    ⏳ 等待页面加载...")
            time.sleep(5)

            # 提取内容
            try:
                app_root = self.driver.find_element(By.TAG_NAME, 'briefing-app-root')
                full_content = app_root.text

                # 提取关键部分
                content_parts = []

                # 1. 提取标题和时间
                lines = full_content.split('\n')
                for i, line in enumerate(lines):
                    if 'Stock Market Update' in line:
                        # 找到标题，往后取相关内容
                        content_parts.append(line)

                        # 提取时间戳
                        if i + 1 < len(lines) and ('Last Updated' in lines[i + 1] or 'Archive' in lines[i + 1]):
                            content_parts.append(lines[i + 1])

                        break

                # 2. 查找 Market Snapshot
                market_snapshot_idx = -1
                for i, line in enumerate(lines):
                    if 'Market Snapshot' in line:
                        market_snapshot_idx = i
                        break

                if market_snapshot_idx > 0:
                    # 提取 Market Snapshot 部分（往后15行）
                    snapshot_lines = lines[market_snapshot_idx:market_snapshot_idx + 15]
                    if snapshot_lines:
                        content_parts.append('\n' + '\n'.join(snapshot_lines))

                # 3. 查找 Industry Watch
                for i, line in enumerate(lines):
                    if 'Industry Watch' in line:
                        # 往后取5行
                        industry_lines = lines[i:min(i + 5, len(lines))]
                        if industry_lines:
                            content_parts.append('\n' + '\n'.join(industry_lines))
                        break

                # 4. 查找 Moving the Market
                for i, line in enumerate(lines):
                    if 'Moving the Market' in line:
                        # 往后取10行
                        moving_lines = lines[i:min(i + 10, len(lines))]
                        if moving_lines:
                            content_parts.append('\n' + '\n'.join(moving_lines))
                        break

                if content_parts:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    final_content = f"=== Stock Market Update - {timestamp} ===\n"
                    final_content += '\n'.join(content_parts)

                    print(f"    ✅ 成功爬取，共 {len(final_content)} 字符")
                    return final_content
                else:
                    print("    ⚠️  未找到关键内容")
                    # 返回前2000字符作为备用
                    if full_content and len(full_content) > 100:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        return f"=== Stock Market Update - {timestamp} ===\n{full_content[:2000]}"
                    return None

            except Exception as e:
                print(f"    ❌ 提取内容失败: {str(e)}")
                return None

        except Exception as e:
            print(f"    ❌ 爬取失败: {str(e)}")
            return None

    def scrape_bond_update(self):
        """爬取 Bond Market Update 最新文章"""
        try:
            print(f"\n📈 [3/3] 爬取 Bond Market Update...")
            print(f"    URL: {self.bond_update_url}")

            self.init_driver()
            self.driver.get(self.bond_update_url)

            print("    ⏳ 等待页面加载...")
            time.sleep(5)

            try:
                app_root = self.driver.find_element(By.TAG_NAME, 'briefing-app-root')
                full_content = app_root.text
                lines = full_content.split('\n')

                content_parts = []

                # 1. 标题和时间
                for i, line in enumerate(lines):
                    if 'Bond Market Update' in line:
                        content_parts.append(line)
                        if i + 1 < len(lines) and 'Last Updated' in lines[i + 1]:
                            content_parts.append(lines[i + 1])
                        break

                # 2. 第一篇文章内容（查找包含ET的时间戳行）
                first_article_start = -1
                for i, line in enumerate(lines):
                    if re.search(r'\d{2}-[A-Za-z]{3}-\d{2}\s+\d{2}:\d{2}\s+ET', line):
                        first_article_start = i
                        break

                if first_article_start > 0:
                    # 查找下一个时间戳作为文章结束标记
                    article_end = len(lines)
                    for i in range(first_article_start + 5, min(first_article_start + 60, len(lines))):
                        if re.search(r'\d{2}-[A-Za-z]{3}-\d{2}\s+\d{2}:\d{2}\s+ET', lines[i]):
                            article_end = i
                            break

                    # 提取第一篇文章
                    content_parts.append('\n')
                    content_parts.append('\n'.join(lines[first_article_start:article_end]))

                if content_parts:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    final_content = f"=== Bond Market Update - {timestamp} ===\n"
                    final_content += '\n'.join(content_parts)

                    print(f"    ✅ 成功爬取，共 {len(final_content)} 字符")
                    return final_content
                else:
                    print("    ⚠️  未找到关键内容")
                    return None

            except Exception as e:
                print(f"    ❌ 提取内容失败: {str(e)}")
                return None

        except Exception as e:
            print(f"    ❌ 爬取失败: {str(e)}")
            return None

    def write_to_google_sheets(self, content, cell, description):
        """写入 Google Sheets"""
        try:
            if not self.sheet or not content:
                return False

            print(f"    📝 正在将内容写入单元格 {cell}...")
            self.sheet.update(range_name=cell, values=[[content]])

            print(f"    ✅ {description} 已写入 {cell}")
            return True

        except Exception as e:
            print(f"    ❌ 写入失败: {str(e)}")
            return False

    def run(self):
        """运行完整流程"""
        print("=" * 70)
        print("🚀 Daily Briefing 自动化工具")
        print("=" * 70)

        # 1. 认证 Google Sheets
        if not self.authenticate_google_sheets():
            return False

        success_count = 0

        try:
            # 2. 爬取 Page One 并写入 H2
            page_one_content = self.scrape_page_one()
            if page_one_content:
                if self.write_to_google_sheets(page_one_content, 'H2', 'Page One'):
                    success_count += 1

            # 3. 爬取 Stock Market Update 并写入 I2
            market_update_content = self.scrape_market_update()
            if market_update_content:
                if self.write_to_google_sheets(market_update_content, 'I2', 'Stock Market Update'):
                    success_count += 1

            # 4. 爬取 Bond Market Update 并写入 J2
            bond_update_content = self.scrape_bond_update()
            if bond_update_content:
                if self.write_to_google_sheets(bond_update_content, 'J2', 'Bond Market Update'):
                    success_count += 1

        finally:
            # 关闭浏览器
            self.close_driver()

        # 输出结果
        print("\n" + "=" * 70)
        if success_count == 3:
            print("🎉 所有内容爬取并保存成功！")
            print(f"   ✅ Page One → H2")
            print(f"   ✅ Stock Market Update → I2")
            print(f"   ✅ Bond Market Update → J2")
        elif success_count > 0:
            print(f"⚠️  部分内容爬取成功 ({success_count}/3)")
        else:
            print("❌ 爬取失败")

        print(f"\n🔗 查看表格: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")
        print("=" * 70)

        return success_count > 0


def main():
    """主函数"""
    automation = DailyBriefingAutomation()
    automation.run()


if __name__ == "__main__":
    main()

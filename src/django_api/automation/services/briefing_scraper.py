import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from observability import get_logger

from .google_sheets import GoogleSheetsService

logger = get_logger(__name__)


class BriefingScraperService:
    """Service for scraping Briefing.com and updating Google Sheets"""

    def __init__(self):
        self.page_one_url = "https://www.briefing.com/page-one"
        self.market_update_url = "https://www.briefing.com/stock-market-update"
        self.bond_update_url = "https://www.briefing.com/bond-market-update"
        self.driver = None
        self.sheets_service = GoogleSheetsService()

    def _init_driver(self):
        """Initialize Chrome driver with headless options"""
        if self.driver:
            return

        logger.info("Initializing Chrome WebDriver")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )

        self.driver = webdriver.Chrome(options=chrome_options)

    def _close_driver(self):
        """Close Chrome driver and release resources"""
        if self.driver:
            logger.info("Closing Chrome WebDriver")
            self.driver.quit()
            self.driver = None

    def scrape_page_one(self) -> str | None:
        """
        Scrape Page One content from Briefing.com.

        Returns:
            The scraped content with timestamp header, or None on failure.
        """
        try:
            logger.info("Scraping Briefing.com Page One", extra={"url": self.page_one_url})
            self._init_driver()
            self.driver.get(self.page_one_url)
            time.sleep(5)  # Wait for JavaScript rendering

            app_root = self.driver.find_element(By.TAG_NAME, "briefing-app-root")
            content = app_root.text

            if content and len(content) > 100:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                final_content = f"=== Daily Briefing Page One - {timestamp} ===\n"
                final_content += f"Source: {self.page_one_url}\n\n"
                final_content += content[:5000]

                logger.info("Page One scrape successful", extra={"content_length": len(content)})
                return final_content

            logger.warning("Page One content empty or too short")
            return None

        except Exception as e:
            logger.exception(
                "Failed to scrape Page One", extra={"url": self.page_one_url, "error": str(e)}
            )
            return None

    def scrape_market_update(self) -> str | None:
        """
        Scrape Stock Market Update from Briefing.com.

        Returns:
            The scraped content with timestamp header, or None on failure.
        """
        try:
            logger.info(
                "Scraping Briefing.com Stock Market Update", extra={"url": self.market_update_url}
            )
            self._init_driver()
            self.driver.get(self.market_update_url)
            time.sleep(5)

            app_root = self.driver.find_element(By.TAG_NAME, "briefing-app-root")
            full_content = app_root.text

            if full_content:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result = f"=== Stock Market Update - {timestamp} ===\n{full_content[:5000]}"

                logger.info(
                    "Stock Market Update scrape successful",
                    extra={"content_length": len(full_content)},
                )
                return result

            logger.warning("Stock Market Update content empty")
            return None

        except Exception as e:
            logger.exception(
                "Failed to scrape Stock Market Update",
                extra={"url": self.market_update_url, "error": str(e)},
            )
            return None

    def scrape_bond_update(self) -> str | None:
        """
        Scrape Bond Market Update from Briefing.com.

        Returns:
            The scraped content with timestamp header, or None on failure.
        """
        try:
            logger.info(
                "Scraping Briefing.com Bond Market Update", extra={"url": self.bond_update_url}
            )
            self._init_driver()
            self.driver.get(self.bond_update_url)
            time.sleep(5)

            app_root = self.driver.find_element(By.TAG_NAME, "briefing-app-root")
            full_content = app_root.text

            if full_content:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result = f"=== Bond Market Update - {timestamp} ===\n{full_content[:5000]}"

                logger.info(
                    "Bond Market Update scrape successful",
                    extra={"content_length": len(full_content)},
                )
                return result

            logger.warning("Bond Market Update content empty")
            return None

        except Exception as e:
            logger.exception(
                "Failed to scrape Bond Market Update",
                extra={"url": self.bond_update_url, "error": str(e)},
            )
            return None

    def run(self) -> bool:
        """
        Run the full scraping process.

        Scrapes three pages from Briefing.com and writes to Google Sheets:
        - Page One -> Cell H2
        - Stock Market Update -> Cell I2
        - Bond Market Update -> Cell J2

        Returns:
            True if at least one page was successfully scraped and written.
        """
        success_count = 0

        try:
            logger.info("Starting Briefing.com scraping workflow")

            # Authenticate with Google Sheets first
            self.sheets_service.authenticate()

            # 1. Scrape Page One -> H2
            content1 = self.scrape_page_one()
            if content1:
                if self.sheets_service.write_cell("H2", content1, "Page One"):
                    success_count += 1

            # 2. Scrape Stock Market Update -> I2
            content2 = self.scrape_market_update()
            if content2:
                if self.sheets_service.write_cell("I2", content2, "Stock Market Update"):
                    success_count += 1

            # 3. Scrape Bond Market Update -> J2
            content3 = self.scrape_bond_update()
            if content3:
                if self.sheets_service.write_cell("J2", content3, "Bond Market Update"):
                    success_count += 1

            logger.info(
                "Briefing.com scraping workflow completed",
                extra={"success_count": success_count, "total_pages": 3},
            )
            return success_count > 0

        finally:
            self._close_driver()

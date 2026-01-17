import time
from datetime import date, datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from observability import get_logger

from ..models import DailyBriefingData

logger = get_logger(__name__)


class BriefingScraperService:
    """Service for scraping Briefing.com and storing data in the database"""

    def __init__(self):
        self.page_one_url = "https://www.briefing.com/page-one"
        self.market_update_url = "https://www.briefing.com/stock-market-update"
        self.bond_update_url = "https://www.briefing.com/bond-market-update"
        self.driver = None

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

    def _save_to_database(
        self, source_type: str, source_url: str, content: str, target_date: date
    ) -> bool:
        """
        Save scraped content to the database.

        Args:
            source_type: Type of content (page_one, stock_market, bond_market).
            source_url: URL of the scraped page.
            content: Scraped content text.
            target_date: Date for which the data is being scraped.

        Returns:
            True if successfully saved, False otherwise.
        """
        try:
            DailyBriefingData.objects.update_or_create(
                date=target_date,
                source_type=source_type,
                defaults={
                    "source_url": source_url,
                    "content": content,
                    "content_length": len(content),
                },
            )
            logger.info(
                "Saved briefing data to database",
                extra={
                    "source_type": source_type,
                    "date": str(target_date),
                    "content_length": len(content),
                },
            )
            return True
        except Exception as e:
            logger.exception(
                "Failed to save briefing data to database",
                extra={"source_type": source_type, "date": str(target_date), "error": str(e)},
            )
            return False

    def run(self) -> bool:
        """
        Run the full scraping process.

        Scrapes three pages from Briefing.com and stores in database:
        - Page One
        - Stock Market Update
        - Bond Market Update

        Returns:
            True if at least one page was successfully scraped and saved.
        """
        success_count = 0
        today = date.today()

        try:
            logger.info("Starting Briefing.com scraping workflow", extra={"date": str(today)})

            # 1. Scrape Page One
            content1 = self.scrape_page_one()
            if content1:
                if self._save_to_database("page_one", self.page_one_url, content1, today):
                    success_count += 1

            # 2. Scrape Stock Market Update
            content2 = self.scrape_market_update()
            if content2:
                if self._save_to_database("stock_market", self.market_update_url, content2, today):
                    success_count += 1

            # 3. Scrape Bond Market Update
            content3 = self.scrape_bond_update()
            if content3:
                if self._save_to_database("bond_market", self.bond_update_url, content3, today):
                    success_count += 1

            logger.info(
                "Briefing.com scraping workflow completed",
                extra={"success_count": success_count, "total_pages": 3, "date": str(today)},
            )
            return success_count > 0

        finally:
            self._close_driver()

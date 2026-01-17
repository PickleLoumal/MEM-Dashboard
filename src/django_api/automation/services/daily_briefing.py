from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from observability import get_logger

from ..models import DailyBriefingData, DailyBriefingReport
from ..prompts import get_daily_briefing_prompt, get_quick_version_prompt
from ..utils.markdown_converter import markdown_to_docx
from .google_drive import GoogleDriveService
from .perplexity_client import PerplexityClient

if TYPE_CHECKING:
    from ..models import AutomationTask

logger = get_logger(__name__)


class DailyBriefingService:
    """Service for generating Daily Briefing reports using AI"""

    def __init__(self, task: AutomationTask | None = None):
        """
        Initialize the Daily Briefing service.

        Args:
            task: Optional AutomationTask instance to link generated reports to.
        """
        self.task = task
        self.drive_service = GoogleDriveService()
        self.perplexity_client = PerplexityClient()
        self.output_dir = Path("/tmp/daily_briefing")  # Use temp dir in container
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_from_database(self, target_date: date) -> str:
        """
        Read scraped data from the database for a specific date.

        Args:
            target_date: The date to retrieve data for.

        Returns:
            Combined content string from all sources.

        Raises:
            ValueError: If no data is found for the specified date.
        """
        content = DailyBriefingData.get_combined_content(target_date)

        if not content:
            logger.error(
                "No briefing data found in database for date",
                extra={"date": str(target_date)},
            )
            raise ValueError(f"No briefing data found for {target_date}")

        return content

    def _save_report_to_database(
        self,
        target_date: date,
        report_type: str,
        content: str,
        drive_url: str = "",
    ) -> DailyBriefingReport | None:
        """
        Save a generated report to the database.

        Args:
            target_date: The date of the report.
            report_type: Type of report (long_version or quick_version).
            content: Report content in Markdown format.
            drive_url: Optional Google Drive URL for the uploaded document.

        Returns:
            The created/updated DailyBriefingReport instance, or None on failure.
        """
        if not self.task:
            logger.warning(
                "No task provided, skipping database save for report",
                extra={"date": str(target_date), "report_type": report_type},
            )
            return None

        try:
            report, created = DailyBriefingReport.objects.update_or_create(
                date=target_date,
                report_type=report_type,
                defaults={
                    "task": self.task,
                    "content": content,
                    "drive_url": drive_url,
                },
            )
            action = "created" if created else "updated"
            logger.info(
                f"Report {action} in database",
                extra={
                    "date": str(target_date),
                    "report_type": report_type,
                    "report_id": report.id,
                },
            )
            return report
        except Exception as e:
            logger.exception(
                "Failed to save report to database",
                extra={
                    "date": str(target_date),
                    "report_type": report_type,
                    "error": str(e),
                },
            )
            return None

    def run(self) -> dict:
        """
        Run the report generation process.

        Workflow:
        1. Read data from database (scraped by Stage 1)
        2. Generate Long Version report using Perplexity AI
        3. Generate Quick Version (5-page summary) from Long Version
        4. Save reports to database and upload to Google Drive

        Returns:
            Dictionary with result URLs for long_version and quick_version.

        Raises:
            ValueError: If data read or report generation fails.
        """
        today_date = date.today()
        today_str = today_date.strftime("%Y-%m-%d")
        result_urls = {}

        logger.info(
            "Starting Daily Briefing report generation",
            extra={"date": today_str},
        )

        # 1. Read data from database (scraped by Stage 1)
        briefing_data = self._read_from_database(today_date)

        logger.info(
            "Database briefing data loaded",
            extra={"data_length": len(briefing_data)},
        )

        # 2. Generate Long Version
        logger.info("Generating Long Version report with Perplexity AI")
        prompt = get_daily_briefing_prompt()
        full_prompt = prompt + f"\n\n[Additional Context from Briefing.com]:\n{briefing_data}\n"

        long_content = self.perplexity_client.generate_report(full_prompt)

        if not long_content:
            logger.error("Perplexity AI returned empty content for long report")
            raise ValueError("Failed to generate long report content")

        logger.info("Long Version content generated", extra={"content_length": len(long_content)})

        # Save Long Version DOCX (使用 Pandoc 专业转换)
        long_filename = f"Daily Briefing {today_str}_Long Version.docx"
        long_path = self.output_dir / long_filename
        markdown_to_docx(
            long_content,
            output_path=long_path,
            title=f"Daily Briefing - {today_str} (Long Version)",
        )

        logger.info("Long Version DOCX saved", extra={"path": str(long_path)})

        # Upload Long Version to Google Drive
        self.drive_service.authenticate()
        long_file = self.drive_service.upload_file(str(long_path))
        long_drive_url = ""
        if long_file:
            long_drive_url = long_file.get("webViewLink", "")
            result_urls["long_version"] = long_drive_url
            logger.info(
                "Long Version uploaded to Google Drive",
                extra={"file_id": long_file.get("id"), "url": long_drive_url},
            )

        # Save Long Version to database
        self._save_report_to_database(
            today_date, "long_version", long_content, long_drive_url
        )

        # 3. Generate Quick Version
        logger.info("Generating Quick Version report (5-page summary)")
        summarize_prompt = get_quick_version_prompt(long_content)

        quick_content = self.perplexity_client.generate_report(summarize_prompt)

        if quick_content:
            logger.info(
                "Quick Version content generated", extra={"content_length": len(quick_content)}
            )

            # Save Quick Version DOCX (使用 Pandoc 专业转换)
            quick_filename = f"Daily Briefing {today_str}_Quick Version.docx"
            quick_path = self.output_dir / quick_filename
            markdown_to_docx(
                quick_content,
                output_path=quick_path,
                title=f"Daily Briefing - {today_str} (Quick Version)",
            )

            logger.info("Quick Version DOCX saved", extra={"path": str(quick_path)})

            # Upload Quick Version to Google Drive
            quick_file = self.drive_service.upload_file(str(quick_path))
            quick_drive_url = ""
            if quick_file:
                quick_drive_url = quick_file.get("webViewLink", "")
                result_urls["quick_version"] = quick_drive_url
                logger.info(
                    "Quick Version uploaded to Google Drive",
                    extra={"file_id": quick_file.get("id"), "url": quick_drive_url},
                )

            # Save Quick Version to database
            self._save_report_to_database(
                today_date, "quick_version", quick_content, quick_drive_url
            )
        else:
            logger.warning("Failed to generate Quick Version, only Long Version available")

        logger.info(
            "Daily Briefing report generation completed",
            extra={"result_urls": result_urls, "date": today_str},
        )

        return result_urls

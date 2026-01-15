from datetime import datetime
from pathlib import Path

from docx import Document

from observability import get_logger

from ..prompts import get_daily_briefing_prompt, get_quick_version_prompt
from ..utils.markdown_converter import convert_markdown_to_word
from .google_drive import GoogleDriveService
from .google_sheets import GoogleSheetsService
from .perplexity_client import PerplexityClient

logger = get_logger(__name__)


class DailyBriefingService:
    """Service for generating Daily Briefing reports using AI"""

    def __init__(self):
        self.sheets_service = GoogleSheetsService()
        self.drive_service = GoogleDriveService()
        self.perplexity_client = PerplexityClient()
        self.output_dir = Path("/tmp/daily_briefing")  # Use temp dir in container
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict:
        """
        Run the report generation process.

        Workflow:
        1. Read data from Google Sheets
        2. Generate Long Version report using Perplexity AI
        3. Generate Quick Version (5-page summary) from Long Version
        4. Upload both versions to Google Drive

        Returns:
            Dictionary with result URLs for long_version and quick_version.

        Raises:
            ValueError: If data read or report generation fails.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        result_urls = {}

        logger.info("Starting Daily Briefing report generation")

        # 1. Authenticate and read data from Sheets
        self.sheets_service.authenticate()
        sheet_data = self.sheets_service.read_all_data()

        if not sheet_data:
            logger.error("Failed to read data from Google Sheets")
            raise ValueError("Failed to read data from Google Sheets")

        logger.info(
            "Google Sheets data loaded",
            extra={"data_length": len(sheet_data)}
        )

        # 2. Generate Long Version
        logger.info("Generating Long Version report with Perplexity AI")
        prompt = get_daily_briefing_prompt()
        full_prompt = prompt + f"\n\n[Additional Context from Google Sheets]:\n{sheet_data}\n"

        long_content = self.perplexity_client.generate_report(full_prompt)

        if not long_content:
            logger.error("Perplexity AI returned empty content for long report")
            raise ValueError("Failed to generate long report content")

        logger.info(
            "Long Version content generated",
            extra={"content_length": len(long_content)}
        )

        # Save Long Version DOCX
        long_filename = f"Daily Briefing {today}_Long Version.docx"
        long_path = self.output_dir / long_filename
        doc_long = Document()
        convert_markdown_to_word(long_content, doc_long)
        doc_long.save(long_path)

        logger.info(
            "Long Version DOCX saved",
            extra={"path": str(long_path)}
        )

        # Upload Long Version
        self.drive_service.authenticate()
        long_file = self.drive_service.upload_file(str(long_path))
        if long_file:
            result_urls["long_version"] = long_file.get("webViewLink")
            logger.info(
                "Long Version uploaded to Google Drive",
                extra={"file_id": long_file.get("id"), "url": result_urls["long_version"]}
            )

        # 3. Generate Quick Version
        logger.info("Generating Quick Version report (5-page summary)")
        summarize_prompt = get_quick_version_prompt(long_content)

        quick_content = self.perplexity_client.generate_report(summarize_prompt)

        if quick_content:
            logger.info(
                "Quick Version content generated",
                extra={"content_length": len(quick_content)}
            )

            # Save Quick Version DOCX
            quick_filename = f"Daily Briefing {today}_Quick Version.docx"
            quick_path = self.output_dir / quick_filename
            doc_quick = Document()
            convert_markdown_to_word(quick_content, doc_quick)
            doc_quick.save(quick_path)

            logger.info(
                "Quick Version DOCX saved",
                extra={"path": str(quick_path)}
            )

            # Upload Quick Version
            quick_file = self.drive_service.upload_file(str(quick_path))
            if quick_file:
                result_urls["quick_version"] = quick_file.get("webViewLink")
                logger.info(
                    "Quick Version uploaded to Google Drive",
                    extra={"file_id": quick_file.get("id"), "url": result_urls["quick_version"]}
                )
        else:
            logger.warning("Failed to generate Quick Version, only Long Version available")

        logger.info(
            "Daily Briefing report generation completed",
            extra={"result_urls": result_urls}
        )

        return result_urls

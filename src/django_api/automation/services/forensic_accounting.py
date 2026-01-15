from pathlib import Path

from docx import Document

from observability import get_logger

from ..prompts import get_forensic_accounting_prompt
from ..utils.markdown_converter import convert_markdown_to_word
from .perplexity_client import PerplexityClient
from .yahoo_finance import YahooFinanceService

logger = get_logger(__name__)


class ForensicAccountingService:
    """Service for generating Forensic Accounting reports"""

    def __init__(self):
        self.yahoo_service = YahooFinanceService()
        self.perplexity_client = PerplexityClient()
        self.output_dir = Path("/tmp/forensic_accounting")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_company(self, company_info: dict) -> str | None:
        """
        Process a single company and generate a forensic accounting report.

        Args:
            company_info: Dictionary with 'name' and 'ticker' keys.

        Returns:
            Path to the generated report file, or None on failure.
        """
        company_name = company_info.get("name")
        ticker = company_info.get("ticker")

        if not company_name or not ticker:
            logger.error(
                "Invalid company info provided",
                extra={"company_info": company_info}
            )
            return None

        logger.info(
            "Processing company for forensic accounting",
            extra={"company": company_name, "ticker": ticker}
        )

        # 1. Fetch stock data
        stock_data = self.yahoo_service.get_stock_data(ticker)

        price_str = str(stock_data["price"]) if stock_data["price"] else "N/A"
        market_cap_str = stock_data["market_cap_text"]
        currency_str = stock_data["currency"] or ""

        # 2. Generate report using prompt from prompts module
        prompt = get_forensic_accounting_prompt(
            company=company_name,
            ticker=ticker,
            price=price_str,
            market_cap=market_cap_str,
            currency=currency_str
        )

        logger.info(
            "Calling Perplexity API for forensic accounting report",
            extra={"company": company_name, "ticker": ticker}
        )

        content = self.perplexity_client.generate_report(prompt)

        if not content:
            logger.error(
                "Failed to generate forensic accounting report",
                extra={"company": company_name, "ticker": ticker}
            )
            return None

        # 3. Save as DOCX
        filename = f"FA - {company_name} ({ticker}).docx"
        file_path = self.output_dir / filename
        doc = Document()
        convert_markdown_to_word(content, doc)
        doc.save(file_path)

        logger.info(
            "Forensic accounting report saved",
            extra={
                "company": company_name,
                "ticker": ticker,
                "file_path": str(file_path),
                "content_length": len(content)
            }
        )
        return str(file_path)

    def run(self, companies: list[dict]) -> list[dict]:
        """
        Run forensic accounting for a list of companies.

        Args:
            companies: List of company dictionaries with 'name' and 'ticker' keys.

        Returns:
            List of result dictionaries with status for each company.
        """
        logger.info(
            "Starting forensic accounting batch process",
            extra={"company_count": len(companies)}
        )

        results = []
        for company in companies:
            try:
                report_path = self.process_company(company)
                if report_path:
                    results.append({
                        "company": company.get("name"),
                        "ticker": company.get("ticker"),
                        "status": "success",
                        "report_path": report_path
                    })
                else:
                    results.append({
                        "company": company.get("name"),
                        "ticker": company.get("ticker"),
                        "status": "failed"
                    })
            except Exception as e:
                logger.exception(
                    "Error processing company for forensic accounting",
                    extra={
                        "company": company.get("name"),
                        "ticker": company.get("ticker"),
                        "error": str(e)
                    }
                )
                results.append({
                    "company": company.get("name"),
                    "ticker": company.get("ticker"),
                    "status": "error",
                    "error": str(e)
                })

        success_count = len([r for r in results if r.get("status") == "success"])
        logger.info(
            "Forensic accounting batch process completed",
            extra={
                "total": len(companies),
                "success": success_count,
                "failed": len(companies) - success_count
            }
        )

        return results

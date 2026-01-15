import json
import os
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from observability import get_logger

logger = get_logger(__name__)


class GoogleSheetsService:
    """Service for interacting with Google Sheets API"""

    def __init__(self, credentials_json: str | dict | None = None):
        """
        Initialize the Google Sheets service.

        Args:
            credentials_json: Either a file path to the service account JSON,
                            a JSON string, or a dict containing credentials.
                            If None, reads from GOOGLE_SHEETS_CREDENTIALS_FILE env var.
        """
        self.credentials_json = credentials_json or os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
        self.client = None
        self.sheet = None
        self._authenticated = False

    def authenticate(self) -> bool:
        """
        Authenticate with Google Sheets API.

        Returns:
            True if authentication successful, False otherwise.
        """
        if self._authenticated and self.client and self.sheet:
            return True

        try:
            logger.info("Authenticating with Google Sheets API")

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]

            # Handle credentials from file path or JSON string/dict
            if isinstance(self.credentials_json, dict):
                # Already a dict
                creds = Credentials.from_service_account_info(self.credentials_json, scopes=scopes)
            elif isinstance(self.credentials_json, str):
                if os.path.exists(self.credentials_json):
                    # It's a file path
                    creds = Credentials.from_service_account_file(
                        self.credentials_json, scopes=scopes
                    )
                else:
                    # Try to find file relative to automation folder
                    automation_dir = Path(__file__).resolve().parents[3] / "automation"
                    creds_path = automation_dir / self.credentials_json

                    if creds_path.exists():
                        creds = Credentials.from_service_account_file(
                            str(creds_path), scopes=scopes
                        )
                    else:
                        # Try to parse as JSON string
                        try:
                            creds_dict = json.loads(self.credentials_json)
                            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                        except json.JSONDecodeError:
                            raise FileNotFoundError(
                                f"Credentials file not found: {self.credentials_json}"
                            )
            else:
                raise ValueError("No credentials provided for Google Sheets")

            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_key(self.spreadsheet_id).sheet1
            self._authenticated = True

            logger.info(
                "Google Sheets authentication successful",
                extra={"spreadsheet_id": self.spreadsheet_id},
            )
            return True

        except Exception as e:
            logger.exception("Google Sheets authentication failed", extra={"error": str(e)})
            return False

    def read_all_data(self) -> str | None:
        """
        Read all data from the sheet and format as a summary string.

        Returns:
            Formatted string with all sheet data, or None on failure.
        """
        try:
            if not self._authenticated:
                self.authenticate()

            logger.info("Reading all data from Google Sheets")

            all_values = self.sheet.get_all_values()

            # Format data as text (limit to first 50 rows)
            sheet_data = "Google Sheets Data Summary:\n\n"
            for i, row in enumerate(all_values[:50], 1):
                sheet_data += f"Row {i}: {' | '.join([str(cell) for cell in row])}\n"

            logger.info(
                "Google Sheets data read successfully",
                extra={"rows_read": len(all_values), "rows_included": min(50, len(all_values))},
            )

            return sheet_data

        except Exception as e:
            logger.exception("Failed to read data from Google Sheets", extra={"error": str(e)})
            return None

    def write_cell(self, cell: str, content: str, description: str = "") -> bool:
        """
        Write content to a specific cell.

        Args:
            cell: Cell reference (e.g., 'H2', 'I2').
            content: Content to write.
            description: Description for logging purposes.

        Returns:
            True if write successful, False otherwise.
        """
        try:
            if not self._authenticated:
                self.authenticate()

            if not self.sheet or not content:
                return False

            logger.info(
                "Writing to Google Sheets cell",
                extra={"cell": cell, "description": description, "content_length": len(content)},
            )

            self.sheet.update(range_name=cell, values=[[content]])

            logger.info(
                "Google Sheets write successful", extra={"cell": cell, "description": description}
            )
            return True

        except Exception as e:
            logger.exception(
                "Failed to write to Google Sheets", extra={"cell": cell, "error": str(e)}
            )
            return False

import os
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from observability import get_logger

logger = get_logger(__name__)


class GoogleDriveService:
    """Service for interacting with Google Drive API using OAuth 2.0"""

    def __init__(self):
        self.oauth_credentials_file = os.getenv(
            "GOOGLE_OAUTH_CREDENTIALS_FILE", "oauth_credentials.json"
        )
        self.token_file = os.getenv("GOOGLE_OAUTH_TOKEN_FILE", "oauth_token.pickle")
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        self.creds = None
        self._service = None

        # Resolve paths relative to automation folder
        self._automation_dir = Path(__file__).resolve().parents[3] / "automation"

    def _get_token_path(self) -> Path:
        """Get the full path to the token file."""
        if os.path.isabs(self.token_file):
            return Path(self.token_file)
        return self._automation_dir / self.token_file

    def _get_oauth_path(self) -> Path:
        """Get the full path to the OAuth credentials file."""
        if os.path.isabs(self.oauth_credentials_file):
            return Path(self.oauth_credentials_file)
        return self._automation_dir / self.oauth_credentials_file

    def authenticate(self) -> bool:
        """
        Get OAuth 2.0 credentials for Google Drive.

        Returns:
            True if authentication successful, False otherwise.
        """
        try:
            token_path = self._get_token_path()
            oauth_path = self._get_oauth_path()

            logger.info("Authenticating with Google Drive API")

            # Try to load from token file first
            if token_path.exists():
                with open(token_path, "rb") as token:
                    self.creds = pickle.load(token)
                logger.info("Loaded existing OAuth token")

            # If no valid credentials, authenticate
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing expired OAuth token")
                    self.creds.refresh(Request())
                else:
                    if not oauth_path.exists():
                        raise FileNotFoundError(
                            f"OAuth credentials file not found: {oauth_path}. "
                            "Please configure GOOGLE_OAUTH_CREDENTIALS_FILE."
                        )

                    logger.info("Starting OAuth flow - browser authorization required")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(oauth_path), scopes=["https://www.googleapis.com/auth/drive.file"]
                    )
                    self.creds = flow.run_local_server(port=0)
                    logger.info("OAuth authorization completed")

                # Save token for next use
                with open(token_path, "wb") as token:
                    pickle.dump(self.creds, token)
                logger.info("OAuth token saved", extra={"token_path": str(token_path)})

            # Create Drive service
            self._service = build("drive", "v3", credentials=self.creds)

            logger.info("Google Drive authentication successful")
            return True

        except Exception as e:
            logger.exception("Google Drive authentication failed", extra={"error": str(e)})
            return False

    def upload_file(self, file_path: str, folder_id: str | None = None) -> dict | None:
        """
        Upload a file to Google Drive using OAuth 2.0.

        Args:
            file_path: Path to the local file to upload.
            folder_id: Google Drive folder ID (optional, defaults to configured folder).

        Returns:
            Dictionary with file info (id, name, webViewLink), or None on failure.
        """
        try:
            if not self._service:
                if not self.authenticate():
                    return None

            folder_id = folder_id or self.folder_id
            filename = os.path.basename(file_path)

            logger.info(
                "Uploading file to Google Drive",
                extra={"filename": filename, "file_path": file_path, "folder_id": folder_id},
            )

            # File metadata
            file_metadata = {
                "name": filename,
            }

            # Set parent folder if specified
            if folder_id:
                file_metadata["parents"] = [folder_id]

            # Determine MIME type based on file extension
            mime_type = "application/octet-stream"
            if file_path.endswith(".docx"):
                mime_type = (
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            elif file_path.endswith(".pdf"):
                mime_type = "application/pdf"
            elif file_path.endswith(".xlsx"):
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            # Upload file
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

            file = (
                self._service.files()
                .create(body=file_metadata, media_body=media, fields="id, name, webViewLink")
                .execute()
            )

            logger.info(
                "File uploaded to Google Drive successfully",
                extra={
                    "file_id": file.get("id"),
                    "filename": file.get("name"),
                    "web_link": file.get("webViewLink"),
                },
            )

            return file

        except Exception as e:
            logger.exception(
                "Failed to upload file to Google Drive",
                extra={"file_path": file_path, "error": str(e)},
            )
            return None

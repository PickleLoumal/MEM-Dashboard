import io
import json
import os
import pickle
import tempfile
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from observability import get_logger

logger = get_logger(__name__)


class GoogleDriveService:
    """Service for interacting with Google Drive API using OAuth 2.0.

    Supports multiple credential and token sources:

    OAuth Credentials (in order of priority):
    1. GOOGLE_OAUTH_CREDENTIALS_JSON env var (JSON string from Secrets Manager)
    2. GOOGLE_OAUTH_CREDENTIALS_FILE env var (file path for local development)

    OAuth Token (in order of priority):
    1. S3 bucket (for ECS/production): s3://{OAUTH_TOKEN_S3_BUCKET}/{OAUTH_TOKEN_S3_KEY}
    2. Local file path: GOOGLE_OAUTH_TOKEN_FILE env var
    """

    DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    def __init__(self):
        # OAuth credentials (JSON string or file path)
        self.oauth_credentials_json = os.getenv("GOOGLE_OAUTH_CREDENTIALS_JSON")
        self.oauth_credentials_file = os.getenv(
            "GOOGLE_OAUTH_CREDENTIALS_FILE", "oauth_credentials.json"
        )

        # OAuth token storage
        self.token_s3_bucket = os.getenv("OAUTH_TOKEN_S3_BUCKET")
        self.token_s3_key = os.getenv("OAUTH_TOKEN_S3_KEY", "automation/oauth_token.pickle")
        self.token_file = os.getenv("GOOGLE_OAUTH_TOKEN_FILE", "oauth_token.pickle")

        # Google Drive folder
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

        self.creds = None
        self._service = None

        # Resolve paths relative to automation folder (for local development)
        self._automation_dir = Path(__file__).resolve().parents[3] / "automation"

        # S3 client (lazy initialization)
        self._s3_client = None

    @property
    def _s3(self):
        """Lazy-load S3 client."""
        if self._s3_client is None and self.token_s3_bucket:
            self._s3_client = boto3.client("s3")
        return self._s3_client

    def _get_token_path(self) -> Path:
        """Get the full path to the local token file."""
        if os.path.isabs(self.token_file):
            return Path(self.token_file)
        return self._automation_dir / self.token_file

    def _load_token_from_s3(self) -> bytes | None:
        """Load OAuth token from S3.

        Returns:
            Token bytes if found, None otherwise.
        """
        if not self.token_s3_bucket or not self._s3:
            return None

        try:
            logger.info(
                "Loading OAuth token from S3",
                extra={"bucket": self.token_s3_bucket, "key": self.token_s3_key},
            )
            response = self._s3.get_object(Bucket=self.token_s3_bucket, Key=self.token_s3_key)
            token_bytes = response["Body"].read()
            logger.info("OAuth token loaded from S3 successfully")
            return token_bytes
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.info("OAuth token not found in S3 (first run)")
            else:
                logger.warning("Failed to load OAuth token from S3", extra={"error": str(e)})
            return None

    def _save_token_to_s3(self, token_bytes: bytes) -> bool:
        """Save OAuth token to S3.

        Args:
            token_bytes: Pickled token bytes.

        Returns:
            True if saved successfully, False otherwise.
        """
        if not self.token_s3_bucket or not self._s3:
            return False

        try:
            logger.info(
                "Saving OAuth token to S3",
                extra={"bucket": self.token_s3_bucket, "key": self.token_s3_key},
            )
            self._s3.put_object(
                Bucket=self.token_s3_bucket,
                Key=self.token_s3_key,
                Body=token_bytes,
                ContentType="application/octet-stream",
            )
            logger.info("OAuth token saved to S3 successfully")
            return True
        except ClientError as e:
            logger.error("Failed to save OAuth token to S3", extra={"error": str(e)})
            return False

    def _load_token(self) -> UserCredentials | None:
        """Load OAuth token from S3 or local file.

        Returns:
            UserCredentials if token found and valid, None otherwise.
        """
        token_bytes = None

        # Priority 1: Try S3
        if self.token_s3_bucket:
            token_bytes = self._load_token_from_s3()

        # Priority 2: Try local file
        if token_bytes is None:
            token_path = self._get_token_path()
            if token_path.exists():
                logger.info("Loading OAuth token from local file", extra={"path": str(token_path)})
                with open(token_path, "rb") as f:
                    token_bytes = f.read()

        if token_bytes:
            try:
                return pickle.loads(token_bytes)
            except Exception as e:
                logger.warning("Failed to deserialize OAuth token", extra={"error": str(e)})

        return None

    def _save_token(self, creds: UserCredentials) -> None:
        """Save OAuth token to S3 and/or local file.

        Args:
            creds: OAuth credentials to save.
        """
        token_bytes = pickle.dumps(creds)

        # Save to S3 if configured
        if self.token_s3_bucket:
            self._save_token_to_s3(token_bytes)

        # Also save to local file (for local development and backup)
        token_path = self._get_token_path()
        try:
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, "wb") as f:
                f.write(token_bytes)
            logger.info("OAuth token saved to local file", extra={"path": str(token_path)})
        except Exception as e:
            logger.warning("Failed to save OAuth token to local file", extra={"error": str(e)})

    def _get_oauth_credentials_config(self) -> dict:
        """Get OAuth client configuration from JSON string or file.

        Returns:
            OAuth client configuration dict.

        Raises:
            ValueError: If no valid OAuth credentials can be found.
        """
        # Priority 1: JSON string from environment (Secrets Manager)
        if self.oauth_credentials_json:
            if self.oauth_credentials_json.strip().startswith("{"):
                try:
                    config = json.loads(self.oauth_credentials_json)
                    logger.info("Using OAuth credentials from JSON string (Secrets Manager)")
                    return config
                except json.JSONDecodeError as e:
                    logger.warning(
                        "Failed to parse GOOGLE_OAUTH_CREDENTIALS_JSON", extra={"error": str(e)}
                    )

        # Priority 2: File path
        oauth_path = None

        # Try absolute path
        if os.path.isabs(self.oauth_credentials_file) and os.path.exists(
            self.oauth_credentials_file
        ):
            oauth_path = Path(self.oauth_credentials_file)

        # Try relative path in current directory
        elif os.path.exists(self.oauth_credentials_file):
            oauth_path = Path(self.oauth_credentials_file)

        # Try relative to automation folder
        else:
            automation_path = self._automation_dir / self.oauth_credentials_file
            if automation_path.exists():
                oauth_path = automation_path

        if oauth_path:
            logger.info("Using OAuth credentials from file", extra={"path": str(oauth_path)})
            with open(oauth_path) as f:
                return json.load(f)

        raise ValueError(
            "No OAuth credentials found. "
            "Set GOOGLE_OAUTH_CREDENTIALS_JSON or GOOGLE_OAUTH_CREDENTIALS_FILE environment variable."
        )

    def authenticate(self) -> bool:
        """
        Get OAuth 2.0 credentials for Google Drive.

        Token storage priority:
        1. S3 bucket (if OAUTH_TOKEN_S3_BUCKET is set)
        2. Local file (GOOGLE_OAUTH_TOKEN_FILE)

        Returns:
            True if authentication successful, False otherwise.
        """
        try:
            logger.info("Authenticating with Google Drive API")

            # Try to load existing token
            self.creds = self._load_token()

            # Check if credentials need refresh or new authorization
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing expired OAuth token")
                    self.creds.refresh(Request())
                    self._save_token(self.creds)
                else:
                    # Need new authorization - this requires browser interaction
                    logger.info("Starting OAuth flow - browser authorization required")

                    oauth_config = self._get_oauth_credentials_config()

                    # Create a temporary file for the OAuth flow
                    # (InstalledAppFlow requires a file path)
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".json", delete=False
                    ) as tmp_file:
                        json.dump(oauth_config, tmp_file)
                        tmp_path = tmp_file.name

                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            tmp_path, scopes=self.DRIVE_SCOPES
                        )
                        self.creds = flow.run_local_server(port=0)
                        logger.info("OAuth authorization completed")
                        self._save_token(self.creds)
                    finally:
                        # Clean up temp file
                        os.unlink(tmp_path)

            # Create Drive service
            self._service = build("drive", "v3", credentials=self.creds)

            logger.info("Google Drive authentication successful")
            return True

        except ValueError as e:
            logger.error("Google Drive credential configuration error", extra={"error": str(e)})
            return False
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

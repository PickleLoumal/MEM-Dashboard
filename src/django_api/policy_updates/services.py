import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

import requests
from django.utils import timezone

logger = logging.getLogger(__name__)


class FederalRegisterServiceError(Exception):
    """Raised when the Federal Register API cannot fulfill a request."""


class FederalRegisterService:
    """
    Lightweight client for the official Federal Register API.
    Documentation: https://www.federalregister.gov/developers/documentation/api/v1
    """

    API_BASE = "https://www.federalregister.gov/api/v1/documents.json"
    DEFAULT_FIELDS = [
        "title",
        "abstract",
        "publication_date",
        "type",
        "html_url",
        "document_number",
        "topics",
        "agency_names",
        "agencies",
        "significant",
    ]
    DEFAULT_TYPES = ["RULE", "NOTICE", "PROPOSED_RULE"]
    MAX_LIMIT = 25

    def __init__(self, session: Optional[requests.Session] = None, timeout: int = 10) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.session.headers.setdefault(
            "User-Agent",
            "MEM Dashboard Policy Feed/1.0 (+https://mem-dashboard-alb-1995066194.ap-east-1.elb.amazonaws.com)",
        )

    def fetch_policy_updates(
        self,
        *,
        limit: int = 8,
        search: Optional[str] = None,
        topics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch recent policy-related documents from the Federal Register.
        """
        per_page = max(1, min(limit, self.MAX_LIMIT))
        start_date = (timezone.now() - timedelta(days=21)).date().isoformat()

        params: Dict[str, Any] = {
            "order": "newest",
            "per_page": per_page,
            "conditions[publication_date][gte]": start_date,
        }

        for doc_type in self.DEFAULT_TYPES:
            params.setdefault("conditions[type][]", [])
            params["conditions[type][]"].append(doc_type)

        params["fields[]"] = self.DEFAULT_FIELDS

        if search:
            params["conditions[term]"] = search

        if topics:
            for topic in topics:
                params.setdefault("conditions[topics][]", [])
                params["conditions[topics][]"].append(topic)

        logger.info("Requesting Federal Register updates: %s", params)

        try:
            response = self.session.get(self.API_BASE, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Federal Register request failed: %s", exc, exc_info=True)
            raise FederalRegisterServiceError("Unable to reach Federal Register API") from exc

        try:
            return response.json()
        except ValueError as exc:
            logger.error("Federal Register response was not valid JSON", exc_info=True)
            raise FederalRegisterServiceError("Invalid response from Federal Register API") from exc

    def normalize_documents(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert the Federal Register payload into the structure expected by the dashboard.
        """
        normalized: List[Dict[str, Any]] = []
        results = payload.get("results") or []

        for doc in results:
            title = doc.get("title") or "Untitled Policy Signal"
            summary = (doc.get("abstract") or "").strip()
            if not summary:
                summary = "No summary provided by the Federal Register."

            publication_date = doc.get("publication_date")
            impact_level = "high" if doc.get("significant") else "medium"
            status = "active" if doc.get("significant") else "watching"

            tags = self._extract_tags(doc)
            source = self._extract_source(doc)

            normalized.append(
                {
                    "title": title,
                    "summary": summary,
                    "category": doc.get("type") or "Policy",
                    "impact_level": impact_level,
                    "status": status,
                    "tags": tags,
                    "source": source,
                    "timestamp": publication_date,
                    "link": doc.get("html_url"),
                    "document_number": doc.get("document_number"),
                }
            )

        return normalized

    @staticmethod
    def _extract_tags(document: Dict[str, Any]) -> List[str]:
        tags: List[str] = []

        if document.get("topics"):
            tags.extend([topic for topic in document["topics"] if topic])

        agencies = document.get("agencies") or []
        tags.extend([agency.get("name") for agency in agencies if agency.get("name")])

        # Deduplicate while preserving order
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        return unique_tags[:6]

    @staticmethod
    def _extract_source(document: Dict[str, Any]) -> str:
        agency_names = document.get("agency_names") or []
        if agency_names:
            return agency_names[0]

        agencies = document.get("agencies") or []
        for agency in agencies:
            if agency.get("name"):
                return agency["name"]

        return "Federal Register"

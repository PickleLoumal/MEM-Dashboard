import logging
from typing import List

from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import FederalRegisterService, FederalRegisterServiceError

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 60 * 5  # five minutes


@api_view(["GET"])
def policy_updates(request):
    """
    Serve curated policy updates sourced from the Federal Register API.
    """
    country = (request.query_params.get("country") or "us").lower()
    try:
        limit = int(request.query_params.get("limit", 8))
    except ValueError:
        limit = 8

    topics_param: List[str] = request.query_params.getlist("topics[]") or request.query_params.getlist("topics") or []
    search_term = request.query_params.get("q")

    cache_key = f"policy_updates_{country}_{limit}_{'_'.join(sorted(topics_param))}_{search_term or 'none'}"
    cached_payload = cache.get(cache_key)
    if cached_payload:
        return Response(cached_payload)

    service = FederalRegisterService()

    try:
        raw_payload = service.fetch_policy_updates(limit=limit, search=search_term, topics=topics_param)
        normalized_documents = service.normalize_documents(raw_payload)
    except FederalRegisterServiceError as exc:
        logger.error("Failed to retrieve Federal Register updates: %s", exc, exc_info=True)
        return Response(
            {
                "success": False,
                "message": str(exc),
                "source": "Federal Register",
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    response_payload = {
        "success": True,
        "source": "Federal Register",
        "country": country.upper(),
        "last_updated": timezone.now().isoformat(),
        "count": len(normalized_documents),
        "data": normalized_documents,
    }

    cache.set(cache_key, response_payload, CACHE_TTL_SECONDS)
    return Response(response_payload)

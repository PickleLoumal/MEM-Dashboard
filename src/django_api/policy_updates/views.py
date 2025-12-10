import logging

from django.core.cache import cache
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import FederalRegisterService, FederalRegisterServiceError

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 60 * 5  # five minutes


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="country",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Country code",
            required=False,
        ),
        OpenApiParameter(
            name="limit",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Number of results",
            required=False,
        ),
        OpenApiParameter(
            name="topics[]",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Topic filters",
            required=False,
        ),
        OpenApiParameter(
            name="q",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Search term",
            required=False,
        ),
    ],
    responses={
        200: inline_serializer(
            name="PolicyUpdatesResponse",
            fields={
                "success": drf_serializers.BooleanField(),
                "source": drf_serializers.CharField(),
                "country": drf_serializers.CharField(),
                "last_updated": drf_serializers.CharField(),
                "count": drf_serializers.IntegerField(),
                "data": drf_serializers.ListField(child=drf_serializers.DictField()),
                "message": drf_serializers.CharField(required=False),
            },
        )
    },
)
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

    topics_param: list[str] = (
        request.query_params.getlist("topics[]") or request.query_params.getlist("topics") or []
    )
    search_term = request.query_params.get("q")

    cache_key = (
        f"policy_updates_{country}_{limit}_{'_'.join(sorted(topics_param))}_{search_term or 'none'}"
    )
    cached_payload = cache.get(cache_key)
    if cached_payload:
        return Response(cached_payload)

    service = FederalRegisterService()

    try:
        raw_payload = service.fetch_policy_updates(
            limit=limit, search=search_term, topics=topics_param
        )
        normalized_documents = service.normalize_documents(raw_payload)
    except FederalRegisterServiceError as exc:
        logger.exception("Failed to retrieve Federal Register updates")
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

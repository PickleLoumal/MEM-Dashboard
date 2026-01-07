"""
OpenAPI Schema Preprocessing and Postprocessing Hooks

These hooks customize the OpenAPI schema generation to produce cleaner
TypeScript service classes via openapi-typescript-codegen.

Key customizations:
- Tag endpoints by Django app name (csi300, fred_us, pdf_service, etc.)
- This generates separate service classes: Csi300Service, FredUsService, PdfService
- Instead of one giant ApiService with all endpoints
"""

from typing import Any

# Mapping of URL prefixes to tag names
# These tags determine the generated TypeScript service class names
URL_PREFIX_TO_TAG = {
    "/api/csi300/": "csi300",
    "/api/fred-us/": "fred_us",
    "/api/fred-jp/": "fred_jp",
    "/api/fred/": "fred_us",  # Legacy route maps to fred_us
    "/api/bea/": "bea",
    "/api/stocks/": "stocks",
    "/api/pdf/": "pdf",
    "/api/policy/": "policy",
    "/api/refinitiv/": "refinitiv",
    "/api/content/": "content",
}


def preprocess_schema(endpoints: list[tuple[str, str, str, Any]]) -> list[tuple[str, str, str, Any]]:
    """
    Preprocess OpenAPI endpoints before schema generation.

    This hook runs before drf-spectacular generates the schema.
    We use it to filter or modify endpoints if needed.

    Args:
        endpoints: List of (path, path_regex, method, callback) tuples

    Returns:
        Modified list of endpoints
    """
    # Currently no preprocessing needed, but hook is available for future use
    return endpoints


def postprocess_schema(result: dict[str, Any], generator: Any, request: Any, public: bool) -> dict[str, Any]:
    """
    Postprocess the generated OpenAPI schema.

    This hook runs after drf-spectacular generates the schema.
    We use it to reassign tags based on URL prefixes.

    Args:
        result: The generated OpenAPI schema dict
        generator: The schema generator instance
        request: The HTTP request (if any)
        public: Whether this is a public schema

    Returns:
        Modified OpenAPI schema
    """
    paths = result.get("paths", {})

    for path, methods in paths.items():
        # Determine the appropriate tag based on URL prefix
        new_tag = None
        for prefix, tag in URL_PREFIX_TO_TAG.items():
            if path.startswith(prefix):
                new_tag = tag
                break

        # If no specific tag found, use 'api' as default
        if new_tag is None:
            if path.startswith("/api/"):
                new_tag = "api"
            else:
                continue  # Skip non-API paths

        # Update tags for all HTTP methods on this path
        for method, operation in methods.items():
            if isinstance(operation, dict) and "tags" in operation:
                operation["tags"] = [new_tag]

    return result


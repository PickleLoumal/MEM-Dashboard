import os
import re
import time

import requests

from observability import get_logger

logger = get_logger(__name__)


class PerplexityClient:
    """
    Client for Perplexity AI API.

    Uses the Sonar Deep Research model for comprehensive financial analysis.
    Requires PERPLEXITY_API_KEY environment variable.
    """

    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.api_url = os.getenv("PERPLEXITY_API_URL", "https://api.perplexity.ai/chat/completions")

        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable is not set")

    def generate_report(
        self,
        prompt: str,
        model: str = "sonar-deep-research",
        max_retries: int = 3,
        timeout: int = 3600,
    ) -> str | None:
        """
        Generate a report using Perplexity AI API.

        Args:
            prompt: The prompt to send to the API.
            model: The model to use (default: sonar-deep-research).
            max_retries: Maximum number of retry attempts.
            timeout: Request timeout in seconds (default: 1 hour for deep research).

        Returns:
            The generated content as a string, or None on failure.

        Raises:
            Exception: If all retry attempts fail.
        """
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a highly intelligent AI financial analyst with deep research capabilities.",
                },
                {"role": "user", "content": prompt},
            ],
        }

        for attempt in range(max_retries):
            try:
                logger.info(
                    "Calling Perplexity API",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                        "model": model,
                        "prompt_length": len(prompt),
                    },
                )

                response = requests.post(self.api_url, headers=headers, json=data, timeout=timeout)
                response.raise_for_status()
                result = response.json()

                if result and "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    # Remove <think> tags if present (internal reasoning)
                    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)

                    logger.info(
                        "Perplexity API call successful",
                        extra={"response_length": len(content), "model": model},
                    )
                    return content.strip()
                raise ValueError("Invalid API response format: missing 'choices' field")

            except requests.Timeout:
                logger.warning(
                    "Perplexity API request timed out",
                    extra={"attempt": attempt + 1, "timeout_seconds": timeout},
                )
                if attempt < max_retries - 1:
                    backoff_time = 30 * (attempt + 1)
                    logger.info(f"Retrying after {backoff_time} seconds")
                    time.sleep(backoff_time)
                else:
                    logger.error("Max retries exceeded due to timeouts")
                    raise

            except requests.HTTPError as e:
                logger.warning(
                    "Perplexity API HTTP error",
                    extra={
                        "attempt": attempt + 1,
                        "status_code": e.response.status_code if e.response else None,
                        "error": str(e),
                    },
                )
                if attempt < max_retries - 1:
                    backoff_time = 10 * (attempt + 1)
                    time.sleep(backoff_time)
                else:
                    logger.error("Max retries exceeded for Perplexity API")
                    raise

            except Exception as e:
                logger.exception(
                    "Perplexity API call failed", extra={"attempt": attempt + 1, "error": str(e)}
                )
                if attempt < max_retries - 1:
                    backoff_time = 10 * (attempt + 1)
                    time.sleep(backoff_time)
                else:
                    logger.error("Max retries exceeded for Perplexity API")
                    raise

        return None

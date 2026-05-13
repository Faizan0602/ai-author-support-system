import json
import logging
from typing import Any, Dict

from pydantic import BaseModel, Field, ValidationError

from app.ai.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class ClassificationResponse(BaseModel):
    """
    Structured query classification response.
    """

    intent: str = Field(...)

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )

    extracted_entities: Dict[str, Any] = Field(
        default_factory=dict
    )


class QueryClassifier:
    """
    AI-powered author query classifier.
    """

    SUPPORTED_INTENTS = [
        "publication_status",
        "royalty_query",
        "dashboard_access",
        "add_on_status",
        "book_sales",
        "author_copy_status",
        "unknown",
    ]

    def __init__(self, ai_service: GeminiService):
        self.ai_service = ai_service

    def _build_prompt(self, query: str) -> str:
        """
        Build strict classification prompt.
        """

        intents = ", ".join(self.SUPPORTED_INTENTS)

        return f"""
You are an AI intent classification engine for an Author Support platform.

Your task is to classify user queries into ONE valid intent.

VALID INTENTS:
[{intents}]

RULES:
1. Return ONLY valid raw JSON.
2. No markdown.
3. No explanation text.
4. confidence must be between 0 and 1.
5. extracted_entities must always be an object.
6. If uncertain, return "unknown".

RESPONSE FORMAT:
{{
    "intent": "string",
    "confidence": 0.95,
    "extracted_entities": {{
        "book_title": "optional value"
    }}
}}

USER QUERY:
"{query}"
"""

    async def classify_query(
        self,
        query: str,
    ) -> ClassificationResponse:
        """
        Classify author support query.
        """

        if not query.strip():
            return self._fallback_response()

        prompt = self._build_prompt(query)

        try:
            raw_response = await self.ai_service.generate_response(
                prompt=prompt,
                temperature=0.1,
            )

            cleaned_response = (
                raw_response.strip()
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            parsed_data = json.loads(cleaned_response)

            validated_response = ClassificationResponse(
                **parsed_data
            )

            if validated_response.intent not in self.SUPPORTED_INTENTS:
                logger.warning(
                    f"Invalid intent received: {validated_response.intent}"
                )

                return self._fallback_response()

            return validated_response

        except json.JSONDecodeError:
            logger.exception("JSON parsing failed")

            return self._fallback_response()

        except ValidationError:
            logger.exception("Pydantic validation failed")

            return self._fallback_response()

        except Exception:
            logger.exception("Unexpected classifier error")

            return self._fallback_response()

    def _fallback_response(self) -> ClassificationResponse:
        """
        Safe fallback classification.
        """

        return ClassificationResponse(
            intent="unknown",
            confidence=0.0,
            extracted_entities={},
        )
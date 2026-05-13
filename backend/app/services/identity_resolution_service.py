import difflib
import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.services.author_service import AuthorService

logger = logging.getLogger(__name__)


class IdentityResolutionResponse(BaseModel):
    """
    Identity resolution result structure.
    """

    matched: bool

    confidence: float

    matched_author: Dict[str, Any] = Field(
        default_factory=dict
    )

    escalation_required: bool


class IdentityResolutionService:
    """
    AI-style fuzzy identity resolution engine.
    """

    ESCALATION_THRESHOLD = 0.85
    MINIMUM_MATCH_THRESHOLD = 0.40

    def __init__(
        self,
        author_service: AuthorService,
    ):
        self.author_service = author_service

    async def resolve_author_identity(
        self,
        identifier: str,
    ) -> IdentityResolutionResponse:
        """
        Resolve author identity using
        exact and fuzzy matching.
        """

        normalized_identifier = (
            identifier.strip().lower()
        )

        if not normalized_identifier:
            return self._fallback_response()

        logger.info(
            f"Resolving identity for: {normalized_identifier}"
        )

        try:
            # =========================
            # Exact email match
            # =========================

            exact_match = (
                self.author_service.get_author_by_email(
                    normalized_identifier
                )
            )

            if exact_match:
                return IdentityResolutionResponse(
                    matched=True,
                    confidence=1.0,
                    matched_author=exact_match,
                    escalation_required=False,
                )

            # =========================
            # Fuzzy matching
            # =========================

            authors = self._fetch_all_authors()

            best_match = None
            best_confidence = 0.0

            for author in authors:
                confidence = self._calculate_similarity(
                    normalized_identifier,
                    author,
                )

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = author

            if (
                best_match
                and best_confidence
                >= self.MINIMUM_MATCH_THRESHOLD
            ):
                escalation_required = (
                    best_confidence
                    < self.ESCALATION_THRESHOLD
                )

                return IdentityResolutionResponse(
                    matched=True,
                    confidence=round(
                        best_confidence,
                        2,
                    ),
                    matched_author=best_match,
                    escalation_required=escalation_required,
                )

            return IdentityResolutionResponse(
                matched=False,
                confidence=round(
                    best_confidence,
                    2,
                ),
                matched_author={},
                escalation_required=True,
            )

        except Exception:
            logger.exception(
                "Identity resolution failed"
            )

            return self._fallback_response()

    def _fetch_all_authors(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Fetch all authors safely.
        """

        response = (
            self.author_service.db
            .table("authors")
            .select("*")
            .execute()
        )

        return response.data

    def _calculate_similarity(
        self,
        identifier: str,
        author: Dict[str, Any],
    ) -> float:
        """
        Calculate best fuzzy similarity score.
        """

        email = (
            author.get("email", "")
            .strip()
            .lower()
        )

        author_name = (
            author.get("author_name", "")
            .strip()
            .lower()
        )

        email_score = difflib.SequenceMatcher(
            None,
            identifier,
            email,
        ).ratio()

        name_score = difflib.SequenceMatcher(
            None,
            identifier,
            author_name,
        ).ratio()

        return max(
            email_score,
            name_score,
        )

    def _fallback_response(
        self,
    ) -> IdentityResolutionResponse:
        """
        Safe fallback response.
        """

        return IdentityResolutionResponse(
            matched=False,
            confidence=0.0,
            matched_author={},
            escalation_required=True,
        )
import json
import logging
from typing import Any, Dict

from pydantic import BaseModel, Field

from app.ai.gemini_service import GeminiService
from app.services.author_service import AuthorService
from app.services.conversation_logger_service import (
    ConversationLoggerService,
)
from app.services.knowledge_base_service import (
    KnowledgeBaseService,
)
from app.services.query_classifier import QueryClassifier

logger = logging.getLogger(__name__)


class QueryResolutionResponse(BaseModel):
    """
    Final workflow response structure.
    """

    intent: str
    confidence: float
    response: str
    escalation_required: bool

    retrieved_data: Dict[str, Any] = Field(
        default_factory=dict
    )


class QueryResolutionService:
    """
    Intelligent AI-powered author support workflow engine.
    """

    ESCALATION_THRESHOLD = 0.80
    DB_CONTEXT_KEYS = (
        "books",
        "royalties",
        "add_on_services",
    )
    INTENT_KEYWORDS = {
        "publication_status": (
            "book",
            "live",
            "publish",
            "published",
            "publishing",
            "status",
        ),
        "book_sales": (
            "book",
            "copies",
            "sale",
            "sales",
            "sold",
        ),
        "author_copy_status": (
            "author",
            "copy",
            "courier",
            "delivery",
            "order",
            "ship",
            "shipped",
            "tracking",
        ),
        "royalty_query": (
            "earning",
            "payment",
            "payout",
            "royalties",
            "royalty",
        ),
        "add_on_status": (
            "add-on",
            "addon",
            "bestseller",
            "distribution",
            "package",
            "service",
        ),
        "dashboard_access": (
            "dashboard",
            "login",
            "password",
            "portal",
        ),
    }

    def __init__(
        self,
        classifier: QueryClassifier,
        author_service: AuthorService,
        ai_service: GeminiService,
        conversation_logger: ConversationLoggerService,
        knowledge_base: KnowledgeBaseService,
    ):
        self.classifier = classifier
        self.author_service = author_service
        self.ai_service = ai_service
        self.conversation_logger = conversation_logger
        self.knowledge_base = knowledge_base

    async def resolve_query(
        self,
        query: str,
        author_email: str,
    ) -> QueryResolutionResponse:
        """
        Resolve author support query end-to-end.
        """

        logger.info(
            f"Resolving query for author: {author_email}"
        )

        try:
            classification = await self.classifier.classify_query(
                query
            )

            intent = classification.intent
            confidence = classification.confidence

            retrieved_data: Dict[str, Any] = {}

            # =========================
            # Knowledge Base Retrieval
            # =========================

            kb_context = (
                self.knowledge_base.build_context(
                    query=query
                )
            )

            has_kb_result = bool(kb_context)

            if kb_context:
                retrieved_data[
                    "knowledge_base"
                ] = kb_context

            # =========================
            # Fetch Author
            # =========================

            author = self.author_service.get_author_by_email(
                author_email
            )

            if not author:
                if has_kb_result:
                    response_text = await self._generate_response(
                        query=query,
                        intent=intent,
                        context=retrieved_data,
                    )

                    await self.conversation_logger.log_conversation(
                        author_email=author_email,
                        user_query=query,
                        detected_intent=intent,
                        confidence_score=confidence,
                        ai_response=response_text,
                        escalation_required=False,
                    )

                    return QueryResolutionResponse(
                        intent=intent,
                        confidence=confidence,
                        response=response_text,
                        escalation_required=False,
                        retrieved_data=retrieved_data,
                    )

                response_text = (
                    "Author account not found. "
                    "Human support escalation triggered."
                )

                await self.conversation_logger.log_conversation(
                    author_email=author_email,
                    user_query=query,
                    detected_intent=intent,
                    confidence_score=confidence,
                    ai_response=response_text,
                    escalation_required=True,
                )

                return self._build_escalation_response(
                    intent=intent,
                    confidence=confidence,
                    message=response_text,
                )

            retrieved_data["author"] = author

            author_id = author["id"]

            # =========================
            # Fetch DB Context
            # =========================

            retrieved_data = self._fetch_context_data(
                intent=intent,
                author_id=author_id,
                context=retrieved_data,
            )

            # =========================
            # Escalation Decision
            # =========================

            escalation_required = self._should_escalate(
                query=query,
                intent=intent,
                confidence=confidence,
                has_kb_result=has_kb_result,
                retrieved_data=retrieved_data,
            )

            # =========================
            # Generate Final Response
            # =========================

            if escalation_required:
                response_text = (
                    "Your request has been escalated "
                    "to our support team for further assistance."
                )

            else:
                response_text = await self._generate_response(
                    query=query,
                    intent=intent,
                    context=retrieved_data,
                )

            # =========================
            # Log Conversation
            # =========================

            await self.conversation_logger.log_conversation(
                author_email=author_email,
                user_query=query,
                detected_intent=intent,
                confidence_score=confidence,
                ai_response=response_text,
                escalation_required=escalation_required,
            )

            return QueryResolutionResponse(
                intent=intent,
                confidence=confidence,
                response=response_text,
                escalation_required=escalation_required,
                retrieved_data=retrieved_data,
            )

        except Exception as e:
            logger.exception(
                "Query resolution workflow failed"
            )

            await self.conversation_logger.log_conversation(
                author_email=author_email,
                user_query=query,
                detected_intent="unknown",
                confidence_score=0.0,
                ai_response="System failure occurred.",
                escalation_required=True,
            )

            return self._build_escalation_response(
                intent="unknown",
                confidence=0.0,
                message=(
                    "System error occurred while "
                    "processing request."
                ),
                extra_data={
                    "system_error": str(e)
                },
            )

    def _should_escalate(
        self,
        query: str,
        intent: str,
        confidence: float,
        has_kb_result: bool,
        retrieved_data: Dict[str, Any],
    ) -> bool:
        """
        Determine escalation requirement.

        Escalate only when:
        - no KB answer exists
        - no DB workflow context exists
        - classifier result has no grounded context to answer from
        """

        if has_kb_result:
            return False

        if (
            self._has_db_context(retrieved_data)
            and self._has_intent_signal(
                query=query,
                intent=intent,
            )
        ):
            return False

        return True

    def _has_db_context(
        self,
        retrieved_data: Dict[str, Any],
    ) -> bool:
        """
        Check whether an intent-specific DB workflow supplied context.
        """

        return any(
            key in retrieved_data
            for key in self.DB_CONTEXT_KEYS
        )

    def _has_intent_signal(
        self,
        query: str,
        intent: str,
    ) -> bool:
        """
        Confirm the query text contains words related to the DB workflow.
        """

        keywords = self.INTENT_KEYWORDS.get(intent, ())
        normalized_query = query.lower()

        return any(
            keyword in normalized_query
            for keyword in keywords
        )

    def _fetch_context_data(
        self,
        intent: str,
        author_id: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Fetch contextual DB data dynamically.
        """

        try:
            if intent in [
                "publication_status",
                "book_sales",
                "author_copy_status",
            ]:
                context["books"] = (
                    self.author_service.get_books_by_author(
                        author_id
                    )
                )

            elif intent == "royalty_query":
                context["royalties"] = (
                    self.author_service.get_royalty_info(
                        author_id
                    )
                )

            elif intent == "add_on_status":
                context["add_on_services"] = (
                    self.author_service.get_add_on_services(
                        author_id
                    )
                )

        except Exception as e:
            logger.exception(
                "Context data fetch failed"
            )

            context["data_warning"] = str(e)

        return context

    async def _generate_response(
        self,
        query: str,
        intent: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Generate grounded contextual AI response.
        """

        prompt = f"""
You are a professional AI Author Support Assistant.

Answer ONLY using the provided database context
and knowledge base context.

USER QUERY:
{query}

INTENT:
{intent}

CONTEXT DATA:
{json.dumps(context, default=str)}

RULES:
1. Be professional and concise.
2. Do not hallucinate information.
3. Use only provided context.
4. Do not expose technical fields or IDs.
5. If information is unavailable, clearly say so.
6. Use KB information if relevant.
7. If KB contains answer, answer naturally.
8. If context cannot answer, say the information is unavailable.
"""

        fallback_response = (
            self._format_knowledge_base_response(
                context["knowledge_base"]
            )
            if context.get("knowledge_base")
            else (
                "I'm unable to generate an AI response right now. "
                "Your request has been escalated to our support team "
                "for further assistance."
            )
        )

        return await self.ai_service.generate_response(
            prompt=prompt.strip(),
            temperature=0.2,
            fallback_response=fallback_response,
        )

    def _format_knowledge_base_response(
        self,
        kb_context: str,
    ) -> str:
        """
        Return a deterministic FAQ answer without spending Gemini quota.
        """

        paragraphs = [
            paragraph.strip()
            for paragraph in kb_context.split("\n\n")
            if paragraph.strip()
        ]

        if not paragraphs:
            return (
                "I found this in our knowledge base, but couldn't "
                "format the details clearly. Please contact support "
                "for the exact information."
            )

        answer = paragraphs[0]

        if len(answer) > 1200:
            answer = f"{answer[:1200].rstrip()}..."

        return answer

    def _build_escalation_response(
        self,
        intent: str,
        confidence: float,
        message: str,
        extra_data: Dict[str, Any] | None = None,
    ) -> QueryResolutionResponse:
        """
        Safe escalation response builder.
        """

        return QueryResolutionResponse(
            intent=intent,
            confidence=confidence,
            response=message,
            escalation_required=True,
            retrieved_data=extra_data or {},
        )

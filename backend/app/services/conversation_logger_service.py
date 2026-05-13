import logging

from supabase import Client

logger = logging.getLogger(__name__)


class ConversationLoggerService:
    """
    Service for logging AI support conversations.
    """

    def __init__(
        self,
        db: Client,
    ):
        self.db = db

    async def log_conversation(
        self,
        author_email: str,
        user_query: str,
        detected_intent: str,
        confidence_score: float,
        ai_response: str,
        escalation_required: bool,
    ) -> bool:
        """
        Persist conversation safely.
        """

        payload = {
            "author_email": author_email,
            "user_query": user_query,
            "detected_intent": detected_intent,
            "confidence_score": confidence_score,
            "ai_response": ai_response,
            "escalation_required": escalation_required,
        }

        try:
            logger.info(
                f"Logging conversation for {author_email}"
            )

            response = (
                self.db
                .table("support_conversations")
                .insert(payload)
                .execute()
            )

            if response.data:
                logger.info(
                    "Conversation logged successfully"
                )

                return True

            logger.warning(
                "Conversation insert returned empty response"
            )

            return False

        except Exception:
            logger.exception(
                "Conversation logging failed"
            )

            # Never crash primary workflow
            return False
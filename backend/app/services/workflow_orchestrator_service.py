import logging
import uuid
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.services.identity_resolution_service import IdentityResolutionService
from app.services.query_resolution_service import QueryResolutionService

# Configure module-level logger
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Enums and Pydantic Schemas
# -----------------------------------------------------------------------------
class SourceChannel(str, Enum):
    """Supported communication channels for the automation platform."""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    DASHBOARD_CHAT = "dashboard_chat"

class ProcessingStatus(str, Enum):
    """Tracks the lifecycle outcome of the workflow."""
    SUCCESS = "success"
    ESCALATED = "escalated"
    FAILED = "failed"
    UNAUTHORIZED = "unauthorized"

class WorkflowRequest(BaseModel):
    """Input payload representing an incoming automation trigger."""
    source_channel: SourceChannel = Field(..., description="The channel origin of the query.")
    author_identifier: str = Field(..., description="The incoming identifier (email, phone, handle, or name).")
    user_query: str = Field(..., description="The raw natural language query.")

class WorkflowResponse(BaseModel):
    """Structured unified output of the fully orchestrated workflow."""
    workflow_id: str = Field(..., description="Unique tracking ID for this execution run.")
    source_channel: SourceChannel = Field(..., description="The origin channel.")
    matched_author: Dict[str, Any] = Field(default_factory=dict, description="Resolved author properties, if found.")
    intent: str = Field(..., description="Classified intent. Might be 'unverified' if identity check failed.")
    confidence: float = Field(..., description="Overall confidence score.")
    escalation_required: bool = Field(..., description="True if human intervention is needed.")
    processing_status: ProcessingStatus = Field(..., description="The final state of this workflow run.")
    final_response: str = Field(..., description="The formatted contextual response to send back to the user.")

# -----------------------------------------------------------------------------
# Orchestration Service
# -----------------------------------------------------------------------------
class WorkflowOrchestratorService:
    """
    Enterprise automation orchestrator. Coordinates identity resolution, query 
    classification, and generative response formulation while routing logic
    specific to the simulated communication channel.
    """

    def __init__(
        self, 
        identity_service: IdentityResolutionService, 
        query_service: QueryResolutionService
    ):
        """
        Initializes the orchestrator with required domain services via dependency injection.
        """
        self.identity_service = identity_service
        self.query_service = query_service

    async def run_workflow(self, request: WorkflowRequest) -> WorkflowResponse:
        """
        Executes the end-to-end multi-channel automation workflow.
        
        Args:
            request (WorkflowRequest): The incoming cross-channel trigger.
            
        Returns:
            WorkflowResponse: Unified execution outcome containing data and routing info.
        """
        workflow_id = str(uuid.uuid4())
        logger.info(
            f"[Workflow {workflow_id}] Orchestrating new {request.source_channel.value} "
            f"query for identifier: {request.author_identifier}"
        )
        
        try:
            # 1. Resolve Identity
            identity_res = await self.identity_service.resolve_author_identity(request.author_identifier)
            
            # Fast-fail or Escalate on Unauthorized/Unverified accounts
            if not identity_res.matched or identity_res.escalation_required:
                kb_context = self.query_service.knowledge_base.build_context(
                    request.user_query
                )

                if kb_context:
                    logger.info(
                        f"[Workflow {workflow_id}] Identity unverified, "
                        "but KB answer found. Handling as FAQ."
                    )

                    query_res = await self.query_service.resolve_query(
                        query=request.user_query,
                        author_email=request.author_identifier,
                    )

                    final_formatted_response = self._apply_channel_formatting(
                        base_response=query_res.response,
                        channel=request.source_channel,
                    )
                    escalation = query_res.escalation_required
                    status = (
                        ProcessingStatus.ESCALATED
                        if escalation
                        else ProcessingStatus.SUCCESS
                    )

                    return WorkflowResponse(
                        workflow_id=workflow_id,
                        source_channel=request.source_channel,
                        matched_author=identity_res.matched_author or {
                            "provided_identifier": request.author_identifier
                        },
                        intent=query_res.intent,
                        confidence=query_res.confidence,
                        escalation_required=escalation,
                        processing_status=status,
                        final_response=final_formatted_response
                    )

                logger.warning(f"[Workflow {workflow_id}] Identity unverified. Escalating.")
                return self._build_unauthorized_response(
                    workflow_id=workflow_id,
                    channel=request.source_channel,
                    identifier=request.author_identifier
                )

            # Extract the actual verified email required for the query resolver
            verified_email = identity_res.matched_author.get("email")
            if not verified_email:
                raise ValueError("Matched author profile is missing a primary email address.")
                
            # 2. Resolve Query Context and Generate Base Response
            query_res = await self.query_service.resolve_query(
                query=request.user_query, 
                author_email=verified_email
            )
            
            # 3. Simulate Channel-Specific Enhancements & Formatting
            final_formatted_response = self._apply_channel_formatting(
                base_response=query_res.response,
                channel=request.source_channel
            )
            
            # 4. Construct unified outcome state
            escalation = query_res.escalation_required
            status = ProcessingStatus.ESCALATED if escalation else ProcessingStatus.SUCCESS
            
            logger.info(f"[Workflow {workflow_id}] Executed successfully. Status: {status.name}")

            return WorkflowResponse(
                workflow_id=workflow_id,
                source_channel=request.source_channel,
                matched_author=identity_res.matched_author,
                intent=query_res.intent,
                confidence=query_res.confidence,
                escalation_required=escalation,
                processing_status=status,
                final_response=final_formatted_response
            )

        except Exception as e:
            logger.error(f"[Workflow {workflow_id}] Workflow crash: {str(e)}", exc_info=True)
            return self._build_failed_response(
                workflow_id=workflow_id, 
                channel=request.source_channel,
                error_msg=str(e)
            )

    def _apply_channel_formatting(self, base_response: str, channel: SourceChannel) -> str:
        """
        Simulates multi-channel formatting constraints.
        (e.g., adding line breaks for email, avoiding Markdown for WhatsApp, etc.)
        """
        # Note: No actual 3rd-party APIs are called here. This just manipulates presentation.
        if channel == SourceChannel.WHATSAPP:
            return f"*Author Support:*\n{base_response}\n\n_Reply 'HUMAN' to speak to an agent._"
        elif channel == SourceChannel.INSTAGRAM:
            return f"Hi! 👋\n{base_response}\n\nNeed more help? DM us 'SUPPORT'."
        elif channel == SourceChannel.EMAIL:
            return f"Dear Author,\n\n{base_response}\n\nWarm regards,\nThe Author Support Team"
        elif channel == SourceChannel.DASHBOARD_CHAT:
            # Keep it concise for in-app widget
            return base_response
            
        return base_response

    def _build_unauthorized_response(self, workflow_id: str, channel: SourceChannel, identifier: str) -> WorkflowResponse:
        """Generates a safe fallback when identity verification fails."""
        safe_response = (
            "We couldn't verify your author identity automatically. "
            "Our support team has been notified and will assist you shortly. "
            "Please ensure you are contacting us from your registered account."
        )
        return WorkflowResponse(
            workflow_id=workflow_id,
            source_channel=channel,
            matched_author={"provided_identifier": identifier},
            intent="unverified_identity",
            confidence=0.0,
            escalation_required=True,
            processing_status=ProcessingStatus.UNAUTHORIZED,
            final_response=self._apply_channel_formatting(safe_response, channel)
        )

    def _build_failed_response(self, workflow_id: str, channel: SourceChannel, error_msg: str) -> WorkflowResponse:
        """Generates a safe fallback when the system encounters a critical crash."""
        safe_response = "We encountered a temporary system issue while processing your request. An agent will be with you shortly."
        return WorkflowResponse(
            workflow_id=workflow_id,
            source_channel=channel,
            matched_author={},
            intent="system_failure",
            confidence=0.0,
            escalation_required=True,
            processing_status=ProcessingStatus.FAILED,
            final_response=self._apply_channel_formatting(safe_response, channel)
        )

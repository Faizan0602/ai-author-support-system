import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from supabase import Client

from app.ai.gemini_service import GeminiService
from app.database.supabase_client import get_supabase_client
from app.services.author_service import AuthorService
from app.services.conversation_logger_service import (
    ConversationLoggerService,
)
from app.services.identity_resolution_service import (
    IdentityResolutionResponse,
    IdentityResolutionService,
)
from app.services.knowledge_base_service import (
    KnowledgeBaseService,
)
from app.services.query_classifier import (
    ClassificationResponse,
    QueryClassifier,
)
from app.services.query_resolution_service import (
    QueryResolutionResponse,
    QueryResolutionService,
)
from app.services.workflow_orchestrator_service import (
    WorkflowOrchestratorService,
    WorkflowRequest,
    WorkflowResponse,
)
from app.utils.config import Settings, get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI Automation"])


# =========================
# Request / Response Models
# =========================

class AskAIRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        description="Prompt for AI generation",
    )


class AskAIResponse(BaseModel):
    response: str


class HealthResponse(BaseModel):
    status: str
    message: str


class ClassifyQueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Author support query",
    )


class ResolveQueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Author support query",
    )

    author_email: str = Field(
        ...,
        min_length=1,
        description="Author email",
    )


class ResolveIdentityRequest(BaseModel):
    identifier: str = Field(
        ...,
        min_length=1,
        description="Author email or author name",
    )


# =========================
# Dependency Injection
# =========================

def get_gemini_service(
    settings: Settings = Depends(get_settings),
) -> GeminiService:
    """
    Dependency provider for GeminiService.
    """

    return GeminiService(
        api_key=settings.GEMINI_API_KEY
    )


def get_query_classifier(
    ai_service: GeminiService = Depends(
        get_gemini_service
    ),
) -> QueryClassifier:
    """
    Dependency provider for QueryClassifier.
    """

    return QueryClassifier(
        ai_service=ai_service
    )


def get_author_service(
    db_client: Client = Depends(
        get_supabase_client
    ),
) -> AuthorService:
    """
    Dependency provider for AuthorService.
    """

    return AuthorService(
        db=db_client
    )


def get_conversation_logger_service(
    db_client: Client = Depends(
        get_supabase_client
    ),
) -> ConversationLoggerService:
    """
    Dependency provider for ConversationLoggerService.
    """

    return ConversationLoggerService(
        db=db_client
    )


def get_identity_resolution_service(
    author_service: AuthorService = Depends(
        get_author_service
    ),
) -> IdentityResolutionService:
    """
    Dependency provider for IdentityResolutionService.
    """

    return IdentityResolutionService(
        author_service=author_service
    )


def get_query_resolution_service(
    classifier: QueryClassifier = Depends(
        get_query_classifier
    ),
    author_service: AuthorService = Depends(
        get_author_service
    ),
    ai_service: GeminiService = Depends(
        get_gemini_service
    ),
    conversation_logger: ConversationLoggerService = Depends(
        get_conversation_logger_service
    ),
) -> QueryResolutionService:
    """
    Dependency provider for QueryResolutionService.
    """

    return QueryResolutionService(
        classifier=classifier,
        author_service=author_service,
        ai_service=ai_service,
        conversation_logger=conversation_logger,
        knowledge_base=KnowledgeBaseService(),
    )


def get_workflow_orchestrator_service(
    identity_service: IdentityResolutionService = Depends(
        get_identity_resolution_service
    ),
    query_service: QueryResolutionService = Depends(
        get_query_resolution_service
    ),
) -> WorkflowOrchestratorService:
    """
    Dependency provider for WorkflowOrchestratorService.
    """

    return WorkflowOrchestratorService(
        identity_service=identity_service,
        query_service=query_service,
    )


# =========================
# Routes
# =========================

@router.get(
    "/health",
    response_model=HealthResponse,
)
async def health_check():
    """
    Health check endpoint.
    """

    return HealthResponse(
        status="success",
        message="AI Author Support System running",
    )


@router.post(
    "/ask-ai",
    response_model=AskAIResponse,
)
async def ask_ai(
    request: AskAIRequest,
    ai_service: GeminiService = Depends(
        get_gemini_service
    ),
):
    """
    AI text generation endpoint.
    """

    try:
        ai_response = await ai_service.generate_response(
            prompt=request.prompt
        )

        return AskAIResponse(
            response=ai_response
        )

    except Exception as e:
        logger.exception("AI route error")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/classify-query",
    response_model=ClassificationResponse,
)
async def classify_query(
    request: ClassifyQueryRequest,
    classifier: QueryClassifier = Depends(
        get_query_classifier
    ),
):
    """
    Classify incoming author support query.
    """

    try:
        result = await classifier.classify_query(
            request.query
        )

        return result

    except Exception as e:
        logger.exception("Query classification failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/resolve-query",
    response_model=QueryResolutionResponse,
)
async def resolve_query(
    request: ResolveQueryRequest,
    resolver: QueryResolutionService = Depends(
        get_query_resolution_service
    ),
):
    """
    Full intelligent query resolution workflow.
    """

    try:
        result = await resolver.resolve_query(
            query=request.query,
            author_email=request.author_email,
        )

        return result

    except Exception as e:
        logger.exception("Query resolution failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/resolve-identity",
    response_model=IdentityResolutionResponse,
)
async def resolve_identity(
    request: ResolveIdentityRequest,
    resolver: IdentityResolutionService = Depends(
        get_identity_resolution_service
    ),
):
    """
    Resolve author identity using email or author name.
    """

    try:
        result = await resolver.resolve_author_identity(
            request.identifier
        )

        return result

    except Exception as e:
        logger.exception("Identity resolution failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/simulate-channel-query",
    response_model=WorkflowResponse,
)
async def simulate_channel_query(
    request: WorkflowRequest,
    orchestrator: WorkflowOrchestratorService = Depends(
        get_workflow_orchestrator_service
    ),
):
    """
    Simulate multi-channel workflow automation.
    """

    try:
        result = await orchestrator.run_workflow(
            request=request
        )

        return result

    except Exception as e:
        logger.exception(
            "Workflow orchestration failed"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
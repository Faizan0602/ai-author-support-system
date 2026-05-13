import logging
from typing import Optional

from supabase import Client, create_client

from app.utils.config import get_settings

logger = logging.getLogger(__name__)

# Singleton client instance
_supabase: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Returns reusable Supabase client instance.
    """

    global _supabase

    if _supabase:
        return _supabase

    try:
        settings = get_settings()

        supabase_url = str(settings.SUPABASE_URL)
        supabase_key = settings.SUPABASE_KEY

        _supabase = create_client(
            supabase_url,
            supabase_key,
        )

        logger.info("Supabase client initialized successfully.")

        return _supabase

    except Exception as e:
        logger.exception("Failed to initialize Supabase client")

        raise RuntimeError(
            f"Supabase connection failed: {str(e)}"
        )
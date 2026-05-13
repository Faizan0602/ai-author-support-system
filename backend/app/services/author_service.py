import logging
from typing import Any, Dict, List, Optional

from supabase import Client

logger = logging.getLogger(__name__)


class AuthorService:
    """
    Service layer for author-related database operations.
    """

    def __init__(self, db: Client):
        self.db = db

    def _execute_query(self, query):
        """
        Execute Supabase query safely.
        """

        try:
            response = query.execute()

            return response.data

        except Exception as e:
            logger.exception("Database query failed")

            raise RuntimeError(
                f"Database operation failed: {str(e)}"
            )

    def get_author_by_email(
        self,
        email: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch author by email.
        """

        logger.info(f"Fetching author: {email}")

        data = self._execute_query(
            self.db.table("authors")
            .select("*")
            .eq("email", email)
            .limit(1)
        )

        if not data:
            return None

        return data[0]

    def get_books_by_author(
        self,
        author_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Fetch books for author.
        """

        logger.info(f"Fetching books for author: {author_id}")

        return self._execute_query(
            self.db.table("books")
            .select("*")
            .eq("author_id", author_id)
        )

    def get_royalty_info(
        self,
        author_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Fetch royalty information.
        """

        logger.info(f"Fetching royalties for author: {author_id}")

        return self._execute_query(
            self.db.table("royalties")
            .select("*")
            .eq("author_id", author_id)
            .order("created_at", desc=True)
        )

    def get_add_on_services(
        self,
        author_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Fetch author add-on services.
        """

        logger.info(f"Fetching add-on services for author: {author_id}")

        return self._execute_query(
            self.db.table("add_on_services")
            .select("*")
            .eq("author_id", author_id)
        )
    
    
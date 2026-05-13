import logging
from pathlib import Path
from typing import List


logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """
    Lightweight Knowledge Base retrieval service.

    Loads BookLeaf FAQ knowledge base text and performs
    simple semantic-like keyword matching.
    """

    def __init__(self):
        self.kb_text = self._load_knowledge_base()

    def _load_knowledge_base(self) -> str:
        """
        Load KB text from local file.
        """

        try:
            kb_path = (
                Path(__file__)
                .resolve()
                .parent.parent
                / "knowledge_base"
                / "bookleaf_faq.txt"
            )

            with open(kb_path, "r", encoding="utf-8") as file:
                data = file.read()

            logger.info("Knowledge base loaded successfully.")

            return data

        except Exception as e:
            logger.exception("Failed to load knowledge base.")
            return ""

    def search_relevant_content(
        self,
        query: str,
        max_chunks: int = 3,
    ) -> List[str]:
        """
        Retrieve relevant KB chunks using keyword matching.
        """

        if not self.kb_text:
            return []

        query_words = query.lower().split()

        paragraphs = self.kb_text.split("\n\n")

        scored_chunks = []

        for paragraph in paragraphs:

            paragraph_lower = paragraph.lower()

            score = sum(
                1
                for word in query_words
                if word in paragraph_lower
            )

            if score > 0:
                scored_chunks.append(
                    (score, paragraph.strip())
                )

        scored_chunks.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        top_chunks = [
            chunk
            for _, chunk in scored_chunks[:max_chunks]
        ]

        return top_chunks

    def build_context(
        self,
        query: str,
    ) -> str:
        """
        Build contextual KB response block.
        """

        chunks = self.search_relevant_content(query)

        if not chunks:
            return ""

        return "\n\n".join(chunks)
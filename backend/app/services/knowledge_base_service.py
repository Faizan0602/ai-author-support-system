import logging
import re
from pathlib import Path
from typing import List, Set


logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """
    Lightweight Knowledge Base retrieval service.

    Loads BookLeaf FAQ knowledge base text and performs
    simple semantic-like keyword matching.
    """

    def __init__(self):
        self.kb_text = self._load_knowledge_base()
        self.stop_words = {
            "a",
            "an",
            "and",
            "are",
            "can",
            "do",
            "does",
            "for",
            "help",
            "how",
            "i",
            "is",
            "it",
            "me",
            "my",
            "need",
            "of",
            "please",
            "request",
            "support",
            "the",
            "to",
            "what",
            "when",
            "where",
            "why",
            "you",
            "your",
        }
        self.single_keyword_matches = {
            "amazon",
            "copyright",
            "dashboard",
            "distribution",
            "isbn",
            "login",
            "password",
            "prime",
            "publishing",
            "refund",
            "royalties",
            "royalty",
            "timeline",
        }

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

        query_words = self._extract_keywords(query)

        if not query_words:
            return []

        paragraphs = self.kb_text.split("\n\n")

        scored_chunks = []

        for paragraph in paragraphs:

            paragraph_words = self._extract_words(paragraph)

            score = sum(
                1
                for word in query_words
                if self._word_matches(word, paragraph_words)
            )

            if score >= self._minimum_match_score(query_words):
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

    def _minimum_match_score(
        self,
        query_words: List[str],
    ) -> int:
        """
        Require enough signal to avoid matching nonsense by one word.
        """

        if len(query_words) == 1:
            if query_words[0] in self.single_keyword_matches:
                return 1

            return 2

        return 2

    def _extract_keywords(
        self,
        text: str,
    ) -> List[str]:
        """
        Extract useful query terms while ignoring common filler words.
        """

        return [
            word
            for word in self._extract_words(text)
            if word not in self.stop_words
            and len(word) > 2
        ]

    def _extract_words(
        self,
        text: str,
    ) -> Set[str]:
        """
        Normalize text into searchable lowercase word tokens.
        """

        return set(
            re.findall(
                r"[a-z0-9]+",
                text.lower(),
            )
        )

    def _word_matches(
        self,
        query_word: str,
        paragraph_words: Set[str],
    ) -> bool:
        """
        Match exact words plus simple variants like publish/publishing.
        """

        if query_word in paragraph_words:
            return True

        return any(
            len(query_word) >= 4
            and len(paragraph_word) >= 4
            and (
                paragraph_word.startswith(query_word)
                or query_word.startswith(paragraph_word)
            )
            for paragraph_word in paragraph_words
        )

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

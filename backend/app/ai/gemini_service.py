import logging
from typing import Optional

import google.generativeai as genai
from google.generativeai.types import generation_types

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Reusable Gemini AI service layer.
    Handles all Gemini API interactions centrally.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "models/gemini-2.5-flash",
    ):
        """
        Initialize Gemini model configuration.
        """

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(model_name)

    async def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        timeout: Optional[int] = 30,
    ) -> str:
        """
        Generate AI response from Gemini model.
        """

        if not prompt or not prompt.strip():
            return "Prompt cannot be empty."

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature
            )

            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config,
                request_options={
                    "timeout": timeout
                },
            )

            # Debug logging
            print("\n================ GEMINI RESPONSE ================\n")

            try:
                print(response.text)
            except Exception:
                print("No response.text found")

            print("\n=================================================\n")

            if not hasattr(response, "text") or not response.text:
                logger.warning("Empty response received from Gemini.")

                return """
{
    "intent": "unknown",
    "confidence": 0.0,
    "extracted_entities": {}
}
"""

            return response.text.strip()

        except generation_types.StopCandidateException as e:
            logger.error(f"Generation stopped: {e}")

            return """
{
    "intent": "unknown",
    "confidence": 0.0,
    "extracted_entities": {}
}
"""

        except Exception as e:
            logger.exception("Gemini API error")

            return f"""
{{
    "intent": "unknown",
    "confidence": 0.0,
    "extracted_entities": {{
        "error": "{str(e)}"
    }}
}}
"""
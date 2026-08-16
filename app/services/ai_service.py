import json
from groq import AsyncGroq 
from groq import (APIConnectionError, APITimeoutError, RateLimitError, InternalServerError, APIError)
from app.exceptions import AIServiceError
import logging
logger = logging.getLogger(__name__)

class Groq_ai:
    def __init__(self, api_key:str):
        self.api_key = api_key
        self.client = AsyncGroq(api_key=self.api_key)
    async def summarize(self, title, description,content, target_language):
        user_content = (
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Content: {content}\n\n"
            f"Task: Translate and summarize the news text above into {target_language}. "
            f"Constraints: "
            f"1. Write a summary of 2-3 sentences (roughly 60-100 words) covering: "
            f"what happened and why it matters. "
            f"2. Base the summary ONLY on the text provided above; do not invent facts. "
            f"3. If Content and Description are missing, state briefly that the article body "
            f"is unavailable instead of guessing. "
            f"4. Evaluate the positivity of the news (1 for positive, 0 for neutral or negative). "
            f"5. Return the response STRICTLY as a JSON object without any formatting blocks "
            f"or additional text. "
            f"Use this exact JSON structure: {{\"summary\": \"your summary here\", \"sentiment\": your_number}}"
        )
        try:
            chat_completion = await self.client.chat.completions.create(
                model = "llama-3.1-8b-instant",
                messages = [
                {
                    "role" : "system",
                    "content" : "You are a news editor",
                },
                {
                    "role" : "user",
                    "content" : user_content
                }
            ],
            response_format = {"type": "json_object"}
        )
            result = json.loads(chat_completion.choices[0].message.content)
            if "summary" not in result or "sentiment" not in result:
                raise ValueError("AI response missing required fields")
            return result
        except(APIConnectionError, APITimeoutError) as exc:
            logger.error("Groq connection/timeout error: %s", type(exc).__name__)
            raise AIServiceError(f"Network error: {exc}") from exc
        except RateLimitError as exc:
            logger.warning("Groq rate limit exceeded: %s", type(exc).__name__)
            raise AIServiceError("Rate limit exceeded - try again later") from exc
        except InternalServerError as exc:
            logger.error("Groq internal server error: %s", type(exc).__name__)
            raise AIServiceError("AI service internal error") from exc
        except APIError as exc:
            logger.error("Groq API error: %s", type(exc).__name__)
            raise AIServiceError(f"AI API error: {exc}") from exc
        except ValueError as exc:
            logger.error("Invalid AI response structure: %s", type(exc).__name__)
            raise AIServiceError("AI response missing required data") from exc
        except Exception as exc:
            logger.critical("Unexpected error in AI service: %s", type(exc).__name__, exc_info=True)
            raise AIServiceError(f"Unexpected error in: {exc}") from exc
        


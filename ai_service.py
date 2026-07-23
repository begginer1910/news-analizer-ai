import json
from groq import AsyncGroq
import logging
logger = logging.getLogger(__name__)

class Groq_ai:
    def __init__(self, api_key:str):
        self.api_key = api_key
        self.client = AsyncGroq(api_key=self.api_key)
    async def summarize(self, title, description,target_language):
        user_content = (
            f"Title: {title}\n"
            f"Description: {description}\n\n"
            f"Task: Translate and summarize the text above into {target_language}. "
            f"Constraints: "
            f"1. The summary MUST be strictly under 150 characters. "
            f"2. Evaluate the positivity of the news (1 for positive, 0 for neutral or negative). "
            f"3. Return the response STRICTLY as a JSON object without any formatting blocks or additional text. "
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
                return {"summary": "", "sentiment": 0}
            return result

        except Exception as e:
            logger.critical(f"Error AI: {e}")
            return {"summary": "", "sentiment": 0}



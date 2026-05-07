import os
import json
from dotenv import load_dotenv
from groq import Groq


class Groq_ai:
    def __init__(self):
        load_dotenv()
        self.client = Groq(
            api_key = os.getenv("GROQ_API_KEY"))
    def summarize(self, title, description,target_language):
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
            chat_completion = self.client.chat.completions.create(
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
            return json.loads(chat_completion.choices[0].message.content)

        except Exception as e:
            print(f"Błąd AI: {e}")
            return {"summary": "Błąd generowania", "sentiment": 0}

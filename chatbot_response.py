import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Current Gemini model
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)


def generate_chitti_response(question):
    """
    Generate a response from Chitti AI.

    Chitti can answer general questions as well as
    HireLens-related questions.
    """

    if not question or not question.strip():
        return {
            "success": False,
            "message": "Please enter a question."
        }

    if not client:
        return {
            "success": False,
            "message": "Chitti AI is not configured. Please check your GEMINI_API_KEY."
        }

    prompt = f"""
You are Chitti, the friendly AI assistant inside HireLens AI.

You can answer ANY general question asked by the user.
You are not limited to job-scam questions.

Give clear, useful and concise answers.

Rules:
- Answer the actual question directly.
- Use simple language.
- Avoid long essay-style responses.
- Use headings and bullet points when useful.
- Give an example when it helps understanding.
- If the user asks for a flowchart, provide a simple text flowchart.
- If the user asks for an explanation, explain step-by-step.
- Do not unnecessarily mention HireLens AI unless the question is related to it.

User question:
{question}
"""

    # Retry temporary Gemini errors
    max_attempts = 3
    wait_times = [2, 4, 8]

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if response and response.text:
                return {
                    "success": True,
                    "response": response.text.strip()
                }

            return {
                "success": False,
                "message": "Chitti received an empty response. Please try again."
            }

        except Exception as e:
            error_text = str(e)

            # Temporary server overload / rate-limit errors
            temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "high demand" in error_text.lower()
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "500" in error_text
            )

            if temporary_error and attempt < max_attempts - 1:
                print(
                    f"Chitti temporary error. "
                    f"Retrying in {wait_times[attempt]} seconds..."
                )

                time.sleep(wait_times[attempt])
                continue

            # Friendly message instead of showing raw Gemini error
            if temporary_error:
                return {
                    "success": False,
                    "message": (
                        "Chitti AI is temporarily busy right now. "
                        "Please try your question again in a few seconds."
                    )
                }

            print("Chitti Error:", error_text)

            return {
                "success": False,
                "message": (
                    "Chitti could not process your question right now. "
                    "Please try again."
                )
            }

    return {
        "success": False,
        "message": "Chitti AI is temporarily unavailable. Please try again."
    }
# ============================================================
# HIRELENS AI - CHITTI CHATBOT
# Lightweight Gemini REST API version
# ============================================================

import os
import json
import urllib.request
import urllib.error

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


# ============================================================
# CHITTI RESPONSE FUNCTION
# ============================================================

def generate_chitti_response(question):

    # --------------------------------------------------------
    # Check question
    # --------------------------------------------------------

    if not question or not question.strip():
        return {
            "success": False,
            "message": "Please enter a question."
        }


    # --------------------------------------------------------
    # Check API key
    # --------------------------------------------------------

    if not API_KEY:
        return {
            "success": False,
            "message": (
                "Chitti AI is not configured. "
                "Please check your GEMINI_API_KEY."
            )
        }


    # --------------------------------------------------------
    # Chitti prompt
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Gemini REST API URL
    # --------------------------------------------------------

    url = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/{MODEL_NAME}:generateContent"
        f"?key={API_KEY}"
    )


    # --------------------------------------------------------
    # Request data
    # --------------------------------------------------------

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 512,
            "thinkingConfig": {
                "thinkingLevel": "low"
            }
        }
    }


    # Convert data to JSON
    request_data = json.dumps(data).encode("utf-8")


    # --------------------------------------------------------
    # Request headers
    # --------------------------------------------------------

    headers = {
        "Content-Type": "application/json"
    }


    # --------------------------------------------------------
    # Create request
    # --------------------------------------------------------

    request = urllib.request.Request(
        url,
        data=request_data,
        headers=headers,
        method="POST"
    )


    # ========================================================
    # SEND REQUEST
    # ========================================================

    try:

        print("Chitti: sending request to Gemini...")

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            response_data = response.read().decode("utf-8")

        result = json.loads(response_data)


        # ----------------------------------------------------
        # Extract Gemini response
        # ----------------------------------------------------

        candidates = result.get("candidates", [])

        if not candidates:
            print("Chitti: Gemini returned no candidates.")

            return {
                "success": False,
                "message": (
                    "Chitti received an empty response. "
                    "Please try again."
                )
            }


        content = candidates[0].get("content", {})

        parts = content.get("parts", [])

        if not parts:
            return {
                "success": False,
                "message": (
                    "Chitti received an empty response. "
                    "Please try again."
                )
            }


        answer = parts[0].get("text", "")


        # ----------------------------------------------------
        # Check answer
        # ----------------------------------------------------

        if answer and answer.strip():

            print("Chitti: response received successfully.")

            return {
                "success": True,
                "response": answer.strip()
            }


        return {
            "success": False,
            "message": (
                "Chitti received an empty response. "
                "Please try again."
            )
        }


    # ========================================================
    # GEMINI API ERRORS
    # ========================================================

    except urllib.error.HTTPError as e:

        status_code = e.code

        try:
            error_body = e.read().decode("utf-8")
            print(
                f"Chitti Gemini HTTP Error {status_code}: "
                f"{error_body}"
            )
        except Exception:
            print(
                f"Chitti Gemini HTTP Error: "
                f"{status_code}"
            )


        # API key problem
        if status_code in (401, 403):

            return {
                "success": False,
                "message": (
                    "Chitti AI could not access Gemini. "
                    "Please check the Gemini API key."
                )
            }


        # Model problem
        if status_code == 404:

            return {
                "success": False,
                "message": (
                    "Chitti AI model is unavailable. "
                    "Please check the Gemini model configuration."
                )
            }


        # Rate limit
        if status_code == 429:

            return {
                "success": False,
                "message": (
                    "Chitti AI is temporarily busy. "
                    "Please try again in a few seconds."
                )
            }


        # Gemini server problem
        if status_code >= 500:

            return {
                "success": False,
                "message": (
                    "Chitti AI is temporarily unavailable. "
                    "Please try again in a few seconds."
                )
            }


        return {
            "success": False,
            "message": (
                "Chitti could not process your question "
                "right now. Please try again."
            )
        }


    # ========================================================
    # TIMEOUT
    # ========================================================

    except TimeoutError:

        print("Chitti: Gemini request timed out.")

        return {
            "success": False,
            "message": (
                "Chitti took too long to respond. "
                "Please try again."
            )
        }


    # ========================================================
    # URL / CONNECTION ERROR
    # ========================================================

    except urllib.error.URLError as e:

        print(
            "Chitti connection error:",
            str(e)
        )

        return {
            "success": False,
            "message": (
                "Chitti could not connect to Gemini. "
                "Please try again."
            )
        }


    # ========================================================
    # OTHER ERRORS
    # ========================================================

    except Exception as e:

        print(
            "Chitti unexpected error:",
            str(e)
        )

        return {
            "success": False,
            "message": (
                "Chitti could not process your question "
                "right now. Please try again."
            )
        }

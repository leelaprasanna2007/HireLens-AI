# ============================================================
# HIRELENS AI - LIGHTWEIGHT IMAGE OCR
# ============================================================
# Uses Gemini Vision instead of EasyOCR.
# This is much lighter for Render's 512 MB free instance.
# ============================================================

import os
import mimetypes

from google import genai
from google.genai import types


# ============================================================
# GEMINI CLIENT
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
        print("Gemini OCR client initialized successfully.")
    except Exception as error:
        print("Gemini OCR initialization error:", error)
else:
    print("GEMINI_API_KEY not found.")


# ============================================================
# IMAGE MIME TYPE
# ============================================================

def get_mime_type(image_path):
    """
    Detect the image MIME type.
    """

    mime_type, _ = mimetypes.guess_type(image_path)

    if mime_type:
        return mime_type

    # Fallback
    extension = os.path.splitext(image_path)[1].lower()

    if extension in [".jpg", ".jpeg"]:
        return "image/jpeg"

    if extension == ".png":
        return "image/png"

    if extension == ".webp":
        return "image/webp"

    if extension == ".gif":
        return "image/gif"

    return "image/jpeg"


# ============================================================
# EXTRACT TEXT FROM IMAGE
# ============================================================

def extract_text_from_image(image_path):

    try:

        # ----------------------------------------------------
        # Validate image path
        # ----------------------------------------------------

        if not image_path:

            print("OCR: No image path provided.")

            return ""

        if not os.path.exists(image_path):

            print(
                "OCR: Image file not found:",
                image_path
            )

            return ""

        # ----------------------------------------------------
        # Validate Gemini client
        # ----------------------------------------------------

        if client is None:

            print(
                "OCR: Gemini client is not available."
            )

            return ""

        print("\n")
        print("=" * 70)
        print("HIRELENS AI - GEMINI IMAGE OCR")
        print("=" * 70)

        print("Reading image...")

        # ----------------------------------------------------
        # Read image
        # ----------------------------------------------------

        with open(image_path, "rb") as image_file:

            image_data = image_file.read()

        if not image_data:

            print("OCR: Image is empty.")

            return ""

        # ----------------------------------------------------
        # Detect image type
        # ----------------------------------------------------

        mime_type = get_mime_type(
            image_path
        )

        print(
            "Image type:",
            mime_type
        )

        # ----------------------------------------------------
        # OCR PROMPT
        # ----------------------------------------------------

        prompt = """
You are an OCR engine for HireLens AI.

Read the job advertisement/poster image carefully.

Extract ALL visible text from the image.

Important:
- Preserve the actual wording as much as possible.
- Do NOT invent missing information.
- Do NOT analyze whether the job is real or fake.
- Do NOT summarize the advertisement.
- Do NOT add explanations.
- Extract company name if visible.
- Extract job role if visible.
- Extract salary if visible.
- Extract location if visible.
- Extract experience requirements if visible.
- Extract email addresses if visible.
- Extract phone numbers if visible.
- Extract application instructions if visible.
- Extract payment/registration/joining/training/security-deposit information if visible.
- Include other important job-related text.
- If some text is unclear, make your best reading but do not create information that is not present.

Return ONLY the extracted text.

Keep separate lines where appropriate.
"""

        # ----------------------------------------------------
        # Create Gemini image part
        # ----------------------------------------------------

        image_part = types.Part.from_bytes(
            data=image_data,
            mime_type=mime_type
        )

        # ----------------------------------------------------
        # Send image to Gemini
        # ----------------------------------------------------

        print("Sending image to Gemini...")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                image_part
            ]
        )

        # ----------------------------------------------------
        # Get response text
        # ----------------------------------------------------

        extracted_text = ""

        if response and response.text:

            extracted_text = response.text.strip()

        # ----------------------------------------------------
        # Display result
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("OCR RESULT")
        print("=" * 70)

        if extracted_text:

            print(extracted_text)

        else:

            print(
                "No readable text detected."
            )

        print("=" * 70)
        print("\n")

        return extracted_text

    except Exception as error:

        print(
            "Gemini OCR Error:",
            str(error)
        )

        return ""


# ============================================================
# DIRECT TESTING
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("HIRELENS AI - IMAGE OCR TEST")
    print("=" * 70)

    image_path = input(
        "Enter image path: "
    ).strip()

    text = extract_text_from_image(
        image_path
    )

    print("\n")
    print("=" * 70)
    print("FINAL EXTRACTED TEXT")
    print("=" * 70)

    if text:

        print(text)

    else:

        print(
            "No readable text was detected."
        )

    print("=" * 70)

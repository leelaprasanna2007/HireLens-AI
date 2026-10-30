import easyocr
import os
import cv2


# ============================================================
# INITIALIZE EASY OCR
# ============================================================

try:
    reader = easyocr.Reader(
        ['en'],
        gpu=False,
        verbose=False
    )
except Exception as error:
    print("EasyOCR initialization error:", error)
    reader = None


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image_path):
    """
    Create a clean enlarged grayscale image for OCR.
    """

    image = cv2.imread(image_path)

    if image is None:
        return None

    # --------------------------------------------------------
    # Upscale image
    # --------------------------------------------------------

    height, width = image.shape[:2]

    scale = 2

    image = cv2.resize(
        image,
        (width * scale, height * scale),
        interpolation=cv2.INTER_CUBIC
    )

    # --------------------------------------------------------
    # Convert to grayscale
    # --------------------------------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------------------------------
    # Improve contrast
    # --------------------------------------------------------

    gray = cv2.equalizeHist(gray)

    # --------------------------------------------------------
    # Light noise reduction
    # --------------------------------------------------------

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    return gray


# ============================================================
# SECOND PREPROCESSING METHOD
# ============================================================

def preprocess_threshold(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return None

    height, width = image.shape[:2]

    image = cv2.resize(
        image,
        (width * 2, height * 2),
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    threshold = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return threshold


# ============================================================
# OCR RESULT CLEANING
# ============================================================

def clean_ocr_line(text):

    if not text:
        return ""

    text = str(text)

    # Remove unnecessary whitespace
    text = " ".join(
        text.split()
    ).strip()

    return text


# ============================================================
# RUN OCR ON ONE IMAGE
# ============================================================

def run_ocr(image):

    if image is None:
        return []

    try:

        results = reader.readtext(
            image,
            detail=1,
            paragraph=False,
            width_ths=0.7,
            height_ths=0.5,
            text_threshold=0.4,
            low_text=0.2,
            link_threshold=0.3,
            mag_ratio=1.0
        )

    except Exception as error:

        print("OCR pass error:", error)

        return []

    detected = []

    for result in results:

        if len(result) < 3:
            continue

        bbox = result[0]
        text = clean_ocr_line(result[1])

        try:
            confidence = float(result[2])
        except (ValueError, TypeError):
            continue

        if not text:
            continue

        # ----------------------------------------------------
        # Keep useful detections
        # ----------------------------------------------------

        if confidence >= 0.15:

            detected.append({
                "text": text,
                "confidence": confidence,
                "bbox": bbox
            })

    return detected


# ============================================================
# SORT OCR RESULTS
# ============================================================

def sort_ocr_results(results):

    def get_position(item):

        bbox = item["bbox"]

        try:
            x = min(point[0] for point in bbox)
            y = min(point[1] for point in bbox)

            return (
                round(y / 25) * 25,
                x
            )

        except Exception:
            return (0, 0)

    return sorted(
        results,
        key=get_position
    )


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(results):

    final_results = []
    seen = set()

    for item in results:

        text = clean_ocr_line(
            item["text"]
        )

        if not text:
            continue

        key = text.lower()

        # Exact duplicate
        if key in seen:
            continue

        seen.add(key)

        final_results.append(
            item
        )

    return final_results


# ============================================================
# MAIN OCR FUNCTION
# ============================================================

def extract_text_from_image(image_path):

    try:

        # ----------------------------------------------------
        # Validate image
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
        # Validate reader
        # ----------------------------------------------------

        if reader is None:

            print(
                "OCR: EasyOCR reader unavailable."
            )

            return ""

        print("\n")
        print("=" * 70)
        print("HIRELENS AI - OCR PROCESSING")
        print("=" * 70)

        # ----------------------------------------------------
        # PASS 1 - ORIGINAL IMAGE
        # ----------------------------------------------------

        print("OCR Pass 1: Original image...")

        original_results = run_ocr(
            image_path
        )

        # ----------------------------------------------------
        # PASS 2 - ENLARGED GRAYSCALE
        # ----------------------------------------------------

        print("OCR Pass 2: Enlarged grayscale image...")

        processed_image = preprocess_image(
            image_path
        )

        processed_results = run_ocr(
            processed_image
        )

        # ----------------------------------------------------
        # PASS 3 - THRESHOLD IMAGE
        # ----------------------------------------------------

        print("OCR Pass 3: Threshold image...")

        threshold_image = preprocess_threshold(
            image_path
        )

        threshold_results = run_ocr(
            threshold_image
        )

        # ----------------------------------------------------
        # COMBINE RESULTS
        # ----------------------------------------------------

        all_results = (
            original_results
            + processed_results
            + threshold_results
        )

        # ----------------------------------------------------
        # Remove duplicates
        # ----------------------------------------------------

        all_results = remove_duplicates(
            all_results
        )

        # ----------------------------------------------------
        # Sort based on poster position
        # ----------------------------------------------------

        all_results = sort_ocr_results(
            all_results
        )

        # ----------------------------------------------------
        # Build final text
        # ----------------------------------------------------

        extracted_lines = []

        for item in all_results:

            text = clean_ocr_line(
                item["text"]
            )

            if text:

                extracted_lines.append(
                    text
                )

        extracted_text = "\n".join(
            extracted_lines
        )

        # ----------------------------------------------------
        # Display OCR result in terminal
        # ----------------------------------------------------

        print("\n")
        print("=" * 70)
        print("OCR RESULT")
        print("=" * 70)

        if extracted_text:

            print(
                extracted_text
            )

        else:

            print(
                "No readable text detected."
            )

        print("=" * 70)
        print("\n")

        return extracted_text.strip()

    except Exception as error:

        print(
            "OCR Error:",
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
from flask import Flask, render_template, request, jsonify
import os
import uuid

# ============================================================
# HIRELENS AI - MODULE IMPORTS
# ============================================================

from information_extraction import extract_job_information
from advanced_scam_detection import detect_scam_patterns
from salary_analysis import analyze_salary
from image_ocr import extract_text_from_image
from chatbot_response import generate_chitti_response
from explanation_generator import generate_explanation
from recommendations import generate_recommendations


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# UPLOAD CONFIGURATION
# ============================================================

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# RISK SCORE CALCULATION
# ============================================================

def calculate_risk_score(detected_flags):
    """
    Calculate risk score from scam detection flags.

    High   = 40 points
    Medium = 20 points
    Low    = 10 points

    Maximum score = 100
    """

    score = 0

    if not isinstance(detected_flags, list):
        return 0

    for flag in detected_flags:

        if not isinstance(flag, dict):
            continue

        risk = str(
            flag.get("risk", "")
        ).strip().lower()

        if risk == "high":
            score += 40

        elif risk == "medium":
            score += 20

        elif risk == "low":
            score += 10

    return min(score, 100)


# ============================================================
# RISK LEVEL
# ============================================================

def get_risk_level(risk_score):
    """
    Convert risk score into a readable risk level.
    """

    if risk_score >= 70:
        return "HIGH RISK"

    elif risk_score >= 40:
        return "MEDIUM RISK"

    else:
        return "LOW RISK"


# ============================================================
# CREATE CONCERNS FROM FLAGS
# ============================================================

def build_concerns(detected_flags):
    """
    Convert detected scam flags into user-friendly concerns.
    """

    concerns = []

    if not isinstance(detected_flags, list):
        return concerns

    for flag in detected_flags:

        if not isinstance(flag, dict):
            continue

        category = flag.get(
            "category",
            "Suspicious Indicator"
        )

        message = flag.get(
            "message",
            ""
        )

        details = flag.get(
            "details",
            []
        )

        if message:
            concern = str(message)
        else:
            concern = str(category)

        if details:

            if isinstance(details, list):

                evidence = ", ".join(
                    str(item)
                    for item in details
                )

            else:

                evidence = str(details)

            concern = (
                concern
                + " Evidence: "
                + evidence
            )

        concerns.append(concern)

    # Remove duplicates
    concerns = list(
        dict.fromkeys(concerns)
    )

    return concerns


# ============================================================
# ANALYZE JOB
# ============================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        # ====================================================
        # 1. GET JOB DESCRIPTION
        # ====================================================

        job_text = request.form.get(
            "job_text",
            ""
        ).strip()


        # ====================================================
        # 2. GET IMAGE
        # ====================================================

        image = request.files.get("image")

        extracted_image_text = ""


        # ====================================================
        # 3. IMAGE OCR
        # ====================================================

        if image and image.filename:

            original_name = image.filename

            extension = os.path.splitext(
                original_name
            )[1].lower()

            # Safe unique filename
            filename = (
                str(uuid.uuid4())
                + extension
            )

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            # Save image
            image.save(image_path)

            print("\n" + "=" * 60)
            print("IMAGE RECEIVED")
            print("=" * 60)
            print("Original file:", original_name)
            print("Saved file:", filename)


            # ------------------------------------------------
            # RUN OCR
            # ------------------------------------------------

            try:

                extracted_image_text = (
                    extract_text_from_image(
                        image_path
                    )
                )

            except Exception as e:

                print(
                    "OCR Error:",
                    str(e)
                )

                extracted_image_text = ""


            print("\n" + "=" * 60)
            print("OCR RESULT")
            print("=" * 60)

            print(
                extracted_image_text
                if extracted_image_text
                else "No text detected."
            )


            # ------------------------------------------------
            # ADD OCR TEXT TO JOB TEXT
            # ------------------------------------------------

            if extracted_image_text:

                if job_text:

                    job_text = (
                        job_text
                        + "\n"
                        + extracted_image_text
                    ).strip()

                else:

                    job_text = (
                        extracted_image_text
                    ).strip()


        # ====================================================
        # 4. VALIDATE INPUT
        # ====================================================

        if not job_text:

            return jsonify({

                "success": False,

                "message": (
                    "Please enter a job description "
                    "or upload a job poster containing "
                    "readable text."
                )

            })


        print("\n" + "=" * 60)
        print("FINAL TEXT FOR ANALYSIS")
        print("=" * 60)
        print(job_text)


        # ====================================================
        # 5. INFORMATION EXTRACTION
        # ====================================================

        try:

            job_info = extract_job_information(
                job_text
            )

        except Exception as e:

            print(
                "Information Extraction Error:",
                str(e)
            )

            job_info = {}


        if not isinstance(job_info, dict):

            job_info = {}


        # Make sure expected fields exist
        expected_fields = [

            "company",
            "job_role",
            "salary",
            "location",
            "experience",
            "email",
            "phone"

        ]

        for field in expected_fields:

            if field not in job_info:

                job_info[field] = "Not detected"


        print("\n" + "=" * 60)
        print("EXTRACTED JOB INFORMATION")
        print("=" * 60)

        for key, value in job_info.items():

            print(
                f"{key}: {value}"
            )


        # ====================================================
        # 6. SCAM DETECTION
        # ====================================================

        try:

            scam_result = detect_scam_patterns(
                job_text
            )

        except Exception as e:

            print(
                "Scam Detection Error:",
                str(e)
            )

            scam_result = {

                "risk_score": 0,

                "concerns": [],

                "suspicious_indicators": [],

                "detected_flags": []

            }


        # ----------------------------------------------------
        # IMPORTANT:
        # advanced_scam_detection.py returns a DICTIONARY.
        # Extract the detected_flags list from that dictionary.
        # ----------------------------------------------------

        if isinstance(
            scam_result,
            dict
        ):

            detected_flags = scam_result.get(
                "detected_flags",
                []
            )

            detector_concerns = scam_result.get(
                "concerns",
                []
            )

            detector_score = scam_result.get(
                "risk_score",
                0
            )

        else:

            detected_flags = []

            detector_concerns = []

            detector_score = 0


        # Make sure detected_flags is a list

        if not isinstance(
            detected_flags,
            list
        ):

            detected_flags = []


        print("\n" + "=" * 60)
        print("DETECTED SCAM FLAGS")
        print("=" * 60)

        print(
            detected_flags
        )


        print("\n" + "=" * 60)
        print("SCAM DETECTOR SCORE")
        print("=" * 60)

        print(
            detector_score
        )


        # ====================================================
        # 7. INITIAL RISK SCORE
        # ====================================================

        risk_score = calculate_risk_score(
            detected_flags
        )


        # If detector supplied a valid higher score,
        # preserve it.

        try:

            detector_score = int(
                detector_score
            )

        except Exception:

            detector_score = 0


        risk_score = max(
            risk_score,
            detector_score
        )


        # ====================================================
        # 8. EXTRACT SALARY / ROLE / EXPERIENCE
        # ====================================================

        salary = job_info.get(
            "salary",
            ""
        )

        job_role = job_info.get(
            "job_role",
            job_info.get(
                "role",
                ""
            )
        )

        experience = job_info.get(
            "experience",
            ""
        )


        # ====================================================
        # 9. SALARY ANALYSIS
        # ====================================================

        try:

            salary_result = analyze_salary(

                salary,

                job_role,

                experience

            )

        except Exception as e:

            print(
                "Salary Analysis Error:",
                str(e)
            )

            salary_result = {

                "assessment":
                    "Unable to analyze",

                "reason":
                    "Salary analysis could not be completed.",

                "monthly_salary":
                    None,

                "job_role":
                    job_role,

                "experience":
                    experience

            }


        if not isinstance(
            salary_result,
            dict
        ):

            salary_result = {

                "assessment":
                    "Unable to analyze",

                "reason":
                    "Salary analysis returned an invalid result.",

                "monthly_salary":
                    None,

                "job_role":
                    job_role,

                "experience":
                    experience

            }


        print("\n" + "=" * 60)
        print("SALARY ANALYSIS")
        print("=" * 60)

        print(
            salary_result
        )


        # ====================================================
        # 10. BUILD RISK CONCERNS
        # ====================================================

        concerns = build_concerns(
            detected_flags
        )


        # Add detector concerns if they exist
        if isinstance(
            detector_concerns,
            list
        ):

            for concern in detector_concerns:

                if concern:

                    concerns.append(
                        str(concern)
                    )


        # Remove duplicate concerns
        concerns = list(
            dict.fromkeys(
                concerns
            )
        )


        # ====================================================
        # 11. ADD SALARY RISK
        # ====================================================

        salary_assessment = str(

            salary_result.get(
                "assessment",
                ""
            )

        ).strip().lower()


        salary_reason = str(

            salary_result.get(
                "reason",
                ""
            )

        ).strip()


        # Only treat suspicious salary as a concern

        if salary_assessment == "very high salary":

            risk_score += 20

            if salary_reason:

                concerns.append(
                    salary_reason
                )


        elif salary_assessment == "high salary":

            risk_score += 10

            if salary_reason:

                concerns.append(
                    salary_reason
                )


        # Remove duplicate concerns again

        concerns = list(
            dict.fromkeys(
                concerns
            )
        )


        # Keep score between 0 and 100

        risk_score = min(
            max(
                risk_score,
                0
            ),
            100
        )


        # ====================================================
        # 12. FINAL RISK LEVEL
        # ====================================================

        risk_level = get_risk_level(
            risk_score
        )


        # ====================================================
        # 13. EXPLAINABLE AI
        # ====================================================

        try:

            explanation = generate_explanation(

                detected_flags,
                risk_score

            )

        except Exception as e:

            print(
                "Explainable AI Error:",
                str(e)
            )

            explanation = {

                "summary":
                    risk_level,

                "risk_factors":
                    [],

                "final_explanation":
                    (
                        "HireLens AI analyzed the available "
                        "information, but a detailed explanation "
                        "could not be generated."
                    )

            }


        if not isinstance(
            explanation,
            dict
        ):

            explanation = {

                "summary":
                    risk_level,

                "risk_factors":
                    [],

                "final_explanation":
                    (
                        "No detailed explanation is available."
                    )

            }


        print("\n" + "=" * 60)
        print("EXPLAINABLE AI")
        print("=" * 60)

        print(
            explanation
        )


        # ====================================================
        # 14. RECOMMENDATIONS
        # ====================================================

        try:

            recommendations = (
                generate_recommendations(

                    detected_flags,

                    risk_level

                )
            )

        except Exception as e:

            print(
                "Recommendation Error:",
                str(e)
            )

            recommendations = [

                (
                    "Verify the employer through "
                    "official sources before proceeding."
                )

            ]


        if not isinstance(
            recommendations,
            list
        ):

            recommendations = [

                str(
                    recommendations
                )

            ]


        print("\n" + "=" * 60)
        print("SAFETY RECOMMENDATIONS")
        print("=" * 60)


        for recommendation in recommendations:

            print(
                "-",
                recommendation
            )


        # ====================================================
        # 15. FINAL RECOMMENDATION SUMMARY
        # ====================================================

        if risk_level == "HIGH RISK":

            recommendation_summary = (

                "🚨 High Risk Detected. "
                "Review the warnings carefully and "
                "verify the employer before taking "
                "further action."

            )

        elif risk_level == "MEDIUM RISK":

            recommendation_summary = (

                "⚠️ Caution Advised. "
                "Some suspicious indicators were detected. "
                "Verify the job and employer independently."

            )

        else:

            recommendation_summary = (

                "✅ Low Risk Based on Available Information. "
                "No major scam indicators were detected, "
                "but verification is still recommended."

            )


        # ====================================================
        # 16. FINAL RESPONSE
        # ====================================================

        result = {

            "success":
                True,


            # -----------------------------------------------
            # JOB INFORMATION
            # -----------------------------------------------

            "job_info":
                job_info,

            "job_information":
                job_info,


            # -----------------------------------------------
            # RISK
            # -----------------------------------------------

            "risk_score":
                risk_score,

            "risk_level":
                risk_level,


            # -----------------------------------------------
            # SCAM INDICATORS
            # -----------------------------------------------

            "concerns":
                concerns,

            "detected_flags":
                detected_flags,


            # -----------------------------------------------
            # SALARY ANALYSIS
            # -----------------------------------------------

            "salary_analysis":
                salary_result,


            # -----------------------------------------------
            # EXPLAINABLE AI
            # -----------------------------------------------

            "explainable_ai":
                explanation,


            # -----------------------------------------------
            # RECOMMENDATIONS
            # -----------------------------------------------

            "recommendations":
                recommendations,


            # -----------------------------------------------
            # OCR
            # -----------------------------------------------

            "ocr_text":
                extracted_image_text,


            # -----------------------------------------------
            # FINAL RECOMMENDATION
            # -----------------------------------------------

            "recommendation":
                recommendation_summary,


            # -----------------------------------------------
            # FRONTEND COMPATIBILITY
            # -----------------------------------------------

            "chatbot_response":
                recommendation_summary

        }


        # ====================================================
        # PRINT FINAL RESULT
        # ====================================================

        print("\n" + "=" * 60)
        print("FINAL HIRELENS RESULT")
        print("=" * 60)

        print(
            result
        )


        return jsonify(
            result
        )


    # ========================================================
    # GENERAL ERROR HANDLING
    # ========================================================

    except Exception as e:

        print("\n" + "=" * 60)
        print("ANALYSIS ERROR")
        print("=" * 60)

        print(
            type(e).__name__
        )

        print(
            str(e)
        )


        return jsonify({

            "success":
                False,

            "message":
                (
                    "An error occurred while analyzing "
                    "the job: "
                    + str(e)
                )

        }), 500


# ============================================================
# CHITTI AI CHAT
# ============================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    try:

        data = request.get_json(
            silent=True
        )


        # ----------------------------------------------------
        # VALIDATE REQUEST
        # ----------------------------------------------------

        if not data:

            return jsonify({

                "success":
                    False,

                "message":
                    "No question received."

            })


        question = str(

            data.get(
                "question",
                ""
            )

        ).strip()


        if not question:

            return jsonify({

                "success":
                    False,

                "message":
                    "Please enter a question."

            })


        print("\n" + "=" * 60)
        print("CHITTI QUESTION")
        print("=" * 60)

        print(
            question
        )


        # ----------------------------------------------------
        # GENERATE CHITTI RESPONSE
        # ----------------------------------------------------

        result = generate_chitti_response(

            question

        )


        # ----------------------------------------------------
        # HANDLE DICTIONARY RESPONSE
        # ----------------------------------------------------

        if isinstance(
            result,
            dict
        ):

            if result.get(
                "success"
            ) is False:

                return jsonify({

                    "success":
                        False,

                    "message":
                        result.get(

                            "message",

                            "Chitti could not generate a response."

                        )

                })


            response = result.get(

                "response",

                result.get(
                    "message",
                    ""
                )

            )


        # ----------------------------------------------------
        # HANDLE STRING RESPONSE
        # ----------------------------------------------------

        else:

            response = str(
                result
            )


        # ----------------------------------------------------
        # EMPTY RESPONSE
        # ----------------------------------------------------

        if not response:

            response = (

                "Sorry, Chitti couldn't generate "
                "a response right now."

            )


        print("\n" + "=" * 60)
        print("CHITTI RESPONSE")
        print("=" * 60)

        print(
            response
        )


        return jsonify({

            "success":
                True,

            "response":
                response

        })


    except Exception as e:

        print("\n" + "=" * 60)
        print("CHITTI ERROR")
        print("=" * 60)

        print(
            type(e).__name__
        )

        print(
            str(e)
        )


        return jsonify({

            "success":
                False,

            "message":
                (
                    "Chitti encountered an error: "
                    + str(e)
                )

        }), 500


# ============================================================
# RUN HIRELENS AI
# ============================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )
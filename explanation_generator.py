def generate_explanation(detected_flags, risk_score=0):
    """
    Explainable AI module for HireLens AI.

    Converts detected scam indicators into clear,
    human-readable explanations.
    """

    if not detected_flags:
        return {
            "summary": "Low Risk",
            "risk_factors": [],
            "final_explanation": (
                "No major suspicious indicators were detected based on "
                "the available job information. However, users should "
                "still independently verify the company and recruiter."
            )
        }

    explanations = []

    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0

    for flag in detected_flags:

        if not isinstance(flag, dict):
            continue

        category = flag.get(
            "category",
            "Unknown Risk Factor"
        )

        risk = flag.get(
            "risk",
            "Medium"
        )

        details = flag.get(
            "details",
            []
        )

        message = flag.get(
            "message",
            "A suspicious pattern was detected."
        )

        # Count risk levels
        if risk.lower() == "high":
            high_risk_count += 1

        elif risk.lower() == "medium":
            medium_risk_count += 1

        else:
            low_risk_count += 1

        # Create explanation
        explanations.append({
            "factor": category,
            "risk": risk,
            "detected_evidence": details,
            "explanation": message
        })

    # ==========================================
    # GENERATE SUMMARY
    # ==========================================

    if risk_score >= 70:

        summary = "High Risk"

        final_explanation = (
            f"HireLens AI detected {high_risk_count} high-risk and "
            f"{medium_risk_count} medium-risk warning indicator(s). "
            "The combination of these indicators makes this job posting "
            "potentially unsafe. Verify the employer before applying "
            "and never pay money to secure a job."
        )

    elif risk_score >= 40:

        summary = "Medium Risk"

        final_explanation = (
            f"HireLens AI detected {high_risk_count} high-risk and "
            f"{medium_risk_count} medium-risk indicator(s). "
            "Some suspicious patterns require additional verification "
            "before proceeding with this opportunity."
        )

    elif risk_score > 0:

        summary = "Low to Medium Risk"

        final_explanation = (
            "A small number of suspicious indicators were detected. "
            "These indicators do not necessarily prove that the job "
            "is fraudulent, but independent verification is recommended."
        )

    else:

        summary = "Low Risk"

        final_explanation = (
            "No strong scam indicators were detected from the available "
            "information. However, users should still verify the employer "
            "and avoid sharing sensitive information unnecessarily."
        )

    return {
        "summary": summary,
        "risk_factors": explanations,
        "final_explanation": final_explanation
    }
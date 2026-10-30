def generate_recommendations(scam_flags, overall_assessment):

    recommendations = []

    # --------------------------------------------------------
    # SAFELY READ DETECTED FLAGS
    # --------------------------------------------------------

    flags_text_parts = []

    if isinstance(scam_flags, list):

        for flag in scam_flags:

            if isinstance(flag, dict):

                category = str(
                    flag.get("category", "")
                )

                message = str(
                    flag.get("message", "")
                )

                details = flag.get(
                    "details",
                    []
                )

                flags_text_parts.append(category)
                flags_text_parts.append(message)

                if isinstance(details, list):

                    flags_text_parts.extend(
                        str(item)
                        for item in details
                    )

                else:

                    flags_text_parts.append(
                        str(details)
                    )

            else:

                flags_text_parts.append(
                    str(flag)
                )

    flags_text = " ".join(
        flags_text_parts
    ).lower()

    # --------------------------------------------------------
    # PAYMENT / REGISTRATION FEE
    # --------------------------------------------------------

    if any(
        keyword in flags_text
        for keyword in [
            "registration",
            "application fee",
            "processing fee",
            "joining fee",
            "security deposit",
            "training fee",
            "verification fee",
            "fee"
        ]
    ):

        recommendations.append(
            "Do not pay registration, processing, "
            "training, verification, or joining fees "
            "to obtain a job."
        )

    # --------------------------------------------------------
    # HIGH / SUSPICIOUS SALARY
    # --------------------------------------------------------

    if any(
        keyword in flags_text
        for keyword in [
            "salary",
            "high salary",
            "unrealistic",
            "income",
            "lakhs"
        ]
    ):

        recommendations.append(
            "Verify whether the offered salary is realistic "
            "for the job role, experience, and requirements."
        )

    # --------------------------------------------------------
    # URGENCY / PRESSURE
    # --------------------------------------------------------

    if any(
        keyword in flags_text
        for keyword in [
            "urgency",
            "urgent",
            "immediately",
            "immediate",
            "limited slots",
            "pressure"
        ]
    ):

        recommendations.append(
            "Be cautious of pressure tactics such as "
            "immediate joining, limited slots, or urgent selection."
        )

    # --------------------------------------------------------
    # WHATSAPP / TELEGRAM
    # --------------------------------------------------------

    if any(
        keyword in flags_text
        for keyword in [
            "whatsapp",
            "telegram",
            "dm"
        ]
    ):

        recommendations.append(
            "Do not rely only on WhatsApp, Telegram, or direct "
            "messages. Verify the recruiter and employer through "
            "official channels."
        )

    # --------------------------------------------------------
    # GENERAL HIGH-RISK ADVICE
    # --------------------------------------------------------

    if overall_assessment == "HIGH RISK":

        recommendations.append(
            "Avoid sharing bank details, OTPs, passwords, "
            "or sensitive documents until the employer is verified."
        )

    # --------------------------------------------------------
    # GENERAL MEDIUM-RISK ADVICE
    # --------------------------------------------------------

    elif overall_assessment == "MEDIUM RISK":

        recommendations.append(
            "Verify the company, recruiter, job details, "
            "salary, and contact information before proceeding."
        )

    # --------------------------------------------------------
    # LOW-RISK ADVICE
    # --------------------------------------------------------

    else:

        recommendations.append(
            "No major warning signs were detected, but always "
            "verify the employer through official sources before "
            "sharing personal information."
        )

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    recommendations = list(
        dict.fromkeys(recommendations)
    )

    return recommendations


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_flags = [
        {
            "category": "Registration Fee",
            "risk": "High",
            "details": ["registration fee"],
            "message": "Registration fee detected."
        },
        {
            "category": "Urgency",
            "risk": "Medium",
            "details": ["apply immediately"],
            "message": "Urgency language detected."
        }
    ]

    result = generate_recommendations(
        test_flags,
        "HIGH RISK"
    )

    print("\nSAFETY RECOMMENDATIONS")
    print("=" * 40)

    for recommendation in result:
        print("•", recommendation)
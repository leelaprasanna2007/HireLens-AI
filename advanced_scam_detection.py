import re


def add_flag(detected_flags, concerns, category, risk, details, message, score):
    """
    Add a risk flag and update concerns.
    """
    detected_flags.append({
        "category": category,
        "risk": risk,
        "details": details,
        "message": message
    })

    concerns.append(message)

    return score


def is_payment_keyword_negated(text, keyword):
    """
    Check whether a payment keyword is explicitly negated.

    Examples that should NOT be flagged:

        No registration fee is required.
        No application fee is required.
        No training fee is required.
        No payment is required.
        No upfront payment.
        Free to apply.
        Without any fee.

    Examples that SHOULD be flagged:

        Pay a registration fee of ₹500.
        Training fee of ₹2,000 is required.
        Candidates must pay an application fee.
        A security deposit is required.
    """

    positions = []
    start = 0

    while True:
        position = text.find(keyword, start)

        if position == -1:
            break

        positions.append(position)
        start = position + len(keyword)

    if not positions:
        return False

    for position in positions:

        # Look around the keyword.
        context_start = max(0, position - 100)
        context_end = min(
            len(text),
            position + len(keyword) + 100
        )

        context = text[context_start:context_end]

        # ------------------------------------------------------
        # Explicit negative statements
        # ------------------------------------------------------

        negative_patterns = [

            # No training fee
            r"\bno\s+(?:registration|application|processing|joining|"
            r"security|training|verification|documentation)\s+fee\b",

            # No registration charge
            r"\bno\s+(?:registration|application|processing|joining|"
            r"security|training|verification|documentation)\s+charges?\b",

            # No fee is required
            r"\bno\s+fee\s+(?:is\s+)?required\b",

            # No payment is required
            r"\bno\s+payment\s+(?:is\s+)?required\b",

            # No upfront payment
            r"\bno\s+upfront\s+payment\b",

            # Without fee/payment
            r"\bwithout\s+(?:any\s+)?fee\b",
            r"\bwithout\s+(?:any\s+)?payment\b",

            # Free to apply
            r"\bfree\s+to\s+apply\b",

            # Does not require fee/payment
            r"\bdoes\s+not\s+require\s+(?:any\s+)?fee\b",
            r"\bdoes\s+not\s+require\s+(?:any\s+)?payment\b",

            # Do not require fee/payment
            r"\bdo\s+not\s+require\s+(?:any\s+)?fee\b",
            r"\bdo\s+not\s+require\s+(?:any\s+)?payment\b",

            # Fee/payment not required
            r"\b(?:fee|payment)\s+is\s+not\s+required\b",
            r"\b(?:fees|payments)\s+are\s+not\s+required\b",

            # No fees/payments
            r"\bno\s+fees\b",
            r"\bno\s+payments\b"
        ]

        for pattern in negative_patterns:

            if re.search(pattern, context):
                return True

    return False


def detect_scam_patterns(text):
    """
    Detect potential job scam and job-ad verification risks.

    Returns a dictionary compatible with app.py:
        risk_score
        concerns
        suspicious_indicators
        detected_flags
    """

    if not text or not str(text).strip():
        return {
            "risk_score": 0,
            "concerns": [],
            "suspicious_indicators": [],
            "detected_flags": []
        }

    text = str(text)
    text_lower = text.lower()

    detected_flags = []
    concerns = []
    risk_score = 0

    # ==========================================================
    # 1. UPFRONT PAYMENT REQUESTS - VERY HIGH RISK
    # ==========================================================

    payment_keywords = [
        "registration fee",
        "registration charge",
        "registration charges",
        "application fee",
        "application charges",
        "processing fee",
        "processing charges",
        "joining fee",
        "joining charges",
        "security deposit",
        "training fee",
        "verification fee",
        "documentation fee",
        "advance payment",
        "upfront payment",
        "pay before joining",
        "payment required",
        "pay to register",
        "pay for registration",
        "pay money",
        "send money",
        "deposit money"
    ]

    payment_found = []

    for keyword in payment_keywords:

        if keyword not in text_lower:
            continue

        # ------------------------------------------------------
        # IMPORTANT FIX:
        #
        # Do not flag a payment keyword when the advertisement
        # explicitly says that the payment/fee is NOT required.
        # ------------------------------------------------------

        if is_payment_keyword_negated(text_lower, keyword):
            continue

        payment_found.append(keyword)

    if payment_found:

        message = (
            "The job asks candidates to pay money before employment "
            f"({', '.join(payment_found)}). This is a major warning sign. "
            "Legitimate employers generally do not require candidates to "
            "pay registration or joining fees."
        )

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Upfront Payment Request",
            "High",
            payment_found,
            message,
            risk_score + 50
        )

    # ==========================================================
    # 2. URGENCY / PRESSURE TACTICS
    # ==========================================================

    urgency_keywords = [
        "apply immediately",
        "urgent hiring",
        "limited slots",
        "last chance",
        "join immediately",
        "immediate joining",
        "hurry up",
        "offer expires",
        "today only",
        "limited vacancies",
        "act now",
        "immediate requirement",
        "apply now",
        "join now"
    ]

    urgency_found = [
        keyword for keyword in urgency_keywords
        if keyword in text_lower
    ]

    if urgency_found:

        message = (
            "The advertisement uses urgency or pressure tactics "
            f"({', '.join(urgency_found)}). Pressure to make a quick "
            "decision can be a warning sign, so verify the employer "
            "before proceeding."
        )

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Urgency or Pressure Tactics",
            "Medium",
            urgency_found,
            message,
            risk_score + 15
        )

    # ==========================================================
    # 3. UNREALISTIC PROMISES
    # ==========================================================

    promise_keywords = [
        "guaranteed job",
        "guaranteed income",
        "100% placement",
        "100 percent placement",
        "earn money easily",
        "earn money quickly",
        "no skills required",
        "instant selection",
        "instant job",
        "guaranteed salary",
        "easy income",
        "work and earn immediately",
        "guaranteed placement",
        "job guaranteed"
    ]

    promise_found = [
        keyword for keyword in promise_keywords
        if keyword in text_lower
    ]

    if promise_found:

        message = (
            "The advertisement makes potentially unrealistic promises "
            f"({', '.join(promise_found)}). These claims should be "
            "independently verified before trusting the offer."
        )

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Unrealistic Promises",
            "High",
            promise_found,
            message,
            risk_score + 25
        )

    # ==========================================================
    # 4. SUSPICIOUS CONTACT METHODS
    # ==========================================================

    contact_keywords = [
        "contact on whatsapp",
        "whatsapp only",
        "telegram",
        "dm for details",
        "message immediately",
        "contact only on whatsapp",
        "send resume on whatsapp",
        "text on whatsapp",
        "join telegram",
        "contact through telegram",
        "message on telegram"
    ]

    contact_found = [
        keyword for keyword in contact_keywords
        if keyword in text_lower
    ]

    if contact_found:

        message = (
            "The job relies on informal communication platforms "
            f"({', '.join(contact_found)}) instead of clearly identified "
            "official company communication. Verify the employer carefully."
        )

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Suspicious Contact Method",
            "Medium",
            contact_found,
            message,
            risk_score + 15
        )

    # ==========================================================
    # 5. VERY LOW / SUSPICIOUS REQUIREMENTS
    # ==========================================================

    requirement_keywords = [
        "no experience required",
        "no qualification required",
        "anyone can apply",
        "no skills required",
        "no interview",
        "direct selection",
        "instant joining without interview",
        "no interview required",
        "no qualification needed"
    ]

    requirement_found = [
        keyword for keyword in requirement_keywords
        if keyword in text_lower
    ]

    if requirement_found:

        message = (
            "The job has unusually low or unclear entry requirements "
            f"({', '.join(requirement_found)}). Verify the recruitment "
            "process before sharing personal information."
        )

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Very Low Entry Requirements",
            "Medium",
            requirement_found,
            message,
            risk_score + 10
        )

    # ==========================================================
    # 6. UNREALISTIC HIGH-INCOME CLAIMS
    # ==========================================================

    high_salary_keywords = [
        "earn 5000 per day",
        "earn 10000 per day",
        "earn lakhs",
        "huge income",
        "unlimited income",
        "high income with no experience",
        "work from home earn",
        "earn thousands per day",
        "earn lakhs per month",
        "₹5000 per day",
        "₹10000 per day"
    ]

    salary_found = [
        keyword for keyword in high_salary_keywords
        if keyword in text_lower
    ]

    if salary_found:

        message = (
            "The advertisement promotes unusually high earnings "
            f"({', '.join(salary_found)}) without sufficient details "
            "about responsibilities or qualifications."
        )

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Potentially Unrealistic Salary Promise",
            "Medium",
            salary_found,
            message,
            risk_score + 15
        )

    # ==========================================================
    # 7. HIDDEN COMPANY INFORMATION
    # ==========================================================

    suspicious_company_terms = [
        "company details will be shared later",
        "company name confidential",
        "company name after registration",
        "details after payment",
        "company details after payment",
        "company name will be shared later"
    ]

    company_found = [
        keyword for keyword in suspicious_company_terms
        if keyword in text_lower
    ]

    if company_found:

        message = (
            "Important company information appears to be hidden or "
            f"delayed ({', '.join(company_found)}). Verify the organization "
            "before sharing personal information or making payments."
        )

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Missing or Hidden Company Information",
            "Medium",
            company_found,
            message,
            risk_score + 20
        )

    # ==========================================================
    # 8. OTP / BANK / SENSITIVE INFORMATION REQUESTS
    # ==========================================================

    sensitive_keywords = [
        "share otp",
        "send otp",
        "provide otp",
        "bank details",
        "bank account details",
        "credit card details",
        "debit card details",
        "cvv",
        "atm pin",
        "upi pin",
        "password",
        "login credentials"
    ]

    sensitive_found = [
        keyword for keyword in sensitive_keywords
        if keyword in text_lower
    ]

    if sensitive_found:

        message = (
            "The advertisement appears to request sensitive financial or "
            f"account information ({', '.join(sensitive_found)}). Never "
            "share OTPs, PINs, passwords, or similar credentials with a recruiter."
        )

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Sensitive Information Request",
            "High",
            sensitive_found,
            message,
            risk_score + 45
        )

    # ==========================================================
    # 9. SUSPICIOUS APPLICATION WEBSITE
    # ==========================================================

    urls = re.findall(
        r"https?://[^\s]+|www\.[^\s]+",
        text_lower
    )

    suspicious_domains = [
        "example.com",
        "example.org",
        "example.net",
        "test.com",
        "test.org",
        "demo.com",
        "sample.com"
    ]

    suspicious_urls = []

    for url in urls:

        clean_url = url.rstrip(".,;:)]}")

        if any(domain in clean_url for domain in suspicious_domains):
            suspicious_urls.append(clean_url)

    if suspicious_urls:

        message = (
            "The advertisement contains a placeholder or non-verifiable "
            f"application website ({', '.join(suspicious_urls)}). This does "
            "not establish that the job is a scam, but the employer should "
            "be independently verified before applying."
        )

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Suspicious Application Website",
            "High",
            suspicious_urls,
            message,
            risk_score + 35
        )

    # ==========================================================
    # 10. MISSING CRITICAL JOB INFORMATION
    # ==========================================================

    company_patterns = [
        r"\bcompany\s*[:\-]",
        r"\borganization\s*[:\-]",
        r"\bemployer\s*[:\-]",
        r"\bwe are hiring\b",
        r"\bour company\b",
        r"\bpvt\.?\s*ltd\b",
        r"\bprivate limited\b",
        r"\bltd\.?\b",
        r"\binc\.?\b",
        r"\bcorporation\b",
        r"\bsolutions\b"
    ]

    salary_patterns = [
        r"\bsalary\b",
        r"\bpay\b",
        r"\bctc\b",
        r"\bpackage\b",
        r"₹\s*[\d,]+",
        r"\brs\.?\s*[\d,]+",
        r"\binr\s*[\d,]+"
    ]

    location_patterns = [
        r"\blocation\b",
        r"\bbased in\b",
        r"\bwork location\b",
        r"\bremote\b",
        r"\bhybrid\b",
        r"\bon[- ]site\b",
        r"\bwork from home\b",
        r"\bwfh\b"
    ]

    experience_patterns = [
        r"\bexperience\b",
        r"\bfresher\b",
        r"\bfreshers\b",
        r"\byears?\s+of\s+experience\b"
    ]

    contact_patterns = [
        r"[\w\.-]+@[\w\.-]+\.\w+",
        r"\b\d{10}\b",
        r"\+\d{1,3}[\s-]?\d{7,12}",
        r"\bwhatsapp\b",
        r"\btelegram\b"
    ]

    missing_fields = []

    if not any(
        re.search(pattern, text_lower)
        for pattern in company_patterns
    ):
        missing_fields.append("company identity")

    if not any(
        re.search(pattern, text_lower)
        for pattern in salary_patterns
    ):
        missing_fields.append("salary/pay information")

    if not any(
        re.search(pattern, text_lower)
        for pattern in location_patterns
    ):
        missing_fields.append("job location/work arrangement")

    if not any(
        re.search(pattern, text_lower)
        for pattern in experience_patterns
    ):
        missing_fields.append("experience/eligibility requirements")

    if not any(
        re.search(pattern, text_lower)
        for pattern in contact_patterns
    ):
        missing_fields.append("verifiable contact information")

    if len(missing_fields) >= 3:

        message = (
            "The advertisement provides limited information needed to "
            "verify the opportunity. Missing details include: "
            + ", ".join(missing_fields)
            + ". This does not prove the job is fraudulent, but the employer "
              "should be verified through reliable sources before applying."
        )

        risk = "Medium"

        if len(missing_fields) >= 5:
            risk = "High"

        score_to_add = 25 if len(missing_fields) >= 5 else 18

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Insufficient Job Information",
            risk,
            missing_fields,
            message,
            risk_score + score_to_add
        )

    # ==========================================================
    # 11. GENERIC / MULTIPLE ROLE POSTER
    # ==========================================================

    role_keywords = [
        "data analyst",
        "business analyst",
        "data scientist",
        "data engineer",
        "software developer",
        "software engineer",
        "web developer",
        "python developer",
        "java developer",
        "copy writer",
        "copywriter",
        "digital marketing",
        "marketing executive",
        "creative designer",
        "graphic designer",
        "ui/ux designer",
        "customer support",
        "hr executive",
        "sales executive"
    ]

    roles_found = [
        role for role in role_keywords
        if role in text_lower
    ]

    if len(set(roles_found)) >= 4 and len(missing_fields) >= 3:

        message = (
            "The advertisement lists several different job roles while "
            "providing limited employer and job details. Multiple-role "
            "posters are not necessarily fraudulent, but this combination "
            "requires additional verification."
        )

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Generic or Broad Job Advertisement",
            "Medium",
            list(set(roles_found)),
            message,
            risk_score + 10
        )

    # ==========================================================
    # 12. COMBINATION RISK
    # ==========================================================

    categories = {
        flag["category"]
        for flag in detected_flags
    }

    verification_risk_categories = {
        "Insufficient Job Information",
        "Suspicious Application Website",
        "Generic or Broad Job Advertisement",
        "Missing or Hidden Company Information"
    }

    verification_count = len(
        categories.intersection(verification_risk_categories)
    )

    if verification_count >= 2 and risk_score < 50:

        message = (
            "Multiple verification concerns were found in the advertisement. "
            "The available information is not sufficient to confidently "
            "establish that the employer and job opportunity are legitimate."
        )

        risk_score = add_flag(
            detected_flags,
            concerns,
            "Multiple Verification Concerns",
            "Medium",
            verification_count,
            message,
            risk_score + 15
        )

    # ==========================================================
    # FINAL SCORE
    # ==========================================================

    risk_score = min(risk_score, 100)

    high_risk_categories = {
        "Upfront Payment Request",
        "Sensitive Information Request"
    }

    if any(
        flag["category"] in high_risk_categories
        for flag in detected_flags
    ):
        risk_score = max(risk_score, 70)

    # ==========================================================
    # RETURN FORMAT FOR app.py
    # ==========================================================

    return {
        "risk_score": risk_score,
        "concerns": concerns,
        "suspicious_indicators": concerns,
        "detected_flags": detected_flags
    }


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    sample = """
    Data Analyst – Work From Home

    Company: NovaTech Solutions
    Location: Remote
    Salary: ₹30,000 – ₹45,000 per month
    Experience: 0–2 years

    We are looking for a Data Analyst to analyze business data,
    prepare reports, create dashboards, and identify useful insights.

    Requirements:
    Basic knowledge of Excel and SQL.
    Familiarity with Power BI or Tableau.
    Freshers are welcome.

    Application:
    Interested candidates can apply through the company's official
    careers portal. No registration, application, processing, or
    training fee is required.

    Benefits:
    Flexible working hours.
    Work from home.
    Performance-based incentives.
    Professional training and development opportunities.
    """

    result = detect_scam_patterns(sample)

    print("\nRISK SCORE:", result["risk_score"])

    print("\nCONCERNS:")

    for concern in result["concerns"]:
        print("-", concern)

    print("\nDETECTED FLAGS:")

    for flag in result["detected_flags"]:
        print(flag)
import re


# ============================================================
# EXTRACT SALARY AMOUNTS
# ============================================================

def extract_salary_amount(salary_text):
    """
    Extract salary amounts and convert them into monthly values.

    Supports examples such as:
    ₹40,000 per month
    Rs 50,000/month
    5 LPA
    ₹6.5 LPA
    5 lakhs per annum
    50000 - 70000 per month
    """

    if not salary_text:
        return []

    text = str(salary_text).lower().strip()

    monthly_amounts = []

    # --------------------------------------------------------
    # LPA / LAKH / LAKHS
    # --------------------------------------------------------

    lakh_matches = re.findall(
        r'(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lac|lakh)',
        text
    )

    for value in lakh_matches:

        annual_salary = float(value) * 100000

        monthly_salary = annual_salary / 12

        monthly_amounts.append(monthly_salary)

    # --------------------------------------------------------
    # THOUSAND / K
    # --------------------------------------------------------

    thousand_matches = re.findall(
        r'(\d+(?:\.\d+)?)\s*(?:k|thousand)',
        text
    )

    for value in thousand_matches:

        amount = float(value) * 1000

        monthly_amounts.append(amount)

    # --------------------------------------------------------
    # REGULAR NUMBERS
    # --------------------------------------------------------

    # Remove numbers already associated with LPA/lakh/k
    cleaned_text = re.sub(
        r'\d+(?:\.\d+)?\s*(?:lpa|lakhs?|lac|lakh|k|thousand)',
        '',
        text
    )

    regular_matches = re.findall(
        r'₹?\s*(\d[\d,]*)',
        cleaned_text
    )

    for value in regular_matches:

        try:

            amount = int(value.replace(",", ""))

            # Ignore very small unrelated numbers
            if amount >= 1000:
                monthly_amounts.append(amount)

        except ValueError:
            continue

    return monthly_amounts


# ============================================================
# SALARY ANALYSIS
# ============================================================

def analyze_salary(salary_text, job_role="", experience=""):
    """
    Analyze whether the offered salary appears realistic.
    """

    # --------------------------------------------------------
    # MISSING SALARY
    # --------------------------------------------------------

    if not salary_text or str(salary_text).strip().lower() in [
        "not detected",
        "unknown",
        "none"
    ]:

        return {
            "assessment": "Unable to analyze",
            "reason": "Salary information could not be detected.",
            "monthly_salary": None,
            "job_role": job_role or "Unknown",
            "experience": experience or "Not specified"
        }

    # --------------------------------------------------------
    # DEFAULT VALUES
    # --------------------------------------------------------

    if not job_role:
        job_role = "Unknown"

    if not experience:
        experience = "Not specified"

    # --------------------------------------------------------
    # EXTRACT SALARY
    # --------------------------------------------------------

    salary_amounts = extract_salary_amount(
        salary_text
    )

    if not salary_amounts:

        return {
            "assessment": "Unable to analyze",
            "reason": "Could not identify a valid salary amount.",
            "monthly_salary": None,
            "job_role": job_role,
            "experience": experience
        }

    # Use highest salary mentioned
    monthly_salary = max(
        salary_amounts
    )

    # --------------------------------------------------------
    # NORMALIZE TEXT
    # --------------------------------------------------------

    role_lower = str(
        job_role
    ).lower()

    experience_lower = str(
        experience
    ).lower()

    # --------------------------------------------------------
    # SALARY ASSESSMENT
    # --------------------------------------------------------

    if monthly_salary >= 100000:

        assessment = "Very High Salary"

        reason = (
            f"The offered salary of approximately "
            f"₹{monthly_salary:,.0f} per month appears "
            f"unusually high for the mentioned role. "
            f"Verify the employer and salary details "
            f"through official sources."
        )

    elif monthly_salary >= 50000:

        assessment = "High Salary"

        if any(
            word in experience_lower
            for word in [
                "fresher",
                "freshers",
                "0 year",
                "0 years",
                "entry level",
                "entry-level",
                "no experience"
            ]
        ):

            reason = (
                f"The offered salary of approximately "
                f"₹{monthly_salary:,.0f} per month is "
                f"relatively high for an entry-level "
                f"position and should be independently verified."
            )

        else:

            reason = (
                f"The offered salary of approximately "
                f"₹{monthly_salary:,.0f} per month is high "
                f"and should be evaluated along with the "
                f"job requirements and company information."
            )

    else:

        assessment = "Reasonable Salary"

        reason = (
            f"The offered salary of approximately "
            f"₹{monthly_salary:,.0f} per month does not appear "
            f"unusually high based on the available information."
        )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {
        "assessment": assessment,
        "reason": reason,
        "monthly_salary": round(monthly_salary),
        "job_role": job_role,
        "experience": experience
    }


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":

    test_salaries = [
        "₹40,000 per month",
        "₹50,000 - ₹70,000 per month",
        "5 LPA",
        "6.5 LPA",
        "5 lakhs per annum",
        "₹80K per month"
    ]

    print("=" * 60)
    print("HIRELENS AI - SALARY ANALYSIS TEST")
    print("=" * 60)

    for salary in test_salaries:

        result = analyze_salary(
            salary,
            "Data Analyst",
            "Freshers"
        )

        print("\nSalary:", salary)
        print("Assessment:", result["assessment"])
        print("Monthly:", result["monthly_salary"])
        print("Reason:", result["reason"])
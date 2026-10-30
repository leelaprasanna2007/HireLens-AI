import re


def verify_company(company_name):
    """
    Performs basic company name validation.
    This does NOT confirm whether a company is currently hiring.
    """

    result = {
        "company": company_name,
        "status": "",
        "message": ""
    }

    # Company not detected
    if not company_name or company_name == "Not detected":

        result["status"] = "NOT AVAILABLE"
        result["message"] = (
            "Company name could not be identified from the job post."
        )

        return result

    # Too short company name
    if len(company_name.strip()) < 3:

        result["status"] = "SUSPICIOUS"
        result["message"] = (
            "The company name appears incomplete or unclear."
        )

        return result

    # Check for suspicious generic names
    suspicious_names = [
        "xyz",
        "abc",
        "unknown",
        "company",
        "test",
        "fake"
    ]

    company_lower = company_name.lower()

    for name in suspicious_names:

        if company_lower == name or company_lower.startswith(name + " "):

            result["status"] = "NEEDS VERIFICATION"
            result["message"] = (
                "The company name appears generic. Verify the employer before proceeding."
            )

            return result

    # Check if company name contains mostly valid characters
    if not re.match(r"^[A-Za-z0-9\s&.,()'-]+$", company_name):

        result["status"] = "NEEDS VERIFICATION"
        result["message"] = (
            "The company name contains unusual characters and should be verified."
        )

        return result

    # Default response
    result["status"] = "BASICALLY VALID"
    result["message"] = (
        "The company name appears properly formatted, but its legitimacy "
        "and current hiring status cannot be confirmed automatically."
    )

    return result


# Testing
if __name__ == "__main__":

    test_companies = [
        "TCS",
        "EXAM360 (INDIA)",
        "XYZ",
        "Not detected"
    ]

    for company in test_companies:

        result = verify_company(company)

        print("\nCompany:", result["company"])
        print("Status:", result["status"])
        print("Message:", result["message"])
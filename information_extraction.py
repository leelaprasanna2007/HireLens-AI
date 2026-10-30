"""
HireLens AI
Information Extraction Module

Supports:
1. Normal job descriptions
2. Job poster / OCR text

Extracted fields:
- Company
- Job Role
- Salary
- Location
- Experience
- Email
- Phone
"""

import re


# ============================================================
# COMMON HELPERS
# ============================================================

def clean_text(text):
    """Clean normal text and OCR text."""

    if not text:
        return ""

    text = str(text)

    replacements = {
        "\u00a0": " ",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\ufeff": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize different line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n[ \t]*\n+", "\n", text)

    return text.strip()


def clean_value(value):
    """Clean an extracted value."""

    if not value:
        return "Not detected"

    value = str(value).strip()

    value = value.strip(" :-|,.;")

    value = re.sub(r"\s+", " ", value)

    if len(value) < 2:
        return "Not detected"

    return value


def unique_preserve_order(items):
    """Remove duplicates while preserving order."""

    result = []

    for item in items:

        item = clean_value(item)

        if item == "Not detected":
            continue

        if item.lower() not in [x.lower() for x in result]:
            result.append(item)

    return result


# ============================================================
# EMAIL
# ============================================================

def extract_email(text):
    """Extract email from normal text or OCR text."""

    # Normal email
    pattern = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}\b"
    )

    match = re.search(pattern, text)

    if match:
        return match.group(0).strip()

    # OCR may insert spaces around @ and .
    ocr_pattern = (
        r"[A-Za-z0-9._%+-]+\s*@\s*"
        r"[A-Za-z0-9.-]+\s*\.\s*"
        r"[A-Za-z]{2,}"
    )

    match = re.search(ocr_pattern, text)

    if match:
        email = re.sub(r"\s+", "", match.group(0))
        return email

    return "Not detected"


# ============================================================
# PHONE
# ============================================================

def extract_phone(text):
    """Extract Indian phone number."""

    patterns = [

        # +91 9876543210
        r"\+91[\s.-]*([6-9]\d{9})",

        # +91-98765-43210
        r"\+91[\s.-]*([6-9]\d{4})[\s.-]*(\d{5})",

        # 98765 43210
        r"\b([6-9]\d{4})[\s.-](\d{5})\b",

        # 9876543210
        r"\b([6-9]\d{9})\b",
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if not match:
            continue

        groups = match.groups()

        if len(groups) == 2:
            number = groups[0] + groups[1]
        else:
            number = groups[0]

        number = re.sub(r"\D", "", number)

        if len(number) == 10 and number[0] in "6789":
            return number

    return "Not detected"


# ============================================================
# SALARY
# ============================================================

def extract_salary(text):
    """
    Extract salary from job descriptions and posters.

    Examples:
    ₹40,000 - ₹55,000 per month
    Rs. 40,000 - Rs. 55,000
    ₹50,000/month
    50K per month
    4 - 6 LPA
    5 LPA
    5 lakhs per annum
    Salary: ₹40,000
    """

    patterns = [

        # ₹40,000 - ₹55,000 per month
        r"((?:₹|rs\.?|inr)\s*[\d,]+"
        r"\s*(?:-|to)\s*"
        r"(?:₹|rs\.?|inr)?\s*[\d,]+"
        r"\s*(?:per\s*month|monthly|/month|pm))",

        # ₹40,000 - ₹55,000
        r"((?:₹|rs\.?|inr)\s*[\d,]+"
        r"\s*(?:-|to)\s*"
        r"(?:₹|rs\.?|inr)?\s*[\d,]+)",

        # 40,000 - 55,000 per month
        r"([\d,]+\s*(?:-|to)\s*[\d,]+"
        r"\s*(?:per\s*month|monthly|/month|pm))",

        # ₹50,000/month
        r"((?:₹|rs\.?|inr)?\s*[\d,]+"
        r"\s*(?:per\s*month|monthly|/month|pm))",

        # 50K per month
        r"((?:₹|rs\.?|inr)?\s*\d+(?:\.\d+)?\s*[kK]"
        r"\s*(?:per\s*month|monthly|/month|pm))",

        # 4 - 6 LPA
        r"(\d+(?:\.\d+)?\s*(?:-|to)\s*"
        r"\d+(?:\.\d+)?\s*(?:lpa|lakhs?|lacs?))",

        # 5 LPA
        r"(\d+(?:\.\d+)?\s*(?:lpa|lakhs?|lacs?))",

        # Salary: ₹40,000
        r"(?:salary|pay|ctc|package)"
        r"\s*[:\-]?\s*"
        r"((?:₹|rs\.?|inr)?\s*[\d,]+"
        r"(?:\s*(?:-|to)\s*"
        r"(?:₹|rs\.?|inr)?\s*[\d,]+)?)",

        # Salary: 50K
        r"(?:salary|pay|ctc|package)"
        r"\s*[:\-]?\s*"
        r"((?:₹|rs\.?|inr)?\s*\d+(?:\.\d+)?\s*[kK])",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = clean_value(match.group(1))

            if value != "Not detected":
                return value

    return "Not detected"


# ============================================================
# EXPERIENCE
# ============================================================

def extract_experience(text):
    """Extract experience requirement."""

    patterns = [

        # 0-2 years
        r"(\d+\s*(?:-|to)\s*\d+\s*(?:years?|yrs?))",

        # 2+ years
        r"(\d+\s*\+\s*(?:years?|yrs?))",

        # Minimum 2 years
        r"((?:minimum|min\.?|at\s+least)"
        r"\s*\d+\s*(?:years?|yrs?))",

        # 2 years experience
        r"(\d+\s*(?:years?|yrs?)"
        r"\s*(?:of\s+)?experience)",

        # Experience: 0-2 years
        r"(?:experience|exp)"
        r"\s*[:\-]\s*"
        r"(\d+\s*(?:-|to|\+)?\s*\d*"
        r"\s*(?:years?|yrs?))",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return clean_value(match.group(1))

    # No experience required
    no_experience_patterns = [
        r"\bno\s+experience\s+(?:is\s+)?required\b",
        r"\bno\s+experience\s+(?:is\s+)?needed\b",
        r"\bexperience\s+not\s+required\b",
        r"\bwithout\s+experience\b",
    ]

    for pattern in no_experience_patterns:

        if re.search(pattern, text, re.IGNORECASE):
            return "No experience required"

    # Freshers
    fresher_patterns = [
        r"\bfreshers?\s+can\s+apply\b",
        r"\bfreshers?\s+welcome\b",
        r"\bfreshers?\b",
        r"\bfresher\b",
    ]

    for pattern in fresher_patterns:

        if re.search(pattern, text, re.IGNORECASE):
            return "Fresher"

    return "Not detected"


# ============================================================
# LOCATION
# ============================================================

def extract_location(text):
    """Extract job location."""

    patterns = [

        # Location: Hyderabad
        r"(?:job\s*location|work\s*location|location|place)"
        r"\s*[:\-]\s*([^\n|]+)",

        # Based in Hyderabad
        r"(?:based\s+in|located\s+in)"
        r"\s+([A-Za-z][A-Za-z .,'-]{2,50})",

        # Work from Hyderabad
        r"(?:work\s+from|working\s+from)"
        r"\s+([A-Za-z][A-Za-z .,'-]{2,50})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:
            continue

        value = clean_value(match.group(1))

        if value == "Not detected":
            continue

        # Stop before another field
        value = re.split(
            r"\s+(?:salary|experience|requirements|"
            r"responsibilities|skills|email|phone|contact)"
            r"\s*[:\-]?",
            value,
            maxsplit=1,
            flags=re.IGNORECASE
        )[0]

        value = clean_value(value)

        if value != "Not detected":
            return value

    # Common locations
    known_locations = [
        "Visakhapatnam",
        "Vishakhapatnam",
        "Bengaluru",
        "Bangalore",
        "Hyderabad",
        "Chennai",
        "Mumbai",
        "Pune",
        "Kolkata",
        "Vijayawada",
        "Srikakulam",
        "Coimbatore",
        "Vizag",
        "Ambattur",
        "New Delhi",
        "Delhi",
        "Remote",
        "Work From Home",
        "WFH",
    ]

    for location in known_locations:

        if re.search(
            r"\b" + re.escape(location) + r"\b",
            text,
            re.IGNORECASE
        ):
            return location

    return "Not detected"


# ============================================================
# JOB ROLE
# ============================================================

def extract_job_role(text):
    """
    Extract one or multiple job roles.

    Example poster:

    Copy writer
    Digital marketing
    Data analyst
    Creative designer

    Output:

    Copy Writer, Digital Marketing, Data Analyst, Creative Designer
    """

    detected_roles = []

    # --------------------------------------------------------
    # Known roles
    # --------------------------------------------------------

    roles = [
        "Senior Data Analyst",
        "Junior Data Analyst",
        "Data Analyst",

        "Senior Business Analyst",
        "Junior Business Analyst",
        "Business Analyst",

        "Senior Data Scientist",
        "Junior Data Scientist",
        "Data Scientist",

        "Senior Data Engineer",
        "Junior Data Engineer",
        "Data Engineer",

        "Machine Learning Engineer",
        "Machine Learning Developer",

        "AI Engineer",
        "AI Developer",

        "Senior Software Engineer",
        "Junior Software Engineer",
        "Software Engineer",

        "Senior Software Developer",
        "Junior Software Developer",
        "Software Developer",

        "Full Stack Developer",
        "Full-Stack Developer",

        "Frontend Developer",
        "Front End Developer",
        "Front-End Developer",

        "Backend Developer",
        "Back End Developer",
        "Back-End Developer",

        "Python Developer",
        "Java Developer",
        "Web Developer",

        "Senior Data Entry Executive",
        "Junior Data Entry Executive",
        "Data Entry Executive",
        "Data Entry Operator",
        "Data Entry Clerk",
        "Data Entry",

        "HR Executive",
        "HR Recruiter",
        "Human Resources Executive",
        "Recruiter",

        "Sales Executive",
        "Sales Manager",

        "Marketing Executive",
        "Digital Marketing Executive",
        "Digital Marketing",

        "Customer Support Executive",
        "Customer Service Executive",
        "Customer Support",

        "Financial Analyst",
        "Accounts Executive",
        "Accountant",

        "UI/UX Designer",
        "UI UX Designer",
        "UI Designer",
        "UX Designer",

        "Graphic Designer",
        "Creative Designer",

        "Content Writer",
        "Copy Writer",
        "Copywriter",

        "Project Manager",
        "Product Manager",

        "Receptionist",
        "Office Assistant",
        "Branch Manager",

        "Intern",
        "Trainee",
    ]

    # Longest first
    roles = sorted(
        roles,
        key=len,
        reverse=True
    )

    # --------------------------------------------------------
    # Search entire OCR/job text
    # --------------------------------------------------------

    for role in roles:

        pattern = r"(?<![A-Za-z])" + re.escape(role) + r"(?![A-Za-z])"

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for match in matches:

            # Convert OCR/text casing into clean title casing
            cleaned_role = clean_value(match)

            if cleaned_role != "Not detected":
                detected_roles.append(cleaned_role)

    # --------------------------------------------------------
    # Explicit "Job Role:" / "Position:" field
    # --------------------------------------------------------

    labelled_patterns = [

        r"(?:job\s*role|job\s*title|position|designation)"
        r"\s*[:\-]\s*([^\n|]+)",
    ]

    for pattern in labelled_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = clean_value(match.group(1))

            if value != "Not detected":

                # Remove other field text if present
                value = re.split(
                    r"\s+(?:salary|location|experience|"
                    r"email|phone|contact)"
                    r"\s*[:\-]?",
                    value,
                    maxsplit=1,
                    flags=re.IGNORECASE
                )[0]

                # If this is a role not already found,
                # add it at the beginning.
                if value.lower() not in [
                    x.lower() for x in detected_roles
                ]:
                    detected_roles.insert(0, value)

    # Remove duplicates
    detected_roles = unique_preserve_order(detected_roles)

    # --------------------------------------------------------
    # Return all roles
    # --------------------------------------------------------

    if detected_roles:
        return ", ".join(detected_roles)

    return "Not detected"


# ============================================================
# COMPANY
# ============================================================

def extract_company(text):
    """
    Extract company name.

    Important:
    Words such as LOGO are NOT treated as company names.

    We only return a company when there is reasonable evidence.
    """

    # --------------------------------------------------------
    # Explicit company label
    # --------------------------------------------------------

    patterns = [

        r"(?:company\s*name|company|organization|"
        r"organisation|employer)"
        r"\s*[:\-]\s*([^\n|]+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = clean_value(match.group(1))

            if value == "Not detected":
                continue

            # Stop at another field
            value = re.split(
                r"\s+(?:job\s*role|job\s*title|"
                r"position|role|salary|location|"
                r"experience|email|phone|contact)"
                r"\s*[:\-]?",
                value,
                maxsplit=1,
                flags=re.IGNORECASE
            )[0]

            value = clean_value(value)

            # Do not accept generic OCR words
            invalid_names = {
                "logo",
                "company",
                "organization",
                "organisation",
                "employer",
                "we are hiring",
                "hiring",
                "join our team",
                "job positions",
            }

            if value.lower() not in invalid_names:
                return value

    # --------------------------------------------------------
    # "ABC Technologies is hiring"
    # --------------------------------------------------------

    hiring_patterns = [

        r"\b([A-Z][A-Za-z0-9&.,' -]{2,60}?)"
        r"\s+is\s+hiring\b",

        r"\b([A-Z][A-Za-z0-9&.,' -]{2,60}?)"
        r"\s+are\s+hiring\b",
    ]

    for pattern in hiring_patterns:

        match = re.search(pattern, text)

        if match:

            value = clean_value(match.group(1))

            invalid_words = [
                "we",
                "we are",
                "company",
                "the company",
                "logo",
            ]

            if value.lower() not in invalid_words:
                return value

    # --------------------------------------------------------
    # Company suffix detection
    # --------------------------------------------------------

    suffix_pattern = (
        r"\b("
        r"[A-Z][A-Za-z0-9&.,' -]{2,50}"
        r"\s+"
        r"(?:Technologies|Technology|Tech|Solutions|"
        r"Services|Systems|Labs|Industries|"
        r"Consulting|Consultancy|Limited|Ltd|"
        r"Private\s+Limited|Pvt\.?\s+Ltd\.?|"
        r"Corporation|Corp\.?|Inc\.?|LLP|Group)"
        r")\b"
    )

    matches = re.findall(
        suffix_pattern,
        text
    )

    for value in matches:

        value = clean_value(value)

        if value != "Not detected":
            return value

    # --------------------------------------------------------
    # Do NOT guess from:
    # LOGO
    # example.com
    # random poster heading
    # --------------------------------------------------------

    return "Not detected"


# ============================================================
# MAIN FUNCTION
# ============================================================

def extract_job_information(text):
    """
    Main function used by app.py.

    Returns exactly the fields expected by HireLens AI.
    """

    result = {
        "company": "Not detected",
        "job_role": "Not detected",
        "salary": "Not detected",
        "location": "Not detected",
        "experience": "Not detected",
        "email": "Not detected",
        "phone": "Not detected",
    }

    if not text:
        return result

    text = clean_text(text)

    if not text:
        return result

    # Extract fields
    result["company"] = extract_company(text)

    result["job_role"] = extract_job_role(text)

    result["salary"] = extract_salary(text)

    result["location"] = extract_location(text)

    result["experience"] = extract_experience(text)

    result["email"] = extract_email(text)

    result["phone"] = extract_phone(text)

    return result


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def extract_information(text):
    """
    Older function name.
    """

    return extract_job_information(text)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("HIRELENS AI - INFORMATION EXTRACTION TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # TEST 1: NORMAL JOB DESCRIPTION
    # --------------------------------------------------------

    normal_job = """
    ABC Technologies is hiring.

    Job Role: Data Analyst
    Salary: ₹40,000 - ₹60,000 per month
    Location: Hyderabad
    Experience: 0-2 years

    Freshers can apply.

    Email: hr@abctech.com
    Contact: 9876543210
    """

    print("\nTEST 1 - NORMAL JOB DESCRIPTION")
    print("-" * 60)

    result = extract_job_information(normal_job)

    for key, value in result.items():
        print(f"{key}: {value}")

    # --------------------------------------------------------
    # TEST 2: POSTER STYLE
    # --------------------------------------------------------

    poster_text = """
    LOGO

    WE ARE HIRING!
    JOIN OUR TEAM

    JOB POSITIONS

    Copy writer
    Digital marketing
    Data analyst
    Creative designer

    APPLY NOW

    Send your resume:
    www.example.com
    """

    print("\nTEST 2 - POSTER STYLE")
    print("-" * 60)

    result = extract_job_information(poster_text)

    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 60)
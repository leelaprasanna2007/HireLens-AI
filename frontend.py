import streamlit as st
import tempfile
import os

from information_extraction import extract_job_information
from advanced_scam_detection import detect_scam_patterns
from salary_analysis import analyze_salary
from image_ocr import extract_text_from_image
from chatbot_response import generate_chatbot_response


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="ScamShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #07111f;
    color: #e5e7eb;
}

/* Hide Streamlit branding */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}


/* Sidebar */

[data-testid="stSidebar"] {
    background-color: #091522;
    border-right: 1px solid #1f2937;
}


/* Main title */

.logo-title {
    font-size: 28px;
    font-weight: 700;
    color: white;
}

.logo-green {
    color: #38d996;
}


/* Sidebar menu */

.menu-item {
    padding: 14px;
    margin-bottom: 8px;
    border-radius: 10px;
    color: #cbd5e1;
    font-size: 16px;
}

.menu-active {
    background: linear-gradient(90deg,#123f36,#0d2a25);
    color: #4ade80;
    padding: 14px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 600;
}


/* Header */

.header-box {
    background-color: #0b1726;
    padding: 18px 25px;
    border-radius: 15px;
    border: 1px solid #1f3347;
}


/* Chat bubbles */

.bot-message {
    background-color: #111e2e;
    padding: 16px;
    border-radius: 15px;
    border: 1px solid #24364b;
    margin-bottom: 12px;
    max-width: 70%;
}

.user-message {
    background: linear-gradient(135deg,#0c3029,#123f36);
    padding: 16px;
    border-radius: 15px;
    border: 1px solid #1f6b58;
    margin-bottom: 12px;
}


/* Analysis cards */

.analysis-card {
    background-color: #0d1928;
    border: 1px solid #213449;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
}


/* Low risk */

.low-risk {
    background: linear-gradient(135deg,#0b332b,#10271f);
    border: 1px solid #237a5c;
    padding: 22px;
    border-radius: 15px;
}


/* High risk */

.high-risk {
    background: linear-gradient(135deg,#3b1518,#241014);
    border: 1px solid #7f3035;
    padding: 22px;
    border-radius: 15px;
}


/* Medium risk */

.medium-risk {
    background: linear-gradient(135deg,#3b2b12,#251d0d);
    border: 1px solid #80611c;
    padding: 22px;
    border-radius: 15px;
}


/* Information rows */

.info-row {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid #1f3347;
}


/* Recommendation */

.recommendation-card {
    background-color: #101c2b;
    border: 1px solid #263a50;
    padding: 18px;
    border-radius: 12px;
}


/* Buttons */

.stButton button {
    background: linear-gradient(90deg,#087f5b,#0fa36f);
    color: white;
    border: none;
    border-radius: 10px;
    height: 45px;
    font-weight: 600;
}

.stButton button:hover {
    background: linear-gradient(90deg,#0fa36f,#19b879);
}


/* Input */

.stTextArea textarea {
    background-color: #0d1928 !important;
    color: white !important;
    border: 1px solid #263a50 !important;
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "job_text" not in st.session_state:
    st.session_state.job_text = ""

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

with st.sidebar:

    st.markdown("""
    <div class="logo-title">
    🛡️ ScamShield <span class="logo-green">AI</span>
    </div>
    <p style="color:#94a3b8;">Job Scam Detection Assistant</p>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="menu-active">💬 New Analysis</div>
    <div class="menu-item">🕘 History</div>
    <div class="menu-item">🛡️ Safety Tips</div>
    <div class="menu-item">❓ How It Works</div>
    <div class="menu-item">🤖 About Chitti</div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="analysis-card">
    <h4 style="color:#4ade80;">🛡️ Stay Safe Online</h4>
    <p style="color:#94a3b8;">
    ScamShield AI helps you identify potential job scams before it's too late.
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    ### 🤖 Chitti AI
    🟢 Online

    Your AI Job Scam Detection Assistant
    """)


# -------------------------------------------------
# HEADER
# -------------------------------------------------

col1, col2 = st.columns([8, 2])

with col1:

    st.markdown("""
    <div class="header-box">
        <h2 style="margin-bottom:5px;">🤖 Chitti <span style="font-size:14px;color:#4ade80;">● Online</span></h2>
        <p style="color:#94a3b8;margin:0;">
        Your AI Job Scam Detection Assistant
        </p>
    </div>
    """, unsafe_allow_html=True)


with col2:

    if st.button("🗑 Clear Chat", use_container_width=True):

        st.session_state.job_text = ""
        st.session_state.analysis_result = None

        st.rerun()


st.markdown("<br>", unsafe_allow_html=True)


# -------------------------------------------------
# MAIN LAYOUT
# -------------------------------------------------

left, right = st.columns([2.2, 1])


# =================================================
# LEFT SIDE - CHAT
# =================================================

with left:

    st.markdown("""
    <div class="bot-message">
    <b>🤖 Chitti</b><br><br>
    Hello! I'm Chitti 👋<br>
    Send me a job description or upload a job poster image,
    and I'll analyze it for potential scam indicators.
    </div>
    """, unsafe_allow_html=True)


    # ---------------------------------------------
    # JOB INPUT
    # ---------------------------------------------

    job_description = st.text_area(
        "Job Description",
        value=st.session_state.job_text,
        placeholder="Paste the job description here...",
        height=180,
        label_visibility="collapsed"
    )


    uploaded_file = st.file_uploader(
        "Upload Job Poster",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )


    analyze_button = st.button(
        "🔍 Analyze Job Opportunity",
        use_container_width=True
    )


    # =================================================
    # ANALYZE BUTTON
    # =================================================

    if analyze_button:

        job_text = job_description


        # ---------------------------------------------
        # IMAGE OCR
        # ---------------------------------------------

        if uploaded_file is not None:

            with st.spinner("📷 Extracting text from image..."):

                suffix = os.path.splitext(uploaded_file.name)[1]

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                ) as temp_file:

                    temp_file.write(uploaded_file.getvalue())

                    image_path = temp_file.name


                extracted_text = extract_text_from_image(image_path)

                job_text = extracted_text

                os.remove(image_path)


        # ---------------------------------------------
        # VALIDATION
        # ---------------------------------------------

        if not job_text.strip():

            st.warning(
                "⚠️ Please enter a job description or upload an image."
            )


        else:

            st.session_state.job_text = job_text


            with st.spinner("🤖 Chitti is analyzing the job opportunity..."):

                try:

                    # ---------------------------------
                    # INFORMATION EXTRACTION
                    # ---------------------------------

                    job_info = extract_job_information(job_text)


                    # ---------------------------------
                    # SCAM DETECTION
                    # ---------------------------------

                    scam_flags = detect_scam_patterns(job_text)


                    # ---------------------------------
                    # SALARY ANALYSIS
                    # ---------------------------------

                    salary_result = analyze_salary(
                        job_info.get("salary", "Not detected")
                    )


                    # ---------------------------------
                    # CHATBOT RESPONSE
                    # ---------------------------------

                    chatbot_response = generate_chatbot_response(
                        job_info,
                        scam_flags
                    )


                    # ---------------------------------
                    # SAVE RESULTS
                    # ---------------------------------

                    st.session_state.analysis_result = {

                        "job_text": job_text,

                        "job_info": job_info,

                        "scam_flags": scam_flags,

                        "salary_result": salary_result,

                        "chatbot_response": chatbot_response

                    }


                except Exception as e:

                    st.error(f"Analysis Error: {e}")


    # =================================================
    # DISPLAY JOB TEXT
    # =================================================

    if st.session_state.analysis_result:

        result = st.session_state.analysis_result


        st.markdown("""
        <div class="bot-message">
        <b>🤖 Chitti</b><br><br>
        🔄 Analyzing the job opportunity...
        </div>
        """, unsafe_allow_html=True)


        st.markdown("### 📄 Job Description")

        st.markdown(
            f"""
            <div class="user-message">
            {result["job_text"].replace(chr(10), "<br>")}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ---------------------------------------------
        # CHATBOT RESPONSE
        # ---------------------------------------------

        st.markdown("### 🤖 Chitti Analysis")

        response = result["chatbot_response"]

        if isinstance(response, str):

            st.markdown(
                f"""
                <div class="bot-message">
                {response.replace(chr(10), "<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.info(str(response))


# =================================================
# RIGHT SIDE - ANALYSIS SUMMARY
# =================================================

with right:

    st.markdown("## 📊 Analysis Summary")


    if st.session_state.analysis_result:

        result = st.session_state.analysis_result

        job_info = result["job_info"]

        scam_flags = result["scam_flags"]


        # ---------------------------------------------
        # RISK CALCULATION
        # ---------------------------------------------

        risk_count = len(scam_flags) if scam_flags else 0


        if risk_count == 0:

            risk_level = "LOW RISK"

            st.markdown("""
            <div class="low-risk">
            <h2 style="color:#4ade80;">🛡️ LOW RISK</h2>
            <p>This job opportunity appears reasonably safe.</p>
            </div>
            """, unsafe_allow_html=True)


        elif risk_count <= 2:

            risk_level = "MEDIUM RISK"

            st.markdown("""
            <div class="medium-risk">
            <h2 style="color:#facc15;">⚠️ MEDIUM RISK</h2>
            <p>Some suspicious indicators were detected.</p>
            </div>
            """, unsafe_allow_html=True)


        else:

            risk_level = "HIGH RISK"

            st.markdown("""
            <div class="high-risk">
            <h2 style="color:#f87171;">🚨 HIGH RISK</h2>
            <p>This job opportunity contains multiple suspicious indicators.</p>
            </div>
            """, unsafe_allow_html=True)


        st.markdown("<br>", unsafe_allow_html=True)


        # ---------------------------------------------
        # RISK INDICATORS
        # ---------------------------------------------

        st.markdown("### 🚩 Risk Indicators")

        if scam_flags:

            for flag in scam_flags:

                if isinstance(flag, dict):

                    message = (
                        flag.get("message")
                        or flag.get("reason")
                        or flag.get("indicator")
                        or "Suspicious indicator detected"
                    )

                    st.markdown(f"🔴 {message}")

                else:

                    st.markdown(f"🔴 {flag}")

        else:

            st.success("No major suspicious indicators detected.")


        st.markdown("<br>", unsafe_allow_html=True)


        # ---------------------------------------------
        # EXTRACTED INFORMATION
        # ---------------------------------------------

        st.markdown("### 📌 Extracted Information")

        st.markdown(
            f"""
            <div class="analysis-card">

            <div class="info-row">
            <b>Company</b>
            <span>{job_info.get("company", "Not detected")}</span>
            </div>

            <div class="info-row">
            <b>Role</b>
            <span>{job_info.get("job_role", "Not detected")}</span>
            </div>

            <div class="info-row">
            <b>Experience</b>
            <span>{job_info.get("experience", "Not detected")}</span>
            </div>

            <div class="info-row">
            <b>Salary</b>
            <span>{job_info.get("salary", "Not detected")}</span>
            </div>

            <div class="info-row">
            <b>Location</b>
            <span>{job_info.get("location", "Not detected")}</span>
            </div>

            <div class="info-row">
            <b>Email</b>
            <span>{job_info.get("email", "Not detected")}</span>
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # ---------------------------------------------
        # RECOMMENDATION
        # ---------------------------------------------

        st.markdown("### 🛡️ Recommendation")

        if risk_level == "HIGH RISK":

            recommendation = """
            Be careful! Avoid paying registration fees or sharing
            sensitive personal information. Verify the company before applying.
            """

        elif risk_level == "MEDIUM RISK":

            recommendation = """
            Some suspicious indicators were found.
            Verify the company and job details before proceeding.
            """

        else:

            recommendation = """
            Everything looks reasonably safe based on the available information.
            Still verify the company through its official website before applying.
            """


        st.markdown(
            f"""
            <div class="recommendation-card">
            {recommendation}
            </div>
            """,
            unsafe_allow_html=True
        )


    else:

        st.markdown("""
        <div class="analysis-card">
        <p style="color:#94a3b8;">
        Your analysis results will appear here.
        </p>
        </div>
        """, unsafe_allow_html=True)


# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <p style="text-align:center;color:#64748b;font-size:13px;">
    ScamShield AI provides analysis based on patterns and data.
    Always verify job opportunities independently.
    </p>
    """,
    unsafe_allow_html=True
)
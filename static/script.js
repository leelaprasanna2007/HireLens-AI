/* =========================================================
   HIRELENS AI - MAIN JAVASCRIPT
   ========================================================= */


/* =========================================================
   GLOBAL VARIABLES
   ========================================================= */

let selectedImage = null;
let isAnalyzing = false;


/* =========================================================
   PAGE INITIALIZATION
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    setupUpload();
    setupAnalyzeButton();
    setupChitti();

});


/* =========================================================
   DASHBOARD
   ========================================================= */

function openDashboard() {

    const landingPage =
        document.getElementById("landingPage");

    const dashboard =
        document.getElementById("dashboard");

    if (landingPage) {
        landingPage.classList.add("hidden");
    }

    if (dashboard) {
        dashboard.classList.remove("hidden");
    }

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


/* =========================================================
   FEATURES SCROLL
   ========================================================= */

function scrollToFeatures() {

    const features =
        document.getElementById("features");

    if (features) {

        features.scrollIntoView({
            behavior: "smooth"
        });

    }
}


/* =========================================================
   IMAGE UPLOAD
   ========================================================= */

function setupUpload() {

    const uploadBtn =
        document.getElementById("uploadBtn");

    const jobPoster =
        document.getElementById("jobPoster");

    const fileName =
        document.getElementById("fileName");


    if (!uploadBtn || !jobPoster) {
        return;
    }


    /* Upload button opens file selector */

    uploadBtn.addEventListener("click", function () {

        if (isAnalyzing) {
            return;
        }

        jobPoster.click();

    });


    /* When image is selected */

    jobPoster.addEventListener("change", function () {

        if (!this.files || this.files.length === 0) {

            selectedImage = null;

            if (fileName) {
                fileName.textContent = "";
            }

            return;
        }


        const file = this.files[0];

        selectedImage = file;


        if (fileName) {

            fileName.textContent =
                "Selected: " + file.name;

        }

    });

}


/* =========================================================
   ANALYZE BUTTON
   ========================================================= */

function setupAnalyzeButton() {

    const analyzeBtn =
        document.getElementById("analyzeBtn");


    if (!analyzeBtn) {
        return;
    }


    analyzeBtn.addEventListener("click", function () {

        analyzeJob();

    });

}


/* =========================================================
   MAIN ANALYSIS FUNCTION
   ========================================================= */

async function analyzeJob() {

    if (isAnalyzing) {
        return;
    }


    const jobDescription =
        document.getElementById("jobDescription");

    const analyzeBtn =
        document.getElementById("analyzeBtn");


    const jobText =
        jobDescription
            ? jobDescription.value.trim()
            : "";


    /*
       User must provide either:
       1. Job description
       OR
       2. Job poster
    */

    if (!jobText && !selectedImage) {

        alert(
            "Please enter a job description or upload a job poster."
        );

        return;
    }


    /* =====================================================
       START ANALYSIS
       ===================================================== */

    isAnalyzing = true;


    if (analyzeBtn) {

        analyzeBtn.disabled = true;

        analyzeBtn.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';

    }


    showAnalysisLoading();


    /* Update top status */

    const jobAnalysisStatus =
        document.getElementById("jobAnalysisStatus");

    if (jobAnalysisStatus) {
        jobAnalysisStatus.textContent = "Analyzing...";
    }


    /* =====================================================
       CREATE FORM DATA
       ===================================================== */

    const formData = new FormData();


    if (jobText) {

        formData.append(
            "job_text",
            jobText
        );

    }


    if (selectedImage) {

        formData.append(
            "image",
            selectedImage
        );

    }


    try {

        /* =================================================
           SEND TO FLASK
           ================================================= */

        const response =
            await fetch("/analyze", {

                method: "POST",

                body: formData

            });


        /* HTTP error */

        if (!response.ok) {

            throw new Error(
                "Server returned status " +
                response.status
            );

        }


        const data =
            await response.json();


        /* Backend error */

        if (
            data.success === false ||
            data.error
        ) {

            throw new Error(
                data.error ||
                data.message ||
                "Analysis failed."
            );

        }


        /* =================================================
           DISPLAY RESULTS
           ================================================= */

        displayAnalysisResults(data);


        /* Analysis complete */

        updateAnalysisCompleteMessage();


        if (jobAnalysisStatus) {
            jobAnalysisStatus.textContent = "Complete";
        }


    } catch (error) {

        console.error(
            "HireLens Analysis Error:",
            error
        );


        showAnalysisError(
            error.message
        );


        if (jobAnalysisStatus) {
            jobAnalysisStatus.textContent = "Error";
        }


    } finally {

        isAnalyzing = false;


        if (analyzeBtn) {

            analyzeBtn.disabled = false;

            analyzeBtn.innerHTML =
                '<i class="fa-solid fa-magnifying-glass"></i> Analyze Job';

        }

    }

}


/* =========================================================
   ANALYSIS LOADING STATE
   ========================================================= */

function showAnalysisLoading() {

    const loadingMessage =
        document.getElementById("loadingMessage");

    const loadingText =
        document.getElementById("loadingText");


    /* Main loading box */

    if (loadingMessage) {

        loadingMessage.classList.remove("hidden");

    }


    if (loadingText) {

        loadingText.textContent =
            "Analyzing your job description...";

    }


    /* Right preview */

    const statusCard =
        document.getElementById(
            "analysisStatusCard"
        );

    const statusTitle =
        document.getElementById(
            "analysisStatusTitle"
        );

    const statusMessage =
        document.getElementById(
            "analysisStatusMessage"
        );


    if (statusCard) {

        statusCard.classList.add(
            "analyzing"
        );

    }


    if (statusTitle) {

        statusTitle.textContent =
            "ANALYZING...";

        statusTitle.classList.add(
            "analyzing-text"
        );

    }


    if (statusMessage) {

        statusMessage.textContent =
            "HireLens AI is checking the job details. Please wait...";

    }


    /* Risk score */

    const riskScore =
        document.getElementById("riskScore");

    const riskLevel =
        document.getElementById("riskLevel");


    if (riskScore) {
        riskScore.textContent = "...";
    }


    if (riskLevel) {
        riskLevel.textContent = "ANALYZING";
    }


    /* Clear previous preview */

    const riskIndicators =
        document.getElementById(
            "riskIndicators"
        );

    if (riskIndicators) {

        riskIndicators.innerHTML = `
            <p class="empty-text">
                🔄 Checking risk indicators...
            </p>
        `;

    }


    const recommendation =
        document.getElementById(
            "recommendation"
        );

    if (recommendation) {

        recommendation.textContent =
            "Analyzing the job opportunity...";

    }


    const salaryAnalysis =
        document.getElementById(
            "salaryAnalysis"
        );

    if (salaryAnalysis) {

        salaryAnalysis.innerHTML = `
            <p class="empty-text">
                🔄 Analyzing salary information...
            </p>
        `;

    }

}


/* =========================================================
   ANALYSIS COMPLETE
   ========================================================= */

function updateAnalysisCompleteMessage() {

    const loadingMessage =
        document.getElementById(
            "loadingMessage"
        );

    if (loadingMessage) {

        loadingMessage.classList.add(
            "hidden"
        );

    }


    const statusCard =
        document.getElementById(
            "analysisStatusCard"
        );

    const statusTitle =
        document.getElementById(
            "analysisStatusTitle"
        );

    const statusMessage =
        document.getElementById(
            "analysisStatusMessage"
        );


    if (statusCard) {

        statusCard.classList.remove(
            "analyzing"
        );

    }


    if (statusTitle) {

        statusTitle.textContent =
            "ANALYSIS COMPLETE ✓";

        statusTitle.classList.remove(
            "analyzing-text"
        );

    }


    if (statusMessage) {

        statusMessage.textContent =
            "Your job analysis is ready.";

    }

}


/* =========================================================
   ANALYSIS ERROR
   ========================================================= */

function showAnalysisError(message) {

    const loadingMessage =
        document.getElementById(
            "loadingMessage"
        );

    if (loadingMessage) {

        loadingMessage.classList.add(
            "hidden"
        );

    }


    const statusCard =
        document.getElementById(
            "analysisStatusCard"
        );

    const statusTitle =
        document.getElementById(
            "analysisStatusTitle"
        );

    const statusMessage =
        document.getElementById(
            "analysisStatusMessage"
        );


    if (statusCard) {

        statusCard.classList.remove(
            "analyzing"
        );

    }


    if (statusTitle) {

        statusTitle.textContent =
            "ANALYSIS FAILED";

        statusTitle.classList.remove(
            "analyzing-text"
        );

    }


    if (statusMessage) {

        statusMessage.textContent =
            message ||
            "Something went wrong while analyzing the job.";

    }


    const riskIndicators =
        document.getElementById(
            "riskIndicators"
        );


    if (riskIndicators) {

        riskIndicators.innerHTML = `
            <p class="empty-text">
                ⚠️ ${escapeHTML(
                    message ||
                    "Unable to analyze the job."
                )}
            </p>
        `;

    }

}


/* =========================================================
   DISPLAY ALL ANALYSIS RESULTS
   ========================================================= */

function displayAnalysisResults(data) {

    console.log(
        "HireLens Analysis Result:",
        data
    );


    /* =====================================================
       RESULT SECTION
       ===================================================== */

    const resultSection =
        document.getElementById(
            "resultSection"
        );


    if (resultSection) {

        resultSection.classList.remove(
            "hidden"
        );

    }


    /* =====================================================
       EXPLAINABLE AI
       ===================================================== */

    displayExplainableAI(
        data.explainable_ai ||
        data.explainableAI ||
        data.explanation ||
        null
    );


    /* =====================================================
       JOB INFORMATION
       ===================================================== */

    displayJobInformation(
        data.job_information ||
        data.jobInformation ||
        data.extracted_information ||
        data.extracted_data ||
        null
    );


    /* =====================================================
       RISK INFORMATION
       ===================================================== */

    displayRiskInformation(data);


    /* =====================================================
       RECOMMENDATION
       ===================================================== */

    displayRecommendation(
        data.recommendation ||
        data.ai_recommendation ||
        data.safety_recommendation ||
        null
    );


    /* =====================================================
       SALARY
       ===================================================== */

    displaySalaryAnalysis(
        data.salary_analysis ||
        data.salaryAnalysis ||
        null
    );


    /* =====================================================
       SCROLL TO RESULTS
       ===================================================== */

    setTimeout(function () {

        if (resultSection) {

            resultSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }

    }, 300);

}


/* =========================================================
   EXPLAINABLE AI
   ========================================================= */

function displayExplainableAI(explanation) {

    const container =
        document.getElementById(
            "explainableAI"
        );


    if (!container) {
        return;
    }


    if (!explanation) {

        container.innerHTML = `
            <p class="empty-text">
                No explainable AI information was returned.
            </p>
        `;

        return;
    }


    let html = "";


    /* Summary */

    if (explanation.summary) {

        html += `
            <div class="result-block">
                <h3>Summary</h3>
                <p>
                    ${formatText(
                        explanation.summary
                    )}
                </p>
            </div>
        `;

    }


    /* Risk factors */

    if (
        explanation.risk_factors &&
        Array.isArray(
            explanation.risk_factors
        )
    ) {

        html += `
            <div class="result-block">
                <h3>Risk Factors</h3>
                <ul>
        `;


        explanation.risk_factors.forEach(
            function (factor) {

                html += `
                    <li>
                        ${formatText(
                            typeof factor === "string"
                                ? factor
                                : factor.details ||
                                  factor.message ||
                                  factor.category ||
                                  JSON.stringify(factor)
                        )}
                    </li>
                `;

            }
        );


        html += `
                </ul>
            </div>
        `;

    }


    /* Evidence */

    if (explanation.evidence) {

        html += `
            <div class="result-block">
                <h3>Evidence</h3>
                <p>
                    ${formatText(
                        explanation.evidence
                    )}
                </p>
            </div>
        `;

    }


    /* Final explanation */

    if (explanation.final_explanation) {

        html += `
            <div class="result-block">
                <h3>Why this result?</h3>
                <p>
                    ${formatText(
                        explanation.final_explanation
                    )}
                </p>
            </div>
        `;

    }


    if (!html) {

        html = `
            <p class="empty-text">
                ${formatText(
                    typeof explanation === "string"
                        ? explanation
                        : JSON.stringify(
                            explanation
                        )
                )}
            </p>
        `;

    }


    container.innerHTML = html;

}


/* =========================================================
   JOB INFORMATION
   ========================================================= */

function displayJobInformation(info) {

    const container =
        document.getElementById(
            "jobInformation"
        );


    if (!container) {
        return;
    }


    if (!info) {

        container.innerHTML = `
            <p class="empty-text">
                No job information was extracted.
            </p>
        `;

        return;
    }


    let html =
        '<div class="job-info-grid">';


    const fields = [
        ["Company", "company"],
        ["Job Role", "job_role"],
        ["Salary", "salary"],
        ["Location", "location"],
        ["Experience", "experience"],
        ["Email", "email"],
        ["Phone", "phone"]
    ];


    fields.forEach(
        function ([label, key]) {

            let value =
                info[key];


            if (
                value === undefined ||
                value === null ||
                value === ""
            ) {

                value = "Not detected";

            }


            html += `
                <div class="job-info-item">
                    <span>${label}</span>
                    <strong>
                        ${escapeHTML(
                            String(value)
                        )}
                    </strong>
                </div>
            `;

        }
    );


    html += "</div>";


    container.innerHTML = html;

}


/* =========================================================
   RISK INFORMATION
   ========================================================= */

function displayRiskInformation(data) {

    const riskScore =
        document.getElementById(
            "riskScore"
        );

    const riskLevel =
        document.getElementById(
            "riskLevel"
        );

    const riskIndicators =
        document.getElementById(
            "riskIndicators"
        );


    /* =====================================================
       SCORE
       ===================================================== */

    let score =
        data.risk_score;


    if (
        score === undefined ||
        score === null
    ) {

        score =
            data.riskScore;

    }


    if (
        score === undefined ||
        score === null
    ) {

        score = "--";

    }


    if (riskScore) {

        riskScore.textContent =
            String(score);

    }


    /* =====================================================
       LEVEL
       ===================================================== */

    let level =
        data.risk_level;


    if (
        level === undefined ||
        level === null
    ) {

        level =
            data.riskLevel;

    }


    if (
        level === undefined ||
        level === null
    ) {

        level = "UNKNOWN";

    }


    if (riskLevel) {

        riskLevel.textContent =
            String(level).toUpperCase();

    }


    /* =====================================================
       FLAGS
       ===================================================== */

    let flags =
        data.detected_flags ||
        data.detectedFlags ||
        data.risk_indicators ||
        data.riskIndicators ||
        [];


    if (!Array.isArray(flags)) {

        flags = [];

    }


    if (!riskIndicators) {
        return;
    }


    if (flags.length === 0) {

        riskIndicators.innerHTML = `
            <p class="empty-text">
                ✓ No major risk indicators detected.
            </p>
        `;

        return;

    }


    let html = "";


    flags.forEach(
        function (flag) {

            let category =
                flag.category ||
                "Risk Indicator";


            let risk =
                flag.risk ||
                flag.level ||
                "Medium";


            let details =
                flag.details ||
                flag.message ||
                flag.description ||
                "Potentially suspicious pattern detected.";


            html += `
                <div class="risk-point">
                    <div class="risk-point-title">
                        ⚠️ ${escapeHTML(
                            String(category)
                        )}
                    </div>

                    <p>
                        ${escapeHTML(
                            String(details)
                        )}
                    </p>

                    <small>
                        Risk: ${escapeHTML(
                            String(risk)
                        )}
                    </small>
                </div>
            `;

        }
    );


    riskIndicators.innerHTML =
        html;

}


/* =========================================================
   AI RECOMMENDATION
   ========================================================= */

function displayRecommendation(
    recommendation
) {

    const element =
        document.getElementById(
            "recommendation"
        );


    if (!element) {
        return;
    }


    if (!recommendation) {

        element.textContent =
            "No recommendation available.";

        return;

    }


    if (
        typeof recommendation === "object"
    ) {

        recommendation =
            recommendation.message ||
            recommendation.text ||
            recommendation.recommendation ||
            recommendation.summary ||
            JSON.stringify(
                recommendation
            );

    }


    element.innerHTML =
        formatText(
            String(recommendation)
        );

}


/* =========================================================
   SALARY ANALYSIS
   ========================================================= */

function displaySalaryAnalysis(
    salary
) {

    const container =
        document.getElementById(
            "salaryAnalysis"
        );


    if (!container) {
        return;
    }


    if (!salary) {

        container.innerHTML = `
            <p class="empty-text">
                No salary analysis available.
            </p>
        `;

        return;

    }


    if (
        typeof salary === "string"
    ) {

        container.innerHTML = `
            <p>
                ${formatText(
                    salary
                )}
            </p>
        `;

        return;

    }


    let html = "";


    if (salary.salary_range) {

        html += `
            <p>
                <strong>Salary Range:</strong>
                ${escapeHTML(
                    String(
                        salary.salary_range
                    )
                )}
            </p>
        `;

    }


    if (salary.assessment) {

        html += `
            <p>
                <strong>Assessment:</strong>
                ${formatText(
                    String(
                        salary.assessment
                    )
                )}
            </p>
        `;

    }


    if (salary.message) {

        html += `
            <p>
                ${formatText(
                    String(
                        salary.message
                    )
                )}
            </p>
        `;

    }


    if (!html) {

        html = `
            <p>
                ${formatText(
                    JSON.stringify(
                        salary
                    )
                )}
            </p>
        `;

    }


    container.innerHTML =
        html;

}


/* =========================================================
   CHITTI AI
   ========================================================= */

function setupChitti() {

    const chatInput =
        document.getElementById(
            "chatInput"
        );

    const sendBtn =
        document.getElementById(
            "sendBtn"
        );


    if (sendBtn) {

        sendBtn.addEventListener(
            "click",
            sendChittiMessage
        );

    }


    if (chatInput) {

        chatInput.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    sendChittiMessage();

                }

            }
        );

    }

}


/* =========================================================
   OPEN CHITTI
   ========================================================= */

function openChat() {

    const chatModal =
        document.getElementById(
            "chatModal"
        );


    if (chatModal) {

        chatModal.classList.remove(
            "hidden"
        );

    }

}


/* =========================================================
   CLOSE CHITTI
   ========================================================= */

function closeChat() {

    const chatModal =
        document.getElementById(
            "chatModal"
        );


    if (chatModal) {

        chatModal.classList.add(
            "hidden"
        );

    }

}


/* =========================================================
   SEND CHITTI MESSAGE
   ========================================================= */

async function sendChittiMessage() {

    const chatInput =
        document.getElementById(
            "chatInput"
        );

    const chatMessages =
        document.getElementById(
            "chatMessages"
        );


    if (!chatInput || !chatMessages) {
        return;
    }


    const message =
        chatInput.value.trim();


    if (!message) {
        return;
    }


    /* User message */

    const userMessage =
        document.createElement("div");

    userMessage.className =
        "user-message";

    userMessage.textContent =
        message;


    chatMessages.appendChild(
        userMessage
    );


    chatInput.value = "";


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    /* Typing message */

    const typingMessage =
        document.createElement("div");

    typingMessage.className =
        "bot-message";

    typingMessage.textContent =
        "Chitti is thinking...";


    chatMessages.appendChild(
        typingMessage
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    try {

        /*
         * Keep Chitti endpoint unchanged.
         * Backend receives:
         * { question: message }
         */

        const response =
            await fetch(
                "/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: message
                    })
                }
            );


        const data =
            await response.json();


        /* Remove typing message */

        typingMessage.remove();


        let reply =
            data.response ||
            data.message ||
            data.answer;


        if (!reply) {

            reply =
                "Sorry, I couldn't generate a response right now.";

        }


        const botMessage =
            document.createElement("div");

        botMessage.className =
            "bot-message";

        botMessage.innerHTML =
            formatText(
                String(reply)
            );


        chatMessages.appendChild(
            botMessage
        );


        chatMessages.scrollTop =
            chatMessages.scrollHeight;


    } catch (error) {

        console.error(
            "Chitti Error:",
            error
        );


        typingMessage.remove();


        const errorMessage =
            document.createElement("div");

        errorMessage.className =
            "bot-message";

        errorMessage.textContent =
            "Sorry, Chitti is temporarily unavailable.";


        chatMessages.appendChild(
            errorMessage
        );


        chatMessages.scrollTop =
            chatMessages.scrollHeight;

    }

}


/* =========================================================
   ESCAPE HTML
   ========================================================= */

function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value;

    return div.innerHTML;

}


/* =========================================================
   FORMAT TEXT
   ========================================================= */

function formatText(value) {

    if (value === null ||
        value === undefined) {

        return "";

    }


    let text =
        String(value);


    text =
        escapeHTML(text);


    /*
     * Convert simple markdown-style formatting
     */

    text =
        text.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    text =
        text.replace(
            /\n/g,
            "<br>"
        );


    return text;

}


/* =========================================================
   CLOSE CHAT WHEN CLICKING OUTSIDE
   ========================================================= */

document.addEventListener(
    "click",
    function (event) {

        const chatModal =
            document.getElementById(
                "chatModal"
            );


        const chatWindow =
            document.querySelector(
                ".chat-window"
            );


        if (
            chatModal &&
            !chatModal.classList.contains("hidden") &&
            event.target === chatModal
        ) {

            if (
                !chatWindow ||
                !chatWindow.contains(
                    event.target
                )
            ) {

                closeChat();

            }

        }

    }
);


/* =========================================================
   ESC KEY - CLOSE CHITTI
   ========================================================= */

document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Escape"
        ) {

            closeChat();

        }

    }
);
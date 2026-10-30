
/* =========================================================
   HIRELENS AI - COMPLETE MAIN JAVASCRIPT
   ========================================================= */

let selectedImage = null;
let isAnalyzing = false;
let isChittiThinking = false;


/* =========================================================
   INITIALIZATION
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    setupUpload();
    setupAnalyzeButton();
    setupChitti();
});


/* =========================================================
   HELPER FUNCTIONS
   ========================================================= */

function getElement(...ids) {
    for (const id of ids) {
        const element = document.getElementById(id);
        if (element) return element;
    }
    return null;
}


function setText(ids, value) {
    const element = getElement(...ids);
    if (element) {
        element.textContent = value ?? "";
    }
}


function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}


function getDisplayText(value) {
    if (value === null || value === undefined) return "Not available";

    if (typeof value === "string" || typeof value === "number") {
        return String(value);
    }

    if (Array.isArray(value)) {
        return value.map(item => {
            if (typeof item === "object") {
                return Object.values(item).join(" - ");
            }
            return String(item);
        }).join("\n");
    }

    if (typeof value === "object") {
        return Object.entries(value)
            .map(([key, val]) => `${key}: ${getDisplayText(val)}`)
            .join("\n");
    }

    return String(value);
}


/* =========================================================
   DASHBOARD
   ========================================================= */

function openDashboard() {
    const landingPage = getElement("landingPage");
    const dashboard = getElement("dashboard");

    if (landingPage) landingPage.classList.add("hidden");
    if (dashboard) dashboard.classList.remove("hidden");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function scrollToFeatures() {
    const features = getElement("features");

    if (features) {
        features.scrollIntoView({
            behavior: "smooth"
        });
    }
}


/* =========================================================
   CHITTI CHAT WINDOW
   ========================================================= */

function openChat() {
    const chatModal = getElement("chatModal", "chittiModal");

    if (chatModal) {
        chatModal.classList.remove("hidden");
        chatModal.style.display = "flex";
    }
}


function closeChat() {
    const chatModal = getElement("chatModal", "chittiModal");

    if (chatModal) {
        chatModal.classList.add("hidden");
        chatModal.style.display = "none";
    }
}


/* =========================================================
   IMAGE UPLOAD
   ========================================================= */

function setupUpload() {
    const uploadBtn = getElement("uploadBtn");
    const jobPoster = getElement("jobPoster", "jobImage");
    const fileName = getElement("fileName");

    if (uploadBtn && jobPoster) {
        uploadBtn.addEventListener("click", event => {
            event.preventDefault();

            if (!isAnalyzing) {
                jobPoster.click();
            }
        });
    }

    if (jobPoster) {
        jobPoster.addEventListener("change", function () {
            if (!this.files || !this.files.length) {
                selectedImage = null;
                if (fileName) fileName.textContent = "";
                return;
            }

            const file = this.files[0];

            if (!file.type.startsWith("image/")) {
                alert("Please upload a valid image.");
                this.value = "";
                selectedImage = null;
                return;
            }

            selectedImage = file;

            if (fileName) {
                fileName.textContent = "Selected: " + file.name;
            }
        });
    }
}


/* =========================================================
   ANALYZE BUTTON
   ========================================================= */

function setupAnalyzeButton() {
    const analyzeBtn = getElement("analyzeBtn");

    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", event => {
            event.preventDefault();
            analyzeJob();
        });
    }
}


/* =========================================================
   ANALYSIS LOADING
   ========================================================= */

function showAnalysisLoading() {
    const loadingMessage = getElement("loadingMessage");
    const loadingText = getElement("loadingText");

    if (loadingMessage) loadingMessage.classList.remove("hidden");

    if (loadingText) {
        loadingText.textContent =
            "Analyzing your job description...";
    }

    const statusCard = getElement("analysisStatusCard");
    const statusTitle = getElement("analysisStatusTitle");
    const statusMessage = getElement("analysisStatusMessage");

    if (statusCard) statusCard.classList.add("analyzing");

    if (statusTitle) {
        statusTitle.textContent = "ANALYZING...";
        statusTitle.classList.add("analyzing-text");
    }

    if (statusMessage) {
        statusMessage.textContent =
            "HireLens AI is checking the job details. Please wait...";
    }

    setText(["riskScore"], "...");
    setText(["riskLevel"], "ANALYZING");
    setText(["recommendation"], "Analyzing the job opportunity...");
    setText(["jobAnalysisStatus"], "Analyzing...");

    const riskIndicators = getElement("riskIndicators");

    if (riskIndicators) {
        riskIndicators.textContent =
            "Checking risk indicators...";
    }
}


/* =========================================================
   ANALYSIS COMPLETE MESSAGE
   ========================================================= */

function updateAnalysisCompleteMessage() {
    const loadingMessage = getElement("loadingMessage");
    const statusCard = getElement("analysisStatusCard");
    const statusTitle = getElement("analysisStatusTitle");
    const statusMessage = getElement("analysisStatusMessage");

    if (loadingMessage) loadingMessage.classList.add("hidden");

    if (statusCard) statusCard.classList.remove("analyzing");

    if (statusTitle) {
        statusTitle.textContent = "ANALYSIS COMPLETE";
        statusTitle.classList.remove("analyzing-text");
    }

    if (statusMessage) {
        statusMessage.textContent =
            "Your job analysis is ready.";
    }

    setText(["jobAnalysisStatus"], "Complete");
}


/* =========================================================
   ANALYSIS ERROR
   ========================================================= */

function showAnalysisError(message) {
    const loadingMessage = getElement("loadingMessage");

    if (loadingMessage) loadingMessage.classList.add("hidden");

    const statusCard = getElement("analysisStatusCard");
    const statusTitle = getElement("analysisStatusTitle");
    const statusMessage = getElement("analysisStatusMessage");

    if (statusCard) statusCard.classList.remove("analyzing");

    if (statusTitle) {
        statusTitle.textContent = "ANALYSIS FAILED";
        statusTitle.classList.remove("analyzing-text");
    }

    if (statusMessage) {
        statusMessage.textContent =
            message || "Something went wrong. Please try again.";
    }

    setText(["jobAnalysisStatus"], "Error");
}


/* =========================================================
   MAIN JOB ANALYSIS
   ========================================================= */

async function analyzeJob() {
    if (isAnalyzing) return;

    const jobDescription = getElement("jobDescription", "jobInput");
    const analyzeBtn = getElement("analyzeBtn");

    const jobText = jobDescription
        ? jobDescription.value.trim()
        : "";

    if (!jobText && !selectedImage) {
        alert("Please enter a job description or upload a job poster.");
        return;
    }

    isAnalyzing = true;

    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
    }

    showAnalysisLoading();

    const formData = new FormData();

    if (jobText) {
        formData.append("job_text", jobText);
    }

    if (selectedImage) {
        formData.append("image", selectedImage);
    }

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server error: " + response.status);
        }

        const data = await response.json();

        if (data.success === false || data.error) {
            throw new Error(data.error || "Analysis failed.");
        }

        displayAnalysisResults(data);
        updateAnalysisCompleteMessage();

    } catch (error) {
        console.error("HireLens Analysis Error:", error);
        showAnalysisError(error.message);

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
   DISPLAY ANALYSIS RESULTS
   ========================================================= */

function displayAnalysisResults(data) {
    console.log("Analysis Results:", data);

    const riskScore = data.risk_score ?? data.score ?? "--";
    const riskLevel = data.risk_level ?? data.risk ?? "Not available";

    setText(["riskScore"], riskScore);
    setText(["riskLevel"], String(riskLevel).toUpperCase());

    const concerns = data.concerns ??
        data.risk_factors ??
        data.flags ??
        [];

    const riskIndicators = getElement("riskIndicators");

    if (riskIndicators) {
        if (Array.isArray(concerns) && concerns.length) {
            riskIndicators.innerHTML = concerns.map(item => {
                const text = typeof item === "object"
                    ? getDisplayText(item.message || item.details || item.category || item)
                    : String(item);

                return `<p class="risk-item">${escapeHTML(text)}</p>`;
            }).join("");
        } else {
            riskIndicators.textContent =
                "No major risk indicators were returned.";
        }
    }

    const jobInfo = data.job_information ?? data.job_info ?? {};

    const jobInfoElement = getElement(
        "jobInformation",
        "jobInfo",
        "extractedInformation"
    );

    if (jobInfoElement) {
        jobInfoElement.textContent = getDisplayText(jobInfo);
    }

    const salaryData = data.salary_analysis ?? {};

    const salaryElement = getElement(
        "salaryAnalysis",
        "salaryResult"
    );

    if (salaryElement) {
        salaryElement.textContent = getDisplayText(salaryData);
    }

    const explanation = data.explainable_ai ??
        data.explanation ??
        {};

    const explanationElement = getElement(
        "explainableAI",
        "explanation",
        "riskExplanation"
    );

    if (explanationElement) {
        explanationElement.textContent = getDisplayText(explanation);
    }

    const recommendationData = data.recommendations ??
        data.recommendation ??
        "";

    const recommendationElement = getElement("recommendation");

    if (recommendationElement) {
        recommendationElement.textContent =
            getDisplayText(recommendationData);
    }

    const resultsSection = getElement(
        "resultsSection",
        "analysisResults",
        "resultSection"
    );

    if (resultsSection) {
        resultsSection.classList.remove("hidden");
        resultsSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
}


/* =========================================================
   CHITTI CHAT SETUP
   ========================================================= */

function setupChitti() {
    const sendBtn = getElement(
        "sendBtn",
        "chittiSendBtn",
        "chatSendBtn",
        "sendMessageBtn"
    );

    const chatInput = getElement(
        "chatInput",
        "chittiInput",
        "userMessage",
        "messageInput"
    );

    const chatForm = getElement(
        "chatForm",
        "chittiForm"
    );

    if (sendBtn) {
        sendBtn.addEventListener("click", event => {
            event.preventDefault();
            sendChittiMessage();
        });
    }

    if (chatInput) {
        chatInput.addEventListener("keydown", event => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendChittiMessage();
            }
        });
    }

    if (chatForm) {
        chatForm.addEventListener("submit", event => {
            event.preventDefault();
            sendChittiMessage();
        });
    }
}


/* =========================================================
   CHITTI MESSAGE DISPLAY
   ========================================================= */

function addChittiMessage(message, sender = "user") {
    const chatMessages = getElement(
        "chatMessages",
        "chittiMessages",
        "chatBody",
        "chatBox",
        "messagesContainer"
    );

    if (!chatMessages) {
        console.error("Chitti message container not found.");
        return;
    }

    const messageElement = document.createElement("div");

    messageElement.className =
        sender === "user"
            ? "user-message"
            : "bot-message";

    messageElement.textContent = message;

    chatMessages.appendChild(messageElement);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}


/* =========================================================
   CHITTI LOADING MESSAGE
   ========================================================= */

function showChittiLoading() {
    const chatMessages = getElement(
        "chatMessages",
        "chittiMessages",
        "chatBody",
        "chatBox",
        "messagesContainer"
    );

    if (!chatMessages) return null;

    const loading = document.createElement("div");

    loading.className = "bot-message chitti-loading";
    loading.textContent = "Chitti is thinking...";

    chatMessages.appendChild(loading);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return loading;
}


/* =========================================================
   SEND MESSAGE TO CHITTI
   ========================================================= */

async function sendChittiMessage() {
    if (isChittiThinking) return;

    const chatInput = getElement(
        "chatInput",
        "chittiInput",
        "userMessage",
        "messageInput"
    );

    if (!chatInput) {
        console.error("Chitti input field not found.");
        return;
    }

    const question = chatInput.value.trim();

    if (!question) return;

    isChittiThinking = true;

    const sendBtn = getElement(
        "sendBtn",
        "chittiSendBtn",
        "chatSendBtn",
        "sendMessageBtn"
    );

    if (sendBtn) sendBtn.disabled = true;

    addChittiMessage(question, "user");

    chatInput.value = "";

    const loadingMessage = showChittiLoading();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        if (!response.ok) {
            throw new Error("Server error: " + response.status);
        }

        const data = await response.json();

        if (loadingMessage) loadingMessage.remove();

        if (data.success === false || data.error) {
            throw new Error(data.error || "Chitti could not process your question.");
        }

        const reply =
            data.response ??
            data.reply ??
            data.message ??
            data.answer ??
            data.chatbot_response;

        if (!reply) {
            throw new Error("Chitti returned an empty response.");
        }

        addChittiMessage(
            typeof reply === "string"
                ? reply
                : getDisplayText(reply),
            "bot"
        );

    } catch (error) {
        console.error("Chitti Error:", error);

        if (loadingMessage) loadingMessage.remove();

        addChittiMessage(
            "Sorry, I couldn't process your question. Please try again.",
            "bot"
        );

    } finally {
        isChittiThinking = false;

        if (sendBtn) sendBtn.disabled = false;

        if (chatInput) chatInput.focus();
    }
}


/* =========================================================
   ENTER KEY COMPATIBILITY
   ========================================================= */

function handleChittiEnter(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendChittiMessage();
    }
}

```javascript
/* =========================================================
   HIRELENS AI - MAIN JAVASCRIPT
   ========================================================= */


/* =========================================================
   GLOBAL VARIABLES
   ========================================================= */

let selectedImage = null;
let isAnalyzing = false;
let isChittiThinking = false;


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


    uploadBtn.addEventListener("click", function () {

        if (isAnalyzing) {
            return;
        }

        jobPoster.click();

    });


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


    if (!jobText && !selectedImage) {

        alert(
            "Please enter a job description or upload a job poster."
        );

        return;

    }


    /* START */

    isAnalyzing = true;


    if (analyzeBtn) {

        analyzeBtn.disabled = true;

        analyzeBtn.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';

    }


    showAnalysisLoading();


    const jobAnalysisStatus =
        document.getElementById("jobAnalysisStatus");

    if (jobAnalysisStatus) {
        jobAnalysisStatus.textContent = "Analyzing...";
    }


    /* FORM DATA */

    const formData =
        new FormData();


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

        const response =
            await fetch("/analyze", {

                method: "POST",
                body: formData

            });


        if (!response.ok) {

            throw new Error(
                "Server returned status " +
                response.status
            );

        }


        const data =
            await response.json();


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


        displayAnalysisResults(data);

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


    if (loadingMessage) {
        loadingMessage.classList.remove("hidden");
    }


    if (loadingText) {

        loadingText.textContent =
            "Analyzing your job description...";

    }


    const statusCard =
        document.getElementById("analysisStatusCard");

    const statusTitle =
        document.getElementById("analysisStatusTitle");

    const statusMessage =
        document.getElementById("analysisStatusMessage");


    if (statusCard) {
        statusCard.classList.add("analyzing");
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


    const riskIndicators =
        document.getElementById("riskIndicators");


    if (riskIndicators) {

        riskIndicators.innerHTML = `
            <p class="empty-text">
                🔄 Checking risk indicators...
            </p>
        `;

    }


    const recommendation =
        document.getElementById("recommendation");


    if (recommendation) {

        recommendation.textContent =
            "Analyzing the job opportunity...";

    }


    const

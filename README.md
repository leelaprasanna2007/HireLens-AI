# 🔍 HireLens AI

### AI-Powered Job Scam Detection & Analysis

**HireLens AI** is a web application that helps job seekers identify **potential scam warning signs** in online job opportunities before applying.

Users can **paste a job description or upload a job poster** and receive an analysis of the job details, salary, warning signs, and overall risk.

---

## ✨ Key Features

- 📝 **Job Description Analysis** — Analyzes pasted job descriptions
- 🖼️ **Job Poster Analysis** — Extracts text from uploaded job posters
- 📋 **Information Extraction** — Identifies company, role, salary, location, experience, email and phone details
- 🚨 **Scam Detection** — Detects common warning signs in job advertisements
- 💰 **Salary Analysis** — Checks potentially unrealistic salary claims
- 📊 **Risk Assessment** — Provides an overall risk level
- 🧠 **Result Explanation** — Explains the reasons behind detected concerns
- 🤖 **Chitti AI Chatbot** — Answers job-related questions

---

## 🚨 Scam Indicators

HireLens AI checks for:

- **Registration / Application Fees**
- **Training / Processing / Joining Fees**
- **Upfront Payment Requests**
- **Unrealistic Salary Promises**
- **Urgency or Pressure Tactics**
- **Suspicious Contact Methods**
- **Very Low Requirements for High-Paying Jobs**
- **Sensitive Information Requests**
- **Suspicious Application Websites**
- **Missing or Incomplete Job Information**
- **Generic or Broad Job Advertisements**
- **Multiple Verification Concerns**

---

## 🔄 Workflow

```text
             ┌─────────────────────┐
             │      Job Input      │
             │ Description / Image │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │   Text Extraction   │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │ Information         │
             │ Extraction          │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │   Scam Detection    │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │   Salary Analysis   │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │   Risk Assessment   │
             └──────────┬──────────┘
                        ↓
             ┌─────────────────────┐
             │ Explanation &       │
             │   Final Result      │
             └─────────────────────┘
```

---

## 🧩 Main Modules

| Module | Purpose |
|---|---|
| `app.py` | Runs the main Flask application |
| `information_extraction.py` | Extracts job details |
| `advanced_scam_detection.py` | Detects scam indicators |
| `salary_analysis.py` | Analyzes salary information |
| `image_ocr.py` | Extracts text from job posters |
| `explanation_generator.py` | Generates result explanations |
| `chatbot_response.py` | Handles Chitti AI responses |

---

## 🛠️ Technologies Used

**Programming:** Python

**Backend:** Flask

**Frontend:** HTML, CSS, JavaScript

**AI:** Google Gemini API

**OCR:** Gemini Vision

**Development:** VS Code, GitHub

**Deployment:** Render

---

## 📁 Project Structure

```text
HireLens-AI/
│
├── app.py
├── information_extraction.py
├── advanced_scam_detection.py
├── salary_analysis.py
├── image_ocr.py
├── explanation_generator.py
├── chatbot_response.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── requirements.txt
└── Procfile
```

---

## 🌐 Live Demo

**HireLens AI:** Add your Render URL here

---

## 🔮 Future Enhancements

- Improved Company Verification
- Better Salary Comparison
- Multiple Language Support
- Additional Scam Detection Patterns
- Enhanced Chitti AI
- Browser Extension

---

## 👤 Author

**Leelaprasanna**

B.Sc. Data Science Student

GitHub: `@leelaprasanna2007`

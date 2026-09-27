# 🤖 AI-Based HR Resume Screening & Candidate Matching System
> **An Intelligent Applicant Tracking System (ATS) combining Document Parsing, Natural Language Processing, Machine Learning, and Dual-Mode Database Architecture.**

---

## 🌟 Executive Summary

The **AI-Based HR Resume Screening & Candidate Matching System** is an enterprise-grade recruitment platform designed to solve candidate screening bottlenecks for HR teams and technical recruiters. It integrates all six foundational software disciplines into one seamless, production-ready system:

1. **🌐 Web Development**: Modern, responsive Dark Glassmorphic UI built with semantic HTML5, Vanilla CSS3, and dynamic Vanilla JavaScript.
2. **⚙️ Backend**: High-throughput asynchronous REST API built with **Python 3 & FastAPI**.
3. **📄 Document Processing**: Multi-format document parser extracting structured text from **PDF (`pypdf`)**, **Word (`python-docx`)**, and **Plain Text (`.txt`)**.
4. **🧠 Natural Language Processing (NLP)**: Ontology of 400+ technical skills, canonical skill normalization, entity extraction (name, email, phone, tenure), and degree level classification.
5. **🤖 Machine Learning**: Semantic candidate-job alignment utilizing **TF-IDF Vectorization**, **Cosine Similarity**, and a multi-attribute weighted scoring algorithm with explainable AI verdicts.
6. **🗄️ Database**: Dual-mode storage architecture supporting native **MongoDB / MongoDB Atlas** with automatic graceful fallback to a high-speed embedded document engine.

---

## 🏗️ System Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                            TALENTAI ARCHITECTURE                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  🌐 FRONTEND (Vanilla HTML5 + Modern CSS3 Glassmorphism + Modular JS)       │
│     ├── Dashboard Overview & Recruitment Analytics                          │
│     ├── Job Openings Manager (CRUD + Tag Cloud)                              │
│     ├── Resume Upload Center (Drag & Drop + Batch Extraction)               │
│     ├── Candidate Pool & Multi-Attribute Search Filters                      │
│     ├── Candidate Matcher (Radial Dials + Subscores + Explainability)        │
│     └── Side-by-Side Comparison Matrix (Winner Badge + Strengths / Gaps)     │
│                                      │                                       │
│                                      ▼ HTTP / REST (Fetch API)               │
│  ⚙️ BACKEND (Python + FastAPI ASGI Server)                                  │
│     ├── /api/auth       (HR Authentication & Role Management)               │
│     ├── /api/jobs       (Job Openings CRUD & Requirements)                   │
│     ├── /api/resumes    (Single/Bulk Upload & Parsing Pipeline)              │
│     ├── /api/candidates (Candidate Search, Status, & Profile Modal)          │
│     ├── /api/matching   (Candidate-Job Semantic Ranking Engine)              │
│     ├── /api/compare    (Comparative Multi-Candidate Matrix)                │
│     ├── /api/analytics  (Metrics, Skill Demand & Score Distributions)        │
│     └── /api/reports    (Streaming CSV Export Engine)                        │
│                                      │                                       │
│          ┌───────────────────────────┴───────────────────────────┐           │
│          ▼                                                       ▼           │
│  📄 DOCUMENT PROCESSING & NLP                            🤖 MACHINE LEARNING │
│     ├── PDF Parser (pypdf)                               ├── TF-IDF Vectorizer│
│     ├── DOCX Parser (python-docx)                        ├── Cosine Similarity│
│     ├── Entity Extractor (Email, Phone, Name)            ├── Skills Ratio    │
│     ├── 400+ Technical Skills Ontology                   ├── Experience Curve│
│     └── Degree Classification (MCA, B.Tech, M.Tech)      └── Composite Score │
│                                      │                                       │
│                                      ▼                                       │
│  🗄️ DATABASE LAYER (Dual-Mode Repository Pattern)                             │
│     ├── Primary: MongoDB Daemon / MongoDB Atlas (pymongo)                    │
│     └── Fallback: Embedded Thread-Safe JSON Document Store (db_store.json)   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 📐 Mathematical & Algorithmic Formulation

### 1. Semantic Text Matching (TF-IDF + Cosine Similarity)
The job vacancy description $D_{\text{job}}$ and the candidate resume text $D_{\text{cand}}$ are transformed into term-frequency inverse document frequency vectors using unigram and bigram tokenization with sublinear scaling:

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$

The semantic text similarity $S_{\text{semantic}}$ is computed via the dot product of normalized vectors:

$$S_{\text{semantic}} = \frac{\vec{V}_{\text{job}} \cdot \vec{V}_{\text{cand}}}{\|\vec{V}_{\text{job}}\| \|\vec{V}_{\text{cand}}\|} \times 100$$

### 2. Skills Match Scoring
Let $R$ denote the set of critical required skills, $P$ denote preferred skills, and $C$ denote candidate skills identified by NLP:

$$S_{\text{skill}} = \left( \frac{|R \cap C|}{|R|} \times 0.85 + \frac{|P \cap C|}{\max(1, |P|)} \times 0.15 \right) \times 100$$

### 3. Experience Match Scoring
Let $E_{\text{cand}}$ be candidate experience years and $E_{\text{req}}$ be job minimum required years:

$$S_{\text{exp}} = \begin{cases} 
100.0, & \text{if } E_{\text{cand}} \ge E_{\text{req}} \\
\left(\frac{E_{\text{cand}}}{E_{\text{req}}}\right) \times 80.0, & \text{if } E_{\text{cand}} < E_{\text{req}}
\end{cases}$$

### 4. Education Qualification Alignment
Degrees are categorized into hierarchical qualification tiers:
- **Tier 5**: Ph.D. / Doctorate
- **Tier 4**: Master's (MCA, M.Tech, M.S., MBA)
- **Tier 3**: Bachelor's (B.Tech, B.E., BCA, B.Sc)
- **Tier 2**: Diploma / Polytechnic
- **Tier 1**: High School

$$S_{\text{edu}} = \begin{cases}
100.0, & \text{if } \text{Tier}_{\text{cand}} \ge \text{Tier}_{\text{job}} \\
75.0,  & \text{if } \text{Tier}_{\text{cand}} = \text{Tier}_{\text{job}} - 1 \\
50.0,  & \text{otherwise}
\end{cases}$$

### 5. Final Composite Match Score
The final candidate suitability score is evaluated through a multi-factor weighted linear combination:

$$\text{Overall Score} = (0.45 \times S_{\text{skill}}) + (0.30 \times S_{\text{semantic}}) + (0.15 \times S_{\text{exp}}) + (0.10 \times S_{\text{edu}})$$

---

## 🗂️ Project Directory Structure

```text
c:\New folder\
├── app\
│   ├── __init__.py
│   ├── config.py                 # System parameters, file limits, scoring weights
│   ├── main.py                   # FastAPI app, static mounting, lifespan setup
│   ├── api\
│   │   ├── __init__.py
│   │   ├── auth.py               # HR login & authentication
│   │   ├── jobs.py               # Job openings CRUD
│   │   ├── candidates.py         # Candidate search, filtering & profile inspection
│   │   ├── resumes.py            # Resume upload & parsing endpoint
│   │   ├── matching.py           # Ranking engine & explainability
│   │   ├── compare.py            # Side-by-side comparative analysis
│   │   ├── analytics.py          # Dashboard metrics & skill demand aggregation
│   │   └── reports.py            # Streaming CSV candidate report download
│   ├── db\
│   │   ├── __init__.py
│   │   ├── client.py             # Dual-mode DB manager (MongoDB + Embedded engine)
│   │   └── seed_data.py          # Sample jobs, candidates & test CV generator
│   ├── models\
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic data schemas
│   └── services\
│       ├── __init__.py
│       ├── document_parser.py    # PDF (pypdf), DOCX (python-docx) text extractor
│       ├── nlp_extractor.py      # Skill ontology, entity extraction, experience parser
│       └── matching_engine.py    # TF-IDF, Cosine similarity & multi-factor engine
├── static\
│   ├── css\
│   │   └── style.css             # Dark Glassmorphism CSS design system
│   ├── js\
│   │   └── app.js                # Frontend state management & interactive logic
│   └── index.html                # Responsive Single Page Application
├── data\
│   ├── uploads\                  # Stored uploaded resumes
│   ├── sample_resumes\           # Real sample .pdf, .docx, and .txt resumes
│   └── db_store.json             # Embedded document store persistence
├── requirements.txt              # Production Python package dependencies
├── README.md                     # Comprehensive system documentation
└── run.py                        # Application entrypoint & ASGI launcher
```

---

## 🚀 Quickstart Guide

### 1. Requirements
- Python 3.10+ (Fully compatible with Python 3.14)
- (Optional) Local MongoDB or MongoDB Atlas URI. *If MongoDB is not running, the application automatically uses the embedded high-speed document engine with identical API behavior!*

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
python run.py
```

Optional CLI flags:
```bash
# Specify custom port or host
python run.py --port 8080 --host 0.0.0.0

# Enable auto-reloading during development
python run.py --reload
```

### 4. Open in Browser
- **HR Dashboard UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Technical Docs**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Test Scenarios & Pre-loaded Data

The system initializes with realistic demo vacancies and candidates:

### 1. Pre-Configured Job Vacancies
- **Senior Python / FastAPI Developer** (Backend Engineering)
- **AI & Machine Learning Engineer** (AI & Data Science)
- **Full Stack MERN Developer** (Product Engineering)
- **Cloud & DevOps Specialist** (Infrastructure)

### 2. Pre-Generated Sample Resumes in `data/sample_resumes/`
You can test uploading via the **Upload Resumes** tab by either dragging and dropping files or clicking the **Quick Test Sample CVs** buttons:
- `Rahul_Sharma_Resume.pdf` (MCA, 3.4 Yrs Exp, Python / FastAPI / Docker specialist)
- `Priya_Patel_Resume.docx` (M.Tech, 2.8 Yrs Exp, AI / NLP / PyTorch specialist)
- `Amit_Verma_Resume.docx` (B.Tech, 4.1 Yrs Exp, React / Node / MongoDB specialist)
- `Neha_Singh_Resume.pdf` (B.Tech, 3.5 Yrs Exp, AWS / Kubernetes / Terraform specialist)
- `Vikram_Rao_Resume.txt` (BCA, 1.2 Yrs Exp, Junior Python Developer)

---

## 📊 Core Features Walkthrough

1. **Dashboard Overview**: Instant metrics showing Active Jobs, Resumes Analyzed, Average Match Score, and High-Match Candidates. Features an interactive SVG Donut Chart showing score distribution and an active Technical Skills Cloud.
2. **Job Openings**: Create new vacancies with customized required/preferred skills, minimum experience, and degree requirements.
3. **Resume Upload Center**: Drag-and-drop zone with instant text extraction, NLP entity parsing, and live candidate ingestion. Includes **Quick One-Click Demo CVs** for immediate testing with sample PDF, DOCX, and TXT resumes.
4. **Candidate Pool**: Full-text candidate search, filter by skills, experience range slider, and qualification dropdown. Includes checkbox selector for multi-candidate comparison.
5. **Candidate Matcher**: Evaluates candidates against any job vacancy with radial match score dials, subscore breakdowns (Skills, Semantic, Experience, Education), and plain-text HR verdicts. Includes interactive score slider filtering.
6. **Side-by-Side Comparison**: Select 2 or 3 candidates to view side-by-side skills matrices, verified strengths, gaps, and automated top-candidate verdicts.
7. **🤖 AI Interview Questions Copilot**: Automatically synthesizes tailored technical, skill-gap probing, and architecture interview questions based on each candidate's specific background and missing skills against the job vacancy.
8. **CSV Export**: Stream live candidate rankings as structured CSV spreadsheets for reporting and stakeholder review.


---

## 🔒 Security & Best Practices
- Strict input sanitation and file extension whitelisting (`.pdf`, `.docx`, `.txt`).
- Unique UUID-based file storage preventing filename collisions.
- Graceful error handling for corrupt or image-only documents.
- Thread-safe persistence across all database read and write operations.

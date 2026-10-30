# TalentIQ AI — Enterprise Resume Screening & Job Matching Platform

> **Commercial Edition 2026** | Built with Python, Streamlit, Scikit-Learn, Plotly, ReportLab & SQLite.

TalentIQ AI is an end-to-end intelligent recruitment and talent analytics platform designed with strict **Role-Based Access Control (RBAC)**, dual **User & Admin Portals**, persistent SQLite storage, automated skill ontology extraction, TF-IDF semantic similarity ranking, multi-candidate comparison, and administrative governance.

---

## 🌟 Major Highlights & Architecture

### 1. 🔐 Dual Portals & Role-Based Access Control (RBAC)
- **Main Landing Page**: Professional landing page presenting both portals with modern gradient cards, architecture telemetry, and navigation router.
- **User Portal (`role: user`)**:
  - Independent user registration with email syntax validation, password strength criteria, and duplicate checking.
  - User login with password visibility toggle, password recovery, and secure logout.
  - Dedicated **User Dashboard**: Upload resumes (PDF/DOCX), run AI screening, view scores, compare candidates, build resumes, and manage account credentials.
  - **Account Data Isolation**: Candidates and screening history are strictly isolated to the authenticated user ID.
- **Admin Portal (`role: admin`)**:
  - Completely separate administrative login gateway with privileged security shield banner.
  - **Strict Backend Authorization**: Users cannot access the Admin Portal by modifying URL parameters, session state, or form data. Unauthorized attempts are rejected and recorded in the audit trail.
  - Dedicated **Admin Dashboard**:
    - **Overview**: Real platform telemetry, registered users, active jobs, global resume volume, and screening counts.
    - **User Management**: View all users, search by name/email, toggle account active/deactivate status, assign roles, and delete accounts (with safety guard for the last admin).
    - **Resume Management**: Global resume metadata monitoring with candidate privacy protection.
    - **Job Management**: Add, edit, and delete job descriptions with instant taxonomy sync.
    - **Reports & Analytics**: Real-time Plotly charts for user roles, department distribution, screening match histograms, and downloadable CSV audit trails.
    - **System Settings**: Admin password modification, infrastructure diagnostics, and privileged session termination.

### 2. 🔑 Security, Cryptography & Credentials
- **Bcrypt 12-Round Password Hashing**: Passwords are never stored in plain text; hashed using cryptographic salt rounds.
- **Brute-Force Rate Limiting**: Temporary account lockout triggered automatically after 5 consecutive failed login attempts.
- **Verification Code Password Recovery**: 8-character cryptographic verification code reset workflow.
- **Audit Logging**: Every authentication event, role change, account status update, and privileged action is recorded in the SQLite audit log.

| Portal | Account Email | Default Password | Role & Purpose |
| :--- | :--- | :--- | :--- |
| **User Portal** | `user@talentiq.ai` | `User@TalentIQ2026` | Standard Candidate Screener / Recruiter |
| **Admin Portal** | `admin@talentiq.ai` | `Admin@TalentIQ2026` | System Administrator (Full Privileges) |
| **Legacy Recruiter** | `sarah.jenkins@talentiq.ai` | `talentiq2026` | Verified Recruiter Alias |

---

### 3. 📄 High-Fidelity Resume Parsing & Deduplication
- **Multi-Format Ingestion**: Extracts text seamlessly from **PDF** (`pypdf`) and **DOCX** (`python-docx`).
- **Cryptographic Deduplication**: Computes SHA-256 content hashes to detect duplicate resume uploads before redundant computation.
- **Entity Extraction**: Robust extractors for candidate names, email addresses, phone numbers, education credentials, and years of experience.

---

### 4. 🎯 Skill Ontology & Hybrid Semantic Matching
- **300+ Industry Skill Taxonomy**: Categorized library covering Languages, Frameworks, Cloud/DevOps, Databases, AI/ML, and Data Engineering.
- **Hybrid Scoring Engine**:
  $$\text{Match Score} = (\text{Semantic Similarity} \times 0.6) + (\text{Skill Match Ratio} \times 0.4)$$
- **TF-IDF Vector Space**: Scikit-Learn TF-IDF vectorizer paired with cosine similarity and sublinear TF scaling.
- **Transparent Match Evidence**: Explains exact matching factors, highlighted skills, and missing candidate requirements.

---

### 5. 📊 Advanced Analytics Dashboard
- **Real Computed KPI Cards**: Total Resumes Uploaded, Unique Jobs Analyzed, Average Job Match Score, and Shortlisted Candidate Count.
- **Interactive Plotly Visualizations**: Match Score Distribution, Top Detected Skills, Skill Demand vs. Missing Gap, and Job-Wise Performance.
- **Zero Fabricated Stats**: Metrics calculate dynamically from real data records.

---

### 6. 🔍 Smart Candidate Management & Filtering
- **Real-Time Multi-Filter Pipeline**: Search by candidate name or resume filename, filter by job role, score range slider, required skills filter (ALL/ANY), and shortlisted-only toggle.
- **Instant Sorting**: Highest Match, Lowest Match, Name (A–Z / Z–A), and Upload Order.
- **Shortlisting**: Toggle candidate shortlist status with real-time SQLite synchronization.

---

### 7. ⚖️ Multi-Candidate Comparison Matrix
- **Side-by-Side Evaluation**: Compare 2 or 3 selected candidates directly across match scores, matched skills, missing skills, education, experience, projects, and certifications.

---

### 8. 📥 Downloadable Reports with Formula Injection Protection
- **Spreadsheet Formula Injection Defense**: All CSV exports sanitize leading formula trigger characters (`=`, `+`, `-`, `@`) with single-quote escaping.
- Export leaderboard rankings, job screening summaries, shortlisted candidate rosters, and administrative audit trails.

---

### 9. 💾 Session Save & Restore Persistence
- Persists screening sessions to disk under `data/sessions/` with JSON export/import capability.

---

### 10. 📝 Integrated Resume Builder
- One-click import from screened candidates into a live builder with ReportLab PDF compilation.

---

## 🏗️ Project Structure

```
resume/
├── app.py                      # Main Streamlit application & routing gateway
├── requirements.txt            # Python dependencies (Streamlit, Scikit-Learn, Plotly, ReportLab, Bcrypt)
├── README.md                   # System documentation & quickstart guide
│
├── data/
│   ├── talentiq.db             # Persistent SQLite database (WAL mode, foreign keys)
│   └── sessions/               # Saved session JSON files
│
├── src/                        # Modular backend & UI components
│   ├── admin.py                # Admin Dashboard (Overview, Users, Resumes, Jobs, Reports, Settings)
│   ├── analytics.py            # KPI aggregation & Plotly charting logic
│   ├── auth.py                 # Bcrypt hashing, validation, session handling & RBAC guards
│   ├── builder.py              # Resume builder state & ReportLab PDF compiler
│   ├── candidate_manager.py    # Search, multi-facet filtering & sorting pipeline
│   ├── comparison.py           # Multi-candidate comparison matrix generator
│   ├── database.py             # SQLite persistence: users, resumes, jobs, screenings, audit logs
│   ├── embeddings.py           # TF-IDF vectorization & cached semantic cosine matching
│   ├── matcher.py              # Candidate ranking & score breakdown utilities
│   ├── parser.py               # PDF & DOCX text parser & entity extractor
│   ├── parsers.py              # Compatibility import bridge for parser functions
│   ├── persistence.py          # Session save/load/export/import to data/sessions/
│   ├── ranker.py               # Multi-factor score calculator & evidence generator
│   ├── reports.py              # Sanitized CSV and text report generators
│   ├── skills.py               # 300+ skill ontology taxonomy and extractor
│   ├── skills_extractor.py     # Compatibility import bridge for skill extractor
│   ├── storage.py              # Session state synchronization & data isolation
│   ├── styles.py               # Commercial SaaS CSS stylesheet & UI renderers
│   └── utils.py                # File hashing (SHA-256), size formatting, truncators
│
└── tests/                      # Automated unit & integration test suite (93 tests)
    ├── test_rbac_and_auth.py   # RBAC, separate portals, lockout, password recovery & isolation tests
    ├── test_analytics.py       # Metrics calculation and Plotly figure validation
    ├── test_auth.py            # Authentication, session state, and credential validation
    ├── test_builder.py         # Builder state and PDF generation validation
    ├── test_candidate_management.py # Filtering, sorting, and search tests
    ├── test_comparison.py      # Multi-candidate comparison matrix verification
    ├── test_embeddings.py      # TF-IDF similarity and caching tests
    ├── test_integration_prompt3.py  # End-to-end integration workflow tests
    ├── test_parsers.py         # PDF/DOCX parsing and heuristic extraction tests
    ├── test_persistence.py     # Session serialization and file I/O tests
    ├── test_ranker.py          # Ranking algorithm and weighting validation
    ├── test_reports.py         # CSV sanitization and dossier export tests
    ├── test_skills.py          # Skill ontology and keyword matching tests
    ├── test_styles.py          # Styling components and SVG logo tests
    └── test_all_style_indentation.py # HTML formatting & Markdown code block defense tests
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.12)
- pip

### 2. Installation
```powershell
# Navigate to the workspace directory
cd c:\Users\eswar\OneDrive\Desktop\resume

# Install required dependencies
pip install -r requirements.txt
```

### 3. Run the Automated Test Suite
```powershell
python -m unittest discover tests
# 93 tests run and pass with 0 failures
```

### 4. Launch the Platform
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🔒 Security Best Practices
1. **Never Expose Passwords**: All user and admin passwords are encrypted using Bcrypt with 12 salt rounds before storage.
2. **Strict Backend Guarding**: Navigating directly or altering session state is intercepted by `require_role(...)` which checks active database records on each execution.
3. **Data Isolation**: User A cannot read or modify User B's candidates, resumes, or match screenings.
4. **Audit Trail**: Every significant administrative and security action is logged in `audit_logs` for compliance.

│   ├── test_storage.py         # Session storage and deduplication tests
│   └── test_utils.py           # Utility function tests
│
├── data/                       # Local application storage
│   ├── resumes/                # Uploaded resume cache
│   └── sessions/               # Saved screening session JSON files
│
└── sample_resumes/             # Bundled sample resumes for testing
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Installation
Open a terminal in the project directory and install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Launch the Application
Run the Streamlit application:

```bash
streamlit run app.py
```

The application will start and open in your default browser at `http://localhost:8501`.

### 4. Running the Automated Test Suite
Execute the comprehensive test suite (all 73 tests run offline without external API requirements):

```bash
python -m unittest discover tests
```

---

## 🔒 Security & Formula Injection Defense

Exported CSV files can pose a security risk if candidate inputs contain spreadsheet formula injection commands (e.g., `=cmd|'...`, `+HYPERLINK(...)`). 

TalentIQ AI implements strict CSV field sanitization via `src/reports.py`:
- All cell values starting with `=, +, -, @, \t, \r` are escaped with a prepended single-quote (`'`).
- Valid numerical negative numbers (e.g., `-1`, `-42.5`) are recognized and preserved.
- Double quotes are escaped according to RFC 4180 specifications.

---

## 👥 Hackathon Presentation Tips
1. **Quick-Start Demo**: Use the **One-Click Demo Login** button on the sign-in screen to instantly authenticate as `Senior Recruiter`.
2. **Preset Resumes**: Upload resumes from the `sample_resumes/` folder to demonstrate real-time ranking against sample tech roles.
3. **Interactive Visuals**: Check the **Analytics** page after running a screening batch to showcase live Plotly interactive charts.
4. **Compare Mode**: Select 2 or 3 candidates in **Candidate Management** and click **Compare Candidates** to display the side-by-side gap analysis.
5. **Session Export**: Demonstrate session persistence by saving the screening run, resetting state, and reloading it via **Saved Sessions**.

---
*TalentIQ AI — Built for Modern, Data-Driven Recruitment.*


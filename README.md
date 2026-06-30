# 🤖 AI Recruiter – Intelligent Candidate Ranking System

> An AI-powered candidate ranking system built for **The Data & AI Challenge (INDIA RUNS 2026)**.
>
> Instead of relying on keyword matching, our system evaluates candidates using career history, technical skills, behavioral signals, experience, and recruiter-oriented reasoning to generate an explainable shortlist.

---

## 📌 Problem Statement

Traditional Applicant Tracking Systems (ATS) rely heavily on keyword matching, often overlooking highly qualified candidates whose resumes use different terminology or demonstrate relevant experience in less obvious ways.

Our objective was to build an intelligent ranking system that evaluates candidates more like an experienced recruiter by considering:

- Technical skills
- Career progression
- Role relevance
- Behavioral signals
- Experience
- Resume consistency
- Explainable reasoning

The final result is a ranked shortlist of candidates that recruiters can trust.

---

# 🚀 Features

- 📄 Intelligent candidate ranking
- 🎯 Job-role relevance scoring
- 🧠 Multi-factor candidate evaluation
- 🛡 Honeypot & profile consistency detection
- 📈 Behavioral signal scoring
- 💼 Career progression analysis
- ⚙ Skill normalization
- 📝 Human-readable reasoning generation
- 📥 CSV export for recruiter workflows
- 🌐 REST API using FastAPI
- 🎨 Interactive frontend dashboard

---

# 🏗 System Architecture

```
                   Job Description
                          │
                          ▼
               Candidate Dataset (JSONL)
                          │
                          ▼
                 Resume Parsing Engine
                          │
                          ▼
                Feature Extraction Layer
        ┌──────────────┬──────────────┐
        │              │              │
        ▼              ▼              ▼
  Skill Score    Career Score   Experience Score
        │              │              │
        └───────┬──────┴───────┬──────┘
                ▼
      Behavioral Signal Analysis
                │
                ▼
        Consistency & Honeypot Checks
                │
                ▼
         Recruiter Ranking Engine
                │
                ▼
      Explainable Candidate Ranking
                │
                ▼
           submission.csv
```

---

# ⚙ Ranking Pipeline

```
Load Candidates
      │
      ▼
Resume Parsing
      │
      ▼
Feature Extraction
      │
      ▼
Skill Matching
      │
      ▼
Career Evaluation
      │
      ▼
Experience Scoring
      │
      ▼
Behavior Analysis
      │
      ▼
Consistency Validation
      │
      ▼
Final Score Calculation
      │
      ▼
Ranking
      │
      ▼
Reason Generation
      │
      ▼
submission.csv
```

---

# 🧠 Scoring Strategy

The ranking engine evaluates every candidate using multiple independent signals.

### 1. Role Relevance

Evaluates how closely the candidate's current role aligns with the target AI/ML position.

---

### 2. Technical Skills

Matches normalized AI/ML technologies including:

- LLMs
- RAG
- Vector Search
- FAISS
- Pinecone
- Weaviate
- Milvus
- LangChain
- Hugging Face
- PyTorch
- TensorFlow
- Docker
- Kubernetes
- MLflow
- Kubeflow

Core skills such as Python and Machine Learning are considered foundational, while specialized technologies receive greater emphasis during explanation generation.

---

### 3. Career Evaluation

Analyzes:

- Production experience
- Deployment evidence
- System development
- Engineering responsibilities
- AI project exposure

---

### 4. Experience Fit

Evaluates whether total professional experience aligns with the target role requirements.

---

### 5. Behavioral Signals

Considers:

- Recruiter response rate
- Platform activity
- Interview completion
- Open-to-work status

---

### 6. Consistency Validation

Detects suspicious profiles using rule-based checks including:

- Unrealistic experience timelines
- Inconsistent skill durations
- Invalid education chronology
- Multiple conflicting current roles

---

# 💡 Explainable AI

Rather than returning only a score, the system generates recruiter-style reasoning explaining why each candidate was selected.

Example:

> Holds a senior AI engineering role closely aligned with the target position. Demonstrates strong expertise in Vector Search and RAG systems with clear production deployment experience. Shows consistent career progression over 7 years and remains actively engaged on the platform, making them a strong shortlist candidate.

---

# 📂 Project Structure

```
AI_Recruiter/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── utils/
│   │
│   ├── data/
│   │   └── candidates.jsonl
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│
├── outputs/
│   └── submission.csv
│
├── notebooks/
│
├── rank.py
│
└── README.md
```

---

# 🛠 Tech Stack

## Backend

- Python
- FastAPI
- Uvicorn

## Data Processing

- JSONL
- Pandas
- NumPy

## Frontend

- React
- Tailwind CSS

## Deployment

- Vercel (Frontend)
- Render (Backend)

---

# 🚀 Installation

## Clone Repository

```bash
git clone <repository-url>
cd AI_Recruiter
```

---

## Install Dependencies

```bash
cd backend

pip install -r requirements.txt
```

---

## Configure Environment

Create `.env`

```env
DATA_PATH=backend/data/candidates.jsonl
OUTPUT_DIR=outputs
TOP_K=100

HOST=127.0.0.1
PORT=8000
ENV=development
```

---

## Run Backend

```bash
cd backend

python -m uvicorn app.main:app --reload
```

Server:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# 📥 Generate Ranking

Run:

```bash
python rank.py
```

or use

```
GET /rank/download
```

to generate

```
submission.csv
```

---

# 📊 API Endpoints

| Method | Endpoint | Description |
|----------|------------|---------------------------|
| GET | / | Health Check |
| GET | /jd | View Job Description |
| GET | /resume | Candidate Sample |
| GET | /rank | Ranked Candidates |
| GET | /rank/download | Download submission.csv |

---

# 📈 Performance

- Dataset Size: 100,000 Candidates
- Output: Top 100 Ranked Candidates
- Deterministic Ranking
- Explainable Results
- Rule-based Hybrid Scoring
- Lightweight CPU Execution

---

# 🎯 Competition Deliverables

- ✅ Working AI Recruiter
- ✅ GitHub Repository
- ✅ Explainable Ranking Engine
- ✅ submission.csv
- ✅ Presentation (PDF)

---

# 👥 Team

| Name | Role |
|------|------|
| Team Member 1 | Team Lead, Backend Integration, Architecture |
| Team Member 2 | Ranking Engine, Feature Engineering |
| Team Member 3 | Frontend, Database, Presentation |

---

# 🔮 Future Improvements

- Semantic resume understanding
- Embedding-based similarity search
- Learning-to-Rank models
- Graph-based career analysis
- Multi-job comparison
- Recruiter feedback loop
- Personalized ranking refinement

---

# 📜 License

This project was developed for **The Data & AI Challenge (INDIA RUNS 2026)**.

For educational and competition purposes.

---

## ⭐ Acknowledgements

Developed as part of **The Data & AI Challenge** under the **INDIA RUNS 2026** initiative.

Our goal was to build a transparent, explainable, and recruiter-centric AI system capable of identifying the most suitable candidates beyond traditional keyword matching.
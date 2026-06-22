# Data-AI-Challenge-AI-Recruiter-
AI system that ranks candidates the way a great recruiter would — not by matching keywords, but by actually understanding who fits the role. 

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/jiya2401/Data-AI-Challenge-AI-Recruiter-.git
cd Data-AI-Challenge-AI-Recruiter-
```

### 2. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Add candidates data
Copy `candidates.jsonl` into `backend/data/` folder.

### 4. Setup environment
```bash
cp .env.example .env
```

### 5. Run the server
```bash
python -m uvicorn app.main:app --reload
```

### 6. Generate submission CSV
Open browser and go to:
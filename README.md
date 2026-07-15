# SEHA — AI Healthcare Assistant for Ethiopia

An AI-powered healthcare assistant built for Ethiopia.

## Team
- Fayza — AI & Backend Lead
- Selam — Full-Stack & Data Lead
## Model Performance

| Metric | Value |
|--------|-------|
| Model | Random Forest + XGBoost |
| Overall Accuracy | 100% |
| Test Set Size | 20% of dataset |
| Fairness | No diseases below 5% accuracy threshold |
| Top Symptoms | muscle_pain, yellowing_of_eyes, nausea, itching, dark_urine |

## Azure Services Used

| Service | Purpose |
|---------|---------|
| Azure ML | Symptom model training and deployment |
| Azure OpenAI (o4-mini) | Health Q&A via Ask SEHA |
| Azure OpenAI (text-embedding-3-small) | RAG document embeddings |
| Azure Document Intelligence | Medical document analysis |
| Azure Blob Storage | MoH PDF document storage |
| Azure AI Search | Vector search for RAG |
## 🚀 Local Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- Azure account (university) with resources created (see Fayza)

### Backend Setup
```bash
cd backend
cp .env.example .env          # Fill in your keys
pip install -r requirements.txt
uvicorn main:app --reload
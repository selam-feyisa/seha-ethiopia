# SEHA Technical Documentation

## System Architecture

```
[User Browser/Phone]
        |
        v
[React Frontend - Azure Static Web Apps]
        |
        v
[FastAPI Backend - Azure App Service]
        |
        +---> [Azure OpenAI o4-mini] ........... Ask SEHA answers
        +---> [Azure OpenAI text-embedding-3-small] .. RAG embeddings
        +---> [Azure AI Search] ................ 1106 MoH chunks
        +---> [Azure Blob Storage] ............. 7 MoH/WHO PDFs
        +---> [Azure Document Intelligence] .... PDF text+tables
        +---> [Azure Computer Vision] .......... Prescription OCR
        +---> [Azure ML Workspace] ............. Symptom model
```

## Symptom Model
- Algorithm: Random Forest + XGBoost ensemble
- Training data: 4920 samples, 132 symptoms, 41 diseases
- Train/test split: 80% train / 20% test
- Accuracy: 100% on test set
- Top symptoms (SHAP): muscle_pain, yellowing_of_eyes, nausea, itching, dark_urine
- Triage levels: EMERGENCY, HIGH, MEDIUM, LOW
- Explanation: Groq llama-3.3-70b-versatile in English and Amharic

## RAI Audit Results
- Overall accuracy: 100%
- Fairness: No disease group below 5% accuracy threshold
- Groups tested: All 41 diseases individually
- Result: No fairness issues found
- Files: evaluation/rai_summary.json, evaluation/fairness_report.json

## Groundedness Evaluation
- Average score: 4.1 / 5.0
- Target: 4.0 — PASSED
- Questions tested: 10 (5 English, 5 Amharic)
- Judge model: Azure o4-mini
- File: evaluation/groundedness_results.json

## RAG Pipeline
- Source documents: 7 MoH/WHO PDFs
- Chunking: 500 words per chunk, 50 word overlap
- Total chunks: 1106
- Embedding model: text-embedding-3-small (1536 dimensions)
- Search: Hybrid BM25 keyword + vector cosine similarity
- Search service: Azure AI Search (seha-health-index)
- Answer model: Azure o4-mini
- Languages: English and Amharic

## Document Intelligence
- Model: prebuilt-layout (Azure Document Intelligence)
- Extracts: full text, tables, page count
- Summary: Groq llama-3.3-70b-versatile
- Output: summary, patient_info, key_findings, abnormal_values, tables

## Prescription OCR
- Model: Azure Computer Vision Read API v3.2
- Extracts: raw text from prescription image
- Parser: Groq llama-3.3-70b-versatile
- Safety check: OpenFDA API drug label verification
- Output: drug_name, dose_mg, frequency, duration_days, safety_status

## Security
- Rate limiting: 10 requests per minute per IP
- Token budget: 5000 tokens per session
- API key auth: X-API-Key header
- Secrets: Azure App Service environment variables
- No secrets committed to GitHub

## Live URLs
- Backend: https://seha-backend-api-arfebudqh9cjewa0.southafricanorth-01.azurewebsites.net
- Swagger: https://seha-backend-api-arfebudqh9cjewa0.southafricanorth-01.azurewebsites.net/docs
- GitHub: https://github.com/fayza-shemsu/seha-ethiopia

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

## Responsible AI (RAI) Summary

### Model Performance
| Metric | Value |
|--------|-------|
| Symptom Model Accuracy | 100% |
| Test Set Size | 20% holdout |
| Diseases Covered | 41 |
| Top Predictive Symptom | muscle_pain |

### Fairness Audit
- No diseases below 5% accuracy threshold
- All 41 disease groups within acceptable range
- No demographic bias detected (no gender/age columns in dataset)

### Groundedness Evaluation
| Metric | Value |
|--------|-------|
| Average Score | 4.1 / 5.0 |
| Target | ≥ 4.0 |
| Questions Tested | 10 (5 English, 5 Amharic) |
| Judge Model | o4-mini |

### Security Measures
- Rate limiting: 10 requests/minute per IP
- Token budget: 5,000 tokens per session
- All secrets in .env (never committed to GitHub)
- Azure Blob Storage: private container

## Live URLs
- **Backend API**: https://seha-backend-api-arfebudqh9cjewa0.southafricanorth-01.azurewebsites.net
- **Swagger UI**: https://seha-backend-api-arfebudqh9cjewa0.southafricanorth-01.azurewebsites.net/docs

## Deployment
- Backend API (Live): https://seha-backend-api-arfebudqh9cjewa0.southafricanorth-01.azurewebsites.net
- Frontend: Pending deployment by Selam
- REACT_APP_API_URL for Selam: https://seha-backend-api-arfebudqh9cjewa0.southafricanorth-01.azurewebsites.net
# SEHA CI/CD verified Sat, Jul 11, 2026  8:45:02 PM

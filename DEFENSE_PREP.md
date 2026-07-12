# SEHA Defense Preparation — Fayza Answers

## Q1: Why RandomForest/XGBoost?
We chose ensemble methods because they work well with tabular symptom data where each symptom is a binary feature (present or not). RandomForest prevents overfitting through bagging — training many trees on random subsets. XGBoost improves accuracy through boosting — each tree corrects errors of the previous one. Both are interpretable through SHAP values, which was critical for our RAI fairness audit.

## Q2: How did you ensure fairness?
We ran SHAP analysis to identify the top 10 symptoms driving predictions. Then we checked model accuracy per disease group — all 41 disease groups stayed within 5 percent of overall accuracy. No demographic bias was found because the dataset does not include gender or age columns. Results are documented in evaluation/fairness_report.json.

## Q3: What is groundedness?
Groundedness measures how much of the AI answer can be traced back to a real source document rather than hallucinated. We tested 10 questions — 5 in English and 5 in Amharic — and used o4-mini as a judge to score each answer 1 to 5. Our average score was 4.1 out of 5.0, above the 4.0 target. Results are in evaluation/groundedness_results.json.

## Q4: How does RAG work?
RAG stands for Retrieval Augmented Generation. We indexed 1106 chunks from 7 MoH and WHO health PDFs into Azure AI Search using text-embedding-3-small embeddings. When a user asks a question, we embed the question, run a hybrid search (keyword plus vector), retrieve the top 5 most relevant chunks, inject them as context into o4-mini, and generate a grounded answer that cites the source document.

## Q5: What if Azure goes down?
The symptom model runs locally using joblib — it does not depend on Azure at all. For the RAG pipeline and document reader, we have try/except error handling everywhere. If any Azure service fails, the API returns a clear error message with HTTP 500 instead of crashing. The frontend shows a user-friendly message.

## Q6: Explain the architecture in under 3 minutes
SEHA has four modules. The Symptom Checker uses a locally trained Random Forest model with SHAP explanations in English and Amharic. The Document Reader uses Azure Document Intelligence to extract text and tables from MoH PDFs, then Groq summarizes them. The Prescription Scanner uses Azure Computer Vision OCR to read handwritten prescriptions and checks drug safety against the FDA API. Ask SEHA is a RAG chatbot that searches 1106 chunks from 7 health guidelines indexed in Azure AI Search and answers in both English and Amharic. Everything is deployed on Azure App Service with GitHub Actions CI/CD.

## Architecture in 3 minutes — say this out loud:
1. User opens the React frontend
2. Selects a module — symptom checker, document reader, prescription scanner, or Ask SEHA
3. Frontend calls FastAPI backend on Azure App Service
4. Backend calls the appropriate Azure service
5. Result comes back in seconds with explanation in English or Amharic
6. Every answer includes a medical disclaimer

import os
import json
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

doc_client = DocumentIntelligenceClient(
    endpoint=os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY"))
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_document(blob_url: str) -> dict:
    poller = doc_client.begin_analyze_document(
        model_id="prebuilt-layout",
        body={"urlSource": blob_url}
    )
    result = poller.result()

    full_text = ""
    for page in result.pages:
        for line in page.lines:
            if len(line.content) > 30:
                full_text += line.content + "\n"

    tables = []
    for table in result.tables:
        rows = {}
        for cell in table.cells:
            if cell.row_index not in rows:
                rows[cell.row_index] = []
            rows[cell.row_index].append(cell.content)
        tables.append(list(rows.values()))

    if len(full_text) > 10000:
        full_text = full_text[:10000] + "\n...[truncated]"

    pages_analyzed = len(result.pages)

    print(f"Extracted {len(full_text)} characters from {pages_analyzed} pages")
    print(f"Found {len(tables)} tables")
    print("\nFirst 500 chars:")
    print(full_text[:500])

    prompt = f"""
You are a medical document analyst for Ethiopian healthcare.
Analyze this medical document and return a JSON object with:
- summary: a simple 2-3 sentence summary anyone can understand
- patient_info: patient name, age, date (null if not found)
- key_findings: list of 3-5 important findings
- abnormal_values: list of any abnormal lab values or danger signs (empty list if none)

Document text:
{full_text}

Return ONLY valid JSON, no markdown, no explanation.
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {"summary": raw, "patient_info": None, "key_findings": [], "abnormal_values": []}

    parsed["pages_analyzed"] = pages_analyzed
    parsed["tables"] = tables
    return parsed
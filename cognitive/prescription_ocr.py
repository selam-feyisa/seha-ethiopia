import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def read_prescription(image_url: str) -> dict:
    from openai import AzureOpenAI

    openai_client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-02-01"
    )

    VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT")
    VISION_KEY = os.getenv("AZURE_VISION_KEY")

    read_url = f"{VISION_ENDPOINT}/vision/v3.2/read/analyze"
    headers = {"Ocp-Apim-Subscription-Key": VISION_KEY, "Content-Type": "application/json"}
    body = {"url": image_url}

    response = requests.post(read_url, headers=headers, json=body)
    operation_url = response.headers["Operation-Location"]

    for _ in range(10):
        time.sleep(2)
        poll = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": VISION_KEY})
        poll_result = poll.json()
        if poll_result.get("status") == "succeeded":
            break

    raw_text = ""
    for read_result in poll_result.get("analyzeResult", {}).get("readResults", []):
        for line in read_result.get("lines", []):
            raw_text += line["text"] + "\n"

    parse_prompt = f"""
Parse this prescription text. Return ONLY a JSON object with these fields:
- drug_name: name of the drug
- dose_mg: dosage in mg (number only, or null)
- frequency: how often (e.g. "twice daily")
- duration_days: number of days (number only, or null)
- doctor_name: prescribing doctor (or null)
- patient_name: patient name (or null)

Prescription text:
{raw_text}

Return ONLY valid JSON. No markdown.
"""

    parse_response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": parse_prompt}],
        max_tokens=300
    )

    raw_parsed = parse_response.choices[0].message.content.strip()
    try:
        prescription = json.loads(raw_parsed)
    except Exception:
        prescription = {"drug_name": "Unknown", "dose_mg": None, "frequency": None,
                        "duration_days": None, "doctor_name": None, "patient_name": None}

    safety_status = "UNKNOWN"
    safety_note = "Could not verify drug safety automatically."

    drug = prescription.get("drug_name", "")
    if drug and drug != "Unknown":
        try:
            fda_url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug}&limit=1"
            fda_resp = requests.get(fda_url, timeout=5)
            if fda_resp.status_code == 200:
                fda_data = fda_resp.json()
                warnings = fda_data["results"][0].get("warnings", [""])[0]
                if warnings:
                    safety_status = "REVIEW NEEDED"
                    safety_note = warnings[:300]
                else:
                    safety_status = "SAFE"
                    safety_note = "No major warnings found in FDA database."
            else:
                safety_status = "REVIEW NEEDED"
                safety_note = "Drug not found in FDA database. Please verify manually."
        except Exception:
            safety_status = "REVIEW NEEDED"
            safety_note = "Could not reach FDA database. Please verify manually."

    prescription["safety_status"] = safety_status
    prescription["safety_note"] = safety_note
    prescription["raw_ocr_text"] = raw_text
    return prescription
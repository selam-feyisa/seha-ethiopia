import os
import json
import time
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

VISION_ENDPOINT = None
VISION_KEY = None

def get_vision_config():
    global VISION_ENDPOINT, VISION_KEY
    VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT", "").rstrip("/")
    VISION_KEY = os.getenv("AZURE_VISION_KEY")

get_vision_config()

def read_prescription(image_url: str) -> dict:
    # Step 1 — Call Azure Vision Read API
    headers = {
        "Ocp-Apim-Subscription-Key": VISION_KEY,
        "Content-Type": "application/json"
    }
    body = {"url": image_url}
    response = requests.post(
        f"{VISION_ENDPOINT}/vision/v3.2/read/analyze",
        headers=headers,
        json=body
    )
    if response.status_code != 202:
        raise Exception(f"Vision API error: {response.status_code} {response.text}")

    operation_location = response.headers["Operation-Location"]

    # Step 2 — Poll until complete
    print("Reading prescription...")
    poll_result = {}
    for _ in range(10):
        time.sleep(2)
        poll = requests.get(
            operation_location,
            headers={"Ocp-Apim-Subscription-Key": VISION_KEY}
        )
        poll_result = poll.json()
        status = poll_result.get("status")
        print(f"Status: {status}")
        if status == "succeeded":
            break

    # Step 3 — Extract text
    raw_text = ""
    for page in poll_result.get("analyzeResult", {}).get("readResults", []):
        for line in page.get("lines", []):
            raw_text += line["text"] + "\n"

    print(f"\nExtracted text:\n{raw_text}")

    # Step 4 — Parse with Groq
    parse_prompt = f"""
Parse this prescription text and return ONLY a JSON object with:
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

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": parse_prompt}],
        max_tokens=300
    )

    raw_parsed = response.choices[0].message.content.strip()
    raw_parsed = raw_parsed.replace("```json", "").replace("```", "").strip()
    try:
        prescription = json.loads(raw_parsed)
    except Exception:
        prescription = {
            "drug_name": "Unknown", "dose_mg": None,
            "frequency": None, "duration_days": None,
            "doctor_name": None, "patient_name": None
        }

    # Step 5 — FDA safety check
    drug = prescription.get("drug_name", "")
    safety_status = "UNKNOWN"
    safety_note = "Could not verify drug safety automatically."

    if drug and drug != "Unknown":
        try:
            fda_url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug}&limit=1"
            fda_resp = requests.get(fda_url, timeout=5)
            if fda_resp.status_code == 200:
                warnings = fda_resp.json()["results"][0].get("warnings", [""])[0]
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
import os
import sys
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from retriever import retrieve

load_dotenv()

def get_openai_client():
    return AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-02-01"
    )

def ask_seha(question: str, language: str = "en") -> dict:
    """
    Takes a health question in English or Amharic.
    Retrieves relevant context from MoH guidelines.
    Returns a grounded answer with sources.
    """
    client = get_openai_client()

    # Step 1: Retrieve relevant context
    context_chunks = retrieve(question, top_k=4)

    if context_chunks:
        context_text = "\n\n".join([
            f"[From: {c['source']}]\n{c['text']}"
            for c in context_chunks
        ])
        sources = list(set(c["source"] for c in context_chunks))
    else:
        context_text = "No specific guideline found. Use general medical knowledge."
        sources = []

    # Step 2: Build prompt based on language
    if language == "am":
        lang_instruction = "Answer in Amharic (አማርኛ). Be clear and simple."
    else:
        lang_instruction = "Answer in English. Be clear and simple."

    system_prompt = f"""You are SEHA, an AI health assistant for Ethiopia.
You answer questions based on Ethiopian Ministry of Health guidelines and WHO recommendations.
Always be accurate, compassionate, and clear.
If you are unsure, say so and recommend seeing a doctor.
{lang_instruction}

Always end your answer with:
⚠️ This is for information only. Please consult a healthcare provider for personal medical advice."""

    user_prompt = f"""Context from medical guidelines:
{context_text}

Question: {question}

Answer based on the context above. If the context doesn't cover the question, use your general medical knowledge but say so."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=600
    )

    answer = response.choices[0].message.content.strip()

    return {
        "question": question,
        "answer": answer,
        "language": language,
        "sources": sources,
        "context_used": len(context_chunks) > 0
    }
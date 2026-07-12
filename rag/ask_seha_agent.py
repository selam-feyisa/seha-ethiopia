import json
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from rag.retriever import retrieve

load_dotenv()

chat_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-12-01-preview"
)

CHAT_DEPLOYMENT = os.getenv("AZURE_CHAT_DEPLOYMENT", "o4-mini")
DISCLAIMER = "⚠️ This is for information only. Please consult a healthcare provider for personal medical advice."

SYSTEM_PROMPT = """## Identity
You are SEHA, an AI health assistant built for Ethiopia. You help patients and healthcare workers understand health information clearly and compassionately.

## Task
Answer health questions based on Ethiopian Ministry of Health guidelines and WHO recommendations. Always ground your answers in the provided context.

## Constraints
- NEVER diagnose a patient
- NEVER prescribe specific medications or dosages
- ALWAYS cite your source document
- ALWAYS end with a medical disclaimer
- If you don't know, say so clearly

## Knowledge
Use ONLY the context provided. If context is insufficient, say "Based on general medical knowledge (not from provided guidelines):" before answering.

## Format
- Use simple, clear language anyone can understand
- Use bullet points for lists
- Keep answers under 300 words
- Always end with: ⚠️ This is for information only. Please consult a healthcare provider for personal medical advice.

## Edge Cases
- If question is in Amharic → respond fully in Amharic
- If question is dangerous or emergency → immediately say "Call emergency services or go to nearest hospital NOW"
- If question is not health-related → politely redirect to health topics"""


def _build_prompts(question: str, language: str = "en"):
    context_chunks = retrieve(question, top_k=5)

    if context_chunks:
        context_text = "\n\n".join([
            f"[Source: {c['source']}, Chunk {c['chunk_id']}]\n{c['text']}"
            for c in context_chunks
        ])
        sources = list(dict.fromkeys(c["source"] for c in context_chunks))
    else:
        context_text = "No specific guideline found."
        sources = []

    if language == "am":
        lang_note = "The user is asking in Amharic. Respond entirely in Amharic."
    else:
        lang_note = "Respond in English."

    user_prompt = f"""{lang_note}

Context from MoH guidelines:
{context_text}

Question: {question}

Answer based ONLY on the context above. For each point you make, mention which source document it came from. If the context does not cover the question, say so explicitly."""

    return SYSTEM_PROMPT, user_prompt, sources, len(context_chunks) > 0


def ask_seha(question: str, language: str = "en") -> dict:
    system_prompt, user_prompt, sources, context_used = _build_prompts(question, language)

    response = chat_client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_completion_tokens=5000
    )

    answer = response.choices[0].message.content.strip()

    return {
        "question": question,
        "answer": answer,
        "language": language,
        "sources": sources,
        "context_used": context_used,
        "disclaimer": DISCLAIMER
    }


def ask_seha_stream(question: str, language: str = "en"):
    system_prompt, user_prompt, sources, context_used = _build_prompts(question, language)

    yield f"data: {json.dumps({'type': 'meta', 'sources': sources, 'context_used': context_used, 'disclaimer': DISCLAIMER})}\n\n"

    stream = chat_client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_completion_tokens=5000,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            yield f"data: {json.dumps({'type': 'token', 'content': delta})}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
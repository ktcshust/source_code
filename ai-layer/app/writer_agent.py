# summarization (OpenAI / llama-cpp fallback)
import os, asyncio
from app.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import time

# OpenAI client modern usage: from openai import OpenAI
try:
    from openai import OpenAI
    _openai_client = None
except Exception:
    OpenAI = None
    _openai_client = None

# llama-cpp fallback
try:
    from llama_cpp import Llama
except Exception:
    Llama = None

def get_openai_client():
    global _openai_client
    if _openai_client is None:
        if OpenAI is None:
            raise RuntimeError("openai package not installed")
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else OpenAI()
    return _openai_client

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def summarize_with_openai(article_text: str, title: str | None = None):
    """
    Use OpenAI Responses API (preferred) to create a concise summary.
    Returns dict: {summary, tokens, model}
    """
    client = get_openai_client()
    prompt = f"""Tóm tắt ngắn gọn (3-5 câu) nội dung bài báo sau, nhấn mạnh điểm mới, ứng dụng AI (nếu có), và mức độ tin cậy nguồn:
Title: {title or ''}
Article:
{article_text}
    
Format: JSON object with keys: summary (string), highlights (list of short strings), source_confidence (low|medium|high)
"""
    # Use Responses API via client.responses.create per OpenAI Python lib docs
    resp = client.responses.create(
        model=settings.OPENAI_MODEL,
        input=prompt,
        max_output_tokens=settings.SUMMARY_MAX_TOKENS,
    )
    # get output text (Responses API may give output_text or structured)
    output_text = ""
    try:
        # prefer structured output if present
        if getattr(resp, "output", None):
            # resp.output may include items
            # fallback to output_text
            output_text = resp.output_text or ""
        else:
            # some clients: resp.output_text
            output_text = getattr(resp, "output_text", "")
    except Exception:
        output_text = str(resp)
    # try parse JSON
    parsed = {}
    try:
        parsed = json.loads(output_text)
    except Exception:
        # fallback: put raw as summary
        parsed = {"summary": output_text.strip(), "highlights": [], "source_confidence": "unknown"}
    return {"summary": parsed.get("summary","").strip(), "highlights": parsed.get("highlights",[]), "source_confidence": parsed.get("source_confidence","unknown"), "model": settings.OPENAI_MODEL}

async def summarize_with_llama(article_text: str, title: str | None = None):
    """
    Local fallback using llama-cpp-python.
    Note: requires Llama and a model file path in settings.LLM_LOCAL_MODEL_PATH
    """
    if Llama is None:
        raise RuntimeError("llama_cpp not installed")
    if not settings.LLM_LOCAL_MODEL_PATH:
        raise RuntimeError("LLM_LOCAL_MODEL_PATH not configured")
    llama = Llama(model_path=settings.LLM_LOCAL_MODEL_PATH)
    prompt = f"Summarize in Vietnamese in 3-5 sentences: {title or ''}\n\n{article_text}"
    out = llama(prompt, max_tokens=settings.SUMMARY_MAX_TOKENS)
    # llama-cpp api returns dict with 'choices'[0]['text'] typically
    text = out.get("choices",[{}])[0].get("text","") if isinstance(out, dict) else str(out)
    return {"summary": text.strip(), "highlights": [], "source_confidence":"unknown", "model":"llama-cpp-local"}

async def summarize_article(article: dict):
    """
    article: dict with 'article_id', 'title', 'text', 'link', 'source'
    returns: summary_doc
    """
    text = article.get("text","")
    title = article.get("title")
    # prefer OpenAI when API key present
    if settings.OPENAI_API_KEY:
        try:
            out = await summarize_with_openai(text, title)
        except Exception as e:
            # fallback to llama if configured
            if settings.LLM_LOCAL_MODEL_PATH:
                out = await summarize_with_llama(text, title)
            else:
                raise
    else:
        # no OpenAI key -> use local llama if provided
        if settings.LLM_LOCAL_MODEL_PATH:
            out = await summarize_with_llama(text, title)
        else:
            raise RuntimeError("No OpenAI key and no local LLM configured")
    summary_doc = {
        "article_id": article.get("article_id"),
        "title": title,
        "link": article.get("link"),
        "source": article.get("source"),
        "summary": out["summary"],
        "highlights": out.get("highlights", []),
        "source_confidence": out.get("source_confidence","unknown"),
        "model": out.get("model"),
        "created_at": __import__("datetime").datetime.utcnow().isoformat()
    }
    return summary_doc


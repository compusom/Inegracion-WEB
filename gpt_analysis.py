import os
from typing import Optional

try:
    import openai
except ImportError:  # handle missing openai
    openai = None


def generate_gpt_insights(text: str) -> str:
    """Return a short GPT-generated summary for the provided text."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not text or not openai:
        return ""
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Resume brevemente el texto proporcionado destacando puntos clave.",
                },
                {"role": "user", "content": text},
            ],
            temperature=0.2,
            max_tokens=150,
        )
        choice = response.choices[0].message
        return choice.get("content", "").strip()
    except Exception:
        return ""

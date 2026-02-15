"""OpenAI-based text optimization (Email, Slack, Translate).

Takes text from the clipboard, processes it with GPT, and returns the result.
"""

from openai import OpenAI

MODEL = "gpt-4o-mini"

SYSTEM_PROMPTS = {
    "email": (
        "You are a professional email editor. "
        "Take the user's raw text and turn it into a well-formatted, polite email. "
        "Add an appropriate greeting and closing. "
        "Use proper paragraph formatting. "
        "Fix grammar and spelling errors. "
        "Keep the original language of the text -- do NOT translate. "
        "Return ONLY the optimized email text, nothing else."
    ),
    "slack": (
        "You are a Slack message editor. "
        "Take the user's raw text and rewrite it as a concise Slack message. "
        "Make it direct, casual but professional -- a friendly chat vibe. "
        "Use short paragraphs. Keep it brief. "
        "Fix grammar and spelling errors. "
        "Keep the original language of the text -- do NOT translate. "
        "Return ONLY the optimized message text, nothing else."
    ),
    "translate_en": (
        "You are a professional translator. "
        "Translate the user's text into English. "
        "Maintain the original tone, style, and formatting. "
        "If the text is already in English, improve grammar and clarity. "
        "Return ONLY the translated text, nothing else."
    ),
    "translate_de": (
        "You are a professional translator. "
        "Translate the user's text into German. "
        "Maintain the original tone, style, and formatting. "
        "If the text is already in German, improve grammar and clarity. "
        "Return ONLY the translated text, nothing else."
    ),
}


def optimize_text(text: str, mode: str, api_key: str) -> str:
    """Optimizes or translates text using OpenAI GPT.

    Args:
        text: The input text to process.
        mode: One of "email", "slack", "translate_en", "translate_de".
        api_key: OpenAI API key.

    Returns:
        The processed text.

    Raises:
        ValueError: If mode is unknown.
        Exception: On API or network errors.
    """
    system_prompt = SYSTEM_PROMPTS.get(mode)
    if not system_prompt:
        raise ValueError(f"Unknown mode: {mode}. Use: {list(SYSTEM_PROMPTS.keys())}")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()

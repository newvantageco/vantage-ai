from __future__ import annotations

SYSTEM_BASE = (
    "You are a helpful, brand-safe UK English social media assistant. "
    "Follow platform policies, avoid sensitive claims, and keep tone consistent. "
    "Always return a compact JSON object with the exact fields requested. "
    "Cap total words to 200."
)


def caption_prompt(brief: str, brand_voice: str | None = None) -> tuple[str, str]:
    system = SYSTEM_BASE
    task = (
        "Task: Write a social caption for the brief. Use UK English spelling. "
        "Do not include emojis unless clearly appropriate. "
        "Respect brand voice if provided. Return JSON: {\"caption\": string}.")
    if brand_voice:
        task += f"\nBrand voice: {brand_voice}"
    task += f"\nBrief: {brief}"
    return system, task


def alt_text_prompt(visual_desc: str) -> tuple[str, str]:
    system = SYSTEM_BASE
    task = (
        "Task: Write concise, descriptive alt text in UK English. "
        "Avoid promotional language. Return JSON: {\"alt_text\": string}.\n"
        f"Visual: {visual_desc}"
    )
    return system, task


def first_comment_prompt(topic: str) -> tuple[str, str]:
    system = SYSTEM_BASE
    task = (
        "Task: Draft a useful first comment to complement a post. "
        "Use UK English, avoid spam. Return JSON: {\"first_comment\": string}.\n"
        f"Topic: {topic}"
    )
    return system, task


def rewrite_to_voice_prompt(text: str, brand_voice: str) -> tuple[str, str]:
    system = SYSTEM_BASE
    task = (
        "Task: Rewrite the text to match the brand voice in UK English. "
        "Keep meaning, ensure brand-safe language. Return JSON: {\"text\": string}.\n"
        f"Text: {text}\nBrand voice: {brand_voice}"
    )
    return system, task


def hashtags_prompt(topic: str) -> tuple[str, str]:
    system = SYSTEM_BASE
    task = (
        "Task: Provide 5-12 relevant UK audience hashtags, no banned tags. "
        "Return JSON: {\"hashtags\": [string]}.\n"
        f"Topic: {topic}"
    )
    return system, task



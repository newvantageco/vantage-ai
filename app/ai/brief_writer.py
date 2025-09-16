from __future__ import annotations

from typing import Any, Dict

from app.services.model_router import ai_router


JsonDict = Dict[str, Any]


SYSTEM = (
    "You are an expert marketing analyst. Write a concise, plain-English weekly brief in UK English. "
    "Use clear headings and bullet points. Keep it actionable and neutral in tone."
)


def _build_prompt(summary: JsonDict) -> str:
    highlights = summary.get("highlights", [])
    issues = summary.get("issues", [])
    actions = summary.get("actions", [])

    def lines(items: list) -> str:
        return "\n".join(f"- {str(x)}" for x in items) if items else "- None"

    prompt = (
        "Turn the following JSON into a short weekly brief with sections 'What worked', "
        "'What didn’t', and 'Do next'. End with exactly three one-click actions in JSON.\n\n"
        f"HIGHLIGHTS:\n{lines(highlights)}\n\n"
        f"ISSUES:\n{lines(issues)}\n\n"
        f"ACTIONS (hints):\n{lines(actions)}\n\n"
        "Output format:\n"
        "### What worked\n"
        "<3-5 bullets>\n\n"
        "### What didn’t\n"
        "<2-4 bullets>\n\n"
        "### Do next\n"
        "<3-5 bullets>\n\n"
        "Actions JSON (exactly three, valid JSON array):\n"
    )
    return prompt


async def write_brief_markdown(summary: JsonDict) -> Dict[str, str]:
    prompt = _build_prompt(summary)
    text = await ai_router.rewrite_to_voice(system=SYSTEM, prompt=prompt)
    # The model returns text; try to split out the trailing JSON if present. Keep markdown intact.
    md = text.strip()
    return {"markdown": md}



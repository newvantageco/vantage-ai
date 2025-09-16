from __future__ import annotations

import asyncio
import os

from app.services.model_router import AIRouter


async def _call_all(router: AIRouter):
    res = {}
    res["caption"] = await router.generate_caption(None, 'return JSON {"caption": "hi"}')
    res["text"] = await router.rewrite_to_voice(None, 'return JSON {"text": "hi"}')
    res["hashtags"] = await router.hashtags(None, 'return JSON {"hashtags": []}')
    res["first_comment"] = await router.first_comment(None, 'return JSON {"first_comment": "hi"}')
    return res


def test_stub_outputs_when_unset():
    os.environ.pop("OPEN_MODEL_ENDPOINT", None)
    os.environ.pop("OPEN_MODEL_API_KEY", None)
    os.environ["MODEL_MODE"] = "open"
    router = AIRouter()
    res = asyncio.run(_call_all(router))
    assert res["caption"].startswith("{\"caption\"")
    assert res["text"].startswith("{\"text\"")
    assert res["hashtags"].startswith("{\"hashtags\"")
    assert res["first_comment"].startswith("{\"first_comment\"")



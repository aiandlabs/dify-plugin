"""Live checks of the plugin's model class against https://api.aiand.com/v1.

Drives AiandLargeLanguageModel with schemas built from this plugin's own YAML files:

    AIAND_API_KEY=sk-... uv run --with "dify_plugin==0.10.2" --with pyyaml python tests/live_test.py [model-id ...]
"""

import base64
import os
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import yaml  # noqa: E402
from dify_plugin.entities.model import AIModelEntity, ModelFeature  # noqa: E402
from dify_plugin.entities.model.message import (  # noqa: E402
    ImagePromptMessageContent,
    PromptMessageTool,
    TextPromptMessageContent,
    UserPromptMessage,
)
from models.llm.llm import AiandLargeLanguageModel  # noqa: E402

KEY = os.environ["AIAND_API_KEY"]
WEATHER = PromptMessageTool(
    name="get_weather",
    description="Get the current weather for a city.",
    parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
)
failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)
    if not ok:
        failures.append(name)


def schemas():
    """Models in _position.yaml order, the order the provider validates against."""
    llm_dir = ROOT / "models/llm"
    position = yaml.safe_load((llm_dir / "_position.yaml").read_text())
    out = []
    for f in llm_dir.glob("*.yaml"):
        if f.name.startswith("_"):
            continue
        d = yaml.safe_load(f.read_text())
        d["fetch_from"] = "predefined-model"
        out.append(AIModelEntity(**d))
    return sorted(out, key=lambda s: position.index(s.model))


def png(r, g, b, size=64):
    raw = b"".join(b"\x00" + bytes([r, g, b]) * size for _ in range(size))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    body = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    return "data:image/png;base64," + base64.b64encode(body).decode()


def collect(gen):
    text, calls = "", []
    for ch in gen:
        text += ch.delta.message.content or ""
        calls += ch.delta.message.tool_calls or []
    return text, calls


def run(llm, schema):
    m = schema.model
    ask = [UserPromptMessage(content="Reply with the single word: pong")]
    params = {"max_tokens": 2048}

    text, _ = collect(llm.invoke(m, {"api_key": KEY}, ask, params, stream=False))
    check(f"{m} blocking", "pong" in text.lower(), text[-40:])

    text, _ = collect(llm.invoke(m, {"api_key": KEY}, ask, params, stream=True))
    check(f"{m} stream", "pong" in text.lower(), text[-40:])

    weather = [UserPromptMessage(content="What's the weather in Tokyo? Use the tool.")]
    _, calls = collect(llm.invoke(m, {"api_key": KEY}, weather, params, tools=[WEATHER], stream=True))
    check(f"{m} tool call", any(c.function.name == "get_weather" for c in calls))

    effort = next((r for r in schema.parameter_rules if r.name == "reasoning_effort"), None)
    if effort and "none" in effort.options:
        text, _ = collect(llm.invoke(m, {"api_key": KEY}, ask, {**params, "reasoning_effort": "none"}, stream=True))
        check(f"{m} reasoning none", "pong" in text.lower() and "<think>" not in text, text[-40:])

    if ModelFeature.VISION in (schema.features or []):
        img = [
            UserPromptMessage(
                content=[
                    ImagePromptMessageContent(format="png", mime_type="image/png", base64_data="", url=png(220, 20, 20)),
                    TextPromptMessageContent(data="What colour is this image? One word."),
                ]
            )
        ]
        text, _ = collect(llm.invoke(m, {"api_key": KEY}, img, params, stream=True))
        check(f"{m} vision", "red" in text.lower(), text[-40:])


def main():
    all_schemas = schemas()
    llm = AiandLargeLanguageModel(model_schemas=all_schemas)
    llm.validate_credentials(all_schemas[0].model, {"api_key": KEY})
    check("credentials", True)
    unknown = set(sys.argv[1:]) - {s.model for s in all_schemas}
    if unknown:
        sys.exit(f"unknown model id: {', '.join(sorted(unknown))}")
    for s in all_schemas:
        if sys.argv[1:] and s.model not in sys.argv[1:]:
            continue
        try:
            run(llm, s)
        except Exception as e:
            check(f"{s.model} error", False, str(e)[:200])
    print(f"\n{len(failures)} failed" if failures else "\nall passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

"""Regenerate models/llm/*.yaml from the public ai& catalog.

Run after ai& adds, retires, or reprices a model:

    python scripts/generate_models.py
"""

import json
from decimal import Decimal
import pathlib
import urllib.request

CATALOG_URL = "https://api.aiand.com/v1/models"
OUT = pathlib.Path(__file__).resolve().parent.parent / "models" / "llm"
DEFAULT_MAX_TOKENS = 8192

FEATURES = {
    "tool_calling": ["tool-call", "multi-tool-call", "stream-tool-call"],
    "reasoning": ["agent-thought"],
    "vision": ["vision"],
    "video": ["video"],
}


def file_name(model_id: str) -> str:
    return model_id.split("/")[-1] + ".yaml"


def price(per_1m: str) -> str:
    return format(Decimal(per_1m).normalize(), "f")


def render(m: dict) -> str:
    features = [f for cap in m["capabilities"] for f in FEATURES.get(cap, [])]
    max_out = m["max_output_tokens"]
    lines = [
        f"model: {m['id']}",
        "label:",
        f"  en_US: {m['id']}",
        "model_type: llm",
        "features:",
        *[f"  - {f}" for f in features],
        "model_properties:",
        "  mode: chat",
        f"  context_size: {m['context_window']}",
        "parameter_rules:",
        "  - name: temperature",
        "    use_template: temperature",
        "  - name: top_p",
        "    use_template: top_p",
        "  - name: max_tokens",
        "    use_template: max_tokens",
        f"    default: {min(DEFAULT_MAX_TOKENS, max_out)}",
        "    min: 1",
        f"    max: {max_out}",
    ]
    efforts = m.get("reasoning_efforts") or []
    if efforts:
        lines += [
            "  - name: reasoning_effort",
            "    type: string",
            "    required: true",
            f"    default: {m['reasoning_effort_default']}",
            "    label:",
            "      en_US: Reasoning effort",
            "      ja_JP: 推論の強度",
            "    help:",
            "      en_US: How much the model reasons before answering. none turns reasoning off where the model supports it.",
            "      ja_JP: 回答前にモデルが推論する量です。none は対応モデルで推論をオフにします。",
            "    options:",
            *[f"      - {e}" for e in efforts],
        ]
    lines += [
        "  - name: response_format",
        "    use_template: response_format",
        "    options:",
        "      - text",
        "      - json_object",
        "      - json_schema",
        "  - name: json_schema",
        "    use_template: json_schema",
        "pricing:",
        f"  input: \"{price(m['input_per_1m'])}\"",
        f"  output: \"{price(m['output_per_1m'])}\"",
        "  unit: \"0.000001\"",
        "  currency: USD",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    with urllib.request.urlopen(CATALOG_URL, timeout=30) as r:
        # A model with a retirement date stays in /v1/models until then; leave it out so a release never ships one.
        models = [m for m in json.load(r)["data"] if not m.get("deprecation_date")]
    for old in OUT.glob("*.yaml"):
        old.unlink()
    for m in models:
        (OUT / file_name(m["id"])).write_text(render(m))
    (OUT / "_position.yaml").write_text("".join(f"- {m['id']}\n" for m in models))
    print(f"wrote {len(models)} models to {OUT}")


if __name__ == "__main__":
    main()

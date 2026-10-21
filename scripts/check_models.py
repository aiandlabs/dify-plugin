"""Load the provider and every model YAML through the Dify SDK's own schemas.

    python scripts/check_models.py
"""

import pathlib
import sys

import yaml
from dify_plugin.entities.model import AIModelEntity
from dify_plugin.entities.model.provider import ProviderEntity

ROOT = pathlib.Path(__file__).resolve().parent.parent
LLM = ROOT / "models" / "llm"

provider = yaml.safe_load((ROOT / "provider" / "aiand.yaml").read_text())
ProviderEntity(**{k: v for k, v in provider.items() if k not in ("models", "extra")})

models = {}
for f in sorted(LLM.glob("*.yaml")):
    if f.name.startswith("_"):
        continue
    data = yaml.safe_load(f.read_text())
    models[data["model"]] = AIModelEntity(**data, fetch_from="predefined-model")

position = yaml.safe_load((LLM / "_position.yaml").read_text())
if sorted(position) != sorted(models):
    sys.exit(f"_position.yaml does not match the model files: {sorted(set(position) ^ set(models))}")

print(f"provider and {len(models)} models match the SDK schemas")

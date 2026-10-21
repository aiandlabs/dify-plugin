"""Load the provider and its model YAMLs through the Dify SDK's own schemas.

    python scripts/check_models.py
"""

import collections
import os
import pathlib
import sys

import yaml
from dify_plugin.entities.model import AIModelEntity, ParameterRule
from dify_plugin.entities.model.provider import ProviderEntity

ROOT = pathlib.Path(__file__).resolve().parent.parent
# The SDK resolves the provider's model globs against the working directory.
os.chdir(ROOT)

provider = ProviderEntity(**yaml.safe_load(pathlib.Path("provider/aiand.yaml").read_text()))
if not provider.models:
    sys.exit("provider/aiand.yaml loaded no models")

# The SDK ignores unknown keys, so a generator typo (e.g. `pricng:`) would otherwise pass silently.
MODEL_KEYS = set(AIModelEntity.model_fields)
RULE_KEYS = set(ParameterRule.model_fields)
errors = []
for f in sorted(pathlib.Path("models/llm").glob("[!_]*.yaml")):
    data = yaml.safe_load(f.read_text())
    errors += [f"{f.name}: unknown key `{k}`" for k in sorted(set(data) - MODEL_KEYS)]
    for rule in data.get("parameter_rules", []):
        errors += [f"{f.name}: rule `{rule.get('name')}` has unknown key `{k}`" for k in sorted(set(rule) - RULE_KEYS)]

position = yaml.safe_load(pathlib.Path("models/llm/_position.yaml").read_text())
loaded = [m.model for m in provider.models]
counts = collections.Counter(position)
errors += [f"_position.yaml lists `{m}` {n} times" for m, n in counts.items() if n > 1]
errors += [f"_position.yaml lists `{m}` but no model file defines it" for m in sorted(set(position) - set(loaded))]
errors += [f"`{m}` has a model file but is missing from _position.yaml" for m in sorted(set(loaded) - set(position))]

if errors:
    sys.exit("\n".join(errors))
print(f"provider and {len(loaded)} models match the SDK schemas")

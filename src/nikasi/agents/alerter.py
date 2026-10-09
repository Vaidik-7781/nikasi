"""Alert wording. The fixed template is the source of truth. A model may reword it,
but its text is used only if it keeps the verdict word first, adds no number that is
not in the template, claims no safety, and stays short. Otherwise: the template."""
from __future__ import annotations
import os, re
from .. import templates

_NUM = re.compile(r"\d+(?:\.\d+)?")
_BANNED = ("safe", "guarantee", "no risk", "definitely", "certainly")

def accept(candidate: str, base: str) -> bool:
    c = candidate.strip()
    if not c or len(c) > 280:
        return False
    verdict = base.split(":")[0].split(" (")[0]          # GO / CAUTION / NO-GO
    if not c.startswith(verdict):
        return False
    if set(_NUM.findall(c)) - set(_NUM.findall(base)):
        return False
    low = c.lower()
    return not any(w in low for w in _BANNED)

def write_alert(item: dict, llm=None) -> tuple[str, str]:
    base = templates.render(item)
    if llm is None or item["state"] == "UNKNOWN":      # never ask a model about missing data
        return base, "template"
    try:
        text = llm(f"Reword this flood alert for a commuter in one or two short sentences. "
                   f"Keep the first word and every number exactly. Add no advice about safety.\n{base}")
    except Exception:
        return base, "template"
    return (text.strip(), "model") if accept(text, base) else (base, "template")

def bedrock_llm(model_id: str | None = None, guardrail_id: str | None = None):
    """Converse API with an optional Guardrail. Returns None when no model is configured."""
    model_id = model_id or os.environ.get("BEDROCK_MODEL_ID")
    if not model_id:
        return None
    guardrail_id = guardrail_id or os.environ.get("GUARDRAIL_ID")
    import boto3
    rt = boto3.client("bedrock-runtime")
    def call(prompt: str) -> str:
        kw = {"modelId": model_id, "messages": [{"role": "user", "content": [{"text": prompt}]}],
              "inferenceConfig": {"maxTokens": 120, "temperature": 0.2}}
        if guardrail_id:
            kw["guardrailConfig"] = {"guardrailIdentifier": guardrail_id,
                                     "guardrailVersion": os.environ.get("GUARDRAIL_VERSION", "DRAFT")}
        return rt.converse(**kw)["output"]["message"]["content"][0]["text"]
    return call

def strands_llm(model_id: str | None = None, guardrail_id: str | None = None):
    """Same job through the open-source Strands Agents SDK (AWS). UNTESTED against a live model.
    Returns None if the SDK or a model id is missing. Install: pip install strands-agents."""
    model_id = model_id or os.environ.get("BEDROCK_MODEL_ID")
    if not model_id:
        return None
    try:
        from strands import Agent
        from strands.models import BedrockModel
    except ImportError:
        return None
    guardrail_id = guardrail_id or os.environ.get("GUARDRAIL_ID")
    kw = {"model_id": model_id}
    if guardrail_id:
        kw.update(guardrail_id=guardrail_id, guardrail_version=os.environ.get("GUARDRAIL_VERSION", "DRAFT"))
    agent = Agent(model=BedrockModel(**kw), tools=[],
                  system_prompt="You reword flood alerts. Keep the first word and every number exactly. Never claim anything is safe.")
    return lambda prompt: str(agent(prompt))

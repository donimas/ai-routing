"""Tiny task router: Haiku classifies the task, a table picks model + effort.

Unknown or unparseable label -> middle tier, never the cheapest.
Needs: pip install anthropic, ANTHROPIC_API_KEY. by @donimas · AI Levels series
"""
import sys

import anthropic

CLASSIFIER = "claude-haiku-5-5"
ROUTES = {  # task type -> (model, effort)
    "lookup": ("claude-haiku-5-5", "low"),     # find, list, summarise, rename
    "edit": ("claude-sonnet-5-5", "medium"),   # scoped feature or fix
    "debug": ("claude-sonnet-5-5", "high"),    # unclear failure, many files
    "risky": ("claude-opus-5-5", "high"),      # auth, payments, migrations, security
}
FALLBACK = ("claude-sonnet-5-5", "medium")
LABELS = ", ".join(ROUTES)


def classify(client: anthropic.Anthropic, task: str) -> str | None:
    msg = client.messages.create(
        model=CLASSIFIER, max_tokens=10, thinking={"type": "disabled"},
        output_config={"effort": "low"},
        system=f"Classify the coding task. Reply with one word only: {LABELS}. "
               "Use 'risky' for auth, payments, data migrations, security or data loss.",
        messages=[{"role": "user", "content": task}],
    )
    label = "".join(b.text for b in msg.content if b.type == "text").strip().lower()
    return label if label in ROUTES else None


def route(client: anthropic.Anthropic, task: str) -> tuple[str | None, str, str, anthropic.types.Message]:
    label = classify(client, task)
    model, effort = ROUTES.get(label, FALLBACK)
    reply = client.messages.create(
        model=model, max_tokens=16000, output_config={"effort": effort},
        messages=[{"role": "user", "content": task}],
    )
    return label, model, effort, reply


if __name__ == "__main__":
    label, model, effort, reply = route(anthropic.Anthropic(), " ".join(sys.argv[1:]))
    print(f"[{label or 'unsure'} -> {model} @ {effort}]")
    print("".join(b.text for b in reply.content if b.type == "text"))

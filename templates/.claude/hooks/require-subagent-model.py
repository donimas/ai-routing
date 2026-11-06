#!/usr/bin/env python3
"""PreToolUse hook for the Agent tool: block subagent spawns with no explicit model.

A spawn is allowed when either
  - the call itself passes `model` (tool_input.model), or
  - the subagent's definition file (.claude/agents/*.md, project or user) has a `model:` line.
Everything else (built-in general-purpose / Explore / Plan, agents without `model:`) is denied,
so nothing silently inherits the main model.

Set ROUTING_HOOK_LOG=/path/file.jsonl to log every input this hook sees.
by @donimas · AI Levels series
"""
import json
import os
import re
import sys
from pathlib import Path


def agent_dirs() -> list[Path]:
    project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    return [Path(project) / ".claude" / "agents", Path.home() / ".claude" / "agents"]


def frontmatter_model(agent_name: str) -> str | None:
    """Return the `model` value of the agent definition named agent_name, or None."""
    for directory in agent_dirs():
        if not directory.is_dir():
            continue
        for path in directory.glob("*.md"):
            match = re.match(r"^---\n(.*?)\n---", path.read_text(encoding="utf-8"), re.S)
            if not match:
                continue
            fields = dict(re.findall(r"^(\w+):\s*(.+?)\s*$", match.group(1), re.M))
            if fields.get("name") == agent_name:
                return fields.get("model")
    return None


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def main() -> None:
    data = json.load(sys.stdin)
    log = os.environ.get("ROUTING_HOOK_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(data) + "\n")
    tool_input = data.get("tool_input") or {}
    if tool_input.get("model"):
        sys.exit(0)
    agent = tool_input.get("subagent_type") or "general-purpose"
    if frontmatter_model(agent):
        sys.exit(0)
    deny(f"Subagent '{agent}' has no explicit model. Retry the Agent call with "
         "model set to haiku (search, tests), sonnet (edits) or opus (risky review), "
         "or delegate to one of the routed agents in .claude/agents/.")


if __name__ == "__main__":
    main()

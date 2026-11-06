# AI Routing cheat sheet: Claude Code

Pick the **cheapest model × effort that reliably solves the task**. When unsure, use the middle tier. Verify by risk. Escalate the failing step, not the whole task.

## Model × effort matrix

| | `low` | `medium` | `high` | `xhigh` / `max` |
| - | - | - | - | - |
| **Haiku 5.5**: $0.10 / $0.50 (≤100K prompt) | find a file, list usages, run tests and report | rename, small mechanical edit | classification with strict rules | rarely worth it, compare with Sonnet |
| **Sonnet 5.5**: $2 / $10 | quick question about code you'll review | **default**: scoped feature, clear bug fix | bug in unfamiliar code, edge cases | long multi-hour task, only if evals show a gain |
| **Opus 5.5**: $4 / $20 | – | architecture question, plan review | **risky diff review**: auth, money, migrations | security audit, hard root cause |
| **Fable 5.1**: $10 / $50 | – | – | ambiguous multi-day work, outage debugging | the hardest work, or as the advisor |

Prices are per 1M input / output tokens. Cache hits cost 0.05× on Opus and Sonnet 5.5, 0.025× on Fable 5.1, 0.1× elsewhere.
**On Claude Code < v2.1.293, `haiku` is Haiku 4.5** ($1 / $5, no effort), and on < v2.1.284, `sonnet` is Sonnet 5. Run `claude update`.

## GOAT setup checklist

- [ ] `.claude/settings.json`: `"model": "sonnet"`, `"effortLevel": "medium"`, `"advisorModel": "opus"`
- [ ] `.claude/agents/`: `code-searcher` (haiku · low, read-only), `implementer` (sonnet · medium), `test-runner` (haiku · low), `reviewer` (opus · high)
- [ ] Every agent has `model:` **and** `effort:` spelled exactly like that (typos are ignored silently)
- [ ] CLAUDE.md routing table: the task → agent map, "unsure → sonnet", "fails twice → reviewer", "no `/model` mid-task"
- [ ] Optional: a `PreToolUse` hook on `Agent` that denies spawns without a model (`require-subagent-model.py`)
- [ ] `env | grep CLAUDE_CODE_`: no stray `CLAUDE_CODE_EFFORT_LEVEL` or `CLAUDE_CODE_SUBAGENT_MODEL(_FORCE)`
- [ ] Measure: `/usage`, `/tasks`, and `claude -p … --output-format json`, then compare **cost per solved task** before and after

## Top 3 pitfalls

1. **Env vars beat your config.** `CLAUDE_CODE_EFFORT_LEVEL` overrides `/effort`, settings and agent `effort:`. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` overrides every agent's `model:`.
2. **Inheritance is the default.** A subagent with no `model:` (built-in Explore and general-purpose included) runs on your main model. Main on Opus means search on Opus.
3. **`/model` mid-task costs a full cache miss.** The next request re-reads the whole conversation uncached (tested: 0 cached tokens read, 37,659 rewritten). Delegate to a fixed-model subagent instead. Subagents don't touch the parent's cache.

Model resolution for subagents: per-call `model` → frontmatter `model` (`inherit` = main) → `CLAUDE_CODE_SUBAGENT_MODEL` → main model.

---

*by @donimas · AI Levels series* · tested on Claude Code 2.1.280 and 2.1.311, 2026-11-06

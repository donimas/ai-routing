## Model routing

You are the orchestrator. Do not do bulk work in the main conversation: delegate it.

| Task type | Delegate to | Model · effort |
| - | - | - |
| Find files, symbols, usages, "where is X" | `code-searcher` | haiku · low |
| Scoped edit: feature, fix, refactor in a few files | `implementer` | sonnet · medium |
| Run tests, lint, build; report failures | `test-runner` | haiku · low |
| Review a risky diff: auth, payments, migrations, security, public API, concurrency | `reviewer` | opus · high |
| Anything else | `general-purpose` with `model: "sonnet"` | sonnet · session effort |

Rules:

1. Every delegation names one of the agents above, or passes `model` explicitly. Never let a subagent inherit the main model by accident.
2. When unsure of the tier, use the middle tier (sonnet). Never the cheapest tier on risky work.
3. Verify by risk: after every `implementer` edit, run `test-runner`. Send the diff to `reviewer` only when it touches the risky list above.
4. Escalate, don't loop: if the same test fails twice after `implementer` fixes, stop retrying. Send the diff and the failure to `reviewer`, then re-run `implementer` with the reviewer's findings. Do not re-run the whole task on a bigger model.
5. Keep one model per task. Do not run `/model` mid-task; delegate instead. A model switch re-reads the whole conversation with no cache hits.
6. Use the advisor before committing to an approach on a multi-file change, and before declaring a long task done.

<!-- by @donimas · AI Levels series -->

# Implicit Knowledge Found

## IK-01
What:
The official test/verification command and the expected passing baseline (27 tests before CR-001).

How was it discovered:
Inferred. README.md documents `pytest -v`, AGENTS.md only says "Run pytest before and after changes". The agent chose `python -m pytest` on its own. No single verification script exists.

Should this remain implicit?
NO

Where should it become explicit?
AGENTS.md (Standard Commands) / scripts/verify_repo.sh

Remediation:
Add Standard Commands to AGENTS.md and a `scripts/verify_repo.sh` that runs the test suite and repository checks with a deterministic PASS/FAIL output.

## IK-02
What:
Which documentation must be updated when code behavior changes (README.md, docs/tracebility.md) and whether that counts as in scope for a task.

How was it discovered:
Not documented. The agent decided to edit README.md and docs/tracebility.md based on the generic AGENTS.md rule "Documentation reflects final behavior".

Risk:
Scope ambiguity: agents may skip required doc updates or modify documentation that should not change, making out-of-scope changes hard to judge.

Should this remain implicit?
NO

Where should it become explicit?
AGENTS.md (Change Rules / Definition of Done) / docs/REPO_MAP.md (Change Guide)

Remediation:
List in the Change Guide which documents must be updated per type of change.

## IK-03
What:
Which git operations the agent may run (e.g. `git stash`, `git checkout`, `git reset`) and which files must never be edited directly (e.g. `data/customers.json`, `.env`).

How was it discovered:
Not documented. The agent ran `git stash` / `git stash pop` to test against the original code; nothing in the repository allowed or forbade it. There is no list of protected paths.

Risk:
An agent could run state-altering git commands or edit runtime data, losing uncommitted work or real customer records.

Should this remain implicit?
NO

Where should it become explicit?
AGENTS.md (Stop Conditions / Change Rules) / docs/REPO_MAP.md (Do Not Edit Directly)

Remediation:
AGENTS.md stop conditions + a deterministic protected-path check in `scripts/check_repo_contract.py`.

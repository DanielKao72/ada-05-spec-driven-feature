# Human Review Decisions

## Change
CR-002

* **Review report:** `results/review-report.md`
* **Commit reviewed:** 3e21ffc

### RF-01
* **Reviewer severity:** SHOULD FIX
* **Human decision:** MODIFIED
* **Reason:** The behavior is valid under the specification. SPEC.md > Error Handling ties HTTP 422 to failed Pydantic validation, and forms such as `2.0` and `1_0` pass it. A custom parser would add code without a requirement that demands it. The reviewer is right that no test pins this behavior, so a framework upgrade could change it unnoticed.
Final severity: SHOULD FIX
Interpretation: For FR-09, AC-17 and TS-19, "non-integer" means a value that Pydantic's integer parsing rejects.
Required action: Do not change production code. Add API tests that pin the current behavior:
    - `limit=2.0`, `offset=1.0`, `limit=1_0`, `offset=1_0`, `limit=+5`, `limit=%205` and `limit=5%20` return HTTP 200 with the expected records.
    - `limit=1.5`, `limit=abc`, `limit=true`, an empty `limit`, `limit=1e1` and `limit=0x10` return HTTP 422.

### RF-02
* **Reviewer severity:** OPTIONAL
* **Human decision:** MODIFIED
* **Reason:** The drift is real and cheap to correct, but the Change Request locks `docs/REPO_MAP.md` during implementation, so one part cannot go to the coder agent.
* **Final severity:** OPTIONAL
* **Required action:**
    - Coder agent: add the missing test files to the project tree in `README.md`, and update the scenario range in the NFR-03 row of `docs/tracebility.md`.
    - Human: update the test file entry in `docs/REPO_MAP.md` in a separate commit.

### RF-03
* **Reviewer severity:** OPTIONAL
* **Human decision:** DEFERRED
* **Reason:** The finding is correct: the message of commit a2eb747 describes work from other commits. Rewording it would change a commit hash cited by the review evidence, and no code changed after the verified commit.
* **Required action:** Do not rewrite history. Record the note in `results/PR_EVIDENCE.md`.

### RF-04
* **Reviewer severity:** OPTIONAL
* **Human decision:** ACCEPTED
* **Reason:** The behavior is correct today, but the response format and the upper limit are not asserted directly. The tests are small and within the scope of CR-002.
* **Required action:** Add one API test that compares a paginated response to the matching slice of the full listing, field for field, and one API test that requests `limit=100` over 101 stored records.

## Open Items From the Review Report
- Missing Evidence 1 (screenshots without a commit hash): capture the next verification as text output together with `git rev-parse HEAD`.
- Missing Evidence 2 (CI not inspected): inspect the `.github/workflows/verify.yml` result on the pull request.
- Missing Evidence 3 (lint and security checks): not configured. Record as a remaining risk.
- Missing Evidence 4 and 5 (5000-digit offset, repeated parameters): no action.
- Missing Evidence 6 (malformed stored records, pre-existing): outside CR-002. Record as a remaining risk for a future change request.
- Missing Evidence 7 (protected-path check compares against HEAD): continue checking file scope with `git diff --name-only`.

## Human Gate
[x] Return to coder-agent
[ ] Ready for final re-review
[ ] Stop / escalate

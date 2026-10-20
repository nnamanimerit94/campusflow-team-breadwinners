# CampusFlow Next — Engineering Contracts

**Status:** Proposed for joint Engineer A / Engineer B review; not yet approved or implemented.  
**Baseline:** Original CampusFlow `main`, commit `807311f` (baseline documentation), 119 existing automated tests passing; manual lifecycle and persistence checks completed.  
**Source of requirements:** *CampusFlow Next — Guided Reliability, Search & Engineering Quality Sprint*, sections 01–11.  
**Purpose:** Agree on data structures, behavior, ownership, and integration boundaries **before feature development**.

## 1. Scope and preservation rules

Upgrade the existing Python standard-library CLI; do not rebuild it or introduce web frameworks, databases, APIs, cloud infrastructure, or paid AI integrations.

Preserve ticket creation, assignment, priority precedence, lifecycle (`open → in_progress → resolved`, and `resolved → open` via reopen), original Open Work Queue, reports, JSON save/load, CLI, and existing regression tests. The original Open Work Queue contains **only `open` tickets**, ordered `critical > high > medium > low`, then ascending numeric ticket ID. Search is a separate read-only view.

Priority precedence: `critical` when urgency is `high` **and** affected users ≥10; else `high` when urgency is `high` **or** affected users ≥10; else `medium` when urgency is `medium` **or** affected users ≥3; otherwise `low`.

## 2. Canonical ticket and note schema

Persist the existing top-level **dictionary keyed by ticket ID** (`{"T001": {...}}`), retaining all original fields and adding `notes`, initially `[]` for new tickets.

```python
{
    "T001": {
        "id": "T001",
        "title": "wifi is down",
        "category": "Network",
        "urgency": "low",
        "affected_users": 40,
        "priority": "high",
        "status": "open",
        "assigned_to": "kingsley",
        "notes": [
            {"note_id": "N001", "author": "Mentor A", "message": "Wi-Fi router reboot attempted"},
            {"note_id": "N002", "author": "Mentor B", "message": "Investigating switch ports"}
        ]
    }
}
```

**Note ID scope:** IDs are sequential **per ticket**, beginning at `N001`. `T001/N001` and `T002/N001` are distinct. Generate the next ID after the greatest existing numeric note ID for that ticket; rejected note operations do **not** consume IDs. Do not fill gaps. Existing notes are returned/displayed in ascending numeric note-ID order. A successful reload must preserve all notes and generate collision-free next ticket/note IDs.

**Legacy compatibility:** Existing valid tickets with all eight original fields but no `notes` are supported. Normalize them to `notes: []` **in a validated working copy**, without modifying the source file during load. Do not silently repair other malformed data. The README will describe this compatibility rule.

**Ticket ID format:** `T` followed by at least three decimal digits, numeric value ≥1 (e.g., `T001`, `T100`, `T1000`); the dictionary key must match the record's `id`. IDs must be unique. Next ID follows the highest existing numeric ID. **Confirm format details with both engineers before implementation**, especially any assumptions in existing tests.

## 3. Validation and lifecycle invariants (Engineer A)

- `title`: string, nonblank after `strip()`.
- `category`: one of `Network`, `Hardware`, `Software`, `Other` (CLI may normalize input).
- `urgency`: `low`, `medium`, `high` (CLI may normalize input).
- `affected_users`: strictly positive **actual integer**; reject zero, negative, float, string, and bool.
- `priority`: must match the prescribed precedence calculated from urgency and affected users.
- `status`: one of `open`, `in_progress`, `resolved`.
- `assigned_to`: `None` or nonblank string; assignment/reassignment to a resolved ticket is forbidden.
- An unassigned `open` ticket cannot move to `in_progress`.
- Allowed lifecycle transitions: `open → in_progress` (assigned), `in_progress → resolved`, `resolved → open` via `reopen_ticket` only. Reject all others.
- All invalid create, assignment, status, and note actions must leave the **entire ticket collection unchanged**.
- Keep current functions' behavior where already tested; business functions may mutate the passed collection on success, while CLI transaction handling stages changes before saving/publishing.

## 4. Notes API (Engineer A owns business logic; Engineer B owns CLI)

**Proposed interface** (subject to joint agreement):

```python
add_note(tickets: dict, ticket_id: str, author: str, message: str) -> dict
get_notes(tickets: dict, ticket_id: str) -> list[dict]
next_note_id(ticket: dict) -> str
```

- `add_note` checks ticket existence, status (`open` or `in_progress`), nonblank author, and message length **5–300 characters after trimming**. It appends exactly one `{"note_id", "author", "message"}` record on success and returns that note. On failure, nothing changes and no ID is consumed.
- `get_notes` retrieves existing notes in ascending numeric ID order, including for resolved tickets; **read-only** (return a safe copy or guarantee no mutation through the returned value).
- `next_note_id` computes without mutating state. It uses the greatest existing note ID on that ticket, not a global counter.
- `KeyError` for an unknown ticket; `TypeError` for incorrect input types; `ValueError` for invalid values, state transitions, and invalid persisted data. The CLI catches these and shows friendly messages.
- Notes remain intact across resolve/reopen and save/reload.

## 5. JSON and transaction contract (Engineer A; CLI integration with B)

**Existing APIs to retain where possible:**

```python
load_tickets(file_path) -> dict
save_tickets(tickets: dict, file_path) -> None
```

- Preserve the existing dictionary JSON envelope; no incompatible migration should be necessary.
- Loading parses **and validates the complete collection** before returning it. Check required ticket fields, types, key/ID consistency, unique IDs, canonical values, priority consistency, legal status, note structure, message constraints, and **note-ID uniqueness within each ticket**.
- JSON object keys cannot express duplicate keys in an ordinary Python dictionary. **Detect duplicate ticket IDs in the raw JSON parsing step** (e.g., via `object_pairs_hook`) rather than relying on a post-`json.load` dictionary scan; reject duplicates rather than silently overwriting records.
- Missing file: preserve the existing behavior of returning `{}`. Malformed JSON or invalid records: raise `ValueError` and do not replace active in-memory state or rewrite source data.
- Reload flow: load/validate to a candidate collection, then replace the active collection **only after full success**. A failed reload retains the prior active collection.
- Saving writes to a temporary file in the destination directory, flushes, then atomically replaces the destination; clean up temporary files after failures. Handle the missing parent `data/` directory deliberately (create it safely or document an enforced setup step; prefer reliable fresh-clone behavior).
- CLI mutation flow: deep-copy current collection → apply business operation to copy → save copy → publish copy only if saving succeeds. Failed validation or save leaves current active state unchanged. Avoid stale references to the old collection after publication.
- The original file should remain intact on a failed write before replacement. Report I/O errors without claiming a successful save.

**Existing-test compatibility to resolve explicitly:** Several old `test_storage.py` cases save intentionally incomplete ticket records and then load or inspect them. Decide whether these tests are storage-only serialization checks or must be updated to use valid ticket fixtures for validated loading; do not weaken new load validation simply to keep incomplete fixtures passing. Update tests transparently and explain the contract change.

## 6. Search and reports (Engineer B)

**Proposed interfaces** (subject to joint agreement):

```python
search_tickets(tickets: dict, title: str = "", category: str = "", status: str = "", priority: str = "") -> list[dict]
get_ticket_report(tickets: dict) -> dict
```

- Search is **read-only**; title uses `casefold()` substring matching. Empty filter means no restriction. All supplied filters use logical **AND**. CLI invalid category/status/priority choices trigger retry. No fuzzy spelling correction.
- Search output includes ticket ID, title, category, priority, status, and assigned mentor.
- Preserve `list_tickets()` and `get_open_work_queue()` behavior. An **optional separate** priority-sorted search view may be added, but never alter original queue semantics.
- Extend existing `get_ticket_report()` keys (`total`, `by_status`, `by_priority`) rather than replacing them. Add `by_category`, `unresolved_count` (`open + in_progress`), `resolved_count`, and `resolution_percentage` (`resolved / total * 100`, or `0.0` for empty). Reopened tickets count by **current** status; no double counting.

## 7. CLI and Engineering Understanding Check (Engineer B)

Add CLI options for **Add Follow-up Note**, **View Ticket Notes**, **Search Tickets**, **Reload Tickets**, and **Engineering Understanding Check** without removing original options 1–8 or 0. The exact new menu numbering is for B to propose and A to approve before coding.

The understanding check contains **six required multiple-choice scenario questions from section 05 of the assessment**. Keep question bank separate from scoring. Accept only A/B/C/D; invalid input re-prompts. Record the first **valid** submitted choice for each question, score one point per correct answer (0–6), and display final score. Prompt for short explanations of at least two answers for mentor discussion; do not automatically mark explanations correct based on keywords. Both engineers complete the check independently.

## 8. Ownership and integration dependencies

| Area | Engineer A | Engineer B |
|---|---|---|
| Validation, ticket ID safety, workflow invariants | Implement + test | Review |
| Note model, add/read/next-ID APIs | Implement + test | Consume APIs in CLI |
| JSON validation, save/reload semantics | Implement + test | CLI reload/menu integration |
| Combined search and reporting | Review | Implement + test |
| Understanding Check, interactive menus, input retries | Review | Implement + test |
| Integration, documentation, bug-hunter tests, PR reviews | Shared | Shared |

**Dependency:** B can implement independent search/reports/quiz logic immediately after contract approval, but note and reload CLI integration depends on A's agreed APIs. Avoid simultaneous edits to `main.py` where possible; B owns CLI changes.

## 9. Verification and collaboration gates

- Keep all existing CampusFlow regression behavior; run `python3 -m unittest discover -s tests -v` from the project root.
- Add **at least 14 meaningful integrated tests**, **at least five authored by each engineer**, covering the assessment's 14 specified scenarios: priority precedence; unassigned transition unchanged; resolved assignment rejection; invalid affected-user types/values; note success and IDs; rejected notes and ID continuity; resolved/reopened notes; case-insensitive title; AND filters; empty report 0%; report counts after resolve/reopen; save/load notes and IDs; corrupt/duplicate JSON preserving state; CLI quiz retry/scoring.
- Each engineer invents **one additional bug-hunter edge test for the other's module**, documenting initial state, input, expected/actual results, test name, and fix if needed.
- Each engineer completes **at least two verified AI learning cycles** in `docs/ai-learning-log.md` (concept gap, exact question, summary, unrelated experiment, independent verification, engineering decision); team records at least one genuinely challenged/changed AI suggestion.
- Create GitHub issues for A and B; use separate feature branches, **at least two focused commits per engineer**, and at least one substantial PR each. Each engineer leaves **at least two substantive review observations/questions** on the other's PR; fix blockers, rerun tests, secure partner approval **before** merge. No self-approval or direct feature commits to `main`.
- After merges, rerun the integrated suite and capture final main SHA, PR URLs, README, baseline-check.md, learning log, CLI demonstration, and individual reflections.

## 10. Observed baseline findings and risks

1. Baseline: 119 automated tests passed and manual creation, priority, assignment, lifecycle, work queue, reports, and persistence were demonstrated.
2. A missing root-level `data/` directory caused a save failure in manual testing; `mkdir -p data` was the workaround.
3. `validation.py` contains an apparently unused duplicate `calculate_priority` with different behavior; `tickets.py` and tests import `priority.py`. Verify references before cleanup.
4. `workflow.py` has an error message missing an f-string prefix for invalid transitions.
5. `load_tickets` currently validates JSON syntax but not full ticket schemas; CLI checks only the top-level dictionary.
6. Existing workflow functions mutate on success; `main.py` currently uses rollback for failed saves. New note operations require careful transaction integration.
7. Old storage fixtures include intentionally incomplete records; review test intent before changing loading semantics.

## 11. Open approval items — agree before feature coding

1. Confirm proposed `add_note`, `get_notes`, `next_note_id`, and `search_tickets` function signatures and error conventions.
2. Confirm numeric ID parsing/format constraints and behavior on malformed ID values.
3. Confirm old-ticket normalization and how strict load validation affects existing test fixtures.
4. Confirm safe-save handling for a missing `data/` directory.
5. Confirm exact CLI menu numbering and reload integration ownership.
6. Confirm which PR lands first and how B will rebase/update before CLI integration.

**Approval record:** Engineer A: _pending_ · Engineer B: _pending_ · Date: _pending_.

[DECISION_LOG M1.md](https://github.com/user-attachments/files/30711176/DECISION_LOG.M1.md)
# GenAI4P MVP — Development Decision Log

**Baseline (frozen as of 2026-08-04):** URD MVP V5.0 · SysSpec & Deployment
Plan V4.1 · DEVPLAN-P1 V1.0

## Purpose

The three baseline documents above are not edited turn-by-turn during the
build. Instead, every design/implementation decision that departs from,
clarifies, extends, or is left open against that baseline gets appended
here — chronologically, never rewritten in place, the same discipline this
project already applies to P2.1's CHANGELOG and PQ1.1's Audit Findings.
At a future rebase point, this log is applied onto the three baseline
documents in one pass, and a new frozen baseline is declared.

**Ownership:** Claude (the implementing AI chat) appends an entry here
whenever a milestone's work produces a decision worth tracking — the human
does not need to ask for it each time. If a new chat session continues
this build, paste this file's current content in first so entry numbering
stays continuous and nothing gets duplicated.

**What qualifies for an entry:** a departure from something URD/SysSpec/
DEVPLAN actually states; a design decision made where the baseline is
silent; a clarification of an ambiguous baseline requirement; a DeepSeek
finding and its resolution (or non-resolution); an open question deferred
to a later milestone. Routine code-writing that just implements the
baseline as written does not need an entry.

**Milestone change counts** are not maintained as a static summary table
here — that would require editing old sections every time a new entry is
added, which this log is designed to avoid. Count `### DEVLOG-M<n>-` lines
under a milestone's heading directly when needed.

---

## Entry format

```
### DEVLOG-M<n>-<seq> — <short title>
Date: <YYYY-MM-DD>
Type: DEPARTURE_FROM_BASELINE | DESIGN_DECISION | CLARIFICATION | OPEN_QUESTION | PROCESS_DECISION
Baseline ref: <doc §section(s), or "none — baseline is silent here">
Claude did: <what was built/proposed>
DeepSeek said: <finding, or "N/A">
Human decision: <decision + rationale, or "Not yet decided">
Status: DECIDED | OPEN | DEFERRED | SUPERSEDED
Rebase action: <what this implies for URD/SysSpec/DEVPLAN at next rebase, or "None">
```

---

## M1 — Landing page (Project Code entry + roster role selection)

### DEVLOG-M1-001 — Identity storage: user_id, no validation join
Date: 2026-08-04
Type: CLARIFICATION
Baseline ref: URD §8.3
Claude did: Roster dropdown sourced directly from `roles_roster`; the
stored `projects.created_by` value is `user_id` (e.g. "PC1"), not
`display_name`. No separate lookup/validation join at insert time — the
value is valid by construction since it can only come from the roster
query.
DeepSeek said: N/A — predates DeepSeek review.
Human decision: Confirmed correct; no join needed.
Status: DECIDED
Rebase action: None — implementation detail, no baseline conflict.

### DEVLOG-M1-002 — Dev governance vs translation governance stay separate
Date: 2026-08-04
Type: CLARIFICATION
Baseline ref: DEVPLAN-P1 §3 (M1 vs M11 split); URD §15
Claude did: M1 code writes only to `projects`. It does not write to
`dev_logs` or `governance_logs` — `governance_logs` wiring is DEVPLAN's
M11 (cross-cutting), not M1.
Human decision: Confirmed explicitly — keep dev-cycle governance (roster
acting as developers) and translation-pipeline governance (roster acting
as operators) from mixing. "You have not to mixed this two job scope."
Status: DECIDED
Rebase action: None — matches DEVPLAN's existing milestone split.

### DEVLOG-M1-003 — Visual identity drawn from P5.1a's palette
Date: 2026-08-04
Type: DESIGN_DECISION
Baseline ref: none — no baseline document specifies web-app visual design
Claude did: Adopted P5.1a SF3 Formatter's existing palette (title_color
#1A3A5C, sec_color #2E4057, header tint #D5E8F0) and Fraunces / IBM Plex
Sans / IBM Plex Mono type roles for the Streamlit app, so the web UI and
the Word deliverables read as one system.
DeepSeek said: Reviewed positively — "shows systems thinking" (M1 review
§3.1, Design Token Consistency).
Human decision: Requested ("I want the UI feel modern for a translator,
easy to navigate"); accepted as delivered.
Status: DECIDED
Rebase action: None required; optionally name this as the convention in
SysSpec §3.1 at next rebase so later milestones inherit it explicitly
rather than by precedent only.

### DEVLOG-M1-004 — Standardized error handling module
Date: 2026-08-04
Type: DESIGN_DECISION (extends URD §20.1)
Baseline ref: URD §20.1 (Error ID, Component, Severity, Observed,
Expected, Suggested next step)
Claude did: Built shared `error_handling.py` (`AppError` dataclass,
`render_error()`) implementing §20.1's field set as a `st.dialog` pop-up
with a copyable `st.code()` block. Added one field beyond the literal
§20.1 list: a best-effort "Likely cause (why)" from `guess_cause()`
pattern-matching, plus a `context` dict for extra diagnostic state.
DeepSeek said: Rated "EXCELLENT... a standout piece of work" (M1 review
§3.1). Separately raised Finding M1-F1: `load_roster()` isn't wrapped in
try/except, so a Supabase failure there bypasses the structured card.
Claude's self-check: F1 is real but under-scoped — `get_supabase_client()`
(called one line earlier, at module top level) has the same exposure and
is the actual first failure point on missing Secrets. Proposed wrapping
both calls together.
Human decision: Confirmed via a status check ("do you need to update your
programs?") — audited all M1 entries against the live code, found this
was the only one still unapplied, and applied it.
Status: DECIDED
Rebase action: If the "Likely cause" field is kept, consider adding it as
an optional 7th field in URD §20.1 at next rebase, since it's now the
working implementation, not just a card the code renders.

### DEVLOG-M1-005 — Project creation left open to all 8 roster identities
Date: 2026-08-04
Type: DEPARTURE_FROM_BASELINE
Baseline ref: URD §7.1 ("Single primary operating user (PC) creates the
Project Code..."), §8.1 ("...entered by the initiating (PC) user"), §8.2
(role × phase matrix — only PC active for project creation in Phase 1),
§23 acceptance-criteria bullet 6 (PC1 → Phase 1 example). Note: SysSpec
§3.1 ("role selection from the eight-user roster") does not itself state
the PC-only restriction — an inconsistency between URD and SysSpec,
surfaced during M1 review, not introduced by this decision.
Claude did: Built the M1 "Who are you?" dropdown to allow any of the 8
roster identities (PC1, PC2, TR1, TR2, QA1, QA2, Lead1, Lead2) to create a
project, following DEVPLAN-P1's and SysSpec §3.1's unrestricted framing.
Flagged the URD/SysSpec inconsistency for a decision before finalizing.
DeepSeek said: Not raised — M1 review's traceability matrix marked the
8-user dropdown as fully §8.3-compliant without noting the §7.1/§8.1
restriction.
Human decision: "For the MVP keep the role-state relationship loose. We
do not know in reality how people are going to use the system." —
deliberate, disclosed decision not to restrict project creation to
PC1/PC2, for the MVP.
Status: DECIDED
Rebase action: At next rebase, either (a) relax URD §7.1/§8.1/§8.2 to
allow any roster identity to create a project, or (b) add an explicit
MVP-scope carve-out note in URD pointing at this entry. SysSpec §3.1
needs no change — it already reflects as-built behaviour.

### DEVLOG-M1-006 — Status display is a loose approximation of §12.1
Date: 2026-08-04
Type: OPEN_QUESTION
Baseline ref: URD §12.1 ("<stage> complete — <detail>" / "Next: <action>")
Claude did: Implemented a lightweight "SETUP" stamp + "ready for the next
step" caption rather than §12.1's literal format, since M1 has no real
pipeline stage to report yet.
Human decision: Not yet raised.
Status: DEFERRED — revisit once M2+ produces a real stage to report.
Rebase action: None yet.

### DEVLOG-M1-007 — This log itself
Date: 2026-08-04
Type: PROCESS_DECISION
Baseline ref: none — a process layered on top of the three baseline docs
Claude did: N/A (human-initiated).
Human decision: Established this append-only decision log as the record
of every future departure/decision/DeepSeek finding from M1 onward, to be
applied onto URD/SysSpec/DEVPLAN at a future rebase rather than editing
those three documents continuously. Claude, as implementer, maintains it.
Status: DECIDED
Rebase action: N/A — this document is an input to the rebase process, not
a target of it.

### DEVLOG-M1-008 — Regression introduced and caught while closing M1-004
Date: 2026-08-04
Type: PROCESS_DECISION
Baseline ref: none
Claude did: While applying the M1-004 fix, the first edit accidentally
deleted `load_roster()`'s definition, the page header block, and the
`M1-ROSTER-EMPTY` empty-roster check — all unrelated to the fix, lost as
collateral damage from restructuring the surrounding code. Caught via
`python3 -m py_compile` before delivery; corrected in a second edit that
restored all three, verified by re-viewing the full file and re-compiling.
DeepSeek said: N/A — not yet re-reviewed since this fix.
Human decision: N/A — disclosed proactively rather than raised.
Status: DECIDED
Rebase action: None. Logged for the same reason PQ1.1 logs its own
drafting errors (Finding F3) — an accurate record beats a clean-looking
one, and this file only carries evidentiary weight if it's a complete
account of what actually happened, mistakes included.

### DEVLOG-M1-009 — Smoke-test items 3/4 lose their code path after M1
Date: 2026-08-04
Type: OPEN_QUESTION
Baseline ref: SysSpec §5.1 (5-item smoke-test checklist, run every deploy)
Claude did: Noticed, while preparing the M1 deploy guide, that M0's
`streamlit_app.py` *was* items 3 (Storage round-trip) and 4 (Secrets-
backed LLM call) — M1 overwrites that file with the landing page, so
after this deploy there is no app code path left to exercise either
check. Neither SysSpec §5.1 nor DEVPLAN-P1 addresses what replaces that
scaffolding once M0's script is gone.
DeepSeek said: N/A — not raised in the M1 review.
Human decision: Not yet decided.
Status: OPEN
Rebase action: Once resolved, SysSpec §5.1 likely needs a note on how
items 3/4 are verified going forward (e.g. a small always-present
diagnostics page, direct console checks, or deferring those two items
until a milestone that naturally exercises them again).

### DEVLOG-M1-010 — DeepSeek Review 2 checked a stale snapshot
Date: 2026-08-04
Type: PROCESS_DECISION
Baseline ref: URD §19.5 / SysSpec §5.4 (DEVGOV-4 review gate)
Claude did: Self-checked DeepSeek's second M1 review against the live
files. It recommends applying the M1-BOOT-FAIL fix as still pending
(already applied), lists DEVLOG-M1-004 as OPEN (file reads DECIDED), and
its backfilled-entries table stops at M1-007 — no mention of M1-008 or
M1-009, both added before this review would have been requested. Its
description of DECISION_LOG.md's schema (field names, status vocabulary)
also doesn't match the actual file, suggesting it was reconstructed from
a description rather than read from the document itself.
DeepSeek said: (this entry is the self-check of DeepSeek's second review)
Human decision: Not yet decided.
Status: OPEN
Rebase action: None directly; process note for SysSpec §5.4 — a review
needs the literal current file contents, not a paraphrase of them, or
DEVGOV-4's gate doesn't actually cover what's being deployed.

### DEVLOG-M1-011 — Roster extended to a 9th identity (GenAI4P Trainer)
Date: 2026-08-04
Type: DEPARTURE_FROM_BASELINE
Baseline ref: URD §8.3 ("seed eight named users... PC1, PC2, TR1, TR2,
QA1, QA2, Lead1, Lead2")
Claude did: Added `TRAINER1` / "GenAI4P Trainer" / `role=PC` to
`roles_roster` so `dev_logs.deployed_by` (SysSpec §5.4) could reference a
real accountable identity for the M1 deploy, rather than reusing a
fictional PC1/PC2 persona or writing a non-roster string into
`deployed_by`. The specific `user_id`/`role` values were Claude's
proposal — the human specified only the display name.
DeepSeek said: N/A — not reviewed.
Human decision: Requested recording "GenAI4P Trainer" as the deploying
identity for the M1 dev_logs entry.
Status: DECIDED (values as proposed — flag if `TRAINER1`/`role=PC` should
be corrected)
Rebase action: At next rebase, URD §8.3 needs either a 9th roster row
made explicit, or a note that MVP dev/deploy accountability may extend
the fixed eight-persona translation roster.

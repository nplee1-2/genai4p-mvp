"""
GenAI4P MVP — Standardized error surfacing.

One shared module so every milestone (M1..M11) reports failures the same
way: WHAT happened, WHERE, and WHY (when knowable) — structured, plain
text, and one click from being pasted into an AI chat for debugging
(DEVPLAN §5.3 / DBG-1: "a structured error card ... not a raw traceback").

Reserved for real system faults (failed DB calls, missing data the app
depends on, unexpected exceptions) — NOT for ordinary input validation
like a blank field. Those stay as plain, friendly st.warning() copy in
the calling page; see M1's streamlit_app.py for that split.

Error ID convention: "{MILESTONE}-{SHORT_COMPONENT}-{FAIL_TYPE}"
e.g. "M1-INSERT-FAIL", "M3-SEAL-MISMATCH". IDs are chosen deliberately at
each call site (not auto-generated) so they stay stable and referenceable
— the same convention this project already uses for QA issues (QV1-001).

Usage:
    from error_handling import AppError, render_error

    try:
        ...
    except Exception as e:
        render_error(AppError(
            error_id="M1-INSERT-FAIL",
            component="projects insert (Supabase)",
            severity="MAJOR",              # CRITICAL / MAJOR / MINOR
            expected="A new row is created in projects.",
            suggested="Check Supabase connectivity/Secrets and retry.",
            exc=e,                          # pass the caught exception directly
            context={"project_code": code, "identity": identity},
        ))
        st.stop()

Assumes Streamlit >= 1.31 (st.dialog with a `width` argument) — safe for
a mid-2026 deploy. If your deployed version is older, drop `width="large"`
below and st.dialog still works.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import streamlit as st


# Best-effort "why", from common error signatures across Supabase/PostgREST
# and general network failures. Not authoritative — the point is to save
# the person (or the AI they paste this to) a first guess, not to replace it.
_CAUSE_HINTS = [
    (("duplicate key", "23505", "already exists"), "A row with this key already exists."),
    (
        ("jwt", "401", "403", "unauthorized", "invalid api key"),
        "Authentication/authorization failed — check the relevant Secret in Streamlit Cloud.",
    ),
    (
        ("timeout", "connection", "could not connect", "network"),
        "Could not reach the service — check connectivity or that the service is up.",
    ),
    (("not found", "404"), "The requested resource does not exist — check the identifier used."),
]


def guess_cause(exc: Exception) -> str:
    text = str(exc).lower()
    for needles, cause in _CAUSE_HINTS:
        if any(n in text for n in needles):
            return cause
    return "Not automatically determined — see Observed detail below."


@dataclass
class AppError:
    error_id: str
    component: str                        # WHERE: function / table / API call
    severity: str                         # CRITICAL / MAJOR / MINOR
    expected: str                         # what should have happened
    suggested: str                        # next step for a human or AI to try
    exc: Optional[Exception] = None       # the caught exception, if any
    observed: Optional[str] = None        # supply directly if there's no exception
    context: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.observed is None:
            self.observed = f"{type(self.exc).__name__}: {self.exc}" if self.exc else "Unspecified."

    @property
    def likely_cause(self) -> str:
        return guess_cause(self.exc) if self.exc else "N/A — no exception was raised."

    def as_text(self) -> str:
        lines = [
            f"Error ID: {self.error_id}",
            f"Component (where): {self.component}",
            f"Severity: {self.severity}",
            f"Observed (what): {self.observed}",
            f"Likely cause (why): {self.likely_cause}",
            f"Expected: {self.expected}",
            f"Suggested next step: {self.suggested}",
            f"Timestamp (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        ]
        if self.context:
            lines.append("Context:")
            for k, v in self.context.items():
                lines.append(f"  {k}: {v}")
        return "\n".join(lines)


def render_error(error: AppError):
    """Pops up a modal with the structured error as one plain-text block.
    st.code()'s built-in copy icon *is* the cut-and-paste path into an AI
    chat — no manual selecting required."""
    st.session_state["_last_app_error"] = error
    _error_dialog()


@st.dialog("Something needs attention", width="large")
def _error_dialog():
    error: AppError = st.session_state.get("_last_app_error")
    if error is None:
        return
    st.markdown(f"**{error.severity} · `{error.error_id}`**")
    st.caption("Copy this block and paste it into your AI chat to help debug.")
    st.code(error.as_text(), language=None)

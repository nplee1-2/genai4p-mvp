"""
GenAI4P Language-Agnostic MVP — Milestone M1
Landing page: Project Code entry + roster role selection.

Implements: URD §8.1, §8.3 | Type: Code (no LLM call, per §10 split)
Exit check: a new row appears in `projects`; identity is recorded in `created_by`.

Replaces the M0 smoke-test script. Assumes:
  - `supabase` (supabase-py) is already in requirements.txt (used by M0's
    Storage round-trip check).
  - SUPABASE_URL / SUPABASE_SECRET_KEY are already set in Streamlit Cloud
    Secrets (per HANDOVER v1.1 §3) — never read from anywhere else.
  - Streamlit >= 1.27 (for st.rerun()) — safe for a mid-2026 deploy.

Job-scope note: this file only ever writes to `projects`. It does not touch
`dev_logs` (build/deploy governance — M1..M11, roster acting as developers)
or `governance_logs` (the P1.1a..P8.2 translation pipeline — roster acting
as pipeline operators). Keeping those two scopes apart is deliberate, not
an oversight — see DEVPLAN §2.2 and HANDOVER's own governance discipline.

Identity recording: the dropdown is populated FROM roles_roster, so any
value it produces is valid by construction — no separate lookup/validation
join is performed (or needed) at insert time.

Visual identity: colors and type roles are drawn from the project's own
P5.1a SF3 Formatter spec (title_color #1A3A5C, sec_color #2E4057) rather
than a generic palette, so the web app and the Word deliverables translators
already receive read as one coherent system.
"""

import streamlit as st
from supabase import create_client, Client

from error_handling import AppError, render_error

st.set_page_config(page_title="GenAI4P — New Project", page_icon="🖋️", layout="centered")

# ── Design tokens (matched to P5.1a's FONT / COLORS spec) ─────────────────
INK = "#1A3A5C"          # = P5.1a FONT.title_color
SLATE = "#2E4057"        # = P5.1a FONT.sec_color
LABEL = "#444444"        # = P5.1a FONT.label_color
PAPER = "#FBFBFA"
CARD_BG = "#FFFFFF"
HEADER_TINT = "#D5E8F0"  # = P5.1a COLORS.header
BORDER = "#E2E5E9"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {{
        font-family: 'IBM Plex Sans', sans-serif;
        background-color: {PAPER};
        color: {LABEL};
    }}
    h1, h2, h3, .app-title {{
        font-family: 'Fraunces', serif;
        color: {INK};
        font-weight: 600;
    }}
    .app-title {{
        font-size: 2.1rem;
        margin-bottom: 0.1rem;
    }}
    .app-subtitle {{
        color: {SLATE};
        font-size: 0.95rem;
        margin-bottom: 1.6rem;
        border-bottom: 1px solid {BORDER};
        padding-bottom: 1rem;
    }}
    [data-testid="stForm"] {{
        background-color: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 1.75rem 1.75rem 1rem 1.75rem;
    }}
    .stButton > button, [data-testid="stFormSubmitButton"] > button {{
        background-color: {INK};
        color: white;
        border-radius: 6px;
        border: none;
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 500;
        padding: 0.5rem 1.4rem;
    }}
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {{
        background-color: {SLATE};
        color: white;
    }}
    .ledger-stamp {{
        display: inline-block;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        letter-spacing: 0.04em;
        color: {INK};
        background-color: {HEADER_TINT};
        border: 1px solid {INK};
        border-radius: 4px;
        padding: 0.15rem 0.6rem;
        margin-right: 0.5rem;
    }}
    .project-code {{
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Supabase client ──────────────────────────────────────────────────────
@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SECRET_KEY"])


@st.cache_data(ttl=300)
def load_roster():
    resp = supabase.table("roles_roster").select("user_id, display_name, role").execute()
    return resp.data or []


# ── Header ─────────────────────────────────────────────────────────────
st.markdown('<div class="app-title">New project</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Give your project a code and tell us who you are '
    '— that\'s all it takes to start.</div>',
    unsafe_allow_html=True,
)

# Client init + roster load share one boot-time guard (DEVLOG-M1-004): a
# missing/invalid Secret fails inside get_supabase_client(), before
# load_roster() ever runs, so both must be covered by the same try/except.
try:
    supabase = get_supabase_client()
    roster = load_roster()
except Exception as e:
    render_error(AppError(
        error_id="M1-BOOT-FAIL",
        component="Supabase client init / roster load",
        severity="CRITICAL",
        expected="Client connects and roster loads.",
        suggested="Check SUPABASE_URL and SUPABASE_SECRET_KEY are both present and correct in Streamlit Secrets.",
        exc=e,
    ))
    st.stop()

if not roster:
    render_error(AppError(
        error_id="M1-ROSTER-EMPTY",
        component="roles_roster load (Supabase)",
        severity="CRITICAL",
        observed="roles_roster query returned zero rows.",
        expected="8 seeded roster rows (PC1, PC2, TR1, TR2, QA1, QA2, Lead1, Lead2).",
        suggested="Confirm roles_roster is seeded and Secrets point at the correct Supabase project.",
    ))
    st.stop()

# Label shown in dropdown -> stored identity value (user_id, e.g. "PC1").
# Sourced directly from roles_roster, so no separate validation is needed.
roster_labels = {
    f"{r['display_name']} — {r['role']} ({r['user_id']})": r["user_id"] for r in roster
}

with st.form("new_project_form", clear_on_submit=False):
    identity_label = st.selectbox("Who are you?", options=list(roster_labels.keys()))
    st.caption("Your role is recorded against this project for governance.")

    project_code = st.text_input("Project code", placeholder="e.g. BM-EN-2026-08")
    st.caption("Pick something memorable — you'll use this code every time you come back.")

    submitted = st.form_submit_button("Create project")

if submitted:
    identity = roster_labels[identity_label]
    code = project_code.strip()

    if not code:
        st.warning("Give the project a code before continuing.")
        st.stop()

    # project_code is the primary key — check uniqueness before insert
    existing = supabase.table("projects").select("project_code").eq("project_code", code).execute()
    if existing.data:
        st.warning(f"'{code}' is already in use. Try a different code.")
        st.stop()

    try:
        supabase.table("projects").insert(
            {
                "project_code": code,
                "created_by": identity,
                # source_lang, target_lang, script_metadata: set in M2
                # phase_status: left to its DB default ('Setup')
            }
        ).execute()
    except Exception as e:
        render_error(AppError(
            error_id="M1-INSERT-FAIL",
            component="projects insert (Supabase)",
            severity="MAJOR",
            expected="A new row is created in projects.",
            suggested="Check Supabase connectivity/Secrets and retry. If it persists, paste this card into the AI chat per DEVPLAN §5.3.",
            exc=e,
            context={"project_code": code, "identity": identity},
        ))
        st.stop()

    st.session_state["active_project_code"] = code
    st.session_state["active_identity"] = identity
    st.rerun()

if st.session_state.get("active_project_code"):
    st.markdown(
        f"""
        <div style="margin-top:1.5rem;">
            <span class="ledger-stamp">SETUP</span>
            <span class="project-code">{st.session_state['active_project_code']}</span>
            <div style="color:{LABEL}; font-size:0.85rem; margin-top:0.4rem;">
                Created by {st.session_state['active_identity']} — ready for the next step.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

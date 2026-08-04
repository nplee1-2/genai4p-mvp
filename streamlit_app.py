import streamlit as st
from supabase import create_client
import anthropic
import hashlib

st.title("Environment verification")

sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SECRET_KEY"])

# 1. Supabase connectivity
result = sb.table("roles_roster").select("*").execute()
st.write("Roster rows found:", len(result.data))

# 2. LLM connectivity
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
msg = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=20,
    messages=[{"role": "user", "content": "Reply with OK"}],
)
st.write("LLM response:", msg.content[0].text)

st.divider()
st.subheader("Smoke test 2 — create a test project row")

roster = [row["user_id"] for row in result.data]
identity = st.selectbox("Acting as", roster)
project_code = st.text_input("Project code", value="TEST-001")

if st.button("Create test project"):
    sb.table("projects").upsert({
        "project_code": project_code,
        "created_by": identity,
    }).execute()
    st.success(f"Row created/updated for {project_code}, created_by={identity}")

if st.button("Show all projects"):
    rows = sb.table("projects").select("*").execute()
    st.write(rows.data)

st.divider()
st.subheader("Smoke test 3 — file upload/download round-trip")

uploaded = st.file_uploader("Upload a test file")
if uploaded is not None:
    file_bytes = uploaded.read()
    sha_before = hashlib.sha256(file_bytes).hexdigest()

    sb.storage.from_("files").upload(
        path=f"test/{uploaded.name}",
        file=file_bytes,
        file_options={"upsert": "true"},
    )
    st.success("Uploaded to Supabase Storage.")

    downloaded = sb.storage.from_("files").download(f"test/{uploaded.name}")
    sha_after = hashlib.sha256(downloaded).hexdigest()

    if sha_before == sha_after:
        st.success(f"Round-trip verified — hashes match ({sha_before[:12]}...)")
    else:
        st.error("Hash mismatch — file changed during round-trip!")

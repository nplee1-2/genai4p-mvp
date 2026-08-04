import streamlit as st
from supabase import create_client
import anthropic

st.title("Environment verification")

# 1. Supabase connectivity
sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SECRET_KEY"])
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

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 🔐 SECURITY ---
ADMIN_USER = "admin"
ADMIN_PASS = "karanos2026"

st.set_page_config(page_title="KaranOS // Bio-Monitor", layout="wide", page_icon="🩺")

# --- 🎨 THEME ---
TEAL, BG = "#218b82", "#f8f9fa"
st.markdown(f"<style>.stApp {{ background-color: {BG}; }} </style>", unsafe_allow_html=True)

# --- 🛡️ LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def check_login():
    if st.session_state.username == ADMIN_USER and st.session_state.password == ADMIN_PASS:
        st.session_state.logged_in = True
    else:
        st.error("⛔ ACCESS DENIED")

if not st.session_state.logged_in:
    with st.form("login"):
        st.markdown(f"<h1 style='color:{TEAL}'>KaranOS Locked</h1>", unsafe_allow_html=True)
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.form_submit_button("Authenticate", on_click=check_login)
    st.stop()

# --- 🧠 PARSER (CLOUD ONLY) ---
SYNC_FILE = "KaranOS_Full_Sync.txt"

@st.cache_data
def load_data():
    data = []
    # DIRECTLY READ THE FILE IN THE REPO
    if os.path.exists(SYNC_FILE):
        st.sidebar.success(f"✅ FOUND: {SYNC_FILE}")
        with open(SYNC_FILE, "r", encoding="utf-8", errors="ignore") as f:
            full_text = f.read()
            # Split by the separator
            sections = full_text.split("--- FILE: ")
            for section in sections[1:]:
                try:
                    lines = section.split("\n", 1)
                    filename = lines[0].strip()
                    content = lines[1] if len(lines) > 1 else ""
                    
                    # SIMPLE METRICS
                    arousal = (len(content)/1000) + (content.count("!") * 2)
                    stability = (content.lower().count("plan") + content.lower().count("sleep")) * 5
                    
                    if "child" in content.lower(): topic = "Nurture"
                    elif "code" in content.lower(): topic = "Logic"
                    else: topic = "Self"

                    data.append({"Filename": filename, "Arousal": arousal, "Stability": stability, "Topic": topic})
                except: pass
    else:
        st.error(f"❌ MISSING: Could not find {SYNC_FILE} in the repository root.")
    
    return pd.DataFrame(data)

# --- 📊 DASHBOARD ---
st.title("KaranOS // Clinical Context")
df = load_data()

if not df.empty:
    c1, c2 = st.columns(2)
    c1.metric("Avg Arousal", f"{df['Arousal'].mean():.1f}")
    c2.metric("Avg Stability", f"{df['Stability'].mean():.1f}")
    
    fig = px.scatter(df, x="Stability", y="Arousal", color="Topic", hover_name="Filename", title="Cognitive State Matrix")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
else:
    st.warning("⚠️ File found but no valid entries detected. Check the separator format.")

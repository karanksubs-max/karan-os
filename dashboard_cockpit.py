import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
import datetime

# --- 🔐 SECURITY CONFIGURATION ---
ADMIN_USER = "admin"
ADMIN_PASS = "karanos2026"  # CHANGE THIS IF YOU WANT

# --- 🏥 KARAN OS: CLINICAL EDITION ---
st.set_page_config(page_title="KaranOS // Bio-Monitor", layout="wide", page_icon="🩺")

# --- 🎨 THEME: SCIENTIFIC MINIMALISM (Hey Brewty) ---
TEAL, PINK, MINT, BG, TEXT = "#218b82", "#eb96aa", "#99d3bb", "#f8f9fa", "#0e3833"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap');
    .stApp {{ background-color: {BG}; color: {TEXT}; font-family: 'Roboto', sans-serif; }}
    section[data-testid="stSidebar"] {{ background-color: #0e3833; }}
    section[data-testid="stSidebar"] * {{ color: #e9dade !important; }}
    .bio-card {{ background: white; padding: 20px; border-radius: 12px; border: 1px solid #e0e0e0; text-align: left; margin-bottom: 10px; }}
    .stTooltipIcon {{ color: {TEAL}; }}
    </style>
""", unsafe_allow_html=True)

# --- 🛡️ SECURITY SYSTEM ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'login_logs' not in st.session_state: st.session_state.login_logs = []

def log_attempt(status, user):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.login_logs.append(f"[{ts}] {user}: {status}")

def check_login():
    user = st.session_state.username
    pwd = st.session_state.password
    if user == ADMIN_USER and pwd == ADMIN_PASS:
        st.session_state.logged_in = True
        log_attempt("SUCCESS", user)
    else:
        st.error("⛔ ACCESS DENIED")
        log_attempt("FAILED", user)

# --- 🔒 LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown(f"<h1 style='text-align:center; color:{TEAL}'>KaranOS Locked</h1>", unsafe_allow_html=True)
        with st.form("login"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Authenticate", on_click=check_login)
    
    # SHOW LOGS ON LOGIN SCREEN TOO
    with st.sidebar:
        st.markdown("### 🛡️ SECURITY LOGS")
        for log in reversed(st.session_state.login_logs):
            color = "#ff4b4b" if "FAILED" in log else "#00c853"
            st.markdown(f"<span style='color:{color}; font-size:12px;'>{log}</span>", unsafe_allow_html=True)
    st.stop() # STOP RENDERING THE REST

# --- 🔓 MAIN DASHBOARD STARTS HERE ---

# --- 🧠 NEURAL PARSER ---
st.sidebar.markdown("### 🩺 BIO-MONITOR")

# CLOUD COMPATIBILITY: Look in current folder first (.)
default_path = "." if os.path.exists("Foxconn Anhalire Property Investment Multiplier .md") else os.path.expanduser("~/Documents/trials")
vault_path = st.sidebar.text_input("Source Path:", value=default_path)

# SHOW LOGS IN SIDEBAR
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🛡️ ACCESS LOGS")
    for log in reversed(st.session_state.login_logs):
        color = "#ff4b4b" if "FAILED" in log else "#00c853"
        st.markdown(f"<span style='color:{color}; font-size:12px;'>{log}</span>", unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

@st.cache_data
def scan_biometrics(path):
    data = []
    if not os.path.exists(path): return pd.DataFrame()
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith((".md", ".txt")):
                try:
                    fp = os.path.join(root, file)
                    with open(fp, 'r', errors='ignore') as f: text = f.read(); lower = text.lower()
                    
                    # BIOMETRICS
                    arousal = (len(text)/1000) + ((lower.count("!") + lower.count("fast")) * 2)
                    stability = (lower.count("sleep") + lower.count("plan") + lower.count("meds")) * 5
                    synth = lower.count("because") + lower.count("connect")
                    
                    if "invest" in lower: topic = "Survival (Wealth)"
                    elif "child" in lower: topic = "Nurture (Edu)"
                    elif "code" in lower: topic = "Logic (System)"
                    else: topic = "Self (Monitor)"
                    
                    data.append({"Filename":file, "Arousal":round(arousal,1), "Stability":stability, "Synthesis":synth, "Topic":topic, "Snippet":text[:100]})
                except: pass
    return pd.DataFrame(data)

# --- RENDER DASHBOARD ---
if os.path.exists(vault_path):
    df = scan_biometrics(vault_path)
    if not df.empty:
        avg_arousal = df['Arousal'].mean()
        avg_stability = df['Stability'].mean()
        
        if avg_arousal > 20 and avg_stability < 5: status, s_col, adv = "High Beta (Risk)", "#fce8e6", "Stop coding. Sleep."
        elif avg_stability > 10: status, s_col, adv = "Grounded Flow", "#e6f4ea", "Maintain velocity."
        else: status, s_col, adv = "Nominal", "#f1f3f4", "Engage creative play."

        st.title("KaranOS // Clinical Context")
        st.markdown(f"**Bio-State:** <span style='background-color:{s_col}; padding:4px;'>{status}</span>", unsafe_allow_html=True)
        st.caption(adv)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AROUSAL (Gas)", f"{avg_arousal:.1f}", help="Speed of thought.")
        c2.metric("STABILITY (Brake)", f"{avg_stability:.1f}", help="Grounding.")
        c3.metric("SYNTHESIS", f"{int(df['Synthesis'].sum())}", help="Creativity.")
        c4.metric("FOCUS", df['Topic'].mode()[0])

        tab1, tab2 = st.tabs(["Safety Matrix", "Logs"])
        with tab1:
            fig = px.scatter(df, x="Stability", y="Arousal", size="Synthesis", color="Topic", hover_name="Filename", title="Arousal vs Stability", color_discrete_map={"Survival (Wealth)":TEAL, "Nurture (Edu)":PINK, "Logic (System)":"#4d6b6b"})
            fig.add_shape(type="rect", x0=0, y0=50, x1=5, y1=200, line=dict(color="Red", dash="dot"))
            st.plotly_chart(fig, use_container_width=True)
        with tab2: st.dataframe(df)
    else: st.warning("No data found.")
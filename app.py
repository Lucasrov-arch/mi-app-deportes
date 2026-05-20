import streamlit as st
import sqlite3
import datetime
from urllib.parse import quote

# 1. APP CONFIG & STYLING
st.set_page_config(page_title="SquadUp", page_icon="⚽", layout="centered")

# Custom CSS for "Argentine Stadium" vibe
st.markdown("""
    <style>
    .main { background-color: #f0f4f0; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #1b5e20; color: white; font-weight: bold; border: 2px solid #2e7d32;
    }
    .event-card {
        background-color: white; padding: 25px; border-radius: 20px;
        border-bottom: 8px solid #1b5e20; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    .sport-tag {
        background-color: #2e7d32; color: white;
        padding: 5px 15px; border-radius: 5px; font-size: 0.8em; text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE (Added WhatsApp Column)
def get_db():
    conn = sqlite3.connect("squadup_v2.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT, title TEXT, sport TEXT, description TEXT, 
            location TEXT, date TEXT, time TEXT, 
            slots_needed INTEGER, fb_link TEXT, phone TEXT
        )
    """)
    conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# 3. INTERFACE
st.title("🏟️ SquadUp")
st.markdown("##### *The stadium is waiting for you.*")

tab_find, tab_create = st.tabs(["🔎 FIND SQUADS", "📣 POST A GAME"])

with tab_create:
    st.info("Fill the form to start the 'Recibimiento'!")
    title = st.text_input("Match Name", placeholder="e.g. Friday Night 5v5")
    
    col1, col2 = st.columns(2)
    with col1:
        sport = st.selectbox("Sport", ["Football", "Padel", "Basketball", "Tennis", "Other"])
        date_ev = st.date_input("Match Day", min_value=datetime.date.today())
        phone = st.text_input("WhatsApp Number", placeholder="e.g. 54911...", help="Include country code")
    with col2:
        slots = st.number_input("Players missing", 1, 22)
        time_ev = st.time_input("Kick-off time")
        loc = st.text_input("📍 Stadium / Pitch Location")

    desc = st.text_area("Extra details (Jersey color, level, etc.)")
    fb = st.text_input("🔗 Link to Facebook Event (Optional)")

    if st.button("🚀 ENTER THE PITCH (Publish)"):
        if title and loc and phone:
            cursor.execute("INSERT INTO events (type, title, sport, description, location, date, time, slots_needed, fb_link,

import streamlit as st
import sqlite3
import datetime
from urllib.parse import quote

# 1. APP CONFIG (SQUADUP)
st.set_page_config(page_title="SquadUp", page_icon="🏀", layout="centered")

# Visual Styling (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3em;
        background-color: #2e7d32; color: white; font-weight: bold; border: none;
    }
    .event-card {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 5px solid #2e7d32; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px; color: #333;
    }
    .sport-tag {
        background-color: #e8f5e9; color: #2e7d32;
        padding: 5px 15px; border-radius: 20px; font-size: 0.85em; font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE ENGINE
def get_db():
    conn = sqlite3.connect("squadup.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT, title TEXT, sport TEXT, description TEXT, 
            location TEXT, date TEXT, time TEXT, 
            slots_needed INTEGER, fb_link TEXT
        )
    """)
    conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# 3. APP INTERFACE
st.title("🏀 SquadUp")
st.markdown("##### *Stop warming the bench. Find your squad.*")

tab_find, tab_create = st.tabs(["🔍 Find Games", "➕ Post a Game"])

with tab_create:
    with st.expander("✨ Create New Activity", expanded=True):
        cat = st.segmented_control("Category:", ["Sports", "General"], default="Sports")
        
        title = st.text_input("Event Title", placeholder="e.g. 5-a-side Football at Downtown")
        
        col1, col2 = st.columns(2)
        with col1:
            sport = st.selectbox("Sport", ["Football", "Padel", "Basketball", "Tennis", "Other"]) if cat == "Sports" else "General"
            date_ev = st.date_input("Date", min_value=datetime.date.today())
        with col2:
            slots = st.number_input("Players Needed", 1, 20) if cat == "Sports" else 0
            time_ev = st.time_input("Time")
            
        loc = st.text_input("📍 Location (Address or Maps link)")
        desc = st.text_area("Description / Rules")
        fb = st.text_input("🔗 Facebook Event Link (Optional)")
        
        if st.button("🚀 PUBLISH GAME"):
            if title and loc:
                cursor.execute("INSERT INTO events (type, title, sport, description, location, date, time, slots_needed, fb_link) VALUES (?,?,?,?,?,?,?,?,?)", 
                               (cat, title, sport, desc, loc, str(date_ev), str(time_ev), slots, fb))
                conn.commit()
                st.balloons()
                st.success("Game live! Check the 'Find Games' tab.")
            else:
                st.warning("Please fill in the Title and Location.")

with tab_find:
    st.write("### Available Squads")
    
    # Filter
    f_sport = st.multiselect("Filter by Sport:", ["Football", "Padel", "Basketball", "Tennis", "Other"])
    
    query = "SELECT * FROM events WHERE slots_needed > 0"
    if f_sport:
        query += f" AND sport IN ({','.join(['?']*len(f_sport))})"
        cursor.execute(query, f_sport)
    else:
        cursor.execute(query)
    
    rows = cursor.fetchall()
    
    if not rows:
        st.info("No games found. Why not create one?")
    
    for row in rows:
        with st.container():
            st.markdown(f"""
                <div class="event-card">
                    <span class="sport-tag">{row[3]}</span>
                    <h3 style='margin-bottom:5px;'>{row[2]}</h3>
                    <p style='margin:0;'>📅 {row[6]} at {row[7]}</p>
                    <p style='margin:0;'>📍 {row[5]}</p>
                    <p style='color: #666; font-size: 0.9em; margin-top:10px;'>{row[4]}</p>
                    <hr style='margin:10px 0;'>
                    <p style='font-size:1.1em;'><b>🔥 {row[8]} slots left!</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button(f"✅ Join Game", key=f"join_{row[0]}"):
                    new_slots = row[8] - 1
                    cursor.execute("UPDATE events SET slots_needed = ? WHERE id = ?", (new_slots, row[0]))
                    conn.commit()
                    st.rerun()
            with c2:
                cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(row[2])}&details={quote(row[4])}&location={quote(row[5])}"
                st.link_button("📅 Calendar", cal_url)
            with c3:
                if row[9]: st.link_button("🔵 Facebook", row[9])

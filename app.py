import streamlit as st
import sqlite3
import datetime
from urllib.parse import quote
import time

# 1. APP CONFIG
st.set_page_config(page_title="SquadUp", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    header[data-testid="stHeader"] { background-color: #74ACDF !important; }
    .event-card {
        background-color: #1e1e1e; padding: 25px; border-radius: 18px;
        border-left: 10px solid #74ACDF; margin-bottom: 25px;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3em;
        background-color: #74ACDF; color: white; font-weight: bold;
    }
    .mail-btn {
        display: inline-block; padding: 10px 20px; border-radius: 8px;
        text-decoration: none; font-weight: bold; margin: 5px; color: white !important;
    }
    .gmail { background-color: #DB4437; }
    .outlook { background-color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE
def get_db():
    conn = sqlite3.connect("squadup_v7.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT, sport TEXT, description TEXT, 
            location TEXT, date TEXT, time TEXT, 
            slots_needed INTEGER, fb_link TEXT, creator_email TEXT
        )
    """)
    conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# 3. UI
st.title("🏟️ SquadUp")
selected_tab = st.radio("", ["🔍 BROWSE GAMES", "📣 HOST A MATCH"], horizontal=True, label_visibility="collapsed")

if selected_tab == "📣 HOST A MATCH":
    st.write("### Host a Match")
    title = st.text_input("Match Title")
    col1, col2 = st.columns(2)
    with col1:
        sport = st.selectbox("Sport", ["Football", "Padel", "Basketball", "Tennis", "Other"])
        date_ev = st.date_input("Date", min_value=datetime.date.today())
        email = st.text_input("Your Email (Private)")
    with col2:
        slots = st.number_input("Slots Needed", 1, 22)
        time_ev = st.time_input("Time")
        loc = st.text_input("📍 Location")
    
    if st.button("🚀 PUBLISH MATCH"):
        if title and loc and email:
            cursor.execute("INSERT INTO events (title, sport, description, location, date, time, slots_needed, fb_link, creator_email) VALUES (?,?,?,?,?,?,?,?,?)", 
                           (title, sport, "", loc, str(date_ev), str(time_ev), slots, "", email))
            conn.commit()
            st.balloons()
            st.success("Match Published!")
            time.sleep(1)
            st.info("Go to 'Browse' to check it.")

else:
    cursor.execute("SELECT * FROM events WHERE slots_needed > 0 ORDER BY date ASC")
    for row in cursor.fetchall():
        with st.container():
            st.markdown(f"""
                <div class="event-card">
                    <h2 style='color:white;'>{row[1]}</h2>
                    <p>📅 {row[5]} | ⏰ {row[6]} | 📍 {row[4]}</p>
                    <h3 style='color:#74ACDF;'>🔥 {row[7]} slots left</h3>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("🙌 JOIN THIS SQUAD"):
                u_name = st.text_input("Name", key=f"n_{row[0]}")
                u_email = st.text_input("Your Email", key=f"e_{row[0]}")
                
                if st.button("CONFIRM JOIN", key=f"c_{row[0]}"):
                    if u_name and u_email:
                        # Update DB
                        cursor.execute("UPDATE events SET slots_needed = ? WHERE id = ?", (row[7]-1, row[0]))
                        conn.commit()
                        
                        # Prepare Mail Data
                        subject = quote(f"SquadUp: {u_name} joined your match!")
                        body = quote(f"Hi! {u_name} ({u_email}) joined your match: {row[1]}. See you there!")
                        
                        # Links directos a Webmails
                        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={row[9]}&su={subject}&body={body}"
                        outlook_url = f"https://outlook.office.com/mail/deeplink/compose?to={row[9]}&subject={subject}&body={body}"
                        
                        st.success(f"Excellent {u_name}! Now, notify the host using your favorite service:")
                        
                        # Botones visuales
                        st.markdown(f"""
                            <div style='text-align: center; margin-top: 10px;'>
                                <a href='{gmail_url}' target='_blank' class='mail-btn gmail'>Open Gmail</a>
                                <a href='{outlook_url}' target='_blank' class='mail-btn outlook'>Open Outlook Web</a>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.divider()
                        st.link_button("📅 Add to Calendar", f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(row[1])}")
                    else:
                        st.error("Please fill your name and email.")

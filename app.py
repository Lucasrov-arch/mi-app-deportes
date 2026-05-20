import streamlit as st
import sqlite3
import datetime
from urllib.parse import quote

# 1. APP CONFIG & stadium style
st.set_page_config(page_title="SquadUp", page_icon="⚽", layout="centered")

# Custom CSS for Argentine Vibes (Celeste y Blanco)
st.markdown("""
    <style>
    .stApp {
        border-top: 15px solid #74ACDF;
        background-color: #ffffff;
    }
    .main { background-color: #f9f9f9; }
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3.5em;
        background-color: #74ACDF; color: white; font-weight: bold; border: none;
    }
    .event-card {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 8px solid #74ACDF; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .sport-tag {
        background-color: #f0f0f0; color: #74ACDF;
        padding: 4px 10px; border-radius: 5px; font-size: 0.8em; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE ENGINE
def get_db():
    conn = sqlite3.connect("squadup_v3.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, title TEXT, sport TEXT, description TEXT, location TEXT, date TEXT, time TEXT, slots_needed INTEGER, fb_link TEXT, phone TEXT)")
    conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# 3. INTERFACE
st.title("🏟️ SquadUp")
st.markdown("### *¡El que no salta, no tiene equipo!*")

tab_find, tab_create = st.tabs(["🔍 FIND SQUADS", "📣 POST A GAME"])

with tab_create:
    st.write("#### Register your match")
    title = st.text_input("Match Title", placeholder="Ej: Futbol 5 en predio central")
    
    col1, col2 = st.columns(2)
    with col1:
        sport = st.selectbox("Sport", ["Football", "Padel", "Basketball", "Tennis", "Other"])
        date_ev = st.date_input("Day", min_value=datetime.date.today())
        phone = st.text_input("WhatsApp (International format)", placeholder="e.g. 54911654321")
    with col2:
        slots = st.number_input("Players needed", 1, 22)
        time_ev = st.time_input("Time")
        loc = st.text_input("📍 Location/Address")

    desc = st.text_area("Extra details")
    fb = st.text_input("Facebook link (Optional)")

    if st.button("🚀 PUBLISH AND ENTER THE PITCH"):
        if title and loc and phone:
            # Línea de inserción corregida para evitar el SyntaxError
            cursor.execute("INSERT INTO events (type, title, sport, description, location, date, time, slots_needed, fb_link, phone) VALUES (?,?,?,?,?,?,?,?,?,?)", ("Sports", title, sport, desc, loc, str(date_ev), str(time_ev), slots, fb, phone))
            conn.commit()
            st.snow() # El efecto de papelitos/nieve
            st.success("MATCH PUBLISHED!")
        else:
            st.error("Missing info! Please fill Title, Location and WhatsApp.")

with tab_find:
    cursor.execute("SELECT * FROM events WHERE slots_needed > 0 ORDER BY date ASC")
    rows = cursor.fetchall()
    
    if not rows:
        st.info("No squads found. Start one above!")
    
    for row in rows:
        with st.container():
            st.markdown(f"""
                <div class="event-card">
                    <span class="sport-tag">{row[3]}</span>
                    <h2 style='color:#333;'>{row[2]}</h2>
                    <p style='margin:0;'>📅 {row[6]} | ⏰ {row[7]}</p>
                    <p style='margin:0;'>📍 {row[5]}</p>
                    <p style='color:#666;'>{row[4]}</p>
                    <h3 style='color:#74ACDF;'>🔥 {row[8]} slots left</h3>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"🙌 JOIN MATCH", key=f"btn_{row[0]}"):
                    new_val = row[8] - 1
                    cursor.execute("UPDATE events SET slots_needed = ? WHERE id = ?", (new_val, row[0]))
                    conn.commit()
                    wa_url = f"https://wa.me/{row[10]}?text=Hi! I want to join: {row[2]}"
                    st.markdown(f'<meta http-equiv="refresh" content="0;URL={wa_url}">', unsafe_allow_html=True)
                    st.rerun()
            with c2:
                cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(row[2])}&location={quote(row[5])}"
                st.link_button("📅 CALENDAR", cal_url)

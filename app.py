import streamlit as st
import sqlite3
import datetime
from urllib.parse import quote
import time

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL (DARK MODE)
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
    .user-profile {
        padding: 10px; background-color: #262626; border-radius: 10px; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE BASE DE DATOS (Usuarios + Eventos)
def get_db():
    conn = sqlite3.connect("squadup_v8.db")
    cursor = conn.cursor()
    # Tabla de Usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY, name TEXT, last_name TEXT, password TEXT
        )
    """)
    # Tabla de Eventos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT, sport TEXT, location TEXT, date TEXT, time TEXT, 
            slots_needed INTEGER, creator_email TEXT
        )
    """)
    conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# 3. GESTIÓN DE SESIÓN (LOGIN)
if 'user' not in st.session_state:
    st.session_state.user = None

with st.sidebar:
    st.title("👤 Player Profile")
    if st.session_state.user is None:
        mode = st.radio("Choose Mode", ["Login", "Sign Up"])
        email_input = st.text_input("Email")
        pass_input = st.text_input("Password", type="password")
        
        if mode == "Sign Up":
            name_input = st.text_input("First Name")
            last_input = st.text_input("Last Name")
            if st.button("Create Account"):
                try:
                    cursor.execute("INSERT INTO users VALUES (?,?,?,?)", (email_input, name_input, last_input, pass_input))
                    conn.commit()
                    st.success("Account created! Please Login.")
                except:
                    st.error("User already exists.")
        else:
            if st.button("Login"):
                cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email_input, pass_input))
                user_data = cursor.fetchone()
                if user_data:
                    st.session_state.user = {"email": user_data[0], "name": user_data[1], "last": user_data[2]}
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    else:
        st.markdown(f"""
            <div class='user-profile'>
                <b>Welcome, {st.session_state.user['name']}!</b><br>
                <small>{st.session_state.user['email']}</small>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

# 4. INTERFAZ PRINCIPAL
st.title("🏟️ SquadUp")

if st.session_state.user is None:
    st.warning("Please Login or Sign Up from the sidebar to interact with matches.")
    st.stop()

tab_find, tab_create = st.tabs(["🔍 BROWSE GAMES", "📣 HOST A MATCH"])

# --- TAB: HOST A MATCH ---
with tab_create:
    st.write(f"### Host a Match")
    st.caption(f"Posting as: {st.session_state.user['name']} {st.session_state.user['last']}")
    
    title = st.text_input("Match Title", placeholder="e.g. Champions League Final (Amateur)")
    col1, col2 = st.columns(2)
    with col1:
        sport = st.selectbox("Sport", ["Football", "Padel", "Basketball", "Tennis", "Other"])
        date_ev = st.date_input("Date", min_value=datetime.date.today())
    with col2:
        slots = st.number_input("Slots Needed", 1, 22)
        time_ev = st.time_input("Time")
    
    loc = st.text_input("📍 Location")

    if st.button("🚀 PUBLISH MATCH"):
        if title and loc:
            cursor.execute("""
                INSERT INTO events (title, sport, location, date, time, slots_needed, creator_email) 
                VALUES (?,?,?,?,?,?,?)""", 
                (title, sport, loc, str(date_ev), str(time_ev), slots, st.session_state.user['email']))
            conn.commit()
            st.balloons()
            st.success("Match live! Your details were filled automatically.")
            time.sleep(2)
            st.rerun()

# --- TAB: BROWSE GAMES ---
with tab_find:
    cursor.execute("SELECT * FROM events WHERE slots_needed > 0 ORDER BY date ASC")
    for row in cursor.fetchall():
        with st.container():
            st.markdown(f"""
                <div class="event-card">
                    <span style="color:#74ACDF; font-weight:bold;">{row[2]}</span>
                    <h2>{row[1]}</h2>
                    <p>📅 {row[4]} | ⏰ {row[5]} | 📍 {row[3]}</p>
                    <h3 style='color:#74ACDF;'>🔥 {row[6]} slots left</h3>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🙌 JOIN AS {st.session_state.user['name'].upper()}", key=f"join_{row[0]}"):
                # Update Slots
                cursor.execute("UPDATE events SET slots_needed = ? WHERE id = ?", (row[6]-1, row[0]))
                conn.commit()
                
                # Auto-generate Mail Notification
                subj = quote(f"SquadUp: {st.session_state.user['name']} joined your match!")
                body = quote(f"Hi! {st.session_state.user['name']} {st.session_state.user['last']} ({st.session_state.user['email']}) has joined: {row[1]}.")
                gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={row[7]}&su={subj}&body={body}"
                
                st.success("Spot confirmed!")
                st.markdown(f"### [✉️ SEND CONFIRMATION VIA GMAIL]({gmail_url})")
                st.balloons()

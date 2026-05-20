import streamlit as st
import sqlite3
import datetime
from urllib.parse import quote
import time

# 1. APP CONFIG & DARK THEME
st.set_page_config(page_title="SquadUp", page_icon="⚽", layout="centered")

# CSS para Dark Mode y Estilo Estadio Nocturno
st.markdown("""
    <style>
    /* Fondo Oscuro Total */
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }
    
    /* Barra superior Celeste */
    header[data-testid="stHeader"] {
        background-color: #74ACDF !important;
    }
    
    /* Texto en modo oscuro */
    h1, h2, h3, h4, h5, p, label, .stMarkdown {
        color: #ffffff !important;
    }

    /* Input boxes en modo oscuro */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #1e1e1e !important;
        color: white !important;
        border: 1px solid #333 !important;
    }

    /* Botones Modernos */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #74ACDF; color: white; font-weight: bold; 
        border: none; transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #5b9bd5;
        transform: translateY(-2px);
    }

    /* Tarjetas de Eventos (Dark Cards) */
    .event-card {
        background-color: #1e1e1e; padding: 25px; border-radius: 18px;
        border-left: 10px solid #74ACDF; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        margin-bottom: 25px;
    }
    
    .sport-tag {
        background-color: #74ACDF; color: white;
        padding: 6px 16px; border-radius: 50px; 
        font-size: 0.8em; font-weight: 800;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE ENGINE
def get_db():
    conn = sqlite3.connect("squadup_v5.db")
    cursor = conn.cursor()
    # Eliminada la columna de teléfono para mayor privacidad
    cursor.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, sport TEXT, description TEXT, location TEXT, date TEXT, time TEXT, slots_needed INTEGER, fb_link TEXT)")
    conn.commit()
    return conn

conn = get_db()
cursor = conn.cursor()

# 3. NAVEGACIÓN
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "🔍 BROWSE GAMES"

# 4. INTERFAZ PRINCIPAL
st.title("🏟️ SquadUp")
st.markdown("##### *The lights are on. It's time to play.*")

# Usamos una variable de estado para controlar la pestaña
tabs = ["🔍 BROWSE GAMES", "📣 HOST A MATCH"]
selected_tab = st.radio("", tabs, horizontal=True, label_visibility="collapsed", key="nav_radio")

if selected_tab == "📣 HOST A MATCH":
    st.write("### Post Your Match")
    title = st.text_input("Match Title", placeholder="e.g. 5v5 Street Football")
    
    col1, col2 = st.columns(2)
    with col1:
        sport = st.selectbox("Sport", ["Football", "Padel", "Basketball", "Tennis", "Other"])
        date_ev = st.date_input("Match Date", min_value=datetime.date.today())
    with col2:
        slots = st.number_input("Players Missing", 1, 22)
        time_ev = st.time_input("Kick-off Time")
    
    loc = st.text_input("📍 Pitch / Stadium Address")
    desc = st.text_area("Details (Rules, jersey colors, etc.)")
    fb = st.text_input("Facebook Link (Optional)")

    if st.button("🚀 PUBLISH & START THE GAME!"):
        if title and loc:
            cursor.execute("INSERT INTO events (title, sport, description, location, date, time, slots_needed, fb_link) VALUES (?,?,?,?,?,?,?,?)", 
                           (title, sport, desc, loc, str(date_ev), str(time_ev), slots, fb))
            conn.commit()
            
            # EFECTO CONFETI (Utilizamos balloons que es lo más parecido a confeti en stadium)
            st.balloons() 
            st.success("MATCH PUBLISHED! Redirecting...")
            time.sleep(2) # Pausa para ver los papelitos
            
            # Redirección forzada al Home
            st.info("Match posted! Go to 'Browse Games' to see it.")
        else:
            st.error("Please fill Title and Location.")

else:
    # PESTAÑA: BROWSE GAMES (Ordenado por fecha)
    cursor.execute("SELECT * FROM events WHERE slots_needed > 0 ORDER BY date ASC, time ASC")
    rows = cursor.fetchall()
    
    if not rows:
        st.info("The stadium is empty. Be the first to host a game!")
    
    for row in rows:
        with st.container():
            st.markdown(f"""
                <div class="event-card">
                    <span class="sport-tag">{row[2]}</span>
                    <h2 style='margin-top: 15px;'>{row[1]}</h2>
                    <p>📅 <b>{row[5]}</b> | ⏰ {row[6]}</p>
                    <p>📍 {row[4]}</p>
                    <p style='color: #bbb;'>{row[3]}</p>
                    <h3 style='color:#74ACDF;'>🔥 {row[7]} slots left</h3>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"🙌 JOIN MATCH", key=f"btn_{row[0]}"):
                    new_val = row[7] - 1
                    cursor.execute("UPDATE events SET slots_needed = ? WHERE id = ?", (new_val, row[0]))
                    conn.commit()
                    st.success("You joined the squad!")
                    st.rerun()
            with c2:
                cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(row[1])}&location={quote(row[4])}"
                st.link_button("📅 ADD TO CALENDAR", cal_url)

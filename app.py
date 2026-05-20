import streamlit as st
import sqlite3
import datetime
from urllib.parse import quote

# 1. CONFIGURACIÓN Y ESTILO VISUAL MÓVIL
st.set_page_config(page_title="MatchDeporte", page_icon="⚽", layout="centered")

# Inyección de CSS para que la app no parezca una página de Excel
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #007bff;
        color: white;
        border: none;
        font-weight: bold;
    }
    .event-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #007bff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .sport-tag {
        background-color: #e1f5fe;
        color: #01579b;
        padding: 4px 12px;
        border-radius: 10px;
        font-size: 0.8em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS (Mantenemos la misma lógica)
def conectar_db():
    conn = sqlite3.connect("eventos_deportivos.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT, titulo TEXT, deporte TEXT, descripcion TEXT, 
            ubicacion TEXT, fecha TEXT, hora TEXT, costo TEXT, 
            cupos_totales INTEGER, cupos_disponibles INTEGER, fb_link TEXT
        )
    """)
    conn.commit()
    return conn

conn = conectar_db()
cursor = conn.cursor()

# 3. INTERFAZ MEJORADA
st.title("⚽ MatchDeporte")
st.markdown("#### *¡Completar tu equipo nunca fue tan fácil!*")

tab_buscar, tab_crear = st.tabs(["🔍 Explorar Partidos", "➕ Crear Actividad"])

with tab_crear:
    with st.expander("✨ Pulsa aquí para crear un evento", expanded=True):
        tipo_evento = st.segmented_control("Categoría:", ["Deporte", "General"], default="Deporte")
        
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            titulo = st.text_input("¿Qué vamos a jugar?", placeholder="Ej: 5 vs 5 en 'El Templo'")
        with col_t2:
            deporte = st.selectbox("Deporte", ["Fútbol", "Pádel", "Básquet", "Tenis", "Otro"]) if tipo_evento == "Deporte" else "N/A"
        
        descripcion = st.text_area("Notas (Nivel, reglas, etc.)")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fecha = st.date_input("Día", min_value=datetime.date.today())
            ubicacion = st.text_input("📍 Lugar (Dirección o Maps)")
        with col_f2:
            hora = st.time_input("Hora")
            cupos = st.number_input("¿Cuántos faltan?", 1, 20) if tipo_evento == "Deporte" else 0

        fb_url = st.text_input("🔗 Link de Facebook (Opcional)")
        
        if st.button("🚀 PUBLICAR AHORA"):
            cursor.execute("INSERT INTO eventos (tipo, titulo, deporte, descripcion, ubicacion, fecha, hora, costo, cupos_totales, cupos_disponibles, fb_link) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                           (tipo_evento, titulo, deporte, descripcion, ubicacion, str(fecha), str(hora), "Consultar", cupos, cupos, fb_url))
            conn.commit()
            st.balloons()
            st.success("¡Publicado! Ve a la pestaña 'Explorar' para verlo.")

with tab_buscar:
    st.write("### Próximas actividades cerca de ti")
    
    cursor.execute("SELECT * FROM eventos ORDER BY fecha ASC")
    for ev in cursor.fetchall():
        # Tarjeta visual con HTML/CSS
        st.markdown(f"""
            <div class="event-card">
                <span class="sport-tag">{ev[3] if ev[1] == 'Deporte' else 'Evento'}</span>
                <h3 style='margin-top: 10px;'>{ev[2]}</h3>
                <p>📅 {ev[6]} a las {ev[7]}</p>
                <p>📍 {ev[5]}</p>
                <p style='color: #555;'>{ev[4]}</p>
                <hr>
                <p><b>👥 Buscamos: {ev[10]} personas</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Botones de acción integrados
        cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(ev[2])}&details={quote(ev[4])}&location={quote(ev[5])}"
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.link_button("📅 Agendar", cal_url)
        with col_b2:
            if ev[11]: st.link_button("🔵 Facebook", ev[11])

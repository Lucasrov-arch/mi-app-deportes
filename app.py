import streamlit as st
import sqlite3
import datetime
from urllib.parse import quote

# 1. CONFIGURACIÓN DE LA PÁGINA (Estilo Móvil)
st.set_page_config(page_title="MatchDeporte", page_icon="⚽", layout="centered")

# 2. CONEXIÓN AUTOMÁTICA A LA BASE DE DATOS
# SQLite crea un archivo local automáticamente. No requiere configuración externa.
def conectar_db():
    conn = sqlite3.connect("eventos_deportivos.db")
    cursor = conn.cursor()
    # Tabla para almacenar los partidos y eventos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            titulo TEXT,
            deporte TEXT,
            descripcion TEXT,
            ubicacion TEXT,
            fecha TEXT,
            hora TEXT,
            costo TEXT,
            cupos_totales INTEGER,
            cupos_disponibles INTEGER,
            fb_link TEXT
        )
    """)
    conn.commit()
    return conn

conn = conectar_db()
cursor = conn.cursor()

# 3. INTERFAZ DE USUARIO
st.title("⚽ MatchDeporte & Eventos")
st.subheader("¡Completa tu equipo o encuentra qué hacer en tu zona!")

# Pestañas de navegación
tab_buscar, tab_crear = st.tabs(["🔍 Buscar Eventos / Partidos", "➕ Publicar Evento"])

# ==========================================
# PESTAÑA: CREAR EVENTO
# ==========================================
with tab_crear:
    st.header("Organiza una Actividad")
    
    # Campo para simplificar la vida si viene de Facebook
    fb_url = st.text_input("🔗 ¿Tiene un link de Facebook? (Pégalo para referencia)", placeholder="https://facebook.com/events/...")
    
    tipo_evento = st.radio("Tipo de Evento:", ["Deporte Amateur (Reclutamiento)", "Evento General (Feria, Concierto, etc.)"])
    
    titulo = st.text_input("Título del Evento / Partido", placeholder="Ej: Fútbol 5 - Falta 1 / Feria Gastronómica")
    
    deporte = "N/A"
    cupos = 0
    if tipo_evento == "Deporte Amateur (Reclutamiento)":
        deporte = st.selectbox("Selecciona el Deporte:", ["Fútbol", "Pádel", "Básquetbol", "Tenis", "Running", "Otro"])
        cupos = st.number_input("¿Cuántos jugadores te faltan?", min_value=1, max_value=22, value=1)
    
    descripcion = st.text_area("Descripción de la actividad", placeholder="Detalla las reglas, nivel de juego o de qué trata el evento.")
    
    st.markdown("📍 **Ubicación**")
    ubicacion = st.text_input("Dirección o enlace de Google Maps", placeholder="Ej: Complejo Deportivo Norte / Calle Falsa 123")
    st.caption("Tip: Puedes pegar el enlace directo que te genera la app de Google Maps aquí.")
    
    # Fecha y Hora
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha del evento", min_value=datetime.date.today())
    with col2:
        hora = st.time_input("Hora de inicio")
        
    # Costo
    es_gratis = st.checkbox("¿Es gratis?")
    costo = "Gratis"
    if not es_gratis:
        costo = st.text_input("Precio o Costo por persona", placeholder="Ej: $5 por persona / Entrada libre")

    # Botón Guardar
    if st.button("🚀 Publicar Evento"):
        if titulo and ubicacion:
            cursor.execute("""
                INSERT INTO eventos (tipo, titulo, deporte, descripcion, ubicacion, fecha, hora, costo, cupos_totales, cupos_disponibles, fb_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tipo_evento, titulo, deporte, descripcion, ubicacion, str(fecha), str(hora), costo, cupos, cupos, fb_url))
            conn.commit()
            st.success("🎉 ¡Evento publicado con éxito en tu localidad!")
        else:
            st.error("Por favor, completa al menos el Título y la Ubicación.")

# ==========================================
# PESTAÑA: BUSCAR EVENTOS
# ==========================================
with tab_buscar:
    st.header("Eventos Disponibles")
    
    # Filtros de búsqueda
    filtro_tipo = st.selectbox("Filtrar por categoría:", ["Todos", "Deporte Amateur (Reclutamiento)", "Evento General (Feria, Concierto, etc.)"])
    
    query = "SELECT * FROM eventos WHERE 1=1"
    parametros = []
    
    if filtro_tipo != "Todos":
        query += " AND tipo = ?"
        parametros.append(filtro_tipo)
        
    cursor.execute(query, parametros)
    resultados = cursor.fetchall()
    
    if not resultados:
        st.info("No hay eventos activos creados en este momento. ¡Sé el primero en crear uno!")
    else:
        for ev in resultados:
            # Estructura de datos de la base: ev[0]=id, ev[1]=tipo, ev[2]=titulo, ev[3]=deporte...
            with st.container():
                st.markdown(f"### {ev[2]}")
                if ev[1] == "Deporte Amateur (Reclutamiento)":
                    st.markdown(f"🏅 **Deporte:** {ev[3]} | 👥 **Cupos que faltan:** {ev[10]}")
                
                st.write(f"📝 {ev[4]}")
                st.write(f"📅 **Fecha:** {ev[6]} | ⏰ **Hora:** {ev[7]}")
                st.write(f"💰 **Costo:** {ev[8]}")
                
                # Enlace de Google Maps limpio
                st.write(f"📍 **Lugar:** {ev[5]}")
                
                # Función: Agregar a Google Calendar de forma gratuita mediante URL dinámica
                formato_fecha = ev[6].replace("-", "")
                formato_hora = ev[7].replace(":", "")[0:4]
                # Enlace simplificado de Google Calendar en formato web público
                cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(ev[2])}&dates={formato_fecha}T{formato_hora}00Z/{formato_fecha}T{formato_hora}00Z&details={quote(ev[4])}&location={quote(ev[5])}"
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    st.colors = "primary"
                    st.markdown(f"[📅 Añadir a Google Calendar]({cal_url})")
                
                if ev[11]: # Si tiene link de Facebook
                    with col_btn2:
                        st.markdown(f"[🔗 Ver en Facebook]({ev[11]})")
                
                st.markdown("---")

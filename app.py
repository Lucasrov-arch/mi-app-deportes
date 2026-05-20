import streamlit as st
import sqlite3
import datetime
from urllib.parse import quote
import time

# 1. APP CONFIG & DARK THEME
st.set_page_config(page_title="SquadUp", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    header[data-testid="stHeader"] { background-color: #74ACDF !important; }
    h1, h2, h3, h4, h5, p, label { color: #ffffff !important; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #74ACDF; color: white; font-weight: bold; border: none;
    }
    .event-card {
        background-color: #1e1e1e; padding: 25px; border-radius: 18px;
        border-left: 10px solid #74ACDF; box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        margin-bottom: 25px;
    }
    .sport-tag {
        background-color: #74ACDF; color: white; padding: 6px 16px; border-radius: 50px; 
        font-size: 0.8em; font-weight: 800; text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE ENGINE (Updated with Hidden Email)
def get_db():
    conn = sqlite3.connect("squadup_v6.db")
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

# 3. INTERFACE
st.title("🏟️ SquadUp")

selected_tab = st.radio("", ["🔍 BROWSE GAMES", "📣 HOST A MATCH"], horizontal=True, label_visibility="collapsed")

# --- TAB: HOST A MATCH ---
if selected_tab == "📣 HOST A MATCH":
    st.write("### Host a Match")
    title = st.text_input("Match Title")
    
    col1, col2 = st.columns(2)
    with col1:
        sport = st.selectbox("Sport", ["Football", "Padel", "Basketball", "Tennis", "Other"])
        date_ev = st.date_input("Date", min_value=datetime.date.today())
        email = st.text_input("Your Email (Private)", help="This won't be shown publicly. It's only for join confirmations.")
    with col2:
        slots = st.number_input("Slots Needed", 1, 22)
        time_ev = st.time_input("Time")
        loc = st.text_input("📍 Location")
    
    desc = st.text_area("Details")
    fb = st.text_input("Facebook Link (Optional)")

    if st.button("🚀 PUBLISH MATCH"):
        if title and loc and email:
            cursor.execute("""
                INSERT INTO events (title, sport, description, location, date, time, slots_needed, fb_link, creator_email) 
                VALUES (?,?,?,?,?,?,?,?,?)""", 
                (title, sport, desc, loc, str(date_ev), str(time_ev), slots, fb, email))
            conn.commit()
            st.balloons()
            st.success("Match published! Your email is safe and hidden.")
            time.sleep(2)
            st.info("Switch to 'Browse Games' to see it.")
        else:
            st.error("Title, Location, and Email are required.")

# --- TAB: BROWSE GAMES ---
else:
    cursor.execute("SELECT * FROM events WHERE slots_needed > 0 ORDER BY date ASC")
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
                    <h3 style='color:#74ACDF;'>🔥 {row[7]} slots left</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Modal-like logic for Joining
            with st.expander("🙌 CLICK HERE TO JOIN THIS SQUAD"):
                st.write("Confirm your attendance:")
                u_name = st.text_input("First Name", key=f"fn_{row[0]}")
                u_last = st.text_input("Last Name", key=f"ln_{row[0]}")
                u_email = st.text_input("Your Email", key=f"em_{row[0]}")
                
                if st.button("CONFIRM MY SPOT", key=f"confirm_{row[0]}"):
                    if u_name and u_last and u_email:
                        # 1. Update Slots
                        new_val = row[7] - 1
                        cursor.execute("UPDATE events SET slots_needed = ? WHERE id = ?", (new_val, row[0]))
                        conn.commit()
                        
                        # 2. Generate Confirmation Emails (mailto links)
                        # To creator
                        subject_to_creator = quote(f"SquadUp: {u_name} joined your {row[2]} match!")
                        body_to_creator = quote(f"Hi!\n\n{u_name} {u_last} ({u_email}) has just joined your match: {row[1]}.\n\nSee you on the pitch!")
                        mail_url = f"mailto:{row[9]}?subject={subject_to_creator}&body={body_to_creator}"
                        
                        st.success(f"Great, {u_name}! You're in.")
                        st.markdown(f"### [✉️ CLICK HERE TO NOTIFY THE HOST]({mail_url})")
                        st.caption("This will open your email app to send a quick confirmation to the host.")
                        
                        # Add to calendar option as well
                        cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(row[1])}&location={quote(row[4])}"
                        st.link_button("📅 ADD TO MY CALENDAR", cal_url)
                    else:
                        st.error("Please fill all fields to join.")

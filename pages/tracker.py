import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# --- Require setup before access ---
if "setup_done" not in st.session_state or not st.session_state.setup_done:
    st.warning("⚠️ Please set up the roster first on the Home page.")
    st.stop()

st.set_page_config(layout='wide')

# --- Init session state ---
if "starters" not in st.session_state:
    st.session_state.starters = []
if "players" not in st.session_state:
    st.session_state.players = [23,33,24,75,11,5,84,44,8,31,17]
if "stats" not in st.session_state:
    st.session_state.stats = []
if "pending_action" not in st.session_state:
    st.session_state.pending_action = None
if "quarter" not in st.session_state:
    st.session_state.quarter = 1
if "max_quarters" not in st.session_state:
    st.session_state.max_quarters = 4
if "clock_running" not in st.session_state:
    st.session_state.clock_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0

# --- Buttons to track ---
buttons = [
    '2PT', '3PT', 'FT',
    'Miss2', 'Miss3', 'MissFT',
    'OREB', 'DREB', 'Ast', 'TO',
    'BLK', 'Foul', 'STL', 'SUB'
]

zones_2pt = [
    "Restricted Area", "In the Paint (Non-RA)",
    "Left corner Mid-Range", "Right corner Mid-Range",
    "Left wing Mid-Range", "Right wing Mid-Range",
    "Top of the Key Mid-Range"
]

zones_3pt = [
    "Left Corner 3", "Right Corner 3",
    "Left Wing 3", "Right Wing 3",
    "Top of the Arc 3"
]

# --- Clock ---
st_autorefresh(interval=1000, key="clock_refresh")

if st.session_state.clock_running:
    elapsed = st.session_state.elapsed + (time.time() - st.session_state.start_time)
else:
    elapsed = st.session_state.elapsed

minutes, seconds = divmod(int(elapsed), 60)
current_game_time = f"{minutes}:{seconds:02d}"

# --- Double Input Flow ---
st.title("🏀 Stat Entry")

col1, col2 = st.columns(2)

with col1:
    selected_player = st.selectbox("Select Player", st.session_state.starters if st.session_state.starters else ["None"])

with col2:
    selected_action = st.selectbox("Select Action", buttons)

if st.button("✅ Log Action") and selected_player != "None":
    if selected_action in ["2PT", "3PT", "Miss2", "Miss3"]:
        st.session_state.pending_action = (selected_player, selected_action, current_game_time)
    elif selected_action in ["FT", "MissFT"]:
        st.session_state.stats.append([selected_player, selected_action, current_game_time, f"Q{st.session_state.quarter}"])
    elif selected_action == "SUB":
        st.session_state.players.append(selected_player)
        st.session_state.starters.remove(selected_player)
        st.session_state.stats.append([selected_player, "SUB_OUT", current_game_time, f"Q{st.session_state.quarter}"])
    else:
        st.session_state.stats.append([selected_player, selected_action, current_game_time, f"Q{st.session_state.quarter}"])
    st.rerun()

# --- Zone Selection if Pending ---
if st.session_state.pending_action:
    player, action, act_time = st.session_state.pending_action
    st.warning(f"🏀 Select Zone for Player {player} | {action} at {act_time}")

    zone_list = zones_2pt if action in ["2PT", "Miss2"] else zones_3pt if action in ["3PT", "Miss3"] else []

    for zone in zone_list:
        if st.button(zone, key=f"zone-{player}-{zone}"):
            st.session_state.stats.append([player, f"{action} ({zone})", act_time, f"Q{st.session_state.quarter}"])
            st.session_state.pending_action = None
            st.rerun()

    if st.button("❌ Cancel"):
        st.session_state.pending_action = None
        st.rerun()

# --- Undo ---
if st.session_state.stats:
    if st.button("↩️ Undo Last Action"):
        st.session_state.stats.pop()
        st.rerun()

# --- Stats Table ---
if st.session_state.stats:
    df = pd.DataFrame(st.session_state.stats, columns=["Player", "Action", "Time", "Quarter"])
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Stats", csv, "game_stats.csv", "text/csv")

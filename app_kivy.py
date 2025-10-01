import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# --- Wide layout + big buttons CSS + Modal CSS ---
st.markdown("""
    <style>
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    div.stButton > button {
        font-size: 22px !important;
        height: 80px !important;
        width: 120px !important;
        margin: 5px !important;
    }
    /* Modal overlay */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        z-index: 9998;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    /* Modal content */
    .modal-content {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        max-width: 600px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        z-index: 9999;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .modal-header {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1f1f1f;
        text-align: center;
    }
    .modal-subheader {
        font-size: 20px;
        margin-bottom: 1.5rem;
        color: #555;
        text-align: center;
    }
    /* Zone button styling */
    .zone-button-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(layout='wide')

# --- Buttons to track ---
buttons = [
    '2PT', '3PT', 'FT',
    'Miss2', 'Miss3', 'MissFT',
    'OREB', 'DREB', 'Ast', 'TO',
    'BLK', 'Foul', 'STL', 'SUB'
]

# --- Zone categories ---
zones_2pt = [
    "Restricted Area",
    "In the Paint (Non-RA)",
    "Left Short Mid-Range",
    "Right Short Mid-Range",
    "Left Long Mid-Range",
    "Right Long Mid-Range",
    "Top of the Key Mid-Range"
]

zones_3pt = [
    "Left Corner 3",
    "Right Corner 3",
    "Left Wing 3",
    "Right Wing 3",
    "Top of the Arc 3"
]

# --- Init session state ---
if "starters" not in st.session_state:
    st.session_state.starters = []
if "players" not in st.session_state:
    st.session_state.players = [23,33,24,75,11,5,84,44,8,31,17]
if "stats" not in st.session_state:
    st.session_state.stats = []
if "pending_action" not in st.session_state:
    st.session_state.pending_action = None  # (player, action, time)
if "quarter" not in st.session_state:
    st.session_state.quarter = 1
if "max_quarters" not in st.session_state:
    st.session_state.max_quarters = 4

# --- MODAL POPUP FOR ZONE SELECTION ---
if st.session_state.pending_action:
    player, action, act_time = st.session_state.pending_action
    
    # Create modal overlay
    st.markdown('<div class="modal-overlay"></div>', unsafe_allow_html=True)
    
    # Modal dialog using container
    modal_container = st.container()
    with modal_container:
        st.markdown('<div class="modal-content">', unsafe_allow_html=True)
        st.markdown(f'<div class="modal-header">🏀 SELECT SHOT ZONE</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="modal-subheader">Player {player} | {action} | {act_time}</div>', unsafe_allow_html=True)
        
        if action in ["2PT", "Miss2"]:
            st.markdown("#### 2-Point Zones")
            zone_cols = st.columns(3)
            for i, z in enumerate(zones_2pt):
                if zone_cols[i % 3].button(z, key=f"zone-{player}-{action}-{z}", use_container_width=True):
                    st.session_state.stats.append([player, f"{action} - {z}", act_time, f"Q{st.session_state.quarter}"])
                    st.session_state.pending_action = None
                    st.rerun()

        elif action in ["3PT", "Miss3"]:
            st.markdown("#### 3-Point Zones")
            zone_cols = st.columns(3)
            for i, z in enumerate(zones_3pt):
                if zone_cols[i % 3].button(z, key=f"zone-{player}-{action}-{z}", use_container_width=True):
                    st.session_state.stats.append([player, f"{action} - {z}", act_time, f"Q{st.session_state.quarter}"])
                    st.session_state.pending_action = None
                    st.rerun()
        
        st.markdown("---")
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.pending_action = None
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Stop rendering the rest of the page when modal is active
    st.stop()

# --- Bench UI ---
st.title('Bench')
if st.session_state.players:
    cols = st.columns(len(st.session_state.players))
    for i, p in enumerate(st.session_state.players):
        if cols[i].button(str(p), key=f"player-{p}"):
            if len(st.session_state.starters) < 5:
                st.session_state.starters.append(p)
                st.session_state.players.remove(p)
                st.session_state.stats.append([p, "SUB_IN", "0:00", f"Q{st.session_state.quarter}"])
                st.rerun()

# --- Quarter Logic ---
st.title("📅 Game Quarter")

col_q1, col_q2, col_q3 = st.columns(3)

# show current quarter
col_q1.markdown(f"## 🏀 Quarter {st.session_state.quarter}")

# next quarter button
if col_q2.button("➡️ Next Quarter"):
    if st.session_state.quarter < st.session_state.max_quarters:
        st.session_state.quarter += 1
    else:
        # after 4 quarters, add OT
        st.session_state.quarter += 1
        st.session_state.max_quarters = st.session_state.quarter  # allow unlimited OTs
    st.rerun()

# reset game button
if col_q3.button("🔄 Reset Game"):
    st.session_state.quarter = 1
    st.session_state.max_quarters = 4
    st.session_state.stats = []
    st.session_state.starters = []
    st.session_state.players = [23,33,24,75,11,5,84,44,8,31,17]
    st.session_state.clock_running = False
    st.session_state.elapsed = 0
    st.session_state.start_time = None
    st.session_state.pending_action = None
    st.rerun()

# --- Clock ---
st.title('Clock')
if "clock_running" not in st.session_state:
    st.session_state.clock_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0

# auto refresh clock
st_autorefresh(interval=1000, key="clock_refresh")

col1, col2, col3 = st.columns(3)
if col1.button("▶️ Start / Resume"):
    if not st.session_state.clock_running:
        st.session_state.clock_running = True
        st.session_state.start_time = time.time()

if col2.button("⏸ Pause"):
    if st.session_state.clock_running:
        st.session_state.elapsed += time.time() - st.session_state.start_time
        st.session_state.clock_running = False

if col3.button("⏹ Reset"):
    st.session_state.clock_running = False
    st.session_state.elapsed = 0
    st.session_state.start_time = None

# calc game time
if st.session_state.clock_running:
    elapsed = st.session_state.elapsed + (time.time() - st.session_state.start_time)
else:
    elapsed = st.session_state.elapsed

minutes, seconds = divmod(int(elapsed), 60)
current_game_time = f"{minutes}:{seconds:02d}"
st.markdown(f"# ⏱ {minutes}:{seconds:02d}")

# --- Stat Tracker ---
st.title("🏀 Basketball Stat Tracker")

BUTTONS_PER_ROW = 7  # adjust this for iPad friendliness

for player in st.session_state.starters:
    st.markdown(f"### Player {player}")

    # break the buttons into rows
    for row_start in range(0, len(buttons), BUTTONS_PER_ROW):
        row_buttons = buttons[row_start:row_start+BUTTONS_PER_ROW]
        cols = st.columns(len(row_buttons))

        for i, b in enumerate(row_buttons):
            if cols[i].button(b, key=f"{player}-{b}"):

                if b == "SUB":
                    st.session_state.players.append(player)
                    st.session_state.starters.remove(player)
                    st.session_state.stats.append([player, "SUB_OUT", current_game_time, f"Q{st.session_state.quarter}"])
                    st.rerun()
                else:
                    if b in ["2PT", "3PT", "Miss2", "Miss3"]:
                        # Trigger modal for zone selection
                        st.session_state.pending_action = (player, b, current_game_time)
                        st.rerun()
                    elif b in ["FT", "MissFT"]:
                        # Free throws don't need zones
                        st.session_state.stats.append([player, b, current_game_time, f"Q{st.session_state.quarter}"])
                        st.rerun()
                    else:
                        st.session_state.stats.append([player, b, current_game_time, f"Q{st.session_state.quarter}"])
                        st.rerun()


# --- Undo ---
if st.session_state.stats:
    if st.button("↩️ Undo Last Action"):
        st.session_state.stats.pop()
        st.rerun()

# --- Stats Table ---
if st.session_state.stats:
    st.subheader("📊 Logged Stats")
    df = pd.DataFrame(st.session_state.stats, columns=["Player", "Action", "Time", "Quarter"])

    # Detect if user is on mobile (basic user-agent check)
    user_agent = st.request.headers.get("user-agent", "").lower() if hasattr(st, "request") else ""
    is_mobile = any(x in user_agent for x in ["iphone", "ipad", "android"])

    if is_mobile:
        st.table(df)  # simpler, static version
    else:
        st.dataframe(df, use_container_width=True)  # interactive version

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Stats as CSV",
        data=csv,
        file_name="game_stats.csv",
        mime="text/csv",
    )
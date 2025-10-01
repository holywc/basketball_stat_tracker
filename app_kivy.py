import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# --- Wide layout + big buttons CSS ---
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
    /* Zone selection alert styling */
    .zone-alert {
        background-color: #ff4b4b;
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin: 2rem 0;
        border: 4px solid #ff0000;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    /* Basketball court styling */
    .court-container {
        position: relative;
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: #1a1a1a;
        border-radius: 10px;
    }
    .court-svg {
        width: 100%;
        height: auto;
        display: block;
    }
    .zone-button-overlay {
        position: absolute;
        cursor: pointer;
        transition: all 0.3s;
        background-color: rgba(255, 255, 255, 0.1);
        border: 2px solid #fff;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 14px;
        text-align: center;
        padding: 5px;
    }
    .zone-button-overlay:hover {
        background-color: rgba(255, 165, 0, 0.5);
        transform: scale(1.05);
        border-color: #ffa500;
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
if "clock_running" not in st.session_state:
    st.session_state.clock_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0

# --- CHECK IF ZONE SELECTION IS PENDING ---
if st.session_state.pending_action:
    player, action, act_time = st.session_state.pending_action
    
    # Show prominent alert at the top
    st.markdown(f"""
        <div class="zone-alert">
            ⚠️ ZONE SELECTION REQUIRED ⚠️<br>
            Player {player} | {action} | {act_time}
        </div>
    """, unsafe_allow_html=True)
    
    st.error("🚨 Click on the court to select a shot zone!")
    
    # Show basketball court with interactive zones
    if action in ["2PT", "Miss2"]:
        st.title("📍 SELECT 2-POINT ZONE ON COURT:")
        
        # Create basketball court SVG with clickable zones
        court_html = """
        <svg viewBox="0 0 500 470" style="width: 100%; max-width: 800px; margin: 0 auto; display: block; background: #d2691e;">
            <!-- Court outline -->
            <rect x="10" y="10" width="480" height="450" fill="#c76f3a" stroke="#fff" stroke-width="3"/>
            
            <!-- Three-point line -->
            <path d="M 10 10 L 10 80 Q 250 200 490 80 L 490 10" fill="none" stroke="#fff" stroke-width="3"/>
            
            <!-- Paint / Key -->
            <rect x="180" y="10" width="140" height="190" fill="rgba(139, 69, 19, 0.3)" stroke="#fff" stroke-width="3"/>
            
            <!-- Free throw circle -->
            <circle cx="250" cy="150" r="60" fill="none" stroke="#fff" stroke-width="3"/>
            
            <!-- Restricted area (semi-circle) -->
            <path d="M 210 10 Q 250 70 290 10" fill="rgba(255, 0, 0, 0.2)" stroke="#fff" stroke-width="2"/>
            
            <!-- Basket -->
            <circle cx="250" cy="20" r="8" fill="orange" stroke="#000" stroke-width="2"/>
            
            <!-- Zone labels for 2PT -->
            <text x="250" y="40" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Restricted</text>
            <text x="250" y="120" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Paint (Non-RA)</text>
            
            <text x="100" y="150" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Left Short</text>
            <text x="100" y="165" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Mid-Range</text>
            
            <text x="400" y="150" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Right Short</text>
            <text x="400" y="165" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Mid-Range</text>
            
            <text x="100" y="280" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Left Long</text>
            <text x="100" y="295" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Mid-Range</text>
            
            <text x="400" y="280" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Right Long</text>
            <text x="400" y="295" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Mid-Range</text>
            
            <text x="250" y="280" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Top of Key</text>
            <text x="250" y="295" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Mid-Range</text>
        </svg>
        """
        st.markdown(court_html, unsafe_allow_html=True)
        
        st.markdown("### Click a zone below:")
        cols = st.columns(3)
        for i, z in enumerate(zones_2pt):
            if cols[i % 3].button(f"✓ {z}", key=f"zone-{player}-{action}-{z}", use_container_width=True):
                st.session_state.stats.append([player, f"{action} - {z}", act_time, f"Q{st.session_state.quarter}"])
                st.session_state.pending_action = None
                st.rerun()

    elif action in ["3PT", "Miss3"]:
        st.title("📍 SELECT 3-POINT ZONE ON COURT:")
        
        # Create basketball court SVG for 3PT zones
        court_html = """
        <svg viewBox="0 0 500 470" style="width: 100%; max-width: 800px; margin: 0 auto; display: block; background: #d2691e;">
            <!-- Court outline -->
            <rect x="10" y="10" width="480" height="450" fill="#c76f3a" stroke="#fff" stroke-width="3"/>
            
            <!-- Three-point line (highlighted) -->
            <path d="M 10 10 L 10 80 Q 250 200 490 80 L 490 10" fill="none" stroke="#00ff00" stroke-width="5"/>
            
            <!-- Paint / Key -->
            <rect x="180" y="10" width="140" height="190" fill="rgba(139, 69, 19, 0.3)" stroke="#fff" stroke-width="3"/>
            
            <!-- Free throw circle -->
            <circle cx="250" cy="150" r="60" fill="none" stroke="#fff" stroke-width="3"/>
            
            <!-- Basket -->
            <circle cx="250" cy="20" r="8" fill="orange" stroke="#000" stroke-width="2"/>
            
            <!-- Zone labels for 3PT -->
            <text x="30" y="40" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Left</text>
            <text x="30" y="55" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Corner 3</text>
            
            <text x="470" y="40" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Right</text>
            <text x="470" y="55" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Corner 3</text>
            
            <text x="100" y="130" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Left</text>
            <text x="100" y="145" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Wing 3</text>
            
            <text x="400" y="130" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Right</text>
            <text x="400" y="145" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Wing 3</text>
            
            <text x="250" y="220" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Top of Arc 3</text>
        </svg>
        """
        st.markdown(court_html, unsafe_allow_html=True)
        
        st.markdown("### Click a zone below:")
        cols = st.columns(3)
        for i, z in enumerate(zones_3pt):
            if cols[i % 3].button(f"✓ {z}", key=f"zone-{player}-{action}-{z}", use_container_width=True):
                st.session_state.stats.append([player, f"{action} - {z}", act_time, f"Q{st.session_state.quarter}"])
                st.session_state.pending_action = None
                st.rerun()
    
    st.markdown("---")
    col_cancel = st.columns([1, 2, 1])
    if col_cancel[1].button("❌ CANCEL (No Zone Selected)", use_container_width=True, type="secondary"):
        st.session_state.pending_action = None
        st.rerun()
    
    # Stop rendering the rest of the page
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
                        # Trigger zone selection
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
import streamlit as st

st.set_page_config(layout="wide")
st.title("🏀 Game Setup")

# Initialize session state
if "roster" not in st.session_state:
    st.session_state.roster = []
if "setup_done" not in st.session_state:
    st.session_state.setup_done = False

# Input: number of players
num_players = st.number_input("How many players?", min_value=1, max_value=20, value=10)

st.subheader("Enter Player Numbers and Names (name optional)")
roster = []
for i in range(num_players):
    cols = st.columns([1, 2])  # smaller input for number, larger for name
    with cols[0]:
        number = st.text_input(f"Player {i+1} Number", key=f"num_{i}")
    with cols[1]:
        name = st.text_input(f"Player {i+1} Name (optional)", key=f"name_{i}")
    if number.strip():  # only add if number entered
        roster.append({"number": number.strip(), "name": name.strip()})

# Save roster
if st.button("✅ Start Game"):
    if roster:
        st.session_state.roster = roster
        st.session_state.players = [p["number"] for p in roster]  # keep only numbers list
        st.session_state.setup_done = True
        st.success("Roster saved! 👉 Go to the **Tracker** page from the sidebar.")
    else:
        st.warning("Please enter at least one player number.")

import requests
import streamlit as st

st.set_page_config(page_title="Stan's Sports Stats", page_icon="🏀", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "nba_player_moves"

@st.cache_data(ttl=3600)
def fetch_nba_transactions():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/transactions?limit=1000"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return []
    
    transactions = []
    for item in data.get('transactions', []):
        date = item.get('date', '')[:10] 
        desc = item.get('description', 'No details provided.')
        
        team_info = item.get('team', {})
        team_name = team_info.get('displayName', 'Unknown Team') if isinstance(team_info, dict) else 'Unknown Team'
        
        transactions.append({
            "Date": date,
            "Team": team_name,
            "Transaction": desc
        })
        
    return transactions

def render_player_moves():
    st.title("🔄 NBA Player Moves")
    
    transactions = fetch_nba_transactions()
    
    if not transactions:
        st.error("Hold up. Having trouble pulling data right now.")
        return

    search_query = st.text_input("🔍 Search Teams (e.g., Lakers, Knicks):", "").strip().lower()
    st.divider()

    results_found = False
    for tx in transactions:
        if search_query in tx['Team'].lower():
            results_found = True
            with st.container():
                st.subheader(tx['Team'])
                st.caption(f"🗓️ {tx['Date']}")
                st.write(tx['Transaction'])
                st.divider()
                
    if not results_found:
        st.info("No moves found for that search.")

def main():
    st.sidebar.title("Stan's Sports Stats")
    
    with st.sidebar.expander("🏀 Basketball", expanded=True):
        st.markdown("**NBA**")
        if st.button("📊 Standings", key="nba_standings_btn", use_container_width=True):
            st.session_state.page = "nba_standings"
        if st.button("🔄 Player Moves", key="nba_moves_btn", use_container_width=True):
            st.session_state.page = "nba_player_moves"
        if st.button("📈 Player Stats", key="nba_stats_btn", use_container_width=True):
            st.session_state.page = "nba_player_stats"
        if st.button("⏱️ Matches Play by Play", key="nba_pbp_btn", use_container_width=True):
            st.session_state.page = "nba_pbp"

    if st.session_state.page == "nba_player_moves":
        render_player_moves()
    elif st.session_state.page == "nba_standings":
        st.title("📊 NBA Standings")
        st.info("🚧 Standings dashboard coming soon.")
    elif st.session_state.page == "nba_player_stats":
        st.title("📈 NBA Player Stats")
        st.info("🚧 Player statistics engine coming soon.")
    elif st.session_state.page == "nba_pbp":
        st.title("⏱️ NBA Matches Play by Play")
        st.info("🚧 Live play-by-play tracker coming soon.")

if __name__ == "__main__":
    main()

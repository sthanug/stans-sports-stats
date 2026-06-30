import requests
import streamlit as st

st.set_page_config(page_title="Stan's Sports Stats", page_icon="🏀", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "nba_player_moves"

@st.cache_data(ttl=3600)
def fetch_transactions(league):
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/{league}/transactions?limit=1000"
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

def render_moves_page(league, title):
    st.title(title)
    transactions = fetch_transactions(league)
    if not transactions:
        st.error("Hold up. Having trouble pulling data right now.")
        return

    search_query = st.text_input("🔍 Search Teams:", "").strip().lower()
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

def render_wnba_standings():
    st.title("📊 WNBA Leaderboard")
    st.divider()
    
    # 15 active teams structured by real league win standings data
    teams = [
        {"rank": 1, "team": "Minnesota Lynx", "record": "15-4", "pct": ".789", "gb": "—"},
        {"rank": 2, "team": "Las Vegas Aces", "record": "14-5", "pct": ".737", "gb": "1.0"},
        {"rank": 3, "team": "Golden State Valkyries", "record": "13-7", "pct": ".650", "gb": "2.5"},
        {"rank": 4, "team": "Atlanta Dream", "record": "12-7", "pct": ".632", "gb": "3.0"},
        {"rank": 5, "team": "New York Liberty", "record": "12-8", "pct": ".600", "gb": "3.5"},
        {"rank": 6, "team": "Dallas Wings", "record": "11-8", "pct": ".579", "gb": "4.0"},
        {"rank": 7, "team": "Indiana Fever", "record": "11-8", "pct": ".579", "gb": "4.0"},
        {"rank": 8, "team": "Washington Mystics", "record": "9-9", "pct": ".500", "gb": "5.5"},
        {"rank": 9, "team": "Toronto Tempo", "record": "9-10", "pct": ".474", "gb": "6.0"},
        {"rank": 10, "team": "Los Angeles Sparks", "record": "8-10", "pct": ".444", "gb": "6.5"},
        {"rank": 11, "team": "Portland Fire", "record": "8-12", "pct": ".400", "gb": "7.5"},
        {"rank": 12, "team": "Phoenix Mercury", "record": "7-13", "pct": ".350", "gb": "8.5"},
        {"rank": 13, "team": "Chicago Sky", "record": "6-13", "pct": ".316", "gb": "9.0"},
        {"rank": 14, "team": "Seattle Storm", "record": "5-15", "pct": ".250", "gb": "10.5"},
        {"rank": 15, "team": "Connecticut Sun", "record": "4-15", "pct": ".211", "gb": "11.0"}
    ]
    
    # Custom Non-Table Grid Layout
    for t in teams:
        col1, col2, col3, col4, col5 = st.columns([1, 4, 2, 2, 2])
        with col1:
            st.write(f"**#{t['rank']}**")
        with col2:
            st.write(f"**{t['team']}**")
        with col3:
            st.text(f"Record: {t['record']}")
        with col4:
            st.text(f"Pct: {t['pct']}")
        with col5:
            st.text(f"GB: {t['gb']}")
        st.divider()
        
    st.subheader("🏆 Postseason Bracket")
    
    # Secure, bulletproof container formatting to gray/blur out postseason section
    st.html(
        """
        <div style="
            filter: grayscale(100%) blur(2px); 
            opacity: 0.4; 
            pointer-events: none; 
            border: 1px solid #444; 
            padding: 25px; 
            border-radius: 8px;
            background-color: #111;
        ">
            <h3 style="margin-top:0; color:#888;">🔒 WNBA Playoffs (Locked until September)</h3>
            <p style="margin-bottom:5px;"><strong>Quarterfinals Matchups Projection:</strong></p>
            <ul style="margin-top:5px; padding-left:20px; color:#aaa;">
                <li>Seed #1 vs. Seed #8</li>
                <li>Seed #2 vs. Seed #7</li>
                <li>Seed #3 vs. Seed #6</li>
                <li>Seed #4 vs. Seed #5</li>
            </ul>
        </div>
        """
    )

def main():
    st.sidebar.title("Stan's Sports Stats")
    
    with st.sidebar.expander("🏀 Basketball", expanded=True):
        with st.expander("🇺🇸 NBA", expanded=st.session_state.page.startswith("nba_")):
            if st.button("📊 Standings", key="nba_standings_btn", use_container_width=True):
                st.session_state.page = "nba_standings"
            if st.button("🔄 Player Moves", key="nba_moves_btn", use_container_width=True):
                st.session_state.page = "nba_player_moves"
            if st.button("📈 Player Stats", key="nba_stats_btn", use_container_width=True):
                st.session_state.page = "nba_player_stats"
            if st.button("⏱️ Matches Play by Play", key="nba_pbp_btn", use_container_width=True):
                st.session_state.page = "nba_pbp"
                
        with st.expander("👩 WNBA", expanded=st.session_state.page.startswith("wnba_")):
            if st.button("📊 Standings", key="wnba_standings_btn", use_container_width=True):
                st.session_state.page = "wnba_standings"
            if st.button("🔄 Player Moves", key="wnba_moves_btn", use_container_width=True):
                st.session_state.page = "wnba_player_moves"
            if st.button("📈 Player Stats", key="wnba_stats_btn", use_container_width=True):
                st.session_state.page = "wnba_player_stats"
            if st.button("⏱️ Matches Play by Play", key="wnba_pbp_btn", use_container_width=True):
                st.session_state.page = "wnba_pbp"

    if st.session_state.page == "nba_player_moves":
        render_moves_page("nba", "🔄 NBA Player Moves")
    elif st.session_state.page == "wnba_player_moves":
        render_moves_page("wnba", "🔄 WNBA Player Moves")
    elif st.session_state.page == "wnba_standings":
        render_wnba_standings()
    elif st.session_state.page == "nba_standings":
        st.title("📊 NBA Standings")
        st.info("🚧 NBA Standings coming soon.")
    elif st.session_state.page == "nba_player_stats":
        st.title("📈 NBA Player Stats")
        st.info("🚧 NBA Statistics coming soon.")
    elif st.session_state.page == "wnba_player_stats":
        st.title("📈 WNBA Player Stats")
        st.info("🚧 WNBA Statistics coming soon.")
    elif st.session_state.page == "nba_pbp":
        st.title("⏱️ NBA Matches Play by Play")
        st.info("🚧 NBA Play-by-Play coming soon.")
    elif st.session_state.page == "wnba_pbp":
        st.title("⏱️ WNBA Matches Play by Play")
        st.info("🚧 WNBA Play-by-Play coming soon.")

if __name__ == "__main__":
    main()

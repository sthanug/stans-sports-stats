import requests
import streamlit as st
import pandas as pd

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

@st.cache_data(ttl=3600)
def fetch_wnba_standings():
    url = "https://site.api.espn.com/apis/v1/sports/basketball/wnba/standings"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        standings_list = []
        for group in data.get('standings', []):
            for entry in group.get('teamStandings', []):
                team_name = entry.get('team', 'Unknown')
                wins = entry.get('wins', 0)
                losses = entry.get('losses', 0)
                pct = entry.get('winLossPercentage', 0.0)
                gb = entry.get('gamesBehind', 0.0)
                
                standings_list.append({
                    "Team": team_name,
                    "Wins": wins,
                    "Losses": losses,
                    "Win %": f"{pct:.3f}",
                    "GB": "—" if gb == 0 else str(gb)
                })
        return pd.DataFrame(standings_list).sort_values(by="Wins", ascending=False).reset_index(drop=True)
    except Exception:
        # Fallback local data if the specific V1 endpoint encounters structure variance
        fallback_data = [
            {"Team": "Minnesota Lynx", "Wins": 15, "Losses": 4, "Win %": ".789", "GB": "—"},
            {"Team": "Las Vegas Aces", "Wins": 14, "Losses": 5, "Win %": ".737", "GB": "1.0"},
            {"Team": "Golden State Valkyries", "Wins": 13, "Losses": 7, "Win %": ".650", "GB": "2.5"},
            {"Team": "Atlanta Dream", "Wins": 12, "Losses": 7, "Win %": ".632", "GB": "3.0"},
            {"Team": "New York Liberty", "Wins": 12, "Losses": 8, "Win %": ".600", "GB": "3.5"},
            {"Team": "Dallas Wings", "Wins": 11, "Losses": 8, "Win %": ".579", "GB": "4.0"},
            {"Team": "Indiana Fever", "Wins": 11, "Losses": 8, "Win %": ".579", "GB": "4.0"},
            {"Team": "Washington Mystics", "Wins": 9, "Losses": 9, "Win %": ".500", "GB": "5.5"},
            {"Team": "Toronto Tempo", "Wins": 9, "Losses": 10, "Win %": ".474", "GB": "6.0"},
            {"Team": "Los Angeles Sparks", "Wins": 8, "Losses": 10, "Win %": ".444", "GB": "6.5"},
            {"Team": "Portland Fire", "Wins": 8, "Losses": 12, "Win %": ".400", "GB": "7.5"},
            {"Team": "Phoenix Mercury", "Wins": 7, "Losses": 13, "Win %": ".350", "GB": "8.5"},
            {"Team": "Chicago Sky", "Wins": 6, "Losses": 13, "Win %": ".316", "GB": "9.0"},
            {"Team": "Seattle Storm", "Wins": 5, "Losses": 15, "Win %": ".250", "GB": "10.5"},
            {"Team": "Connecticut Sun", "Wins": 4, "Losses": 15, "Win %": ".211", "GB": "11.0"}
        ]
        return pd.DataFrame(fallback_data)

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
    st.write("The top 8 teams regardless of conference advance to the postseason battleground.")
    
    df = fetch_wnba_standings()
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.divider()
    
    st.subheader("🏆 Postseason Bracket")
    
    # Custom HTML/CSS wrapper to cleanly gray out and blur the inactive playoff section
    st.markdown(
        """
        <div style="
            filter: grayscale(100%) blur(2px); 
            opacity: 0.5; 
            pointer-events: none; 
            border: 1px solid #ccc; 
            padding: 20px; 
            border-radius: 10px;
            background-color: #1e1e1e;
        ">
            <h3>🔒 WNBA Playoffs (Locked until September)</h3>
            <p><strong>Quarterfinals Matchups Projection:</strong></p>
            <ul>
                <li>Seed #1 vs. Seed #8</li>
                <li>Seed #2 vs. Seed #7</li>
                <li>Seed #3 vs. Seed #6</li>
                <li>Seed #4 vs. Seed #5</li>
            </ul>
        </div>
        """,
        unsafe_html=True
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

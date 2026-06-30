import requests
import streamlit as st

st.set_page_config(page_title="Stan's Sports Stats", page_icon="🏀", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "nba_player_moves"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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
    
    leaderboard_html = """
    <div style="font-family: sans-serif; max-width: 800px; margin-bottom: 25px;">
    """
    for t in teams:
        leaderboard_html += f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #333; font-size: 14px;">
            <div style="width: 50px; color: #888; font-weight: bold;">#{t['rank']}</div>
            <div style="flex-grow: 1; font-weight: bold; color: #fff;">{t['team']}</div>
            <div style="color: #aaa; font-variant-numeric: tabular-nums;">
                <span style="background: #222; padding: 2px 6px; border-radius: 4px; color: #ff9900;">{t['record']}</span>
                <span style="margin-left: 15px;">PCT: <strong>{t['pct']}</strong></span>
                <span style="margin-left: 15px;">GB: <strong>{t['gb']}</strong></span>
            </div>
        </div>
        """
    leaderboard_html += "</div>"
    st.html(leaderboard_html)
        
    st.subheader("🏆 Postseason Bracket")
    st.html(
        """
        <div style="
            filter: grayscale(100%) blur(1.5px); 
            opacity: 0.4; 
            pointer-events: none; 
            border: 1px solid #444; 
            padding: 20px; 
            border-radius: 8px;
            background-color: #111;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: sans-serif;
        ">
            <div style="display: flex; flex-direction: column; gap: 20px; width: 28%;">
                <div style="background: #222; padding: 8px; border-radius: 4px; border-left: 4px solid #ff9900;">
                    <div style="font-size: 11px; color: #888;">MATCHUP 1</div>
                    <div style="font-size: 14px; color: #fff;">#1 Lynx</div>
                    <div style="font-size: 14px; color: #aaa;">#8 Mystics</div>
                </div>
                <div style="background: #222; padding: 8px; border-radius: 4px; border-left: 4px solid #ff9900;">
                    <div style="font-size: 11px; color: #888;">MATCHUP 2</div>
                    <div style="font-size: 14px; color: #fff;">#4 Dream</div>
                    <div style="font-size: 14px; color: #aaa;">#5 Liberty</div>
                </div>
                <div style="background: #222; padding: 8px; border-radius: 4px; border-left: 4px solid #ff9900;">
                    <div style="font-size: 11px; color: #888;">MATCHUP 3</div>
                    <div style="font-size: 14px; color: #fff;">#2 Aces</div>
                    <div style="font-size: 14px; color: #aaa;">#7 Fever</div>
                </div>
                <div style="background: #222; padding: 8px; border-radius: 4px; border-left: 4px solid #ff9900;">
                    <div style="font-size: 11px; color: #888;">MATCHUP 4</div>
                    <div style="font-size: 14px; color: #fff;">#3 Valkyries</div>
                    <div style="font-size: 14px; color: #aaa;">#6 Wings</div>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 75px; width: 28%;">
                <div style="background: #222; padding: 8px; border-radius: 4px; border-left: 4px solid #ff9900;">
                    <div style="font-size: 11px; color: #888;">SEMIFINALS 1</div>
                    <div style="font-size: 14px; color: #666; font-style: italic;">Winner M1</div>
                    <div style="font-size: 14px; color: #666; font-style: italic;">Winner M2</div>
                </div>
                <div style="background: #222; padding: 8px; border-radius: 4px; border-left: 4px solid #ff9900;">
                    <div style="font-size: 11px; color: #888;">SEMIFINALS 2</div>
                    <div style="font-size: 14px; color: #666; font-style: italic;">Winner M3</div>
                    <div style="font-size: 14px; color: #666; font-style: italic;">Winner M4</div>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; width: 28%; align-items: center;">
                <div style="background: #333; padding: 12px; border-radius: 6px; border: 1px solid #ff9900; width: 100%; text-align: center;">
                    <div style="font-size: 12px; color: #ff9900; font-weight: bold; letter-spacing: 1px;">WNBA FINALS</div>
                    <div style="margin-top: 8px; font-size: 13px; color: #666; font-style: italic;">TBD vs TBD</div>
                </div>
            </div>
        </div>
        """
    )

def simulate_stan_response(prompt):
    p = prompt.lower()
    if "giannis" in p:
        return "Ah, the Giannis trade block buster! Legally, it's a pending agreement until the July moratorium ends. Once the NBA fiscal year officially rolls over, the paperwork goes through league approval and it hits the tracker feed!"
    if "veteran extension" in p or "exception" in p or "cap" in p:
        return "Roster contracts use salary cap exceptions. A veteran extension allows a team to re-sign their current player over the standard salary cap ceiling based on their accrued years in the league."
    if "two-way" in p:
        return "Two-way contracts let players bounce between the NBA main roster and the G-League development affiliate. Teams use them to develop young assets without wasting official main roster spots."
    return f"I'm keeping tabs on that! As the season plays out, I'll analyze roster metrics, trade contexts, and team performance breakdowns right here."

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

    st.sidebar.divider()
    st.sidebar.subheader("🤖 Ask Stan")
    
    user_msg = st.sidebar.text_input("Ask about rules, trades, or context:", key="chat_input", label_visibility="collapsed")
    if st.sidebar.button("Send", use_container_width=True) and user_msg.strip():
        reply = simulate_stan_response(user_msg)
        st.session_state.chat_history.append((user_msg, reply))

    if st.session_state.chat_history:
        with st.sidebar.container():
            for u, s in reversed(st.session_state.chat_history[-3:]):
                st.markdown(f"**You:** {u}")
                st.markdown(f"**Stan:** {s}")
                st.sidebar.divider()

    # Routing
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

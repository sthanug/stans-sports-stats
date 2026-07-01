import requests
import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Stan's Sports Stats", page_icon="🏀", layout="wide")

# Custom Orange & Black Basketball Theme Injection
st.html(
    """
    <style>
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #0b0b0c !important;
            border-right: 1px solid #222;
        }
        /* Primary button custom color overrides */
        .stButton > button[kind="primary"] {
            background-color: #ff5500 !important;
            border-color: #ff5500 !important;
            color: #ffffff !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #e04400 !important;
            border-color: #e04400 !important;
        }
        /* Custom styled code metrics badges */
        .sport-badge {
            background: #161618;
            border: 1px solid #ff5500;
            padding: 2px 8px;
            border-radius: 4px;
            color: #ff5500;
            font-family: monospace;
            font-weight: bold;
        }
    </style>
    """
)

if "page" not in st.session_state:
    st.session_state.page = "nba_player_moves"
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = False
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

@st.cache_data(ttl=1800)
def fetch_live_wnba_standings():
    url = "https://site.api.espn.com/apis/v2/sports/basketball/wnba/standings"
    
    official_wnba_teams = [
        "Minnesota Lynx", "Las Vegas Aces", "Golden State Valkyries", "Atlanta Dream",
        "New York Liberty", "Dallas Wings", "Indiana Fever", "Washington Mystics",
        "Toronto Tempo", "Los Angeles Sparks", "Portland Fire", "Phoenix Mercury",
        "Chicago Sky", "Seattle Storm", "Connecticut Sun"
    ]
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        teams_list = []
        # ESPN API separates standings by conference structures inside 'children'
        for conference in data.get('children', []):
            for entry in conference.get('standings', {}).get('entries', []):
                team_info = entry.get('team', {})
                team_name = team_info.get('displayName', 'Unknown Team')
                
                # Filter check to guarantee accurate roster visibility
                if team_name not in official_wnba_teams:
                    continue
                
                stats_array = entry.get('stats', [])
                
                # Bulletproof fallback parameters
                w_l_record = "0-0"
                win_pct = 0.0
                games_behind = "—"
                
                for metric in stats_array:
                    metric_type = str(metric.get('type', '')).lower()
                    metric_name = str(metric.get('name', '')).lower()
                    metric_abbr = str(metric.get('abbreviation', '')).upper()
                    
                    # Extract overall win-loss breakdown records accurately
                    if metric_type == 'overall' or metric_name == 'overall' or metric_abbr in ['W-L', 'REC']:
                        w_l_record = metric.get('displayValue', w_l_record)
                    
                    # Extract precise mathematical win percentage split 
                    elif metric_type == 'winpercent' or metric_name == 'winpercent' or metric_abbr == 'PCT':
                        win_pct = metric.get('value', win_pct)
                        
                    # Extract structural division games behind distance margin
                    elif metric_type == 'gamesbehind' or metric_name == 'gamesbehind' or metric_abbr == 'GB':
                        gb_val = metric.get('displayValue', '—')
                        games_behind = "—" if gb_val == "0" or gb_val == "0.0" else str(gb_val)
                
                teams_list.append({
                    "team": team_name,
                    "record": w_l_record,
                    "pct": f"{win_pct:.3f}" if isinstance(win_pct, (int, float)) and win_pct <= 1 else str(win_pct),
                    "gb": games_behind
                })
        
        # Sort values cleanly by active win percentage calculations
        teams_list.sort(key=lambda x: float(x['pct']) if x['pct'] != '0.0' else 0.0, reverse=True)
        return teams_list
    except Exception:
        return []

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
    
    teams = fetch_live_wnba_standings()
    
    if not teams:
        st.error("Hold up. Having trouble pulling data right now.")
        return
        
    leaderboard_html = '<div style="font-family: sans-serif; max-width: 800px; margin-bottom: 25px;">'
    for idx, t in enumerate(teams, 1):
        leaderboard_html += f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #222; font-size: 14px;">
            <div style="width: 50px; color: #666; font-weight: bold;">#{idx}</div>
            <div style="flex-grow: 1; font-weight: bold; color: #fff;">{t['team']}</div>
            <div style="color: #aaa;">
                <span class="sport-badge">{t['record']}</span>
                <span style="margin-left: 15px;">PCT: <strong style="color:#fff;">{t['pct']}</strong></span>
                <span style="margin-left: 15px;">GB: <strong style="color:#fff;">{t['gb']}</strong></span>
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
            opacity: 0.3; 
            pointer-events: none; 
            border: 1px solid #333; 
            padding: 20px; 
            border-radius: 8px;
            background-color: #0c0c0d;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: sans-serif;
        ">
            <div style="display: flex; flex-direction: column; gap: 20px; width: 28%;">
                <div style="background: #161618; padding: 8px; border-radius: 4px; border-left: 4px solid #ff5500;">
                    <div style="font-size: 11px; color: #666;">MATCHUP 1</div>
                    <div style="font-size: 14px; color: #fff;">#1 Seed</div>
                    <div style="font-size: 14px; color: #888;">#8 Seed</div>
                </div>
                <div style="background: #161618; padding: 8px; border-radius: 4px; border-left: 4px solid #ff5500;">
                    <div style="font-size: 11px; color: #666;">MATCHUP 2</div>
                    <div style="font-size: 14px; color: #fff;">#4 Seed</div>
                    <div style="font-size: 14px; color: #888;">#5 Seed</div>
                </div>
                <div style="background: #161618; padding: 8px; border-radius: 4px; border-left: 4px solid #ff5500;">
                    <div style="font-size: 11px; color: #666;">MATCHUP 3</div>
                    <div style="font-size: 14px; color: #fff;">#2 Seed</div>
                    <div style="font-size: 14px; color: #888;">#7 Seed</div>
                </div>
                <div style="background: #161618; padding: 8px; border-radius: 4px; border-left: 4px solid #ff5500;">
                    <div style="font-size: 11px; color: #666;">MATCHUP 4</div>
                    <div style="font-size: 14px; color: #fff;">#3 Seed</div>
                    <div style="font-size: 14px; color: #888;">#6 Seed</div>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 75px; width: 28%;">
                <div style="background: #161618; padding: 8px; border-radius: 4px; border-left: 4px solid #ff5500;">
                    <div style="font-size: 11px; color: #666;">SEMIFINALS 1</div>
                    <div style="font-size: 14px; color: #555; font-style: italic;">Winner M1</div>
                    <div style="font-size: 14px; color: #555; font-style: italic;">Winner M2</div>
                </div>
                <div style="background: #161618; padding: 8px; border-radius: 4px; border-left: 4px solid #ff5500;">
                    <div style="font-size: 11px; color: #666;">SEMIFINALS 2</div>
                    <div style="font-size: 14px; color: #555; font-style: italic;">Winner M3</div>
                    <div style="font-size: 14px; color: #555; font-style: italic;">Winner M4</div>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; width: 28%; align-items: center;">
                <div style="background: #161618; padding: 12px; border-radius: 6px; border: 1px solid #ff5500; width: 100%; text-align: center;">
                    <div style="font-size: 12px; color: #ff5500; font-weight: bold; letter-spacing: 1px;">FINALS</div>
                    <div style="margin-top: 8px; font-size: 13px; color: #555; font-style: italic;">TBD vs TBD</div>
                </div>
            </div>
        </div>
        """
    )

def query_huggingface_live(user_input):
    try:
        token = st.secrets["HF_TOKEN"]
        client = InferenceClient("meta-llama/Meta-Llama-3-8B-Instruct", token=token)
        
        system_instruction = (
            "You are Stan, a high-energy, hyped-up, enthusiastic sports broadcaster and analyst! "
            "Bring extreme energy, catchphrases, and excitement to your breakdowns of sports regulations, "
            "statistical trends, and trade contexts across leagues. Be 100% accurate with league names "
            "(never confuse basketball's WNBA with soccer's NWSL). "
            "CRITICAL: Your response must be extremely punchy, concise, and under 50 words total."
        )
        
        messages = [{"role": "system", "content": system_instruction}]
        for role, text in st.session_state.chat_history:
            messages.append({"role": "user" if role == "user" else "assistant", "content": text})
        
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat_completion(
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Stan is adjusting his microphone. (Error: {str(e)})"

def main():
    st.sidebar.title("Stan's Sports Stats")
    
    if not st.session_state.ai_mode:
        if st.sidebar.button("🤖 Ask Stan (AI)", key="enter_ai_btn", use_container_width=True, type="primary"):
            st.session_state.ai_mode = True
            st.rerun()
            
        st.sidebar.divider()
        
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
    else:
        if st.sidebar.button("⬅️ Back to Navigation", key="exit_ai_btn", use_container_width=True):
            st.session_state.ai_mode = False
            st.rerun()
            
        st.sidebar.divider()
        
        st.sidebar.html(
            """
            <div style="display: flex; justify-content: center; margin-bottom: 15px;">
                <svg width="55" height="55" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="#ff5500" stroke-width="2.5"/>
                    <path d="M6 12H18M12 6V18" stroke="#ff5500" stroke-width="1.5" stroke-dasharray="2 2"/>
                    <circle cx="12" cy="11" r="2.5" fill="#ffffff"/>
                    <path d="M9.5 15.5C10.2 16.5 13.8 16.5 14.5 15.5" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
            """
        )
        
        st.sidebar.subheader("🤖 Ask Stan")
        st.sidebar.write("Get insights on rules, historical player contexts, or cross-league trades:")
        
        with st.sidebar.form(key="chat_form", clear_on_submit=True):
            user_msg = st.text_input("Message Stan...", placeholder="Type your multi-sport query...")
            submit_clicked = st.form_submit_button("Send Query", use_container_width=True)
            
        if submit_clicked and user_msg.strip():
            ai_reply = query_huggingface_live(user_msg)
            st.session_state.chat_history.append(("user", user_msg))
            st.session_state.chat_history.append(("model", ai_reply))

        if st.session_state.chat_history:
            st.sidebar.divider()
            with st.sidebar.container():
                for role, text in st.session_state.chat_history[-6:]:
                    if role == "user":
                        st.markdown(f"🙋‍♂️ **You:** {text}")
                    else:
                        st.markdown(f"🤖 **Stan:** {text}")
                    st.sidebar.divider()

    # Routing Engine
    if st.session_state.page == "nba_player_moves":
        render_moves_page("nba", "🔄 NBA Player Moves")
    elif st.session_state.page == "wnba_player_moves":
        render_moves_page("wnba", "🔄 WNBA Player Moves")
    elif st.session_state.page == "wnba_standings":
        render_wnba_standings()
    elif st.session_state.page == "nba_standings":
        st.info("NBA Standings coming soon.")
    elif st.session_state.page == "nba_player_stats":
        st.info("NBA Statistics coming soon.")
    elif st.session_state.page == "wnba_player_stats":
        st.info("WNBA Statistics coming soon.")
    elif st.session_state.page == "nba_pbp":
        st.info("NBA Play-by-Play coming soon.")
    elif st.session_state.page == "wnba_pbp":
        st.info("WNBA Play-by-Play coming soon.")

if __name__ == "__main__":
    main()

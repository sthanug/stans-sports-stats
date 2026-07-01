import requests
import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Stan's Sports Stats", page_icon="🏀", layout="wide")

# Premium Aesthetic Minimalist Theme Injection
st.html(
    """
    <style>
        /* Base page background layout */
        .stApp {
            background-color: #0d0e10 !important;
            color: #e4e6eb !important;
        }
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #121316 !important;
            border-right: 1px solid #1f2226;
        }
        /* Custom styled league elements */
        .sport-badge {
            background: #1a1c23;
            border: 1px solid #ff5500;
            padding: 4px 10px;
            border-radius: 6px;
            color: #ff5500;
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        /* Clean table row headers */
        .table-row {
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 12px 16px; 
            border-bottom: 1px solid #1f2226; 
            font-size: 14px;
            background-color: #121316;
            margin-bottom: 4px;
            border-radius: 6px;
            transition: background 0.2s ease;
        }
        .table-row:hover {
            background-color: #181a20;
        }
        /* Streamlit primary button overrides */
        .stButton > button[kind="primary"] {
            background-color: #ff5500 !important;
            border-color: #ff5500 !important;
            color: #ffffff !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #e04400 !important;
            border-color: #e04400 !important;
        }
        .stButton > button {
            border-radius: 6px !important;
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
        for conference in data.get('children', []):
            for entry in conference.get('standings', {}).get('entries', []):
                team_info = entry.get('team', {})
                team_name = team_info.get('displayName', 'Unknown Team')
                
                if team_name not in official_wnba_teams:
                    continue
                
                stats_array = entry.get('stats', [])
                
                w_l_record = "0-0"
                win_pct = 0.0
                games_behind = "—"
                
                for metric in stats_array:
                    metric_type = str(metric.get('type', '')).lower()
                    metric_name = str(metric.get('name', '')).lower()
                    metric_abbr = str(metric.get('abbreviation', '')).upper()
                    
                    if metric_type == 'overall' or metric_name == 'overall' or metric_abbr in ['W-L', 'REC']:
                        w_l_record = metric.get('displayValue', w_l_record)
                    elif metric_type == 'winpercent' or metric_name == 'winpercent' or metric_abbr == 'PCT':
                        win_pct = metric.get('value', win_pct)
                    elif metric_type == 'gamesbehind' or metric_name == 'gamesbehind' or metric_abbr == 'GB':
                        gb_val = metric.get('displayValue', '—')
                        games_behind = "—" if gb_val == "0" or gb_val == "0.0" else str(gb_val)
                
                teams_list.append({
                    "team": team_name,
                    "record": w_l_record,
                    "pct": f"{win_pct:.3f}" if isinstance(win_pct, (int, float)) and win_pct <= 1 else str(win_pct),
                    "gb": games_behind
                })
        
        teams_list.sort(key=lambda x: float(x['pct']) if x['pct'] != '0.0' else 0.0, reverse=True)
        return teams_list
    except Exception:
        return []

def render_moves_page(league, title):
    st.title(title)
    transactions = fetch_transactions(league)
    if not transactions:
        st.error("Roster feed currently unavailable.")
        return

    search_query = st.text_input("🔍 Filter by team name:", "").strip().lower()
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
        st.info("No transaction records match your filters.")

def render_wnba_standings():
    st.title("📊 WNBA Leaderboard")
    st.divider()
    
    teams = fetch_live_wnba_standings()
    if not teams:
        st.error("Leaderboard metrics currently unavailable.")
        return
        
    leaderboard_html = '<div style="max-width: 900px; margin-bottom: 30px;">'
    for idx, t in enumerate(teams, 1):
        leaderboard_html += f"""
        <div class="table-row">
            <div style="display: flex; align-items: center; gap: 16px;">
                <span style="width: 24px; color: #53565a; font-weight: 700;">{idx}</span>
                <span style="font-weight: 600; color: #ffffff; font-size: 15px;">{t['team']}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 24px;">
                <span class="sport-badge">{t['record']}</span>
                <span style="color: #888e96; min-width: 80px;">PCT: <strong style="color:#ffffff; font-family: monospace;">{t['pct']}</strong></span>
                <span style="color: #888e96; min-width: 60px;">GB: <strong style="color:#ffffff; font-family: monospace;">{t['gb']}</strong></span>
            </div>
        </div>
        """
    leaderboard_html += "</div>"
    st.html(leaderboard_html)
        
    st.subheader("🏆 Postseason Bracket")
    st.html(
        """
        <div style="
            filter: grayscale(100%); 
            opacity: 0.2; 
            pointer-events: none; 
            border: 1px solid #22252a; 
            padding: 24px; 
            border-radius: 8px;
            background-color: #121316;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: -apple-system, sans-serif;
        ">
            <div style="display: flex; flex-direction: column; gap: 16px; width: 28%;">
                <div style="background: #1c1d22; padding: 10px; border-radius: 6px; border-left: 3px solid #ff5500;">
                    <div style="font-size: 10px; color: #53565a; font-weight: 700;">MATCHUP 1</div>
                    <div style="font-size: 13px; color: #fff; font-weight: 600; margin-top: 2px;">#1 Seed</div>
                    <div style="font-size: 13px; color: #888e96;">#8 Seed</div>
                </div>
                <div style="background: #1c1d22; padding: 10px; border-radius: 6px; border-left: 3px solid #ff5500;">
                    <div style="font-size: 10px; color: #53565a; font-weight: 700;">MATCHUP 2</div>
                    <div style="font-size: 13px; color: #fff; font-weight: 600; margin-top: 2px;">#4 Seed</div>
                    <div style="font-size: 13px; color: #888e96;">#5 Seed</div>
                </div>
                <div style="background: #1c1d22; padding: 10px; border-radius: 6px; border-left: 3px solid #ff5500;">
                    <div style="font-size: 10px; color: #53565a; font-weight: 700;">MATCHUP 3</div>
                    <div style="font-size: 13px; color: #fff; font-weight: 600; margin-top: 2px;">#2 Seed</div>
                    <div style="font-size: 13px; color: #888e96;">#7 Seed</div>
                </div>
                <div style="background: #1c1d22; padding: 10px; border-radius: 6px; border-left: 3px solid #ff5500;">
                    <div style="font-size: 10px; color: #53565a; font-weight: 700;">MATCHUP 4</div>
                    <div style="font-size: 13px; color: #fff; font-weight: 600; margin-top: 2px;">#3 Seed</div>
                    <div style="font-size: 13px; color: #888e96;">#6 Seed</div>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 68px; width: 28%;">
                <div style="background: #1c1d22; padding: 10px; border-radius: 6px; border-left: 3px solid #ff5500;">
                    <div style="font-size: 10px; color: #53565a; font-weight: 700;">SEMIFINALS 1</div>
                    <div style="font-size: 13px; color: #444; font-style: italic; margin-top: 2px;">TBD</div>
                </div>
                <div style="background: #1c1d22; padding: 10px; border-radius: 6px; border-left: 3px solid #ff5500;">
                    <div style="font-size: 10px; color: #53565a; font-weight: 700;">SEMIFINALS 2</div>
                    <div style="font-size: 13px; color: #444; font-style: italic; margin-top: 2px;">TBD</div>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; width: 28%; align-items: center;">
                <div style="background: #1c1d22; padding: 16px; border-radius: 6px; border: 1px solid #ff5500; width: 100%; text-align: center;">
                    <div style="font-size: 11px; color: #ff5500; font-weight: 700; letter-spacing: 1px;">FINALS</div>
                    <div style="margin-top: 6px; font-size: 13px; color: #444; font-style: italic;">TBD</div>
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
            "You are Stan, a highly knowledgeable, tactical sports analyst. "
            "Provide intelligent, deeply analytical context on sports regulations, "
            "roster trends, and trade structures across professional sports. "
            "Maintain a professional, objective, and expert tone. Avoid broadcaster-style hype, "
            "exclamation marks, or generic sports catchphrases. Ensure exact precision with league names. "
            "CRITICAL: Your total response must be highly concise, direct, and under 50 words total."
        )
        
        messages = [{"role": "system", "content": system_instruction}]
        for role, text in st.session_state.chat_history:
            messages.append({"role": "user" if role == "user" else "assistant", "content": text})
        
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat_completion(
            messages=messages,
            max_tokens=100,
            temperature=0.4 # Dropped temperature slightly for cleaner, more predictable responses
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analytical feed connection offline. (Error: {str(e)})"

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
        
        # Cleaner, professional flat geometric badge icon
        st.sidebar.html(
            """
            <div style="display: flex; justify-content: center; margin-bottom: 15px;">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect width="24" height="24" rx="6" fill="#1a1c23"/>
                    <circle cx="12" cy="12" r="8" stroke="#ff5500" stroke-width="2"/>
                    <path d="M8 12H16M12 8V16" stroke="#ff5500" stroke-width="1" stroke-linecap="round"/>
                </svg>
            </div>
            """
        )
        
        st.sidebar.subheader("🤖 Ask Stan")
        st.sidebar.write("Query cross-league data trends, transaction contexts, or cap regulations:")
        
        with st.sidebar.form(key="chat_form", clear_on_submit=True):
            user_msg = st.text_input("Message Stan...", placeholder="Enter tactical inquiry...")
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
                        st.markdown(f"👤 **You:** {text}")
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
        st.info("NBA Standings database currently offline.")
    elif st.session_state.page == "nba_player_stats":
        st.info("NBA Statistics records currently offline.")
    elif st.session_state.page == "wnba_player_stats":
        st.info("WNBA Statistics records currently offline.")
    elif st.session_state.page == "nba_pbp":
        st.info("NBA Play-by-Play feed currently offline.")
    elif st.session_state.page == "wnba_pbp":
        st.info("WNBA Play-by-Play feed currently offline.")

if __name__ == "__main__":
    main()

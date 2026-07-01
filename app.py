import base64
import requests
import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Stan's Sports Stats", page_icon="🏀", layout="wide")

# Convert the micro-icon asset into a safe inline base64 string
def load_button_icon(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

icon_b64 = load_button_icon("ministan.png")

st.html(
    f"""
    <style>
        .stApp {{
            background: radial-gradient(circle at 50% 10%, #16181d 0%, #0b0c0e 100%) !important;
            color: #f1f3f5 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        
        [data-testid="stSidebar"] {{
            background-color: #0f1013 !important;
            border-right: 1px solid #1a1d24;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4);
        }}
        
        .sport-badge {{
            background: rgba(255, 85, 0, 0.08);
            border: 1px solid rgba(255, 85, 0, 0.4);
            padding: 6px 14px;
            border-radius: 4px;
            color: #ff5500;
            font-family: "SF Mono", "Roboto Mono", monospace;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 8px rgba(255, 85, 0, 0.1);
        }}
        
        .table-row {{
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 14px 20px; 
            border: 1px solid #1a1d24;
            background: linear-gradient(180deg, #13151a 0%, #0f1014 100%);
            margin-bottom: 8px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .table-row:hover {{
            background: linear-gradient(180deg, #171a21 0%, #12141a 100%);
            border-color: rgba(255, 85, 0, 0.3);
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
        }}
        
        /* Native centering rules for the explicit HTML button replacement */
        .native-stan-btn {{
            background: linear-gradient(135deg, #ff6611 0%, #d43d00 100%) !important;
            border: none !important;
            color: #ffffff !important;
            border-radius: 6px !important;
            font-weight: 700 !important;
            letter-spacing: 0.3px;
            box-shadow: 0 4px 12px rgba(212, 61, 0, 0.3) !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 10px !important;
            width: 100% !important;
            padding: 10px 14px !important;
            cursor: pointer !important;
            font-size: 14px !important;
        }}
        .native-stan-btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(212, 61, 0, 0.45) !important;
        }}
        
        .stButton > button {{
            border-radius: 6px !important;
            border-color: #262930 !important;
            background-color: #13151a !important;
        }}
        
        /* Hard-kill any lingering Streamlit image overlays or toolbar elements */
        button[title="View fullscreen"], 
        [data-testid="stImage"] button, 
        .stImage button,
        [data-testid="stSidebar"] button[title="View fullscreen"],
        [data-testid="stElementToolbar"] {{
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }}
        [data-testid="stImage"] img, .stImage img, [data-testid="stSidebar"] img {{
            cursor: default !important;
            pointer-events: none !important;
        }}
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
                
                for metric in stats_array:
                    metric_type = str(metric.get('type', '')).lower()
                    metric_name = str(metric.get('name', '')).lower()
                    metric_abbr = str(metric.get('abbreviation', '')).upper()
                    
                    if metric_type == 'overall' or metric_name == 'overall' or metric_abbr in ['W-L', 'REC']:
                        w_l_record = metric.get('displayValue', w_l_record)
                    elif metric_type == 'winpercent' or metric_name == 'winpercent' or metric_abbr == 'PCT':
                        win_pct = metric.get('value', win_pct)
                
                teams_list.append({
                    "team": team_name,
                    "record": w_l_record,
                    "pct": f"{win_pct:.3f}" if isinstance(win_pct, (int, float)) and win_pct <= 1 else str(win_pct)
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
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analytical feed connection offline. (Error: {str(e)})"

def main():
    st.sidebar.image("s3logo.png", use_container_width=True)
    
    if not st.session_state.ai_mode:
        # A fully custom native component layout that can never generate full-screen overlays
        btn_container = st.sidebar.empty()
        with btn_container:
            st.html(
                f"""
                <div class="native-stan-btn" onclick="window.parent.postMessage({{type: 'streamlit:set_component_value', value: 'launch_ai'}}, '*')">
                    <img src="data:image/png;base64,{icon_b64}" style="width: 20px; height: 20px; border-radius: 4px; pointer-events: none;">
                    <span>Ask Stan (AI)</span>
                </div>
                """
            )
        
        # A clean invisible state trigger hook to track framework events securely
        click_check = st.sidebar.toggle("Launch Hook", key="hidden_hook_trigger", label_visibility="collapsed")
        if click_check:
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
        
        st.sidebar.image(
            "stan.png", 
            use_container_width=True,
            output_format="PNG"
        )
        
        st.sidebar.subheader("Ask Stan")
        st.sidebar.write("Ask Stan about any sports news:")
        
        with st.sidebar.form(key="chat_form", clear_on_submit=True):
            user_msg = st.text_input("Message Stan...", placeholder="Type here...")
            submit_clicked = st.form_submit_button("Send", use_container_width=True)
            
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
                        st.html(
                            f'<div style="display: flex; gap: 8px; align-items: flex-start; margin-bottom: 4px;">'
                            f'<img src="data:image/png;base64,{icon_b64}" style="width: 20px; height: 20px; border-radius: 4px; flex-shrink: 0; margin-top: 2px;">'
                            f'<div><strong>Stan:</strong> {text}</div>'
                            f'</div>'
                        )
                    st.sidebar.divider()

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

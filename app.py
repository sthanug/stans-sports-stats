import base64
import requests
import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Stan's Sports Stats", page_icon="s3favicon.png", layout="wide")

def load_button_icon(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

icon_b64 = load_button_icon("ministan.png")

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
        team_name = "Unknown Team"
        logo_url = ""
        
        if isinstance(team_info, dict):
            team_name = team_info.get('displayName', 'Unknown Team')
            logos = team_info.get('logos', [])
            if logos and isinstance(logos, list):
                logo_url = logos[0].get('href', '')

        transactions.append({
            "Date": date,
            "Team": team_name,
            "Transaction": desc,
            "Logo": logo_url
        })
    return transactions

@st.cache_data(ttl=1800)
def fetch_live_standings(league):
    url = f"https://site.api.espn.com/apis/v2/sports/basketball/{league}/standings"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        teams_list = []
        for conference in data.get('children', []):
            conferences_or_divisions = conference.get('children', [conference])
            for group in conferences_or_divisions:
                for entry in group.get('standings', {}).get('entries', []):
                    team_info = entry.get('team', {})
                    team_name = team_info.get('displayName', 'Unknown Team')
                    team_id = team_info.get('id', '')
                    
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
                        "id": team_id,
                        "team": team_name,
                        "record": w_l_record,
                        "pct": f"{win_pct:.3f}" if isinstance(win_pct, (int, float)) and win_pct <= 1 else str(win_pct)
                    })
        
        unique_teams = {v['team']: v for v in teams_list}.values()
        sorted_teams = sorted(unique_teams, key=lambda x: float(x['pct']) if x['pct'] != '0.0' else 0.0, reverse=True)
        return list(sorted_teams)
    except Exception:
        return []

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
        
        h1, h2, h3, strong, a {{
            color: #ff5500 !important;
        }}
        
        .sport-badge {{
            background: rgba(255, 85, 0, 0.12);
            border: 1px solid #ff5500;
            padding: 6px 14px;
            border-radius: 4px;
            color: #ff5500;
            font-family: "SF Mono", "Roboto Mono", monospace;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 8px rgba(255, 85, 0, 0.2);
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
            border-color: #ff5500;
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(255, 85, 0, 0.15);
        }}
        
        .stButton > button, div.stButton > button[kind="primary"], .stButton > button[kind="secondary"] {{
            background: linear-gradient(135deg, #ff6611 0%, #d43d00 100%) !important;
            border: 1px solid #ff5500 !important;
            color: #ffffff !important;
            border-radius: 6px !important;
            box-shadow: 0 4px 12px rgba(212, 61, 0, 0.3) !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            height: 42px !important;
        }}
        
        div.stButton > button p, .stButton > button div, .stButton > button span {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 10px !important;
            width: 100% !important;
            font-weight: 700 !important;
            letter-spacing: 0.3px !important;
            text-align: center !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1 !important;
        }}
        
        div.stButton > button[kind="primary"] p::before {{
            content: "";
            background-image: url("data:image/png;base64,{icon_b64}");
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            width: 20px;
            height: 20px;
            display: inline-block;
            flex-shrink: 0;
            border-radius: 4px;
        }}
        
        .stButton > button:hover, div.stButton > button[kind="primary"]:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(212, 61, 0, 0.55) !important;
            border-color: #ffffff !important;
        }}
        
        .orange-info-message {{
            background: rgba(255, 85, 0, 0.05) !important;
            border: 1px solid #ff5500 !important;
            color: #f1f3f5 !important;
            border-radius: 6px !important;
            padding: 16px 20px !important;
            margin: 20px 0 !important;
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            font-weight: 500 !important;
            box-shadow: 0 4px 12px rgba(255, 85, 0, 0.05) !important;
        }}
        
        hr {{
            border-color: rgba(255, 85, 0, 0.3) !important;
        }}
        
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

def render_under_construction():
    st.html(
        """
        <div class="orange-info-message">
            <span>🚧 I'm still working on this page! 🚧</span>
        </div>
        """
    )

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
                if tx['Logo']:
                    st.html(
                        f"""
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                            <img src="{tx['Logo']}" style="width: 32px; height: 32px; object-fit: contain;">
                            <h3 style="margin: 0; color: #ff5500;">{tx['Team']}</h3>
                        </div>
                        """
                    )
                else:
                    st.subheader(tx['Team'])
                    
                st.caption(f"🗓️ {tx['Date']}")
                st.write(tx['Transaction'])
                st.divider()
    if not results_found:
        st.info("No transaction records match your filters.")

def render_standings_page(league, title):
    st.title(title)
    st.divider()
    
    teams = fetch_live_standings(league)
    if not teams:
        st.error("Leaderboard metrics currently unavailable.")
        return
        
    leaderboard_html = '<div style="max-width: 900px; margin-bottom: 30px;">'
    for idx, t in enumerate(teams, 1):
        if t['id']:
            logo_url = f"https://a.espncdn.com/i/teamlogos/basketball/nba/500/scoreboard/{t['id']}.png"
            logo_html = f'<img src="{logo_url}" style="width: 24px; height: 24px; object-fit: contain; flex-shrink: 0;">'
        else:
            logo_html = ''

        leaderboard_html += f"""
        <div class="table-row">
            <div style="display: flex; align-items: center; gap: 16px;">
                <span style="width: 24px; color: #ff5500; font-weight: 700;">{idx}</span>
                <div style="display: flex; align-items: center; gap: 10px;">
                    {logo_html}
                    <span style="font-weight: 600; color: #ffffff; font-size: 15px;">{t['team']}</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 24px;">
                <span class="sport-badge">{t['record']}</span>
                <span style="color: #888e96; min-width: 80px;">PCT: <strong style="color:#ff5500; font-family: monospace;">{t['pct']}</strong></span>
            </div>
        </div>
        """
    leaderboard_html += "</div>"
    st.html(leaderboard_html)

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
        if st.sidebar.button("Ask Stan (AI)", key="enter_ai_btn", use_container_width=True, type="primary"):
            st.session_state.ai_mode = True
            st.rerun()
            
        st.sidebar.divider()
        
        with st.sidebar.expander("🏀 Basketball", expanded=True):
            with st.expander("🇺🇸 NBA", expanded=st.session_state.page.startswith("nba_")):
                if st.button("📰 News", key="nba_news_btn", use_container_width=True):
                    st.session_state.page = "nba_news"
                if st.button("📊 Standings", key="nba_standings_btn", use_container_width=True):
                    st.session_state.page = "nba_standings"
                if st.button("🔄 Player Moves", key="nba_moves_btn", use_container_width=True):
                    st.session_state.page = "nba_player_moves"
                if st.button("📈 Player Stats", key="nba_stats_btn", use_container_width=True):
                    st.session_state.page = "nba_player_stats"
                if st.button("⏱️ Matches Play by Play", key="nba_pbp_btn", use_container_width=True):
                    st.session_state.page = "nba_pbp"
                    
            with st.expander("👩 WNBA", expanded=st.session_state.page.startswith("wnba_")):
                if st.button("📰 News", key="wnba_news_btn", use_container_width=True):
                    st.session_state.page = "wnba_news"
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
                            f'<div><strong style="color:#ff5500;">Stan:</strong> {text}</div>'
                            f'</div>'
                        )
                    st.sidebar.divider()

    if st.session_state.page == "nba_player_moves":
        render_moves_page("nba", "🔄 NBA Player Moves")
    elif st.session_state.page == "wnba_player_moves":
        render_moves_page("wnba", "🔄 WNBA Player Moves")
    elif st.session_state.page == "wnba_standings":
        render_standings_page("wnba", "📊 WNBA Leaderboard")
    elif st.session_state.page == "nba_standings":
        render_standings_page("nba", "📊 NBA Leaderboard")
    elif st.session_state.page in ["nba_news", "wnba_news", "nba_player_stats", "wnba_player_stats", "nba_pbp", "wnba_pbp"]:
        render_under_construction()

if __name__ == "__main__":
    main()

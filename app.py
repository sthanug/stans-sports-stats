import base64
import requests
import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="Stan's Sports Stats", page_icon="🏀", layout="wide")

# Convert the micro-icon asset into an un-fullscreenable base64 inline string string safely
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
        
        /* Flex alignment specifications to absolutely center button content elements */
        div.stButton > button[kind="primary"] {{
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
            text-align: center !important;
        }}
        div.stButton > button[kind="primary"]::before {{
            content: "";
            background-image: url("data:image/png;base64,{icon_b64}");
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            width: 20px;
            height: 20px;
            display: inline-block;
            flex-shrink: 0;
        }}
        div.stButton > button[kind="primary"]:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(212, 61, 0, 0.45) !important;
        }}
        .stButton > button {{
            border-radius: 6px !important;
            border-color: #262930 !important;
            background-color: #13151a !important;
        }}
        
        /* Strict global rules targeting and completely hiding fullscreen utilities and overlays */
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
            border: 1

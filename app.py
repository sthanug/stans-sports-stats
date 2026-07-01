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
def fetch_team_map(league):
    url = f"https://site.api.espn.com/apis/v2/sports/basketball/{league}/standings"
    team_map = {}
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        for conference in data.get('children', []):
            conferences_or_divisions = conference.get('children', [conference])
            for group in conferences_or_divisions:
                for entry in group.get('standings', {}).get('entries', []):
                    team_info = entry.get('team', {})
                    name = team_info.get('displayName', '')
                    short_name = team_info.get('shortDisplayName', '')
                    team_id = team_info.get('id', '')
                    if team_id:
                        if name:
                            team_map[name.lower().strip()] = team_id
                        if short_name:
                            team_map[short_name.lower().strip()] = team_id
    except Exception:
        pass
    return team_map

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
        
        unique_teams = {v['team']: v for v in teams

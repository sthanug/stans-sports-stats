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
                    team_id = team_info.get('id', '')
                    if name and team_id:
                        team_map[name.lower().strip()] = team_id
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

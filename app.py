import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Stan's Sports Stats", page_icon="🏀", layout="wide")
st.title("🏀 Stan's Sports Stats")

def get_nba_transactions():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/transactions"
    data = requests.get(url).json()
    
    transactions = []
    
    if 'transactions' in data:
        for item in data['transactions']:
            date = item.get('date', '')[:10] 
            desc = item.get('description', '')
            
            team = item.get('team', {})
            team_name = team.get('displayName', 'Unknown') if isinstance(team, dict) else 'Unknown'
            
            transactions.append({
                "Date": date,
                "Team": team_name,
                "Transaction": desc
            })
            
    return pd.DataFrame(transactions)

try:
    df = get_nba_transactions()
    
    search_query = st.text_input("🔍 Search Teams:")
    
    if search_query:
        df = df[df['Team'].str.contains(search_query, case=False, na=False)]
    
    st.dataframe(df, use_container_width=True, hide_index=True)

except Exception:
    st.error("Error fetching data.")

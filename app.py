import requests
import streamlit as st

st.set_page_config(page_title="Stan's Sports Stats", page_icon="🏀", layout="wide")

@st.cache_data(ttl=3600)
def fetch_nba_transactions():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/transactions?limit=1000"
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

def render_player_moves():
    st.title("🔄 Player Moves")
    
    transactions = fetch_nba_transactions()
    
    if not transactions:
        st.error("Hold up. Having trouble pulling data right now.")
        return

    search_query = st.text_input("🔍 Search Teams (e.g., Lakers, Knicks):", "").strip().lower()
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

def main():
    st.sidebar.title("Stan's Sports Stats")
    
    features = {
        "🔄 Player Moves": render_player_moves,
        "📊 Play-by-Play (Coming Soon)": lambda: st.info("🚧 Play-by-play engine coming soon."),
        "📈 Team Stats (Coming Soon)": lambda: st.info("🚧 Team statistics coming soon.")
    }
    
    selection = st.sidebar.selectbox("🏀 NBA Categories:", list(features.keys()))
    
    features[selection]()

if __name__ == "__main__":
    main()

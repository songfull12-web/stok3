import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="CANSLIM Scanner", layout="wide")
st.title("🚀 CANSLIM 퀀트 스캐너")

# 2. 분석 종목 리스트
tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'META', 'AMZN', 'NFLX', 'AMD', 'PYPL']

def get_data(symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.info
        hist = t.history(period="1y")
        if hist.empty: return None
        
        q_growth = info.get('earningsQuarterlyGrowth', 0)
        a_growth = info.get('earningsGrowth', 0)
        rs = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
        high_52w = hist['High'].max()
        curr = hist['Close'].iloc[-1]
        near_high = (curr / high_52w) * 100
        
        return {
            "Ticker": symbol, "Price": round(curr, 2),
            "Q Growth(%)": round(q_growth * 100, 2) if q_growth else 0,
            "A Growth(%)": round(a_growth * 100, 2) if a_growth else 0,
            "RS Score": round(rs, 2), "Near 52W(%)": round(near_high, 2)
        }
    except: return None

# 3. UI 구성
st.sidebar.header("Filter")
min_rs = st.sidebar.slider("Min RS Score", -50, 100, 10)

if st.button('Scan Start'):
    results = []
    bar = st.progress(0)
    for i, t in enumerate(tickers):
        d = get_data(t)
        if d: results.append(d)
        bar.progress((i + 1) / len(tickers))
    
    if results:
        df = pd.DataFrame(results)
        res = df[df['RS Score'] >= min_rs]
        st.dataframe(res.style.highlight_max(axis=0, subset=['RS Score'], color='lightgreen'))
    else:
        st.error("No Data")

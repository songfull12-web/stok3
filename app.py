import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="CANSLIM Quant Scanner", layout="wide")
st.title("🚀 CANSLIM 퀀트 스캐너")
st.write("Yahoo Finance 데이터를 활용한 실시간 퀀트 분석 도구입니다.")

# 2. 분석할 종목 리스트 (미국 주요 종목)
tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'META', 'AMZN', 'NFLX', 'AMD', 'PYPL']

def get_canslim_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        # 데이터 가져오기
        info = ticker.info
        hist = ticker.history(period="1y")

        if hist.empty:
            return None

        # C & A: 이익 성장률 (Quarterly & Annual)
        q_growth = info.get('earningsQuarterlyGrowth', 0)
        a_growth = info.get('earningsGrowth', 0)

        # L: Relative Strength (1년간 주가 상승률로 간이 계산)
        rs_score = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100

        # N: 52주 신고가 근접도
        high_52w = hist['High'].max()
        current_price = hist['Close'].iloc[-1]
        near_high = (current_price / high_52w) * 100

        return {
            "Ticker": ticker_symbol,
            "Price": round(current_price, 2),
            "Q Growth (%)": round(q_growth * 100, 2) if q_growth else 0,
            "A Growth (%)": round(a_growth * 100, 2) if a_growth else 0,
            "RS Score": round(rs_score, 2),
            "Near 52W High (%)": round(near_high, 2)
        }
    except Exception:
        return None

# 3. 사이드바 필터 설정
st.sidebar.header("📊 필터 설정")
min_rs = st.sidebar.slider("최소 RS 점수 (상승률)", -50, 100, 10)
min_high = st.sidebar.slider("52주 신고가 근접도 (%)", 50, 100, 85)

# 4. 실행 버튼 및 결과 표시
if st.button('스캔 시작'):
    results = []
    my_bar = st.progress(0)
    
    for i, t in enumerate(tickers):
        data = get_canslim_data(t)
        if data:
            results.append(data)
        my_bar.progress((i + 1) / len(tickers))

    if results:
        df = pd.DataFrame(results)
        # 필터 적용
        filtered_df = df[(df['RS Score'] >= min_rs) & (df['Near 52W High (%)'] >= min_high)]
        
        st.subheader("📋 분석 결과")
        if not filtered_df.empty:
            # RS Score 기준 강조 표시
            st.dataframe(filtered_df.style.highlight_max(axis=0, subset=['RS Score'], color='lightgreen'))
        else:
            st.warning("설정한 조건에 맞는 종목이 현재 없습니다. 필터를 조절해 보세요.")
    else:
        st.error("데이터를 가져오는 중에 문제가 발생했습니다.")

import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz
import json
import os

st.set_page_config(
    page_title="AlphaPulse HQ Pro AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. भारतीय समय (IST)
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)
current_hour = now_ist.hour
current_minute = now_ist.minute
time_str = now_ist.strftime("%d-%b-%Y | %I:%M:%S %p")

is_weekday = now_ist.weekday() < 5
is_live = is_weekday and ((current_hour == 9 and current_minute >= 15) or (10 <= current_hour < 15) or (current_hour == 15 and current_minute <= 30))

# 2. लाइव मार्केट डेटा फेच
@st.cache_data(ttl=60)
def get_data():
    tickers = {
        "NIFTY 50": "^NSEI",
        "INDIA VIX": "^INDIAVIX",
        "CRUDE OIL": "CL=F",
        "GOLD": "GC=F",
        "BITCOIN": "BTC-USD",
        "NASDAQ": "^IXIC"
    }
    res = {}
    for k, sym in tickers.items():
        try:
            h = yf.Ticker(sym).history(period="2d")
            if len(h) >= 2:
                c = h['Close'].iloc[-1]
                p = h['Close'].iloc[-2]
                res[k] = {"price": round(c, 2), "pct": round(((c - p)/p)*100, 2), "chg": round(c - p, 2)}
            elif len(h) == 1:
                res[k] = {"price": round(h['Close'].iloc[-1], 2), "pct": 0.0, "chg": 0.0}
            else:
                res[k] = {"price": 0.0, "pct": 0.0, "chg": 0.0}
        except:
            res[k] = {"price": 0.0, "pct": 0.0, "chg": 0.0}
    return res

mkt = get_data()

# डार्क प्रीमियम UI
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    .card { background-color: #161b22; border-radius: 8px; padding: 14px; border: 1px solid #30363d; margin-bottom: 8px; }
    .val-green { color: #00c087; font-weight: 700; }
    .val-red { color: #ff4d4f; font-weight: 700; }
    .status-badge { display: inline-block

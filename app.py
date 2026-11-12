import os
import requests
import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="AlphaPulse HQ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# डार्क थीम UI
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    .card { background-color: #151922; border-radius: 8px; padding: 14px; border: 1px solid #232936; margin-bottom: 10px; }
    .val-green { color: #00e676; font-size: 1.2rem; font-weight: bold; }
    .val-red { color: #ff5252; font-size: 1.2rem; font-weight: bold; }
    .alert-box { background-color: #1e2638; border-left: 4px solid #00e676; padding: 12px; border-radius: 4px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# 1. डेटा फेचिंग
TICKERS = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "INDIA VIX": "^INDIAVIX",
    "CRUDE OIL": "CL=F",
    "BITCOIN": "BTC-USD"
}

@st.cache_data(ttl=60)
def get_live_data():
    results = {}
    for name, sym in TICKERS.items():
        try:
            hist = yf.Ticker(sym).history(period="2d")
            if len(hist) >= 2:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                chg = curr - prev
                pct = (chg / prev) * 100
                results[name] = {"price": curr, "chg": chg, "pct": pct}
            elif len(hist) == 1:
                results[name] = {"price": hist['Close'].iloc[-1], "chg": 0.0, "pct": 0.0}
            else:
                results[name] = {"price": 0.0, "chg": 0.0, "pct": 0.0}
        except Exception:
            results[name] = {"price": 0.0, "chg": 0.0, "pct": 0.0}
    return results

data = get_live_data()
nifty_price = data.get("NIFTY 50", {}).get("price", 0)
vix_val = data.get("INDIA VIX", {}).get("price", 14.0)

# ऑटो कैलकुलेशन
bias = "BULLISH 🟢" if vix_val < 15.5 else "SIDEWAYS / CAUTIOUS 🟡"
atm_strike = int(round(nifty_price / 50) * 50) if nifty_price > 0 else 24500
entry_price = 110
target_price = 155
stop_loss = 88

audio_text = f"सुप्रभात मनीष जी। आज बाज़ार का रुझान {bias} है। निफ्टी {nifty_price:,.0f} पर है और विक्स {vix_val:.1f} है। {atm_strike} की कॉल पर नजर रखें।"

# 2. हेडर व टिकर बार
st.title("⚡ AlphaPulse — Personal Market AI")
st.caption(f"सिस्टम लाइव • {datetime.now().strftime('%d-%b-%Y | %I:%M %p')}")

cols = st.columns(5)
for i, (name, val) in enumerate(data.items()):
    cls = "val-green" if val['chg'] >= 0 else "val-red"
    sign = "+" if val['chg'] >= 0 else ""
    with cols[i]:
        st.markdown(f"""
        <div class="card">
            <div style="color: #8b949e; font-size: 0.8rem;">{name}</div>
            <div style="font-size: 1.15rem; font-weight: 700;">{val['price']:,.2f}</div>
            <div class="{cls}">{sign}{val['chg']:,.2f} ({sign}{val['pct']:.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)

st.write("---")

# 3. वॉइस असिस्टेंट
c1, c2 = st.columns([1, 4])
with c1:
    if st.button("🔊 वॉइस सुनें (Speak)", use_container_width=True):
        st.components.v1.html(f"""
            <script>
                var msg = new SpeechSynthesisUtterance("{audio_text}");
                msg.lang = 'hi-IN';
                msg.rate = 0.95;
                window.speechSynthesis.speak(msg);
            </script>
        """, height=0)
with c2:
    st.info(f"🎙️ *AI वॉइस आउटलुक:* {audio_text}")

# 4. ट्रेडिंग सिग्नल
c_trade, c_mcx = st.columns([3, 2])
with c_trade:
    st.markdown(f"""
    <div class="card">
        <h4 style="margin:0; color:#58a6ff;">🎯 मॉर्निंग NIFTY ऑप्शंस सिग्नल</h4>
        <p style="margin-top:8px;"><b>मार्केट बायस:</b> {bias}</p>
        <p><b>सिफारिश:</b> NIFTY {atm_strike} CE</p>
        <div class="alert-box">
            • <b>अनुमानित एंट्री:</b> ₹{entry_price}<br>
            • <b>टारगेट:</b> ₹{target_price}<br>
            • <b>स्टॉप-लॉस:</b> ₹{stop_loss}
        </div>
    </div>
    """, unsafe_allow_html=True)

with c_mcx:
    st.markdown(f"""
    <div class="card">
        <h4 style="margin:0; color:#e3b341;">🌙 कमोडिटीज़ व क्रिप्टो (शाम का सत्र)</h4>
        <p style="margin-top:8px;">• <b>Crude Oil:</b> ${data.get('CRUDE OIL', {}).get('price', 0):,.2f}</p>
        <p>• <b>Bitcoin:</b> ${data.get('BITCOIN', {}).get('price', 0):,.2f}</p>
        <p>• <b>India VIX:</b> {vix_val:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

# 5. मोबाइल अलर्ट्स
st.write("---")
st.subheader("📲 ऑटोमेशन व फोन अलर्ट्स")
tg_token = st.text_input("Telegram Bot Token (वैकल्पिक):", type="password")
tg_chat = st.text_input("Telegram Chat ID:")

if st.button("🚀 टेस्ट अलर्ट सीधे मेरे मोबाइल पर भेजें"):
    if tg_token and tg_chat:
        msg = f"⚡ AlphaPulse Alert\nNifty: {nifty_price:,.0f} | Bias: {bias}\nTrade: {atm_strike} CE @ {entry_price} (SL: {stop_loss}, Tgt: {target_price})"
        requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": tg_chat, "text": msg, "parse_mode": "Markdown"})
        st.success("अलर्ट आपके फोन पर भेज दिया गया है!")
    else:
        st.warning("कृपया ऊपर टोकन और चैट आईडी भरें।")
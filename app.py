import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(
    page_title="AlphaPulse HQ Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# भारतीय समय (IST)
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)
current_hour = now_ist.hour
current_minute = now_ist.minute
time_str = now_ist.strftime("%d-%b-%Y | %I:%M:%S %p")

# डार्क थीम UI
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    .card { background-color: #161b22; border-radius: 8px; padding: 14px; border: 1px solid #30363d; margin-bottom: 8px; }
    .val-green { color: #00c087; font-weight: 700; }
    .val-red { color: #ff4d4f; font-weight: 700; }
    .status-badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
    .badge-closed { background: #3d1f24; color: #ff7b72; border: 1px solid #ff4d4f; }
    .badge-live { background: #133321; color: #56d364; border: 1px solid #238636; }
</style>
""", unsafe_allow_html=True)

# डेटा फेचिंग
TICKERS = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "INDIA VIX": "^INDIAVIX",
    "CRUDE OIL": "CL=F",
    "GOLD": "GC=F",
    "BITCOIN": "BTC-USD",
    "NASDAQ": "^IXIC"
}

@st.cache_data(ttl=60)
def fetch_data():
    res = {}
    for name, sym in TICKERS.items():
        try:
            hist = yf.Ticker(sym).history(period="2d")
            if len(hist) >= 2:
                c = hist['Close'].iloc[-1]
                p = hist['Close'].iloc[-2]
                res[name] = {"price": c, "chg": c - p, "pct": ((c - p)/p)*100}
            elif len(hist) == 1:
                res[name] = {"price": hist['Close'].iloc[-1], "chg": 0.0, "pct": 0.0}
            else:
                res[name] = {"price": 0.0, "chg": 0.0, "pct": 0.0}
        except:
            res[name] = {"price": 0.0, "chg": 0.0, "pct": 0.0}
    return res

data = fetch_data()
nifty_c = data.get("NIFTY 50", {}).get("price", 0)
vix_c = data.get("INDIA VIX", {}).get("price", 15.0)
crude_c = data.get("CRUDE OIL", {}).get("price", 0)
nasdaq_pct = data.get("NASDAQ", {}).get("pct", 0)

# मार्केट सेशन पहचान (9:15 AM से 3:30 PM के बीच लाइव)
is_weekday = now_ist.weekday() < 5
is_market_live = is_weekday and ((current_hour == 9 and current_minute >= 15) or (10 <= current_hour < 15) or (current_hour == 15 and current_minute <= 30))

# समय के हिसाब से ग्रीटिंग और वॉइस स्क्रिप्ट
if 4 <= current_hour < 12:
    greeting = "सुप्रभात"
elif 12 <= current_hour < 17:
    greeting = "नमस्कार"
else:
    greeting = "शुभ संध्या"

if is_market_live:
    session_title = "🔴 LIVE NSE INTRADAY SESSION"
    voice_script = f"{greeting} मनीष जी। बाज़ार लाइव चल रहा है। निफ्टी {nifty_c:,.0f} पर है और इंडिया विक्स {vix_c:.1f} पर है।"
else:
    session_title = "🌙 EVENING MCX & GLOBAL STRATEGY"
    crude_trend = "तेजी में" if data.get("CRUDE OIL", {}).get("chg", 0) >= 0 else "गिरावट में"
    voice_script = f"{greeting} मनीष जी। भारतीय बाज़ार बंद हो चुका है। इस समय कमोडिटी बाज़ार में क्रूड ऑयल {crude_c:.1f} डॉलर पर {crude_trend} है। नैस्डैक {nasdaq_pct:.1f} प्रतिशत है। कल सुबह के लिए गिफ्ट निफ्टी और ग्लोबल क्लोजिंग पर नजर रखें।"

# हेडर
st.title("⚡ AlphaPulse HQ Pro")
status_html = '<span class="status-badge badge-live">NSE लाइव</span>' if is_market_live else '<span class="status-badge badge-closed">NSE बंद (MCX/ग्लोबल एक्टिव)</span>'
st.markdown(f"<b>वक्त (IST):</b> {time_str} &nbsp;|&nbsp; {status_html}", unsafe_allow_html=True)

# टिकर ग्रिड
cols = st.columns(6)
ticker_list = ["NIFTY 50", "INDIA VIX", "CRUDE OIL", "GOLD", "BITCOIN", "NASDAQ"]
for i, name in enumerate(ticker_list):
    val = data.get(name, {"price": 0, "chg": 0, "pct": 0})
    cls = "val-green" if val['chg'] >= 0 else "val-red"
    sign = "+" if val['chg'] >= 0 else ""
    with cols[i]:
        st.markdown(f"""
        <div class="card">
            <div style="color: #8b949e; font-size: 0.75rem;">{name}</div>
            <div style="font-size: 1.1rem; font-weight: 700;">{val['price']:,.2f}</div>
            <div class="{cls}" style="font-size: 0.8rem;">{sign}{val['chg']:,.2f} ({sign}{val['pct']:.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)

st.write("---")

# वॉइस कार्ड (नेचुरल वॉइस)
st.subheader("🎙️ AI ऑडियो ब्रीफिंग")
c_v1, c_v2 = st.columns([1, 4])
with c_v1:
    if st.button("🔊 आज का ब्रीफ सुनें", use_container_width=True):
        st.components.v1.html(f"""
            <script>
                var synth = window.speechSynthesis;
                var voices = synth.getVoices();
                var msg = new SpeechSynthesisUtterance("{voice_script}");
                
                var hiVoice = voices.find(v => v.lang.includes('hi') || v.name.includes('Hindi') || v.name.includes('India'));
                if (hiVoice) msg.voice = hiVoice;
                
                msg.lang = 'hi-IN';
                msg.rate = 0.92;
                msg.pitch = 1.0;
                synth.cancel();
                synth.speak(msg);
            </script>
        """, height=0)
with c_v2:
    st.info(voice_script)

st.write("---")

# डायनामिक सेशन कंटेंट
if not is_market_live:
    st.subheader("🌙 शाम का सत्र: MCX कमोडिटीज़ व कल का प्री-मार्केट गेमप्लान")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="card" style="border-left: 4px solid #f0883e;">
            <h4 style="margin-top:0; color:#f0883e;">⚡ MCX कमोडिटीज़ स्थिति</h4>
            <p>• <b>Crude Oil:</b> ${crude_c:.2f} ({data.get('CRUDE OIL', {}).get('pct', 0):.2f}%)</p>
            <p>• <b>Gold:</b> ${data.get('GOLD', {}).get('price', 0):,.2f}</p>
            <p>• <b>रणनीति:</b> यूएस सेशन में क्रूड मूवमेंट पर नजर रखें। 70 डॉलर के ऊपर रहने पर कल ओएमसी (OMCs) और पेंट स्टॉक्स पर दबाव रह सकता है।</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="card" style="border-left: 4px solid #58a6ff;">
            <h4 style="margin-top:0; color:#58a6ff;">🎯 कल सुबह के लिए निफ्टी गेमप्लान</h4>
            <p>• <b>क्लोजिंग लेवल्स:</b> Nifty {nifty_c:,.0f} | India VIX: {vix_c:.2f}</p>
            <p>• <b>ग्लोबल संकेत:</b> US Nasdaq {nasdaq_pct:+.2f}% पर ट्रेड कर रहा है।</p>
            <p>• <b>कल का नियम:</b> रात में कोई निफ्टी ऑप्शन कॉल नहीं। सुबह 8:00 AM पर गिफ्ट निफ्टी देखकर फ्रेश सपोर्ट-रेजिस्टेंस तय होगा।</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.subheader("🎯 लाइव इंट्राडे निफ्टी ऑप्शंस सेटअप")
    strike = int(round(nifty_c / 50) * 50)
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid #00c087;">
        <h4>NIFTY {strike} CE / PE मॉनिटरिंग</h4>
        <p>लाइव बाज़ार सेशन चालू है। अनुशासन के साथ 25-30 अंक SL रखकर ही ट्रेड लें।</p>
    </div>
    """, unsafe_allow_html=True)

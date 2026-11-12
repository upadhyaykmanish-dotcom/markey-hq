mport streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
import json
import os
from google import genai

# API Key
GEMINI_KEY = "AQ.Ab8RN6KOv3QD2n7-ptoxMq5Dgbo753X3uc9eeVO1qzLJkg2Brg"

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

# 2. सेल्फ-लर्निंग मेमोरी सिस्टम
MEMORY_FILE = "user_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"rules": ["कैलकुलेटेड रिस्क मैनेजमेंट 1:2 रखें", "रात में नो ऑप्शन ट्रेड"], "notes": []}

def save_memory(mem):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

user_memory = load_memory()

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

# 3. मार्केट डेटा
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
gold_c = data.get("GOLD", {}).get("price", 0)
nasdaq_pct = data.get("NASDAQ", {}).get("pct", 0)

is_weekday = now_ist.weekday() < 5
is_market_live = is_weekday and ((current_hour == 9 and current_minute >= 15) or (10 <= current_hour < 15) or (current_hour == 15 and current_minute <= 30))

# हेडर
st.title("⚡ AlphaPulse HQ Pro — AI Terminal")
status_html = '<span class="status-badge badge-live">NSE लाइव</span>' if is_market_live else '<span class="status-badge badge-closed">NSE बंद (MCX/ग्लोबल एक्टिव)</span>'
st.markdown(f"<b>वक्त (IST):</b> {time_str} &nbsp;|&nbsp; {status_html}", unsafe_allow_html=True)

# टिकर ग्रिड
cols = st.columns(6)
for i, name in enumerate(["NIFTY 50", "INDIA VIX", "CRUDE OIL", "GOLD", "BITCOIN", "NASDAQ"]):
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

# 4. शाम का सत्र व कल का प्री-मार्केट गेमप्लान
if not is_market_live:
    st.subheader("🌙 शाम का सत्र: MCX कमोडिटीज़ व कल का प्री-मार्केट गेमप्लान")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="card" style="border-left: 4px solid #f0883e;">
            <h4 style="margin-top:0; color:#f0883e;">⚡ MCX कमोडिटीज़ स्थिति</h4>
            <p>• <b>Crude Oil:</b> ${crude_c:.2f} ({data.get('CRUDE OIL', {}).get('pct', 0):+.2f}%)</p>
            <p>• <b>Gold:</b> ${gold_c:,.2f} ({data.get('GOLD', {}).get('pct', 0):+.2f}%)</p>
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

st.write("---")

# 5. फुल-स्क्रीन वॉइस व चैट इंटरफ़ेस
st.subheader("🎙️ AI वॉइस टर्मिनल से बातचीत")

user_query = st.chat_input("यहाँ पूछें या फोन के माइक से बोलें (उदा: 'क्रूड का क्या हाल है?' या 'नियम याद रखो: 1:3 रिस्क')")

if user_query:
    with st.spinner("AI डेटा प्रोसेस कर रहा है..."):
        try:
            client = genai.Client(api_key=GEMINI_KEY)
            sys_context = f"""
            आप मनीष जी के पर्सनल सीनियर मार्केट AI रणनीतिकार हैं।
            वर्तमान समय (IST): {time_str}
            मार्केट स्थिति: {'NSE लाइव' if is_market_live else 'NSE बंद, MCX और यूएस लाइव'}
            लाइव भाव: Nifty={nifty_c:.0f}, India VIX={vix_c:.2f}, Crude Oil=${crude_c:.2f}, Gold=${gold_c:.2f}, Nasdaq={nasdaq_pct:.2f}%
            मनीष जी की सेव की गई मेमोरी/रूल्स: {user_memory['rules']}
            
            नियम:
            1. सीधे, सटीक और प्राकृतिक हिंदी में बात करें।
            2. अगर मनीष जी कोई नया नियम बताएं, तो कहें 'मनीष जी, मैंने यह नियम अपनी मेमोरी में जोड़ लिया है'।
            3. रात के समय ऑप्शंस ट्रेडिंग न करने की सलाह पर अडिग रहें।
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[sys_context, f"मनीष जी का सवाल: {user_query}"]
            )
            ai_reply = response.text
            
            if any(k in user_query for k in ["याद", "नियम", "सेव", "जोड़ो", "नोट"]):
                user_memory["rules"].append(user_query)
                save_memory(user_memory)
            
            st.markdown(f"*🤖 AI:* {ai_reply}")
            
            # ऑटोमैटिक हिंदी ऑडियो
            cleaned_audio = ai_reply.replace('"', '').replace("'", "").replace('\n', ' ')
            st.components.v1.html(f"""
                <script>
                    var synth = window.speechSynthesis;
                    var voices = synth.getVoices();
                    var msg = new SpeechSynthesisUtterance("{cleaned_audio[:350]}");
                    var hiVoice = voices.find(v => v.lang.includes('hi') || v.name.includes('Hindi') || v.name.includes('India'));
                    if (hiVoice) msg.voice = hiVoice;
                    msg.lang = 'hi-IN';
                    msg.rate = 0.95;
                    synth.cancel();
                    synth.speak(msg);
                </script>
            """, height=0)
        except Exception as e:
            st.error(f"एरर आया: {e}")

with st.expander("🧠 AI द्वारा याद रखे गए आपके नियम (Memory Log)"):
    for r in user_memory["rules"]:
        st.write(f"• {r}")

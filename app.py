import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

st.set_page_config(
    page_title="AlphaPulse HQ Pro — Trading Terminal",
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

# 2. लाइव मार्केट डेटा
@st.cache_data(ttl=60)
def fetch_market():
    tickers = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "INDIA VIX": "^INDIAVIX",
        "CRUDE OIL": "CL=F",
        "GOLD": "GC=F",
        "NASDAQ": "^IXIC"
    }
    out = {}
    for name, sym in tickers.items():
        try:
            h = yf.Ticker(sym).history(period="5d")
            if len(h) >= 2:
                c = h['Close'].iloc[-1]
                p = h['Close'].iloc[-2]
                hi = h['High'].iloc[-1]
                lo = h['Low'].iloc[-1]
                out[name] = {"price": round(c, 2), "pct": round(((c - p)/p)*100, 2), "high": round(hi, 2), "low": round(lo, 2)}
            else:
                out[name] = {"price": 0.0, "pct": 0.0, "high": 0.0, "low": 0.0}
        except:
            out[name] = {"price": 0.0, "pct": 0.0, "high": 0.0, "low": 0.0}
    return out

mkt = fetch_market()
nifty_c = mkt.get("NIFTY 50", {}).get("price", 24000.0)
vix_c = mkt.get("INDIA VIX", {}).get("price", 15.0)
crude_c = mkt.get("CRUDE OIL", {}).get("price", 70.0)
gold_c = mkt.get("GOLD", {}).get("price", 2600.0)
nasdaq_pct = mkt.get("NASDAQ", {}).get("pct", 0.0)

# 3. स्वचालित स्ट्राइक व लेवल कैलकुलेटर (पिवट / रेंज ब्रेकआउट मैथ)
atm_strike = int(round(nifty_c / 50.0) * 50)
call_strike = atm_strike
put_strike = atm_strike

# लेवल्स
buy_above = round(nifty_c + 45, 0)
buy_target = round(buy_above + 70, 0)
buy_sl = round(buy_above - 30, 0)

sell_below = round(nifty_c - 45, 0)
sell_target = round(sell_below - 70, 0)
sell_sl = round(sell_below + 30, 0)

# हेडर UI
st.title("⚡ AlphaPulse HQ Pro — मार्केट व ऑप्शंस टर्मिनल")
status_badge = "🟢 लाइव ट्रेडिंग सेशन" if is_live else "🌙 प्री-मार्केट व कमोडिटी सत्र"
st.caption(f"वक्त (IST): {time_str} | स्थिति: {status_badge}")

# टिकर ग्रिड
c1, c2, c3, c4, c5, c6 = st.columns(6)
tickers_list = ["NIFTY 50", "BANK NIFTY", "INDIA VIX", "CRUDE OIL", "GOLD", "NASDAQ"]
cols = [c1, c2, c3, c4, c5, c6]

for i, t in enumerate(tickers_list):
    val = mkt.get(t, {"price": 0, "pct": 0})
    cols[i].metric(t, f"{val['price']:,}", f"{val['pct']:+}%")

st.divider()

# 4. कल सुबह का निफ्टी ऑप्शंस एक्शन प्लान (स्ट्राइक व स्तर)
st.subheader("🎯 कल सुबह के लिए निफ्टी ट्रेडिंग लेवल्स व स्ट्राइक प्राइस")

col_left, col_right = st.columns(2)

with col_left:
    st.success(f"""
    ### 🟢 बुलिश सेटअप (कॉल / CE साइड)
    * *फोकस स्ट्राइक:* *NIFTY {call_strike} CE*
    * *एंट्री कंडीशन:* निफ्टी *{buy_above}* के ऊपर 5 मिनट की कैंडल क्लोज करे
    * *टारगेट:* *{buy_target}*
    * *स्टॉप लॉस:* *{buy_sl}* (कड़ा 30 अंक का SL)
    * *रिस्क-रिवॉर्ड:* 1:2.3
    """)

with col_right:
    st.error(f"""
    ### 🔴 बियरिश सेटअप (पुट / PE साइड)
    * *फोकस स्ट्राइक:* *NIFTY {put_strike} PE*
    * *एंट्री कंडीशन:* निफ्टी *{sell_below}* के नीचे 5 मिनट की कैंडल क्लोज करे
    * *टारगेट:* *{sell_target}*
    * *स्टॉप लॉस:* *{sell_sl}* (कड़ा 30 अंक का SL)
    * *रिस्क-रिवॉर्ड:* 1:2.3
    """)

st.divider()

# 5. ग्लोबल संकेत व कमोडिटी समीकरण
st.subheader("🌐 ग्लोबल संकेत व कमोडिटी आउटलुक")
g1, g2 = st.columns(2)
with g1:
    st.info(f"""
    *कच्चा तेल (Crude Oil) & गोल्ड:*
    * Crude Oil: *${crude_c}* | Gold: *${gold_c}*
    * *ट्रेड प्रभाव:* क्रूड यदि 70 डॉलर के ऊपर टिकता है, तो कल ऑयल मार्केटिंग (BPCL, IOC, HPCL) और एशियन पेंट्स जैसे शेयरों पर बिकवाली दबाव रह सकता है।
    """)
with g2:
    st.warning(f"""
    *विक्स (India VIX) & ओवरनाइट रणनीति:*
    * India VIX: *{vix_c}* | US Nasdaq: *{nasdaq_pct:+}%*
    * *नियम:* रात में किसी भी प्रकार का अनहेज्ड निफ्टी ऑप्शन न रखें। सुबह 8:00 AM पर गिफ्ट निफ्टी का गैप-अप या गैप-डाउन देखकर ही पहली 15 मिनट की रेंज मार्क करें।
    """)

st.divider()

# 6. इंटरैक्टिव वॉयस असिस्टेंट (सीधे इनबिल्ट Python + ब्राउज़र ऑडियो, बिना किसी Gemini API के)
st.subheader("🎙️ लाइव वॉइस असिस्टेंट")

voice_data_summary = (
    f"मनीष जी, निफ्टी का क्लोजिंग स्तर {nifty_c} है। "
    f"कल के लिए बुलिश कॉल एंट्री {buy_above} के ऊपर बनेगी जिसमें स्ट्राइक प्राइस {call_strike} कॉल रहेगी। "
    f"बियरिश पुट एंट्री {sell_below} के नीचे बनेगी जिसमें स्ट्राइक प्राइस {put_strike} पुट रहेगी। "
    f"स्टॉपलॉस 30 अंक का रहेगा। क्रूड ऑयल {crude_c} डॉलर पर है।"
)

st.components.v1.html(f"""
<div style="background:#161b22; padding:18px; border-radius:10px; border:1px solid #30363d; display:flex; align-items:center; justify-content:space-between;">
    <div>
        <div style="color:#ffffff; font-size:1.1rem; font-weight:600; font-family:sans-serif;">ट्रेडिंग लेवल्स व स्ट्राइक ऑडियो में सुनें</div>
        <div style="color:#8b949e; font-size:0.9rem; font-family:sans-serif; margin-top:4px;">बटन दबाते ही असिस्टेंट पूरा गेमप्लान बोलकर सुनाएगा।</div>
    </div>
    <button onclick="playAudioPlan()" style="background:#238636; color:#ffffff; border:none; padding:12px 24px; border-radius:6px; font-size:1rem; font-weight:600; cursor:pointer;">
        🔊 लेवल्स बोलकर सुनाओ
    </button>
</div>

<script>
function playAudioPlan() {{
    window.speechSynthesis.cancel();
    const msg = new SpeechSynthesisUtterance("{voice_data_summary}");
    msg.lang = 'hi-IN';
    msg.rate = 0.95;
    window.speechSynthesis.speak(msg);
}}
</script>
""", height=100)

with st.expander("🧠 ट्रेडिंग अनुशासन नियम (Memory Rules)"):
    st.write("1. हमेशा 1:2 रिस्क-रिवॉर्ड का सख्ती से पालन करें।")
    st.write("2. बिना स्टॉपलॉस कोई ऑप्शन ट्रेड नहीं।")
    st.write("3. 9:15 AM से 9:30 AM के बीच केवल बाज़ार की पहली कैंडल का हाई-लो ऑब्जर्व करें।")

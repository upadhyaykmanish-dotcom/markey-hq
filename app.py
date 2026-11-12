import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

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

# हेडर
st.title("⚡ AlphaPulse HQ Pro — AI Market Terminal")
status_label = "🟢 NSE लाइव" if is_live else "🔴 NSE बंद (MCX/ग्लोबल एक्टिव)"
st.caption(f"वक्त (IST): {time_str} | {status_label}")

# टिकर ग्रिड (6 कार्ड्स)
cols = st.columns(6)
for i, name in enumerate(["NIFTY 50", "INDIA VIX", "CRUDE OIL", "GOLD", "BITCOIN", "NASDAQ"]):
    val = mkt.get(name, {"price": 0, "chg": 0, "pct": 0})
    sign = "+" if val['chg'] >= 0 else ""
    with cols[i]:
        st.metric(label=name, value=f"{val['price']:,.2f}", delta=f"{sign}{val['chg']:,.2f} ({sign}{val['pct']}%)")

st.divider()

# 3. शाम का सत्र व कल का प्री-मार्केट गेमप्लान
nifty_c = mkt.get("NIFTY 50", {}).get("price", 0)
vix_c = mkt.get("INDIA VIX", {}).get("price", 0)
crude_c = mkt.get("CRUDE OIL", {}).get("price", 0)
gold_c = mkt.get("GOLD", {}).get("price", 0)
nasdaq_pct = mkt.get("NASDAQ", {}).get("pct", 0)

if not is_live:
    st.subheader("🌙 शाम का सत्र: MCX कमोडिटीज़ व कल का प्री-मार्केट गेमप्लान")
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"""
        *⚡ MCX कमोडिटीज़ स्थिति*
        * Crude Oil: ${crude_c:,.2f} ({mkt.get('CRUDE OIL', {}).get('pct', 0):+.2f}%)
        * Gold: ${gold_c:,.2f} ({mkt.get('GOLD', {}).get('pct', 0):+.2f}%)
        * रणनीति: 70 डॉलर के ऊपर क्रूड रहने पर कल पेंट और ओएमसी स्टॉक्स पर दबाव रह सकता है।
        """)
    with c2:
        st.success(f"""
        *🎯 कल सुबह के लिए निफ्टी गेमप्लान*
        * क्लोजिंग लेवल्स: Nifty {nifty_c:,.0f} | India VIX: {vix_c:.2f}
        * ग्लोबल संकेत: US Nasdaq {nasdaq_pct:+.2f}% पर ट्रेड कर रहा है।
        * कल का नियम: रात में कोई ओवरनाइट ऑप्शन कॉल नहीं। सुबह 8:00 AM पर गिफ्ट निफ्टी देखकर फ्रेश सपोर्ट-रेजिस्टेंस तय होगा।
        """)
else:
    strike = int(round(nifty_c / 50) * 50)
    st.info(f"🎯 लाइव इंट्राडे निफ्टी {strike} CE / PE मॉनिटरिंग चालू है। अनुशासन के साथ 25-30 अंक SL रखकर ही ट्रेड लें।")

st.divider()

# 4. इंटरैक्टिव नेचुरल वॉयस टर्मिनल
st.subheader("🎙️ Gemini AI नेचुरल वॉइस असिस्टेंट")

voice_app_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        margin: 0;
        background: transparent;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #ffffff;
    }}
    .terminal-box {{
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    .mic-btn {{
        background: #238636;
        color: #ffffff;
        border: none;
        border-radius: 50px;
        padding: 12px 22px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: 0.2s;
    }}
    .mic-btn.active {{
        background: #da3633;
    }}
    .status-text {{
        font-size: 0.95rem;
        color: #8b949e;
    }}
    .output-area {{
        margin-top: 14px;
        padding: 14px;
        background: #0d1117;
        border-radius: 8px;
        border: 1px solid #21262d;
    }}
    .user-q {{ color: #58a6ff; font-weight: 600; margin-bottom: 6px; }}
    .ai-ans {{ color: #3fb950; font-size: 1.05rem; line-height: 1.5; }}
</style>
</head>
<body>

<div class="terminal-box">
    <button class="mic-btn" id="btnTalk" onclick="startTalk()">🎙️ बोलकर पूछें</button>
    <div class="status-text" id="statusMsg">बटन दबाएँ और बोलें (उदा: "क्रूड का क्या हाल है?" या "कल निफ्टी कैसा रहेगा?")</div>
</div>

<div class="output-area" id="outputBox" style="display:none;">
    <div class="user-q" id="userQuery"></div>
    <div class="ai-ans" id="aiResponse"></div>
</div>

<script>
    const btn = document.getElementById('btnTalk');
    const statusMsg = document.getElementById('statusMsg');
    const outputBox = document.getElementById('outputBox');
    const userQuery = document.getElementById('userQuery');
    const aiResponse = document.getElementById('aiResponse');

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    let rec = null;
    const synth = window.speechSynthesis;

    function speakGemini(text) {{
        synth.cancel();
        const msg = new SpeechSynthesisUtterance(text);
        msg.lang = 'hi-IN';
        msg.rate = 1.0;
        msg.pitch = 1.0;

        const voices = synth.getVoices();
        const preferred = voices.find(v => (v.lang === 'hi-IN' || v.lang.startsWith('hi')) && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('India')));
        if (preferred) msg.voice = preferred;

        msg.onend = function() {{
            btn.classList.remove('active');
            btn.innerHTML = "🎙️ बोलकर पूछें";
            statusMsg.innerText = "अगला सवाल पूछने के लिए बटन दबाएँ";
        }};

        synth.speak(msg);
    }}

    function getInsight(q) {{
        const text = q.toLowerCase();
        if (text.includes("क्रूड") || text.includes("crude") || text.includes("तेल")) {{
            return "मनीष जी, कच्चा तेल वर्तमान में {crude_c} डॉलर पर चल रहा है। यदि यह 70 डॉलर के ऊपर बना रहता है, तो कल पेंट और पेट्रोलियम विपणन कंपनियों के शेयरों पर कुछ दबाव देखने को मिल सकता है।";
        }} else if (text.includes("गोल्ड") || text.includes("सोना") || text.includes("gold")) {{
            return "गोल्ड {gold_c} डॉलर के स्तर पर ट्रेड कर रहा है। इसमें अंतरराष्ट्रीय दरों के कारण मामूली उतार-चढ़ाव जारी है।";
        }} else if (text.includes("निफ्टी") || text.includes("nifty") || text.includes("कल")) {{
            return "निफ्टी आज {nifty_c} पर बंद हुआ है और इंडिया विक्स {vix_c} है। रात के समय किसी भी प्रकार का ओवरनाइट ऑप्शन ट्रेड न रखें। कल सुबह 8:00 बजे गिफ्ट निफ्टी का रुख देखकर ही सही स्तर तय करेंगे।";
        }} else if (text.includes("विक्स") || text.includes("vix")) {{
            return "इंडिया विक्स {vix_c} पर है, जो सामान्य और स्थिर वोलैटिलिटी का संकेत दे रहा है।";
        }} else {{
            return "मनीष जी, वर्तमान में निफ्टी {nifty_c}, क्रूड {crude_c} डॉलर और गोल्ड {gold_c} डॉलर पर है। अपनी पूंजी की सुरक्षा के लिए हमेशा 1:2 रिस्क-रिवॉर्ड का अनुशासन बनाए रखें।";
        }}
    }}

    function startTalk() {{
        if (!SpeechRec) {{
            alert("कृपया Google Chrome का उपयोग करें जिसमें वॉइस सपोर्ट उपलब्ध है।");
            return;
        }}

        rec = new SpeechRec();
        rec.lang = 'hi-IN';
        rec.continuous = false;
        rec.interimResults = false;

        rec.onstart = function() {{
            btn.classList.add('active');
            btn.innerHTML = "🔴 सुन रहा हूँ...";
            statusMsg.innerText = "आप बोलिए, मैं सुन रहा हूँ...";
        }};

        rec.onresult = function(e) {{
            const said = e.results[0][0].transcript;
            outputBox.style.display = 'block';
            userQuery.innerText = '🗣️ आपने पूछा: "' + said + '"';

            const reply = getInsight(said);
            aiResponse.innerText = '🤖 Gemini: ' + reply;
            statusMsg.innerText = "जवाब दिया जा रहा है...";
            speakGemini(reply);
        }};

        rec.onerror = function() {{
            btn.classList.remove('active');
            btn.innerHTML = "🎙️ बोलकर पूछें";
            statusMsg.innerText = "माइक बंद हो गया। दोबारा बोलने के लिए क्लिक करें।";
        }};

        try {{
            rec.start();
        }} catch(err) {{}}
    }}
</script>
</body>
</html>
"""

st.components.v1.html(voice_app_html, height=190)

# 5. नियमों का बैकअप लॉग
with st.expander("🧠 आपके ट्रेडिंग नियम (Disciplines)"):
    st.write("• हमेशा 1:2 रिस्क-रिवॉर्ड रेशियो का सख्ती से पालन करें")
    st.write("• रात के सत्र में कोई ओवरनाइट निफ्टी ऑप्शंस नहीं")
    st.write("• सुबह गिफ्ट निफ्टी और ग्लोबल संकेत देखकर ही एंट्री लें")

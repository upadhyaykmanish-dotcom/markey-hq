import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

st.set_page_config(
    page_title="AlphaPulse Voice Agent",
    page_icon="🎙️",
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
        "NIFTY": "^NSEI",
        "CRUDE": "CL=F",
        "GOLD": "GC=F",
        "VIX": "^INDIAVIX",
        "NASDAQ": "^IXIC"
    }
    res = {}
    for k, sym in tickers.items():
        try:
            h = yf.Ticker(sym).history(period="2d")
            if len(h) >= 2:
                c = h['Close'].iloc[-1]
                p = h['Close'].iloc[-2]
                res[k] = {"price": round(c, 2), "pct": round(((c - p)/p)*100, 2)}
            elif len(h) == 1:
                res[k] = {"price": round(h['Close'].iloc[-1], 2), "pct": 0.0}
            else:
                res[k] = {"price": 0.0, "pct": 0.0}
        except:
            res[k] = {"price": 0.0, "pct": 0.0}
    return res

mkt = get_data()

# डार्क प्रीमियम UI
st.markdown("""
<style>
    .stApp { background-color: #080b10; color: #ffffff; }
    .voice-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
        background: #111622;
        border-radius: 16px;
        border: 1px solid #232c3d;
        margin-top: 20px;
    }
    .pulse-orb {
        width: 120px;
        height: 120px;
        background: radial-gradient(circle, #00c087 10%, #080b10 80%);
        border-radius: 50%;
        box-shadow: 0 0 35px rgba(0, 192, 135, 0.4);
        animation: orb-pulse 2s infinite ease-in-out;
        margin-bottom: 20px;
    }
    @keyframes orb-pulse {
        0% { transform: scale(0.92); opacity: 0.7; }
        50% { transform: scale(1.08); opacity: 1; box-shadow: 0 0 50px rgba(0, 192, 135, 0.7); }
        100% { transform: scale(0.92); opacity: 0.7; }
    }
    .status-text { font-size: 1.2rem; font-weight: 600; color: #58a6ff; }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ AlphaPulse Voice AI — हैंड्स-फ्री मार्केट असिस्टेंट")
st.caption(f"समय (IST): {time_str} | स्थिति: {'NSE लाइव' if is_live else 'NSE बंद (कमोडिटी / यूएस लाइव)'}")

# टिकर समरी
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("NIFTY 50", f"{mkt['NIFTY']['price']:,}", f"{mkt['NIFTY']['pct']}%")
c2.metric("INDIA VIX", f"{mkt['VIX']['price']}", f"{mkt['VIX']['pct']}%")
c3.metric("CRUDE OIL ($)", f"{mkt['CRUDE']['price']}", f"{mkt['CRUDE']['pct']}%")
c4.metric("GOLD ($)", f"{mkt['GOLD']['price']:,}", f"{mkt['GOLD']['pct']}%")
c5.metric("NASDAQ", f"{mkt['NASDAQ']['price']:,}", f"{mkt['NASDAQ']['pct']}%")

st.markdown("""
<div class="voice-container">
    <div class="pulse-orb"></div>
    <div class="status-text">असिस्टेंट एक्टिव है — आप सीधे बोलें</div>
    <p style="color: #8b949e; margin-top: 8px;">(उदा: "क्रूड ऑयल का क्या रुख है?", "कल निफ्टी कैसा रहेगा?", "गोल्ड का भाव बताओ")</p>
</div>
""", unsafe_allow_html=True)

# 3. फुल ऑटोमैटिक टू-वे वॉइस इंजन (JavaScript Web Speech + TTS)
market_summary_text = (
    f"वर्तमान में निफ्टी {mkt['NIFTY']['price']} पर है। "
    f"इंडिया विक्स {mkt['VIX']['price']} पर चल रहा है। "
    f"कच्चा तेल {mkt['CRUDE']['price']} डॉलर और सोना {mkt['GOLD']['price']} डॉलर पर ट्रेड कर रहा है। "
    f"अमेरिकी नैस्डैक {mkt['NASDAQ']['pct']} प्रतिशत पर है।"
)

st.components.v1.html(f"""
<div id="agent-box" style="text-align:center; padding: 15px; color:#c9d1d9; font-family:sans-serif;">
    <p id="user-said" style="font-size: 1.1rem; color: #58a6ff; font-weight: 500;">माइक ऑन है, बोलिए...</p>
    <p id="ai-replied" style="font-size: 1.15rem; color: #00c087; font-weight: 600; margin-top: 10px;"></p>
</div>

<script>
    const synth = window.speechSynthesis;
    let recognition = null;
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

    function speak(text) {{
        synth.cancel();
        const msg = new SpeechSynthesisUtterance(text);
        msg.lang = 'hi-IN';
        msg.rate = 0.95;
        
        const voices = synth.getVoices();
        const hiVoice = voices.find(v => v.lang.includes('hi') || v.name.includes('Hindi'));
        if (hiVoice) msg.voice = hiVoice;
        
        msg.onend = function() {{
            startListening();
        }};
        synth.speak(msg);
    }}

    function generateAnswer(query) {{
        const q = query.toLowerCase();
        const mktData = "{market_summary_text}";
        
        if (q.includes("क्रूड") || q.includes("crude") || q.includes("तेल")) {{
            return "क्रूड ऑयल इस समय {mkt['CRUDE']['price']} डॉलर पर ट्रेड कर रहा है। यदि यह 70 डॉलर के ऊपर टिकता है तो कल पेंट और टायर कंपनियों पर दबाव रह सकता है।";
        }} else if (q.includes("गोल्ड") || q.includes("gold") || q.includes("सोना")) {{
            return "सोना {mkt['GOLD']['price']} डॉलर के स्तर पर चल रहा है, इसमें {mkt['GOLD']['pct']} प्रतिशत का बदलाव देखा गया है।";
        }} else if (q.includes("निफ्टी") || q.includes("nifty") || q.includes("कल")) {{
            return "निफ्टी {mkt['NIFTY']['price']} पर क्लोज हुआ है और विक्स {mkt['VIX']['price']} है। रात में ऑप्शंस में कोई पोजीशन न रखें, सुबह गिफ्ट निफ्टी देखकर ही फ्रेश एंट्री प्लान करें।";
        }} else if (q.includes("विक्स") || q.includes("vix")) {{
            return "इंडिया विक्स {mkt['VIX']['price']} पर है, जो बाज़ार में सामान्य वोलैटिलिटी का संकेत दे रहा है।";
        }} else {{
            return mktData + " रिस्क मैनेजमेंट हमेशा एक अनुपात दो रखें।";
        }}
    }}

    function startListening() {{
        if (!SpeechRec) {{
            document.getElementById('user-said').innerText = "आपका ब्राउज़र वॉइस सपोर्ट नहीं करता। कृपया क्रोम इस्तेमाल करें।";
            return;
        }}
        
        recognition = new SpeechRec();
        recognition.lang = 'hi-IN';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = function() {{
            document.getElementById('user-said').innerText = "🎙️ सुन रहा हूँ... बोलिए";
        }};

        recognition.onresult = function(event) {{
            const transcript = event.results[0][0].transcript;
            document.getElementById('user-said').innerText = '🗣️ आपने कहा: "' + transcript + '"';
            
            const reply = generateAnswer(transcript);
            document.getElementById('ai-replied').innerText = '🤖 जवाब: ' + reply;
            speak(reply);
        }};

        recognition.onerror = function() {{
            setTimeout(startListening, 2000);
        }};

        recognition.onend = function() {{
            if (!synth.speaking) {{
                setTimeout(startListening, 1000);
            }}
        }};

        try {{
            recognition.start();
        }} catch(e) {{}}
    }}

    // पेज लोड होते ही ऑटो स्टार्ट
    window.onload = function() {{
        setTimeout(() => {{
            speak("नमस्ते मनीष जी। अल्फा पल्स वॉइस असिस्टेंट तैयार है। आप जो पूछना चाहें, सीधे बोलें।");
        }}, 800);
    }};
</script>
""", height=220)

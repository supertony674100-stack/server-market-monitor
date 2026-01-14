import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 

# ==========================================
# 0. Time Zone Setup (Taiwan CST)
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)

# ==========================================
# 1. Language Interface Definitions
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "24H 全球 AI & 伺服器戰情室",
        "market_label": "關注領域",
        "btn_run": "立即分析情報",
        "btn_email": "📧 寄送郵件給 Tony",
        "running": "正在掃描 NVIDIA, AMD, Google, MSFT 與在地供應鏈...",
        "success": "分析完成！點擊下方按鈕即可發送郵件。",
        "tabs": ["🔥 最新情報", "📈 供應鏈趨勢", "🎯 建議開發策略"],
        "markets": ["全球 (NVIDIA/AMD/IT 巨頭)", "日本 (Local)", "台灣 (Supply Chain)"]
    },
    "日本語": {
        "page_title": "24H 全球 AI & サーバー戦況ルーム",
        "market_label": "注目領域",
        "btn_run": "情報を取得して分析",
        "btn_email": "📧 Tonyにメールを送信",
        "running": "動向を分析中...",
        "success": "分析完了！メールを送信できます。",
        "tabs": ["🔥 最新ニュース", "📈 サプライチェーン", "🎯 推導開発戦略"],
        "markets": ["グローバル", "日本国内", "台灣サプライチェーン"]
    },
    "English": {
        "page_title": "24H Global AI & Server Intelligence",
        "market_label": "Target Domains",
        "btn_run": "Fetch Intelligence",
        "btn_email": "📧 Send Email to Tony",
        "running": "Scanning Market Dynamics...",
        "success": "Analysis Complete! Click to email.",
        "tabs": ["🔥 News", "📈 Tech Trends", "🎯 Strategies"],
        "markets": ["Global", "Japan", "Taiwan"]
    }
}

ui_lang = st.sidebar.radio("🌐 Language", ["繁體中文", "日本語", "English"])
T = LANG_LABELS[ui_lang]

st.set_page_config(page_title=T["page_title"], layout="wide")
st.title(f"📊 {T['page_title']}")

# ==========================================
# 2. API Key Setup
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing! Please set GEMINI_API_KEY in Secrets.")
    st.stop()

# ==========================================
# 3. Sidebar & Metrics
# ==========================================
st.sidebar.divider()
st.sidebar.header("⚙️ Config")
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
col1.metric("Taiwan Time", current_tw_time.strftime("%H:%M"))
col2.metric("Market Monitor", "2026 LIVE")

# ==========================================
# 4. Main Intelligence Logic
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        try:
            prompt = f"Today's Date: {report_date}. Task: BD Intelligence Report for {ui_lang} (NVIDIA, AMD, Japan GPU market, Taiwan Supply Chain). Use markers [PART_1_NEWS], [PART_2_TECH], [PART_3_STRATEGY]."
            
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            full_text = response.text
            
            # Simple Tab Display
            tab1, tab2, tab3 = st.tabs(T["tabs"])
            with tab1: st.markdown(full_text)

            # --- Password-Free Email Button ---
            st.divider()
            email_subject = f"AI News Report - {report_date}"
            email_body = f"Hello Tony,\n\nGenerated at: {current_tw_time.strftime('%H:%M')} (CST)\n\n{full_text}"
            
            mailto_link = f"mailto:tonyh@supermicro.com?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"
            
            st.markdown(
                f'<a href="{mailto_link}" target="_blank" style="text-decoration: none;"><button style="background-color: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">{T["btn_email"]}</button></a>', 
                unsafe_allow_html=True
            )
            st.info(T["success"])
            
        except Exception as e:
            st.error(f"Error: {e}")

st.sidebar.divider()
st.sidebar.caption(f"Timezone: Asia/Taipei")

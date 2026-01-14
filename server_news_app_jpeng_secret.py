import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 

# ==========================================
# 0. 台灣時區設定 (CST)
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)

# ==========================================
# 1. 多國語言定義 (移除多餘分頁標籤)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "24H 全球 AI & 伺服器戰情室",
        "market_label": "關注領域",
        "btn_run": "立即生成綜合情報報告",
        "btn_email": "📧 寄送報告給 Tony",
        "running": "正在掃描 WW 科技巨頭、NVIDIA、日本市場與台灣供應鏈...",
        "success": "報告生成完成！",
        "report_header": "🔥 全球 AI 綜合戰情報告",
        "markets": ["WW Giant Tech (Google/MSFT/AWS/Apple/Meta)", "NVIDIA/AMD", "日本 GPU 市場", "台灣供應鏈"]
    },
    "English": {
        "page_title": "24H Global AI & Server Intelligence",
        "market_label": "Target Domains",
        "btn_run": "Generate Integrated Report",
        "btn_email": "📧 Send Report to Tony",
        "running": "Scanning WW Tech Giants, NVIDIA, Japan & Taiwan...",
        "success": "Report Generated!",
        "report_header": "🔥 Global AI Integrated Intelligence",
        "markets": ["WW Giant Tech", "NVIDIA/AMD", "Japan Market", "Taiwan Supply Chain"]
    }
}

ui_lang = st.sidebar.radio("🌐 Language", ["繁體中文", "English"])
T = LANG_LABELS[ui_lang]

st.set_page_config(page_title=T["page_title"], layout="wide")
st.title(f"📊 {T['page_title']}")

# ==========================================
# 2. API Key 設定
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing! Please set GEMINI_API_KEY in Secrets.")
    st.stop()

# ==========================================
# 3. 側邊欄與時間指標 (Taiwan Time)
# ==========================================
st.sidebar.divider()
st.sidebar.header("⚙️ Config")
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
col1.metric("Taiwan Time (CST)", current_tw_time.strftime("%Y-%m-%d %H:%M"))
col2.metric("Market Monitor", "2026 LIVE")

# ==========================================
# 4. 核心情報生成邏輯
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        try:
            # 強化後的 Prompt：加入 WW Giant Tech 動態
            prompt = f"""
            Today's Date: {report_date} (Taiwan Time).
            Task: Comprehensive BD Intelligence Report.
            
            Focus Areas:
            1. **WW Giant Tech Dynamics**: Deep dive into Google, Microsoft, Amazon (AWS), Meta, and Apple's latest AI infrastructure, model updates, and data center investments.
            2. **NVIDIA & AMD**: GPU roadmap, Blackwell availability, and major server orders.
            3. **Japan Market**: Local demand for GPU servers (Sakura Internet, SoftBank, etc.) and sovereign AI trends.
            4. **Taiwan Supply Chain**: Updates on TSMC, Foxconn, Quanta, and cooling technology.
            
            Output Requirements:
            - Language: {ui_lang}.
            - Format: Professional markdown with clear headings.
            - Tone: Actionable business development insights for a senior manager.
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            full_text = response.text
            
            # 直接在主頁面顯示報告內容
            st.header(T["report_header"])
            st.markdown(full_text)

            # --- 郵件發送按鈕 ---
            st.divider()
            email_subject = f"Comprehensive AI Report - {report_date}"
            email_body = f"Hello Tony,\n\nGenerated at: {current_tw_time.strftime('%H:%M')} (Taiwan Time)\n\n{full_text}"
            
            mailto_link = f"mailto:tonyh@supermicro.com?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"
            
            st.markdown(
                f'<a href="{mailto_link}" target="_blank" style="text-decoration: none;"><button style="background-color: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 18px;">{T["btn_email"]}</button></a>', 
                unsafe_allow_html=True
            )
            st.success(T["success"])
            
        except Exception as e:
            st.error(f"Error: {e}")

st.sidebar.divider()
st.sidebar.caption("System: 2026 AI Intelligence Dashboard")

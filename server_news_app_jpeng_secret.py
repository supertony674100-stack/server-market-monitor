import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz  # Added for Taiwan Time Zone support

# ==========================================
# 0. Time Zone Setup (Taiwan)
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
        "markets": ["全球 (NVIDIA/AMD/IT 巨頭)", "日本 (Local Companies)", "台灣 (Supply Chain)"]
    },
    "日本語": {
        "page_title": "24H 全球 AI & サーバー戦況ルーム",
        "market_label": "注目領域",
        "btn_run": "情報を取得して分析",
        "btn_email": "📧 Tonyにメールを送信",
        "running": "NVIDIA, AMD, Google, MSFT などの最新動向を分析中...",
        "success": "分析完了！下のボタンをクリックして送信してください。",
        "tabs": ["🔥 最新ニュース", "📈 サプライチェーン", "🎯 推導開発戦略"],
        "markets": ["グローバル", "日本国内", "台灣サプライチェーン"]
    },
    "English": {
        "page_title": "24H Global AI & Server Intelligence",
        "market_label": "Target Domains",
        "btn_run": "Fetch Intelligence",
        "btn_email": "📧 Send Email to Tony",
        "running": "Scanning Market Dynamics (NVIDIA, AMD, Cloud Giants)...",
        "success": "Analysis Complete! Click the button below to email.",
        "tabs": ["🔥 News", "📈 Tech Trends", "🎯 Strategies"],
        "markets": ["Global", "Japan", "Taiwan"]
    }
}

ui_lang = st.sidebar.radio("🌐 Select Interface Language", ["繁體中文", "日本語", "English"])
T = LANG_LABELS[ui_lang]

st.set_page_config(page_title=T["page_title"], layout="wide")
st.title(f"📊 {T['page_title']}")

# ==========================================
# 2. API Key & Client Setup
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing! Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# ==========================================
# 3. Sidebar & Metrics (Using Taiwan Time)
# ==========================================
st.sidebar.divider()
st.sidebar.header("⚙️ Search Config")
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
# Display formatted Taiwan time
col1.metric("Taiwan Time (CST)", current_tw_time.strftime("%Y-%m-%d %H:%M"))
col2.metric("Market Monitor", "2026 LIVE")

# ==========================================
# 4. Execution Logic
# ==========================================
if st.sidebar.button(T["btn_run"]):
    # Use Taiwan date for the prompt
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        try:
            prompt = f"""
            Today's Date: {report_date} (Taiwan Time Zone)
            Task: Senior Business Development Manager Intelligence Report. 
            Target: NVIDIA, AMD, Google, Microsoft AI infrastructure, Japan GPU server market, and Taiwan Supply Chain.
            ... (Omitting full prompt for brevity) ...
            """

            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())] 
                )
            )

            full_text = response.text
            
            # Simple UI Tabs
            tab1, tab2, tab3 = st.tabs(T["tabs"])
            with tab1: st.markdown(full_text)

            # ==========================================
            # 5. Secure Email Generation
            # ==========================================
            st.divider()
            email_subject = f"AI Intelligence Report - {report_date}"
            email_body = f"Hello Tony,\n\nGenerated at: {current_tw_time.strftime('%H:%M')} (Taiwan Time)\n\n{full_text}"
            
            subject_encoded = urllib.parse.quote(email_subject)
            body_encoded = urllib.parse.quote(email_body)
            mailto_link = f"mailto:tonyh@supermicro.com?subject={subject_encoded}&body={body_encoded}"
            
            st.markdown(
                f'''
                <a href="{mailto_link}" target="_blank" style="text-decoration: none;">
                    <button style="background-color: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">
                        {T["btn_email"]}
                    </button>
                </a>
                ''', 
                unsafe_allow_html=True
            )
            st.info(T["success"])
            
        except Exception as e:
            st.error(f"Execution Error: {e}")

st.sidebar.

import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse

# ==========================================
# 0. Language Interface Definitions
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
        "markets": ["グローバル (NVIDIA/AMD/IT大手)", "日本 (国内企業)", "台湾 (サプライチェーン)"]
    },
    "English": {
        "page_title": "24H Global AI & Server Intelligence",
        "market_label": "Target Domains",
        "btn_run": "Fetch Intelligence",
        "btn_email": "📧 Send Email to Tony",
        "running": "Scanning Market Dynamics (NVIDIA, AMD, Cloud Giants)...",
        "success": "Analysis Complete! Click the button below to email.",
        "tabs": ["🔥 News", "📈 Tech Trends", "🎯 Strategies"],
        "markets": ["Global (NVIDIA/AMD/Big Tech)", "Japan (Local Companies)", "Taiwan (Supply Chain)"]
    }
}

# Interface Language Selection
ui_lang = st.sidebar.radio("🌐 Select Interface Language", ["繁體中文", "日本語", "English"])
T = LANG_LABELS[ui_lang]

st.set_page_config(page_title=T["page_title"], layout="wide")
st.title(f"📊 {T['page_title']}")

# ==========================================
# 1. API Key & Client Setup
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing! Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# ==========================================
# 2. Sidebar & Metrics
# ==========================================
st.sidebar.divider()
st.sidebar.header("⚙️ Search Config")
selected_markets = st.sidebar.multiselect(
    T["market_label"], 
    T["markets"],
    default=T["markets"]
)

col1, col2 = st.columns(2)
col1.metric("Current Time", datetime.now().strftime("%H:%M"))
col2.metric("Market Monitor", "2026 LIVE")

# ==========================================
# 3. Execution Logic
# ==========================================
if st.sidebar.button(T["btn_run"]):
    current_date = datetime.now().strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        try:
            # Build Professional BD Prompt
            prompt = f"""
            Today's Date: {current_date}
            Task: Senior Business Development Manager Intelligence Report. 
            Target: NVIDIA, AMD, Google, Microsoft AI infrastructure, Japan GPU server market, and Taiwan Supply Chain.
            
            Strict Sourcing Instructions:
            - Global: Real-time trends of NVIDIA, AMD, and IT giants (Blackwell, AI chips, CapEx).
            - Japan: Local updates on Sakura Internet, SoftBank, NTT, and GPU server demand.
            - Taiwan: Latest Supply Chain movements (TSMC, Quanta, Foxconn, etc.).
            
            Formatting:
            Use markers: [PART_1_NEWS], [PART_2_TECH], and [PART_3_STRATEGY].
            The entire output MUST be in {ui_lang}. Tone: Professional and actionable.
            """

            # Call Gemini with Google Search tool enabled
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())] 
                )
            )

            full_text = response.text
            
            # Parsing logic into tabs
            parts = {"NEWS": "", "TECH": "", "STRATEGY": ""}
            try:
                parts["NEWS"] = full_text.split("[PART_1_NEWS]")[1].split("[PART_2_TECH]")[0]
                parts["TECH"] = full_text.split("[PART_2_TECH]")[1].split("[PART_3_STRATEGY]")[0]
                parts["STRATEGY"] = full_text.split("[PART_3_STRATEGY]")[1]
            except:
                parts["NEWS"] = full_text # Fallback

            # Display Tabs
            tab1, tab2, tab3 = st.tabs(T["tabs"])
            with tab1: st.markdown(parts["NEWS"])
            with tab2: st.markdown(parts["TECH"])
            with tab3:
                st.success("🎯 Business Development Strategies")
                st.markdown(parts["STRATEGY"])

            # ==========================================
            # 4. Password-Free Email Generation
            # ==========================================
            st.divider()
            email_subject = f"AI Intelligence Report - {current_date}"
            email_body = f"Hello Tony,\n\nHere is the latest AI Intelligence Report:\n\n{full_text}"
            
            # URL Encoding for the mailto link
            subject_encoded = urllib.parse.quote(email_subject)
            body_encoded = urllib.parse.quote(email_body)
            mailto_link = f"mailto:tonyh@supermicro.com?subject={subject_encoded}&body={body_encoded}"
            
            # Styled Button to open user's email client
            st.markdown(
                f'''
                <a href="{mailto_link}" target="_blank" style="text-decoration: none;">
                    <button style="
                        background-color: #007bff; 
                        color: white; 
                        padding: 12px 24px; 
                        border: none; 
                        border-radius: 8px; 
                        cursor: pointer; 
                        font-weight: bold;
                        font-size: 16px;">
                        {T["btn_email"]}
                    </button>
                </a>
                ''', 
                unsafe_allow_html=True
            )
            st.info(T["success"])
            
        except Exception as e:
            st.error(f"Execution Error: {e}")

st.sidebar.divider()
with st.sidebar.expander("ℹ️ System Info"):
    st.caption("2026 AI Intelligence Dashboard")
    st.caption("Customized for Tony @ Supermicro")

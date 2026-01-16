import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import pytz 
import time 

# ==========================================
# 1. 核心定義 (確保 UI 順序正確)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "全球 AI 算力戰略導航中心",
        "market_label": "戰略關注領域",
        "btn_run": "立即生成 2026 全球戰略報告",
        "running": "正在同步全球 AI 供應鏈動態...",
        "success": "戰略報告生成完成！",
        "report_header": "🔍 全球 AI 算力與供應鏈整合導航報告",
        "retry_msg": "⏳ 正在重新連接 API (快速重試)...",
        "markets": ["WW Giant Tech", "NVIDIA/AMD 戰略", "日本 AI 垂直市場", "台灣 AI 供應鏈核心"]
    },
    "日本語": {
        "page_title": "グローバル AI 算力戦略ナビゲーター",
        "market_label": "戦略的注力領域",
        "btn_run": "戦略報告を生成",
        "running": "市場データを分析中...",
        "success": "分析が完了しました！",
        "report_header": "🔍 グローバル AI 算力・サプライチェーン報告",
        "retry_msg": "⏳ 再試行中...",
        "markets": ["WWテック大手", "NVIDIA/AMD 戦略", "日本国内SP", "台灣サプライチェーン"]
    },
    "English": {
        "page_title": "Global AI Strategy Navigator",
        "market_label": "Strategic Focus",
        "btn_run": "Generate Intelligence",
        "running": "Scanning AI markets...",
        "success": "Intelligence Generated!",
        "report_header": "🔍 Global AI & Supply Chain Intelligence",
        "retry_msg": "⏳ Retrying...",
        "markets": ["WW Giant Tech", "NVIDIA/AMD Dynamics", "Japan AI Verticals", "Taiwan Supply Chain"]
    }
}

# --- 初始化頁面 ---
st.set_page_config(page_title="AI Strategy Navigator", layout="wide")
ui_lang = st.sidebar.radio("🌐 Language", list(LANG_LABELS.keys()))
T = LANG_LABELS[ui_lang]

st.title(f"🚀 {T['page_title']}")

# ==========================================
# 2. 環境與 API 設定
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing! Please set GEMINI_API_KEY in Secrets.")
    st.stop()

st.sidebar.divider()
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
col1.metric("Taiwan Time (CST)", current_tw_time.strftime("%Y-%m-%d %H:%M"))
col2.metric("Market Status", "2026 LIVE (Paid Tier)")

# ==========================================
# 3. 核心邏輯 (效能模式：2.0-Flash + 短重試)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 使用 Gemini 2.0 Flash 配合 Google Search 工具
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=f"""
                    Today's Date: {report_date}. 
                    Task: Professional AI Strategic Intelligence Report for {ui_lang}.
                    Focus Areas: {', '.join(selected_markets)}.
                    Include: Market trends, Supply chain shifts, and key Japanese/Taiwanese company moves.
                    """,
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                )
                full_text = response.text
                break
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    st.warning(f"{T['retry_msg']} (Attempt {attempt + 1})")
                    # 既然已開付費版，通常只需等 3-5 秒即可避開短暫抖動
                    time.sleep(5) 
                else:
                    st.error(f"Execution Error: {e}")
                    st.stop()

        if full_text:
            st.header(T["report_header"])
            st.markdown(full_text)
            st.success(T["success"])

st.sidebar.divider()
st.sidebar.caption("System: 2026 AI Strategic Hub | Paid Tier Active")

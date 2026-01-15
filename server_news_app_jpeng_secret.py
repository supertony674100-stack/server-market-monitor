import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 
import time 

# ==========================================
# 1. コア定義 (NameError 防止のため最上部に配置)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "全球 AI 算力戰略導航中心",
        "market_label": "戰略關注領域",
        "btn_run": "生成 2026 全球戰略情報",
        "running": "正在掃描供應鏈動態...",
        "success": "戰略報告生成完成！",
        "report_header": "🔍 全球 AI 算力與供應鏈整合導航報告",
        "retry_msg": "⚠️ 偵測到流量限制，為確保成功，將等待 40 秒後自動重試...",
        "markets": ["WW Giant Tech", "NVIDIA/AMD 戰略", "日本 AI 垂直市場", "台灣 AI 供應鏈核心"]
    },
    "日本語": {
        "page_title": "グローバル AI 算力戦略ナビゲーター",
        "market_label": "戦略的注力領域",
        "btn_run": "戦略報告を生成",
        "running": "分析中...",
        "success": "戦略分析が完了しました！",
        "report_header": "🔍 グローバル AI 算力・サプライチェーン報告",
        "retry_msg": "⚠️ 制限を検知。40秒後に再試行します...",
        "markets": ["WWテック大手", "NVIDIA/AMD 戦略", "日本国内SP", "台灣サプライチェーン"]
    },
    "English": {
        "page_title": "Global AI Strategy Navigator",
        "market_label": "Strategic Focus",
        "btn_run": "Generate Intelligence",
        "running": "Scanning markets...",
        "success": "Intelligence Generated!",
        "report_header": "🔍 Global AI & Supply Chain Intelligence",
        "retry_msg": "⚠️ Rate limit detected. Retrying in 40s...",
        "markets": ["WW Giant Tech", "NVIDIA/AMD Dynamics", "Japan AI Verticals", "Taiwan Supply Chain"]
    }
}

# --- ページ設定の初期化 ---
st.set_page_config(page_title="AI Strategy Navigator", layout="wide")
ui_lang = st.sidebar.radio("🌐 Select Language", ["繁體中文", "日本語", "English"])
T = LANG_LABELS[ui_lang]

st.title(f"🚀 {T['page_title']}")

# ==========================================
# 2. 環境および API 設定
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing! Please check Streamlit Secrets.")
    st.stop()

st.sidebar.divider()
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
col1.metric("Taiwan Time (CST)", current_tw_time.strftime("%Y-%m-%d %H:%M"))
col2.metric("Market Monitor", "2026 LIVE")

# ==========================================
# 3. コアロジック (3段階自動リトライ + 40秒冷却)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 安定性の高い gemini-2.0-flash を使用
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=f"Today's Date: {report_date}. Strategic AI Report for {ui_lang}.",
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                )
                full_text = response.text
                break
                
            except Exception as e:
                # 429 流量制限の検知
                if "429" in str(e) and attempt < max_retries - 1:
                    st.warning(f"{T['retry_msg']} (試行 {attempt + 1})")
                    time.sleep(40) 
                else:
                    st.error(f"Execution Error: {e}")
                    st.stop()

        if full_text:
            st.header(T["report_header"])
            st.markdown(full_text)
            st.success(T["success"])

st.sidebar.divider()
st.sidebar.caption("System: 2026 AI Strategy Navigator")

import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 
import time 

# ==========================================
# 1. 最優先定義 (防止任何 NameError)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "全球 AI 算力戰略導航中心",
        "market_label": "戰略關注領域",
        "btn_run": "生成 2026 全球戰略情報",
        "running": "正在掃描全球供應鏈與日本市場...",
        "success": "報告生成完成！",
        "retry_msg": "⚠️ 配額吃緊，將等待 45 秒後自動重試...",
        "quota_error": "❌ 配額已完全耗盡。請等待 1-5 分鐘後再試，或更換 API Key。",
        "markets": ["WW Giant Tech", "NVIDIA/AMD 戰略", "日本 AI 垂直市場", "台灣 AI 供應鏈核心"]
    },
    "日本語": {
        "page_title": "グローバル AI 算力戦略ナビゲーター",
        "market_label": "戦略的注力領域",
        "btn_run": "戦略報告を生成",
        "running": "市場データを分析中...",
        "success": "分析が完了しました！",
        "retry_msg": "⚠️ 制限を検知。45秒後に再試行します...",
        "quota_error": "❌ クォータ制限です。数分待ってから再試行してください。",
        "markets": ["WWテック大手", "NVIDIA/AMD 戦略", "日本国内SP", "台灣サプライチェーン"]
    },
    "English": {
        "page_title": "Global AI Strategy Navigator",
        "market_label": "Strategic Focus",
        "btn_run": "Generate Intelligence",
        "running": "Scanning AI markets...",
        "success": "Intelligence Generated!",
        "retry_msg": "⚠️ Rate limit. Retrying in 45s...",
        "quota_error": "❌ Quota exhausted. Please wait a few minutes.",
        "markets": ["WW Giant Tech", "NVIDIA/AMD Dynamics", "Japan AI Verticals", "Taiwan Supply Chain"]
    }
}

# --- 初始化頁面 ---
st.set_page_config(page_title="AI Strategy Navigator", layout="wide")
ui_lang = st.sidebar.radio("🌐 Language", list(LANG_LABELS.keys()))
T = LANG_LABELS[ui_lang]

# --- 顯示 UI ---
st.title(f"🚀 {T['page_title']}")

# ==========================================
# 2. API 與時間設定
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing in Secrets!")
    st.stop()

st.sidebar.divider()
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
col1.metric("Taiwan Time (CST)", current_tw_time.strftime("%Y-%m-%d %H:%M"))
col2.metric("Market Monitor", "2026 LIVE")

# ==========================================
# 3. 生成邏輯 (強化重試與保護機制)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    with st.spinner(T["running"]):
        report_date = current_tw_time.strftime("%Y-%m-%d")
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 執行生成
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=f"Generate a professional AI strategy report for {report_date}. Lang: {ui_lang}.",
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.7
                    )
                )
                full_text = response.text
                break # 成功則跳出
                
            except Exception as e:
                err_str = str(e)
                if "429" in err_str:
                    if attempt < max_retries - 1:
                        st.warning(f"{T['retry_msg']} ({attempt + 1}/{max_retries})")
                        time.sleep(45) # 稍微超過要求的 40 秒以保險
                    else:
                        st.error(T["quota_error"])
                        st.info("💡 提示：免費版 Google Search API 限制較嚴，建議每 5 分鐘執行一次。")
                else:
                    st.error(f"Error: {err_str}")
                    st.stop()

        if full_text:
            st.markdown("---")
            st.markdown(full_text)
            st.success(T["success"])

st.sidebar.divider()
st.sidebar.caption("System: 2026 AI Strategy Navigator")

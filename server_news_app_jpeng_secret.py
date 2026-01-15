import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 
import time 

# ==========================================
# 1. 核心定義區 (放在最頂端，防止 NameError)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "全球 AI 算力戰略導航中心",
        "market_label": "戰略關注領域",
        "btn_run": "生成 2026 全球戰略情報",
        "btn_email": "📧 寄送報告摘要給 Tony",
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
        "btn_email": "📧 Tonyにレポートを送信",
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
        "btn_email": "📧 Send Report Summary to Tony",
        "running": "Scanning markets...",
        "success": "Intelligence Generated!",
        "report_header": "🔍 Global AI & Supply Chain Intelligence",
        "retry_msg": "⚠️ Rate limit detected. Retrying in 40s...",
        "markets": ["WW Giant Tech", "NVIDIA/AMD Dynamics", "Japan AI Verticals", "Taiwan Supply Chain"]
    }
}

# --- 初始化頁面 ---
st.set_page_config(page_title="AI Strategy Navigator", layout="wide")
ui_lang = st.sidebar.radio("🌐 Select Language", ["繁體中文", "日本語", "English"])
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
    st.error("API Key missing! Please check Streamlit Secrets.")
    st.stop()

st.sidebar.divider()
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
col1.metric("Taiwan Time (CST)", current_tw_time.strftime("%Y-%m-%d %H:%M"))
col2.metric("Market Monitor", "2026 LIVE")

# ==========================================
# 3. 核心邏輯 (3階段自動重試 + 40秒冷卻)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 這裡使用 2.0-flash，因為這是您環境中唯一能通過 404 檢查的模型
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=f"Today's Date: {report_date}. Strategic AI Report for {ui_lang}.",
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                )
                full_text = response.text
                break
                
            except Exception as e:
                # 偵測到 429 流量限制
                if "429" in str(e) and attempt < max_retries - 1:
                    # 重要：截圖顯示 API 要求 35 秒，所以我們必須等 40 秒才能解鎖
                    st.warning(f"{T['retry_msg']} (第 {attempt + 1} 次重試)")
                    time.sleep(40) 
                else:
                    st.error(f"Execution Error: {e}")
                    st.stop()

        if full_text:
            st.header(T["report_header"])
            st.markdown(full_text)

            # --- 郵件發送 ---
            st.divider()
            email_subject = f"AI Strategy Report - {report_date}"
            email_summary = full_text[:500].replace('\n', '%0D%0A') 
            mailto_link = f"mailto:tonyh@supermicro.com?subject={urllib.parse.quote(email_subject)}&body=Hello Tony,%0D%0A%0D%0A{email_summary}..."
            
            st.markdown(
                f'<a href="{mailto_link}" target="_blank"><button style="background-color: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer;">{T["btn_email"]}</button></a>', 
                unsafe_allow_html=True
            )
            st.success(T["success"])

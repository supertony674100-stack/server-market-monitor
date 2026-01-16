import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 
import time 

# ==========================================
# 1. 核心定義 (優先放在最頂端，絕對防止 NameError)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "2026 全球 AI 算力戰略監控中心",
        "market_label": "戰略關注領域 (24H 監控)",
        "btn_run": "執行深度戰略掃描",
        "btn_email": "📧 將今日報告寄送至我的 Email",
        "running": "正在調用 Google Search 掃描供應鏈動態...",
        "success": "戰略報告生成完成！",
        "report_header": "🔍 2026 AI 算力與供應鏈即時戰略報告",
        "retry_msg": "⏳ 正在重試 (付費版快速通道)...",
        "markets": ["WW Giant Tech", "NVIDIA/AMD 戰略", "日本市場 (Sakura/SoftBank)", "台灣供應鏈 (液冷/網通)"]
    },
    "日本語": {
        "page_title": "2026 グローバル AI 算力戦略ナビゲーター",
        "market_label": "戦略的注力領域",
        "btn_run": "戦略報告を生成",
        "btn_email": "📧 レポートをメールで送信",
        "running": "日本・台湾市場データを深度分析中...",
        "success": "戦略分析が完了しました！",
        "report_header": "🔍 2026 グローバル AI 算力・サプライチェーン報告",
        "retry_msg": "⏳ 再試行中...",
        "markets": ["WWテック大手", "NVIDIA/AMD 戦略", "日本国内DC", "台灣サプライチェーン"]
    }
}

# --- 頁面初始化 ---
st.set_page_config(page_title="AI Strategy Navigator", layout="wide")
ui_lang = st.sidebar.radio("🌐 Language", list(LANG_LABELS.keys()))
T = LANG_LABELS[ui_lang]

st.title(f"🚀 {T['page_title']}")
st.info("ℹ️ **系統狀態：已開啟 24H 深度戰略監控**。")

# ==========================================
# 2. 環境與 API 設定 (請確保 Key 已更新)
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key 缺失！請在 Streamlit Secrets 設定新的 GEMINI_API_KEY。")
    st.stop()

st.sidebar.divider()
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

# ==========================================
# 3. 核心邏輯 (Tony 專屬：日本/台灣深度追蹤)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 這裡加入了 Tony 指定的日本 DC 與台灣供應鏈深度指令
                strategic_prompt = f"""
                Current Date: {report_date}. Lang: {ui_lang}.
                Deep Dive Tasks:
                1. **Japan Market**: Track Sakura Internet & SoftBank AI data center expansion and GPU procurement.
                2. **Taiwan Supply Chain**: Monitor Liquid Cooling (Cold Plate/CDU) and 800G/1.6T networking capacity changes.
                3. **Strategic Insight**: Provide business intelligence based on the last 24h news.
                """

                # 使用 Gemini 2.0 Flash (解決 404 問題)
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=strategic_prompt,
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                )
                full_text = response.text
                break
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    st.warning(f"{T['retry_msg']} (第 {attempt + 1} 次重試)")
                    time.sleep(10) # 付費版重試間隔只需 10 秒
                else:
                    st.error(f"Execution Error: {e}")
                    st.stop()

        if full_text:
            st.header(T["report_header"])
            st.markdown(full_text)
            st.success(T["success"])

            # --- 郵件選項 (寄送至 tonyh@supermicro.com) ---
            st.divider()
            email_subject = f"AI Strategy Report - {report_date}"
            email_body = f"Hello Tony,%0D%0A%0D%0AHere is your daily AI strategy report...%0D%0A%0D%0A{full_text[:500].replace(chr(10), '%0D%0A')}..."
            mailto_link = f"mailto:tonyh@supermicro.com?subject={urllib.parse.quote(email_subject)}&body={email_body}"
            
            st.markdown(f'<a href="{mailto_link}" target="_blank"><button style="background-color: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer;">{T["btn_email"]}</button></a>', unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.caption(f"Last Sync: {current_tw_time.strftime('%Y-%m-%d %H:%M:%S')}")

import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 
import time 

# ==========================================
# 1. 核心定義 (包含 English, 繁體中文, 日本語)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "2026 全球 AI 算力戰略監控中心",
        "market_label": "戰略關注領域 (24H 監控)",
        "btn_run": "執行深度戰略掃描",
        "btn_email": "📧 將報告寄送至我的 Email",
        "running": "正在掃描日本與台灣供應鏈動態...",
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
        "running": "日本・台湾市場を分析中...",
        "success": "戦略分析が完了しました！",
        "report_header": "🔍 2026 グローバル AI 算力・サプライチェーン報告",
        "retry_msg": "⏳ 再試行中...",
        "markets": ["WWテック大手", "NVIDIA/AMD 戦略", "日本国内DC", "台灣サプライチェーン"]
    },
    "English": {
        "page_title": "2026 Global AI Strategy Navigator",
        "market_label": "Strategic Focus (24H Monitor)",
        "btn_run": "Run Deep Strategic Scan",
        "btn_email": "📧 Send Report to my Email",
        "running": "Scanning Japan & Taiwan supply chains...",
        "success": "Strategic Intelligence Generated!",
        "report_header": "🔍 2026 Global AI & Supply Chain Intelligence",
        "retry_msg": "⏳ Retrying (Paid Tier High Speed)...",
        "markets": ["WW Giant Tech", "NVIDIA/AMD Dynamics", "Japan Market (Sakura/SoftBank)", "Taiwan SC (Liquid Cooling/Networking)"]
    }
}

# --- 頁面初始化 ---
st.set_page_config(page_title="AI Strategy Navigator", layout="wide")
ui_lang = st.sidebar.radio("🌐 Language / 言語", list(LANG_LABELS.keys()))
T = LANG_LABELS[ui_lang]

st.title(f"🚀 {T['page_title']}")
st.info(f"ℹ️ **Status: 24H Proactive Monitoring Enabled (Paid Tier 1).**")

# ==========================================
# 2. API 與時間設定
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key 缺失！請確保在 Streamlit Secrets 設定正確的 GEMINI_API_KEY。")
    st.stop()

st.sidebar.divider()
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

# ==========================================
# 3. 核心戰略掃描邏輯 (Tony 專屬深度追蹤)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 結合 Tony 關注的日本 DC 與台灣供應鏈關鍵技術
                strategic_prompt = f"""
                Current Date: {report_date}. Lang: {ui_lang}.
                Track:
                1. Japan: Latest on Sakura Internet GPU clusters & SoftBank AI-RAN/DC expansion.
                2. Taiwan SC: Liquid Cooling capacity (cold plates/CDU) and 800G/1.6T networking adoption.
                Requirement: Professional business intelligence summary.
                """

                # 使用 Gemini 2.0 Flash 效能模式
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=strategic_prompt,
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                )
                full_text = response.text
                break
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    st.warning(f"{T['retry_msg']} (Attempt {attempt + 1})")
                    time.sleep(5) 
                else:
                    st.error(f"Execution Error: {e}")
                    st.stop()

        if full_text:
            st.header(T["report_header"])
            st.markdown(full_text)
            st.success(T["success"])

            # --- 郵件選項 (Option for Tony) ---
            st.divider()
            email_subject = f"AI Strategy Report - {report_date}"
            email_body = f"Hello Tony,%0D%0A%0D%0AHere is your 2026 AI Strategic Report summary.%0D%0A%0D%0A{full_text[:1000].replace(chr(10), '%0D%0A')}..."
            mailto_link = f"mailto:tonyh@supermicro.com?subject={urllib.parse.quote(email_subject)}&body={email_body}"
            
            st.markdown(
                f'''
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6;">
                    <h4>📬 Intelligence Archive Option</h4>
                    <p style="font-size: 14px; color: #555;">Would you like to archive this report to your Supermicro inbox?</p>
                    <a href="{mailto_link}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">
                            {T["btn_email"]}
                        </button>
                    </a>
                </div>
                ''', 
                unsafe_allow_html=True
            )

st.sidebar.divider()
st.sidebar.caption(f"Last Intelligence Sync: {current_tw_time.strftime('%Y-%m-%d %H:%M:%S')} | Paid Tier 1 Active")

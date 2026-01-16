import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 
import time 

# ==========================================
# 1. 核心定義 (包含 WW, 日本, 台灣)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "2026 全球 AI 算力戰略監控中心",
        "market_label": "戰略關注領域 (全球同步)",
        "btn_run": "執行全球深度戰略掃描",
        "btn_email": "📧 寄送精華摘要至我的 Email",
        "running": "正在同步 WW / 日本 / 台灣供應鏈數據...",
        "success": "全球戰略報告生成完成！",
        "report_header": "🔍 2026 全球 AI 算力與供應鏈整合戰略報告",
        "retry_msg": "⏳ 正在重試 (付費版快速通道)...",
        "markets": ["WW AI News (US/EU)", "NVIDIA/AMD/Broadcom", "日本市場 (Sakura/SoftBank)", "台灣供應鏈 (液冷/網通)"]
    },
    "日本語": {
        "page_title": "2026 グローバル AI 算力戦略ナビゲーター",
        "market_label": "戦略的注力領域",
        "btn_run": "グローバル戦略報告を生成",
        "btn_email": "📧 要約をメールで送信",
        "running": "WW・日本・台湾市場を分析中...",
        "success": "戦略分析が完了しました！",
        "report_header": "🔍 2026 グローバル AI 算力・サプライチェーン報告",
        "retry_msg": "⏳ 再試行中...",
        "markets": ["WW AI ニュース", "NVIDIA/AMD 戦略", "日本国内DC", "台湾サプライチェーン"]
    },
    "English": {
        "page_title": "2026 Global AI Strategy Navigator",
        "market_label": "Strategic Focus (Worldwide)",
        "btn_run": "Run Worldwide Strategic Scan",
        "btn_email": "📧 Send Summary to my Email",
        "running": "Scanning WW, Japan, and Taiwan markets...",
        "success": "Global Intelligence Generated!",
        "report_header": "🔍 2026 Worldwide AI & Supply Chain Intelligence",
        "retry_msg": "⏳ Retrying...",
        "markets": ["Worldwide AI News", "NVIDIA/AMD/Broadcom", "Japan DC Expansion", "Taiwan SC (Cooling/Networking)"]
    }
}

st.set_page_config(page_title="Global AI Strategy Navigator", layout="wide")
ui_lang = st.sidebar.radio("🌐 Language / 言語", list(LANG_LABELS.keys()))
T = LANG_LABELS[ui_lang]

st.title(f"🚀 {T['page_title']}")
st.info("ℹ️ **系統狀態：24H 全球主動監控模式 (Paid Tier 1)。**")

# ==========================================
# 2. 環境與 API 設定
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
# 3. 核心戰略掃描邏輯 (追加 Worldwide 要求)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 結合 Worldwide, 日本, 台灣的綜合指令
                strategic_prompt = f"""
                Current Date: {report_date}. Lang: {ui_lang}.
                Objective: Provide a Worldwide AI Intelligence Report.
                
                Content Pillars:
                1. **Worldwide (WW)**: Latest on US Big Tech (NVIDIA, Google, MSFT, OpenAI), Global AI regulation, and next-gen chip releases.
                2. **Japan**: Track Sakura Internet & SoftBank AI data center expansion and GPU cluster updates.
                3. **Taiwan**: Deep dive into Liquid Cooling (Cold Plate/CDU) and 800G/1.6T networking capacity.
                
                Instruction: Use Google Search for news from the last 24-48 hours. Provide professional strategic insights.
                """

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

            # --- 郵件發送優化 (解決內容消失問題) ---
            st.divider()
            email_subject = f"WW AI Strategic Report - {report_date}"
            
            # 擷取前 1200 字作為摘要，避免超過郵件連結長度限制
            summary_for_email = full_text[:1200].replace('\n', '%0D%0A')
            email_body = (
                f"Hello Tony,%0D%0A%0D%0A"
                f"Here is the Global AI Strategic Summary for {report_date}:%0D%0A%0D%0A"
                f"{summary_for_email}...%0D%0A%0D%0A"
                f"---%0D%0A"
                f"[Note: Please check the Streamlit App for the full detailed report.]"
            )
            
            mailto_link = f"mailto:tonyh@supermicro.com?subject={urllib.parse.quote(email_subject)}&body={email_body}"
            
            st.markdown(
                f'''
                <div style="background-color: #f0f7ff; padding: 20px; border-radius: 10px; border: 1px solid #cce5ff;">
                    <h4>📬 戰略報告存檔 (Email Archive)</h4>
                    <p style="font-size: 14px; color: #555;">點擊下方按鈕將「精華摘要」發送至您的信箱：</p>
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
st.sidebar.caption(f"Last Worldwide Sync: {current_tw_time.strftime('%Y-%m-%d %H:%M:%S')} | Paid Tier Active")

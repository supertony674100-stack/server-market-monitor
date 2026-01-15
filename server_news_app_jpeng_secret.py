import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 
import time 

# ==========================================
# 0. 台灣時區設定 (CST)
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)

# ==========================================
# 1. 專業命名與多國語言定義 (已補齊所有變數)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "全球 AI 算力戰略與供應鏈導航中心",
        "market_label": "戰略關注領域",
        "btn_run": "生成 2026 全球戰略情報",
        "btn_email": "📧 寄送報告摘要給 Tony",
        "running": "正在掃描全球供應鏈動態...",
        "success": "戰略報告生成完成！",
        "report_header": "🔍 全球 AI 算力與供應鏈整合導航報告",
        "retry_msg": "⚠️ 偵測到流量限制 (429)，將等待 30 秒後自動重試...",
        "markets": ["WW Giant Tech", "NVIDIA/AMD 戰略", "日本 AI 垂直市場與大型 SP", "台灣 AI 供應鏈核心"]
    },
    "日本語": {
        "page_title": "グローバル AI 算力戦略・サプライチェーンナビゲーター",
        "market_label": "戦略的注力領域",
        "btn_run": "戦略インテリジェンス報告を生成",
        "btn_email": "📧 Tonyにレポート要約を送信",
        "running": "垂直市場とサプライチェーンを分析中...",
        "success": "戦略分析が完了しました！",
        "report_header": "🔍 グローバル AI 算力・サプライチェーン統合報告",
        "retry_msg": "⚠️ 流量制限(429)を検知。30秒後に再試行します...",
        "markets": ["WWテック大手", "NVIDIA/AMD 戦略", "日本国内SP・垂直市場", "台湾サプライチェーン"]
    },
    "English": {
        "page_title": "Global AI Strategy & Supply Chain Navigator",
        "market_label": "Strategic Focus",
        "btn_run": "Generate Strategic Intelligence",
        "btn_email": "📧 Send Report Summary to Tony",
        "running": "Scanning AI vertical markets...",
        "success": "Strategic Intelligence Generated!",
        "report_header": "🔍 Global AI & Supply Chain Integrated Intelligence",
        "retry_msg": "⚠️ Rate limit (429) detected. Retrying in 30s...",
        "markets": ["WW Giant Tech", "NVIDIA/AMD Dynamics", "Japan SP & AI Verticals", "Taiwan Supply Chain"]
    }
}

# 設定頁面配置
st.set_page_config(page_title="AI Strategy Navigator", layout="wide")

# 介面語言選擇
ui_lang = st.sidebar.radio("🌐 Select Interface Language", ["繁體中文", "日本語", "English"])
T = LANG_LABELS[ui_lang]

st.title(f"🚀 {T['page_title']}")

# ==========================================
# 2. API Key 設定
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing! Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# ==========================================
# 3. 側邊欄與時間指標
# ==========================================
st.sidebar.divider()
st.sidebar.header("⚙️ Strategic Config")
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
col1.metric("Taiwan Time (CST)", current_tw_time.strftime("%Y-%m-%d %H:%M"))
col2.metric("Market Monitor", "2026 LIVE")

# ==========================================
# 4. 戰略情報生成邏輯 (模型: 1.5-Flash, 重試: 30s)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                prompt = f"""
                Today's Date: {report_date} (Taiwan Time).
                Task: Integrated Strategic AI Intelligence Report for {ui_lang}.
                Focus: WW Giants, Japan SPs (Sakura, SoftBank), and Taiwan Supply Chain (TSMC, Cooling).
                Format: Professional Business Intelligence report.
                """
                
                # 使用穩定的 1.5-flash
                response = client.models.generate_content(
                    model='gemini-1.5-flash', 
                    contents=prompt,
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                )
                full_text = response.text
                break
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    st.warning(f"{T['retry_msg']} (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(30) # 依照要求改為 30 秒
                else:
                    st.error(f"Execution Error: {e}")
                    st.stop()

        if full_text:
            st.header(T["report_header"])
            st.markdown(full_text)

            # ==========================================
            # 5. 安全郵件發送
            # ==========================================
            st.divider()
            email_subject = f"AI Strategy Report - {report_date}"
            email_summary = full_text[:500].replace('\n', '%0D%0A') 
            email_body = f"Hello Tony,%0D%0A%0D%0AGenerated at: {current_tw_time.strftime('%H:%M')} (CST)%0D%0A%0D%0A--- REPORT SUMMARY ---%0D%0A{email_summary}...%0D%0A"
            
            subject_encoded = urllib.parse.quote(email_subject)
            mailto_link = f"mailto:tonyh@supermicro.com?subject={subject_encoded}&body={email_body}"
            
            st.markdown(
                f'''
                <a href="{mailto_link}" target="_blank" style="text-decoration: none;">
                    <button style="background-color: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px;">
                        {T["btn_email"]}
                    </button>
                </a>
                ''', 
                unsafe_allow_html=True
            )
            st.success(T["success"])

st.sidebar.divider()
st.sidebar.caption("System: 2026 AI Strategy Navigator")

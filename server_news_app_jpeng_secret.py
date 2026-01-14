import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime, timedelta
import urllib.parse
import pytz 
import time 

# ==========================================
# 0. 台灣時區設定 (CST) 與 24H 時間計算
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)
yesterday_tw_time = current_tw_time - timedelta(days=1)

# ==========================================
# 1. 專業多國語言定義 (包含 24H 戰情標籤)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "24H 全球 AI 算力即時戰情室",
        "market_label": "戰略關注領域",
        "btn_run": "生成過去 24H 全球情報報告",
        "btn_email": "📧 寄送今日快報給 Tony",
        "running": "正在掃描過去 24 小時內之全球、日本與台灣媒體...",
        "success": "24H 戰報生成完成！",
        "report_header": "⚡ 過去 24 小時 AI 算力與供應鏈即時情報",
        "retry_msg": "⚠️ 偵測到流量限制 (429)，正在等待重試...",
        "markets": ["全球科技巨頭 (WW)", "NVIDIA/AMD 供應鏈", "日本垂直市場", "台灣供應鏈核心"]
    },
    "日本語": {
        "page_title": "24H グローバル AI 戦略インテリジェンス",
        "market_label": "戦略的注力領域",
        "btn_run": "過去 24 時間のインテリジェンスを生成",
        "btn_email": "📧 今日の速報を Tony に送信",
        "running": "過去 24 時間の日本、台湾、グローバルメディアを分析中...",
        "success": "24H レポートが完了しました！",
        "report_header": "⚡ 過去 24 時間：AI 算力・サプライチェーン速報",
        "retry_msg": "⚠️ 流量制限(429)を検知。再試行中...",
        "markets": ["グローバル大手 (WW)", "NVIDIA/AMD 動向", "日本国内市場", "台湾サプライチェーン"]
    },
    "English": {
        "page_title": "24H Global AI Real-time Intel Center",
        "market_label": "Strategic Focus",
        "btn_run": "Generate Past 24H Intelligence",
        "btn_email": "📧 Send Today's Intel to Tony",
        "running": "Scanning past 24 hours of local media in TW, JP, and WW...",
        "success": "24H Intelligence Generated!",
        "report_header": "⚡ Past 24H: Global AI & Supply Chain Intelligence",
        "retry_msg": "⚠️ Rate limit (429) detected. Retrying...",
        "markets": ["Global Giants (WW)", "NVIDIA/AMD Dynamics", "Japan Verticals", "Taiwan Supply Chain"]
    }
}

ui_lang = st.sidebar.radio("🌐 Language Selector", ["繁體中文", "日本語", "English"])
T = LANG_LABELS[ui_lang]

st.set_page_config(page_title=T["page_title"], layout="wide")
st.title(f"⚡ {T['page_title']}")

# ==========================================
# 2. API Key 設定
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing! Please set GEMINI_API_KEY in Secrets.")
    st.stop()

# ==========================================
# 3. 側邊欄與即時指標
# ==========================================
st.sidebar.divider()
st.sidebar.header("⚙️ Intel Config")
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
col1.metric("Current Time (CST)", current_tw_time.strftime("%Y-%m-%d %H:%M"))
col2.metric("Scan Window", "Past 24 Hours")

# ==========================================
# 4. 24H 核心情報生成邏輯 (多地搜尋來源)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    time_window = f"from {yesterday_tw_time.strftime('%Y-%m-%d %H:%M')} to {current_tw_time.strftime('%Y-%m-%d %H:%M')} (Taiwan Time)"
    
    with st.spinner(T["running"]):
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 深度強化 Prompt：嚴格執行 24H 限制與指定多國來源
                prompt = f"""
                Current Time: {current_tw_time.strftime('%Y-%m-%d %H:%M')} (Taiwan Time).
                Task: Generate a 'Past 24 Hours Only' AI Strategic Intelligence Report.
                Window: {time_window}.

                Search Strategy (STRICTLY within the last 24 hours):
                1. **Japan (日本)**: Prioritize Nikkei (日本経済新聞), Nikkan Kogyo (日刊工業新聞), ITmedia. Focus on GPU server demand (Sakura, Softbank) and Sovereign AI.
                2. **Taiwan (台灣)**: Prioritize Digitimes (電子時報), Economic Daily News (經濟日報), Commercial Times (工商時報). Focus on TSMC, Foxconn, Quanta, and cooling tech orders.
                3. **Worldwide (WW)**: Prioritize Reuters, CNBC, TechCrunch, The Verge, and Official Company Newsrooms (NVIDIA, Google, MSFT, AWS, OpenAI).
                
                Content Focus:
                - New hardware announcements or server purchase orders.
                - Data center expansion or investment news.
                - Breakthroughs in AI chips or cooling systems.
                - Key executive statements or policy changes in AI infrastructure.

                Output Requirements:
                - Language: {ui_lang}.
                - Provide specific citations/source names for news from the last 24 hours.
                - Format: Professional bullet-point executive summary.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=prompt,
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                )
                full_text = response.text
                break 
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    st.warning(f"{T['retry_msg']} (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(15) 
                else:
                    st.error(f"Error: {e}")
                    st.stop()

        if full_text:
            st.header(T["report_header"])
            st.info(f"Report Window: {time_window}")
            st.markdown(full_text)

            # ==========================================
            # 5. 安全郵件發送 (確保 24H 標籤)
            # ==========================================
            st.divider()
            email_subject = f"24H AI Intel Report - {report_date}"
            raw_summary = full_text[:600] # 稍微放寬摘要長度
            raw_body = (
                f"Hello Tony,\n\n"
                f"This is the latest 24-hour AI Intelligence update.\n"
                f"Generated at: {current_tw_time.strftime('%H:%M')} (CST)\n\n"
                f"--- 24H SUMMARY (WW, JP, TW) ---\n"
                f"{raw_summary}...\n\n"
                f"[See Full Analysis in the 2026 Dashboard]"
            )
            
            sub_enc = urllib.parse.quote(email_subject)
            body_enc = urllib.parse.quote(raw_body)
            mailto_link = f"mailto:tonyh@supermicro.com?subject={sub_enc}&body={body_enc}"
            
            st.markdown(
                f'''
                <a href="{mailto_link}" target="_blank" style="text-decoration: none;">
                    <button style="background-color: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 18px;">
                        {T["btn_email"]}
                    </button>
                </a>
                ''', 
                unsafe_allow_html=True
            )
            st.success(T["success"])

st.sidebar.divider()
st.sidebar.caption("Sourcing: Nikkei, Nikkan Kogyo, Digitimes, Reuters, CNBC")

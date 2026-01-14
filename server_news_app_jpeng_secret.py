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
today_str = current_tw_time.strftime('%Y-%m-%d')

# ==========================================
# 1. 專業多國語言定義 (切換為「當日最新」)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "AI 算力即時情報站 (當日最新)",
        "market_label": "戰略關注領域",
        "btn_run": "生成今日最新情報",
        "btn_email": "📧 寄送當日快報給 Tony",
        "running": f"正在檢索 {today_str} 全球、日本與台灣之即時動態...",
        "success": "今日戰報生成完成！",
        "report_header": f"🚀 {today_str} 當日最新 AI 算力與供應鏈即時情報",
        "retry_msg": "⚠️ 流量限制 (429)，正在重新抓取最新消息...",
        "markets": ["全球巨頭 (WW)", "NVIDIA/AMD 快報", "日本在地動態", "台灣供應鏈即時"]
    },
    "日本語": {
        "page_title": "AI 戦略インテリジェンス (当日最新)",
        "market_label": "戦略的注力領域",
        "btn_run": "当日最新のインテリジェンスを生成",
        "btn_email": "📧 当日速報を Tony に送信",
        "running": f"{today_str} の日本、台湾、グローバルの最新ニュースをスキャン中...",
        "success": "当日レポートが完了しました！",
        "report_header": f"🚀 {today_str} 當日最新：AI 算力・サプライチェーン速報",
        "retry_msg": "⚠️ 流量制限(429)を検知。最新情報を再取得中...",
        "markets": ["グローバル大手 (WW)", "NVIDIA/AMD 動向", "日本国内最新情報", "台湾サプライチェーン"]
    },
    "English": {
        "page_title": "AI Intel Center (Today's Latest)",
        "market_label": "Strategic Focus",
        "btn_run": "Generate Today's Latest Intel",
        "btn_email": "📧 Send Today's Intel to Tony",
        "running": f"Scanning today's ({today_str}) local media in TW, JP, and WW...",
        "success": "Today's Intelligence Generated!",
        "report_header": f"🚀 {today_str} Today's Latest: AI & Supply Chain Intel",
        "retry_msg": "⚠️ Rate limit (429) detected. Refreshing latest info...",
        "markets": ["Global Giants (WW)", "NVIDIA/AMD Dynamics", "Japan Latest", "Taiwan Supply Chain"]
    }
}

ui_lang = st.sidebar.radio("🌐 Language Selector", ["繁體中文", "日本語", "English"])
T = LANG_LABELS[ui_lang]

st.set_page_config(page_title=T["page_title"], layout="wide")
st.title(f"🚀 {T['page_title']}")

# ==========================================
# 2. API Key 設定
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing!")
    st.stop()

# ==========================================
# 3. 側邊欄指標
# ==========================================
st.sidebar.divider()
st.sidebar.header("⚙️ Intel Config")
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
col1.metric("Current Date (CST)", today_str)
col2.metric("Intelligence Priority", "BREAKING NEWS")

# ==========================================
# 4. 當日核心情報生成邏輯 (強調 Today's Breaking News)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    with st.spinner(T["running"]):
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 終極強化 Prompt：鎖定「當日最新」並要求引用今日來源
                prompt = f"""
                Current Date/Time: {current_tw_time.strftime('%Y-%m-%d %H:%M')} (Taiwan Time).
                Task: Generate a 'Today's Latest Breaking News' AI Strategic Report.
                
                Search Focus (STRICTLY prioritize news from {today_str}):
                1. **Japan**: Today's breaking stories from Nikkei, Nikkan Kogyo, and Yahoo News Japan Tech. Focus on any server orders or data center deals announced today.
                2. **Taiwan**: Today's top headlines from Digitimes, Economic Daily News, and Commercial Times. Focus on TSMC daily ops, AI server shipments (Foxconn/Quanta/Wistron) and cooling tech news.
                3. **Worldwide (WW)**: Today's breaking news from Reuters, CNBC, Bloomberg Technology, and official company press releases from NVIDIA, AMD, and the Cloud Giants (AWS/Azure/GCP).

                Key Intelligence Requirements:
                - Highlight news items that were published within the last 12-18 hours leading up to {today_str}.
                - Provide specific citations for each "Today's News" item.
                - Focus on actionable BD intel: "Who is buying?", "Who is building?", "Who is supplying?".

                Output Requirements:
                - Language: {ui_lang}.
                - Format: High-level executive briefing with bullet points.
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
            st.markdown(full_text)

            # ==========================================
            # 5. 安全郵件發送 (主題標註當日)
            # ==========================================
            st.divider()
            email_subject = f"TODAY'S AI BREAKING INTEL - {today_str}"
            raw_summary = full_text[:600]
            raw_body = (
                f"Hello Tony,\n\n"
                f"Here is today's ({today_str}) latest AI market intelligence.\n"
                f"Generated at: {current_tw_time.strftime('%H:%M')} (CST)\n\n"
                f"--- TODAY'S BREAKING SUMMARY ---\n"
                f"{raw_summary}...\n\n"
                f"[Full Real-time Dashboard Access Required]"
            )
            
            sub_enc = urllib.parse.quote(email_subject)
            body_enc = urllib.parse.quote(raw_body)
            mailto_link = f"mailto:tonyh@supermicro.com?subject={sub_enc}&body={body_enc}"
            
            st.markdown(
                f'''
                <a href="{mailto_link}" target="_blank" style="text-decoration: none;">
                    <button style="background-color: #d9534f; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 18px;">
                        {T["btn_email"]}
                    </button>
                </a>
                ''', 
                unsafe_allow_html=True
            )
            st.success(T["success"])

st.sidebar.divider()
st.sidebar.caption(f"Status: Monitoring live for {today_str}")

import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 

# ==========================================
# 0. 台灣時區設定 (CST)
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)

# ==========================================
# 1. 專業混合命名與多國語言定義
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "全球 AI 算力戰略與供應鏈導航中心",
        "market_label": "戰略關注領域",
        "btn_run": "生成全球戰略情報報告",
        "btn_email": "📧 寄送報告給 Tony",
        "running": "正在掃描全球科技巨頭、日本服務供應商與 AI 供應鏈...",
        "success": "戰略分析完成！",
        "report_header": "🔍 全球 AI 算力與供應鏈整合導航報告",
        "markets": ["WW Giant Tech", "NVIDIA/AMD 戰略", "日本大型 SP 與垂直市場", "台灣 AI 供應鏈核心"]
    },
    "日本語": {
        "page_title": "グローバル AI 算力戦略・サプライチェーンナビゲーター",
        "market_label": "戦略的注力領域",
        "btn_run": "戦略インテリジェンス報告を生成",
        "btn_email": "📧 Tonyにレポートを送信",
        "running": "日本大手SP、垂直市場、テック大手を分析中...",
        "success": "戦略分析が完了しました！",
        "report_header": "🔍 グローバル AI 算力・サプライチェーン統合報告",
        "markets": ["WWテック大手", "NVIDIA/AMD 戦略", "日本大手SP・垂直市場", "台湾サプライチェーン"]
    },
    "English": {
        "page_title": "Global AI Strategy & Supply Chain Navigator",
        "market_label": "Strategic Focus",
        "btn_run": "Generate Strategic Intelligence",
        "btn_email": "📧 Send Report to Tony",
        "running": "Scanning Tech Giants, JP Service Providers & AI Verticals...",
        "success": "Strategic Intelligence Generated!",
        "report_header": "🔍 Global AI & Supply Chain Integrated Intelligence",
        "markets": ["WW Giant Tech", "NVIDIA/AMD Dynamics", "Japan SP & Vertical Market", "Taiwan Supply Chain"]
    }
}

# 介面語系選擇
ui_lang = st.sidebar.radio("🌐 Select Language", ["繁體中文", "日本語", "English"])
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
    st.error("API Key missing! Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# ==========================================
# 3. 側邊欄與時間指標 (Taiwan Time CST)
# ==========================================
st.sidebar.divider()
st.sidebar.header("⚙️ Strategic Config")
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
col1.metric("Taiwan Time (CST)", current_tw_time.strftime("%Y-%m-%d %H:%M"))
col2.metric("Market Monitor", "2026 LIVE")

# ==========================================
# 4. 戰略情報生成邏輯 (已整合日本 SP 與在地媒體搜尋)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        try:
            # 整合您的最新需求：日本 SP 動態、垂直市場與在地媒體
            prompt = f"""
            Today's Date: {report_date} (Taiwan Time).
            Task: Integrated Strategic AI Intelligence Report for {ui_lang}.
            
            Sourcing Strategy: 
            Prioritize local news and vertical-specific journals for high-fidelity intelligence.
            - **Japan**: Focus on Nikkei (日本経済新聞), Nikkan Kogyo Shimbun (日刊工業新聞), and Semiconductor Portal.
            - **Taiwan**: Focus on Digitimes, Commercial Times (工商時報), and Economic Daily News.
            
            Intelligence Focus:
            1. **Global Tech Giants (WW Giant Tech)**: Latest moves by Google, MSFT, AWS, Meta, Apple in AI infrastructure.
            2. **Japanese Service Providers & AI Industry**: 
               - Strategic updates on SoftBank (AI-RAN/OpenAI investment), Sakura Internet (GPU capacity expansion), and NTT (IOWN/LLM).
               - Japanese AI industry startups and ecosystem dynamics.
            3. **Japan AI Vertical Supply Chain**: 
               - Japan's role in AI-driven industrial robotics, medical AI hardware, and automotive (AD/SDV).
            4. **Taiwan AI Supply Chain**: TSMC (Advanced packaging), Quanta, Foxconn, and latest Liquid Cooling developments.
            
            Output Requirements:
            - Language: {ui_lang}.
            - Format: Professional Business Intelligence report with structured Markdown headings.
            - Content: Integrated analysis of supply chain movements and actionable BD strategies.
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            full_text = response.text
            
            st.header(T["report_header"])
            st.markdown(full_text)

            # ==========================================
            # 5. 安全郵件發送 (透過 mailto)
            # ==========================================
            st.divider()
            email_subject = f"Strategic AI Report: {T['page_title']} - {report_date}"
            email_body = f"Hello Tony,\n\nSource: {T['page_title']}\nGenerated at: {current_tw_time.strftime('%H:%M')} (CST)\n\n{full_text}"
            
            subject_encoded = urllib.parse.quote(email_subject)
            body_encoded = urllib.parse.quote(email_body)
            mailto_link = f"mailto:tonyh@supermicro.com?subject={subject_encoded}&body={body_encoded}"
            
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
            
        except Exception as e:
            st.error(f"Execution Error: {e}")

st.sidebar.divider()
st.sidebar.caption("System: 2026 AI Strategy Navigator")

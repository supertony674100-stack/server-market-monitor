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
        "running": "正在優先掃描在地媒體、科技巨頭與 AI 供應鏈動態...",
        "success": "戰略報告生成完成！",
        "report_header": "🔍 全球 AI 算力與供應鏈整合導航報告",
        "markets": ["WW Giant Tech", "NVIDIA/AMD 戰略", "日本市場 Sovereign AI", "台灣 AI 供應鏈核心"]
    },
    "日本語": {
        "page_title": "グローバル AI 算力戦略・サプライチェーンナビゲーター",
        "market_label": "戦略的注力領域",
        "btn_run": "戦略インテリジェンス報告を生成",
        "btn_email": "📧 Tonyにレポートを送信",
        "running": "ローカルメディア、テック大手、サプライチェーンを分析中...",
        "success": "戦略分析が完了しました！",
        "report_header": "🔍 グローバル AI 算力・サプライチェーン統合報告",
        "markets": ["WWテック大手", "NVIDIA/AMD 戦略", "日本国内市場動向", "台湾サプライチェーン"]
    },
    "English": {
        "page_title": "Global AI Strategy & Supply Chain Navigator",
        "market_label": "Strategic Focus",
        "btn_run": "Generate Strategic Intelligence",
        "btn_email": "📧 Send Report to Tony",
        "running": "Prioritizing local media & global infrastructure scanning...",
        "success": "Strategic Intelligence Generated!",
        "report_header": "🔍 Global AI & Supply Chain Integrated Intelligence",
        "markets": ["WW Giant Tech", "NVIDIA/AMD Dynamics", "Japan Market Insights", "Taiwan Supply Chain"]
    }
}

ui_lang = st.sidebar.radio("🌐 Select Interface Language", ["繁體中文", "日本語", "English"])
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
# 3. 側邊欄與時間指標
# ==========================================
st.sidebar.divider()
st.sidebar.header("⚙️ Strategic Config")
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2 = st.columns(2)
col1.metric("Taiwan Time (CST)", current_tw_time.strftime("%Y-%m-%d %H:%M"))
col2.metric("Market Monitor", "2026 LIVE")

# ==========================================
# 4. 戰略情報生成邏輯 (在地媒體搜尋強化)
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        try:
            # 關鍵修改點：在 Prompt 中強制要求在地媒體來源
            prompt = f"""
            Today's Date: {report_date} (Taiwan Time).
            Task: Integrated Strategic AI Intelligence Report for {ui_lang}.
            
            Sourcing Strategy: 
            Actively search for and prioritize local news media and industry-specific journals from each region to ensure first-hand intelligence. 
            - For Japan: Prioritize sources like Nikkei (日本経済新聞), NHK, and ITmedia.
            - For Taiwan: Prioritize sources like Commercial Times (工商時報), Economic Daily News (經濟日報), and Digitimes.
            
            Intelligence Focus:
            1. **Global Tech Giants (WW Giant Tech)**: Latest moves by Google, Microsoft, Amazon (AWS), Meta, and Apple.
            2. **GPU & Accelerator Landscape**: NVIDIA (Blackwell/GB200) and AMD (MI300/400) updates.
            3. **Japan Sovereign AI & Market**: GPU server demand from Sakura Internet, SoftBank, and NTT.
            4. **Taiwan Supply Chain Ecosystem**: Critical updates on TSMC (CoWoS/Advanced Nodes), Foxconn, Quanta, and thermal management (Liquid Cooling).
            
            Output Requirements:
            - Language: {ui_lang}.
            - Format: Professional Business Intelligence report with structured Markdown headings.
            - Content: Merge 'Supply Chain Trends' and 'BD Strategies' into a single coherent analysis.
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
            
            mailto_link = f"mailto:tonyh@supermicro.com?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"
            
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

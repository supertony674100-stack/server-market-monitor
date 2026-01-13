import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime

# ==========================================
# 0. 多國語言介面與內容語言定義
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "24H 全球 AI & 伺服器戰情室",
        "sidebar_header": "搜尋偏好設定",
        "market_label": "關注市場與即時來源",
        "ui_lang_label": "切換系統語言",
        "btn_run": "立即獲取今日情報",
        "running": "正在分析全球動態並擬定開發策略...",
        "success": "情報分析與開發策略已生成！",
        "summary_title": "🎯 業務機會與建議開發策略",
        "markets": ["全球 (USA/Global IT)", "日本 (Local Companies)", "台灣 (Supply Chain)"]
    },
    "日本語": {
        "page_title": "24H 全球 AI & サーバー戦況ルーム",
        "sidebar_header": "検索設定",
        "market_label": "注目市場とリアルタイムソース",
        "ui_lang_label": "システム語言切替",
        "btn_run": "今日の情報と戦略を取得",
        "running": "各地の動向をスキャンし、開発戦略を策定中...",
        "success": "インテリジェンス分析と開発戦略が完了しました！",
        "summary_title": "🎯 営業機会と推奨開発戦略",
        "markets": ["グローバル (USA/Global IT)", "日本 (国内企業)", "台湾 (サプライチェーン)"]
    },
    "English": {
        "page_title": "24H Global AI & Server Intelligence",
        "sidebar_header": "Search Preferences",
        "market_label": "Target Markets & Live Sources",
        "ui_lang_label": "Switch System Language",
        "btn_run": "Fetch Today's Intelligence & Strategy",
        "running": "Scanning trends and formulating development strategies...",
        "success": "Intelligence & Strategy Analysis Complete!",
        "summary_title": "🎯 Business Opportunities & Development Strategies",
        "markets": ["Global (USA/Global IT)", "Japan (Local Companies)", "Taiwan (Supply Chain)"]
    }
}

# 1. 介面設定
if "lang_choice" not in st.session_state:
    st.session_state.lang_choice = "繁體中文"

ui_lang = st.sidebar.radio("🌐 Language Select", ["繁體中文", "日本語", "English"], key="lang_choice")
T = LANG_LABELS[ui_lang]

st.set_page_config(page_title=T["page_title"], layout="wide")
st.title(f"📊 {T['page_title']}")

# 2. 安全讀取金鑰
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing! Please set GEMINI_API_KEY in Secrets.")
    st.stop()

# 3. 側邊欄設定
st.sidebar.divider()
st.sidebar.header(T["sidebar_header"])

selected_markets = st.sidebar.multiselect(
    T["market_label"], 
    T["markets"],
    default=T["markets"]
)

if st.sidebar.button(T["btn_run"]):
    current_date = datetime.now().strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        try:
            # 構建包含「建議開發策略」的進階 Prompt
            prompt = f"""
            Today's Date: {current_date}
            Task: Act as a Senior Business Development (BD) Manager in the AI Server industry.
            Provide a high-level market intelligence report and actionable development strategies.
            
            Strict Sourcing Instructions:
            - Global: Latest real-time AI/IT trends from USA/Europe (e.g., NVIDIA updates, Hyperscaler CapEx).
            - Japan: Prioritize Japanese local news regarding companies like Sakura Internet, SoftBank, NTT, etc.
            - Taiwan: Focus on the latest Supply Chain movements (TSMC, ODM/OEMs).
            
            Report Structure:
            1. LATEST MARKET NEWS (Specific to: {', '.join(selected_markets)})
            2. SUPPLY CHAIN & TECH TRENDS (Focus on Blackwell, Liquid Cooling, or specialized AI chips)
            3. SUMMARY & RECOMMENDED DEVELOPMENT STRATEGIES:
               - Identify specific companies or government projects with high potential.
               - Explain WHY they are opportunities (e.g., new data center announcement, government subsidy).
               - RECOMMEND A STRATEGY: Provide specific, actionable advice on how to approach these leads (e.g., "Highlight liquid cooling compatibility," "Position as a redundant supplier for GPU clusters," or "Engage with their procurement team regarding the upcoming Q3 expansion").
            
            Constraints:
            - Use a highly professional, strategic consultant tone.
            - NO email headers, signatures, or generic greetings.
            - The entire output MUST be in {ui_lang}.
            """

            # 使用 gemini-2.5-flash
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())] 
                )
            )

            st.success(T["success"])
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Execution Error: {e}")

st.sidebar.divider()
st.sidebar.caption(f"System Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

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
        "market_label": "關注領域",
        "btn_run": "立即分析情報",
        "running": "正在掃描 NVIDIA, AMD, Google, MSFT 與在地動態...",
        "success": "分析完成！",
        "tabs": ["🔥 最新情報", "📈 供應鏈趨勢", "🎯 建議開發策略"],
        "markets": ["全球 (NVIDIA/AMD/IT 巨頭)", "日本 (Local Companies)", "台灣 (Supply Chain)"]
    },
    "日本語": {
        "page_title": "24H 全球 AI & サーバー戦況ルーム",
        "market_label": "注目領域",
        "btn_run": "情報を取得して分析",
        "running": "NVIDIA, AMD, Google, MSFT などの最新動向を分析中...",
        "success": "分析と戦略策定が完了しました！",
        "tabs": ["🔥 最新ニュース", "📈 サプライチェーン", "🎯 推導開発戦略"],
        "markets": ["グローバル (NVIDIA/AMD/IT大手)", "日本 (国内企業)", "台湾 (サプライチェーン)"]
    },
    "English": {
        "page_title": "24H Global AI & Server Intelligence",
        "market_label": "Target Domains",
        "btn_run": "Fetch Intelligence",
        "running": "Scanning NVIDIA, AMD, Google, MSFT and more...",
        "success": "Analysis Complete!",
        "tabs": ["🔥 News", "📈 Tech Trends", "🎯 Strategies"],
        "markets": ["Global (NVIDIA/AMD/Big Tech)", "Japan (Local Companies)", "Taiwan (Supply Chain)"]
    }
}

# 1. 介面語系選擇 (驅動整個 GUI)
ui_lang = st.sidebar.radio("🌐 Select Language", ["繁體中文", "日本語", "English"])
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

# 3. 側邊欄：搜尋設定 (手機版會自動隱藏，點擊左上角才彈出)
st.sidebar.divider()
st.sidebar.header("⚙️ Search Config")
selected_markets = st.sidebar.multiselect(
    T["market_label"], 
    T["markets"],
    default=T["markets"]
)

# --- 手機頂部優化：使用卡片呈現指標 ---
col1, col2 = st.columns(2)
col1.metric("Update Time", datetime.now().strftime("%H:%M"))
col2.metric("Market Monitor", "2026 LIVE")

if st.sidebar.button(T["btn_run"]):
    current_date = datetime.now().strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        try:
            # 針對四大巨頭、日本、台灣構建強效 Prompt
            prompt = f"""
            Today's Date: {current_date}
            Task: Senior BD Manager Intelligence Report. 
            Focus specifically on NVIDIA, AMD, Google, and Microsoft AI infrastructures.
            
            Strict Sourcing Instructions:
            - Global: Real-time trends of NVIDIA, AMD, Google, and Microsoft (new AI chips, server orders, data center CapEx).
            - Japan: Prioritize local news on companies like Sakura Internet, SoftBank, NTT, etc.
            - Taiwan: Latest Supply Chain movements (TSMC, Quanta, Foxconn, etc.).
            
            Format Instructions:
            Separate the report into exactly three parts using these specific markers:
            [PART_1_NEWS] - Today's headlines and IT giant dynamics.
            [PART_2_TECH] - Supply chain & Blackwell/Liquid Cooling trends.
            [PART_3_STRATEGY] - Summary, identified opportunities, and RECOMMENDED BD STRATEGIES for each.
            
            Constraints:
            - The entire output MUST be in {ui_lang}.
            - No email headers or signatures.
            - Professional, actionable consultant tone.
            """

            # 使用 gemini-2.5-flash
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())] 
                )
            )

            full_text = response.text
            
            # 簡易解析邏輯將內容分入三個 Tab
            parts = {"NEWS": "", "TECH": "", "STRATEGY": ""}
            try:
                parts["NEWS"] = full_text.split("[PART_1_NEWS]")[1].split("[PART_2_TECH]")[0]
                parts["TECH"] = full_text.split("[PART_2_TECH]")[1].split("[PART_3_STRATEGY]")[0]
                parts["STRATEGY"] = full_text.split("[PART_3_STRATEGY]")[1]
            except:
                parts["NEWS"] = full_text # 備援邏輯

            # --- 手機友善：分頁呈現 ---
            tab1, tab2, tab3 = st.tabs(T["tabs"])
            
            with tab1:
                st.markdown(parts["NEWS"])
            
            with tab2:
                st.markdown(parts["TECH"])
            
            with tab3:
                st.success("🎯 Business Development Opportunities & Strategies")
                st.markdown(parts["STRATEGY"])
            
        except Exception as e:
            st.error(f"Execution Error: {e}")

st.sidebar.divider()
with st.sidebar.expander("ℹ️ About System"):
    st.caption("2026 AI Intelligence Dashboard")
    st.caption(f"Optimized for Mobile & Desktop")

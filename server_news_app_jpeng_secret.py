import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime

# ==========================================
# 0. 多國語言介面定義 (新增分頁標籤與手機市場)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "24H 全球 AI & 伺服器 & 行動通訊戰情室",
        "market_label": "關注領域",
        "btn_run": "立即分析情報",
        "running": "正在掃描 NVIDIA, AMD, Google, MSFT 等巨頭動態...",
        "success": "分析完成！",
        "tabs": ["🔥 最新情報", "📈 供應鏈趨勢", "🎯 建議開發策略"],
        "markets": ["全球 (NVIDIA/AMD/IT 巨頭)", "日本 (Local Companies)", "台灣 (Supply Chain)", "行動裝置 (AI Phone)"]
    },
    "日本語": {
        "page_title": "24H 全球 AI & サーバー & モバイル戦況ルーム",
        "market_label": "注目領域",
        "btn_run": "情報を取得して分析",
        "running": "NVIDIA, AMD, Google, MSFT などの最新動向を分析中...",
        "success": "分析と戦略策定が完了しました！",
        "tabs": ["🔥 最新ニュース", "📈 サプライチェーン", "🎯 推奨開発戦略"],
        "markets": ["グローバル (NVIDIA/AMD/IT大手)", "日本 (国内企業)", "台湾 (サプライチェーン)", "モバイル (AIスマホ)"]
    },
    "English": {
        "page_title": "24H Global AI, Server & Mobile Intelligence",
        "market_label": "Target Domains",
        "btn_run": "Fetch Intelligence",
        "running": "Scanning NVIDIA, AMD, Google, MSFT and more...",
        "success": "Analysis Complete!",
        "tabs": ["🔥 News", "📈 Tech Trends", "🎯 Strategies"],
        "markets": ["Global (NVIDIA/AMD/Big Tech)", "Japan (Local Companies)", "Taiwan (Supply Chain)", "Mobile (AI Phone)"]
    }
}

# 1. 介面語系選擇 (驅動 GUI)
ui_lang = st.sidebar.radio("🌐 Select Language", ["繁體中文", "日本語", "English"])
T = LANG_LABELS[ui_lang]

st.set_page_config(page_title=T["page_title"], layout="wide")
st.title(f"📊 {T['page_title']}")

# 2. 安全讀取金鑰
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key missing in Secrets!")
    st.stop()

# 3. 側邊欄設定 (手機版會自動收納)
st.sidebar.header("⚙️ Search Config")
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

# --- 手機頂部資訊卡 ---
col1, col2 = st.columns(2)
col1.metric("Update Time", datetime.now().strftime("%H:%M"))
col2.metric("Market Status", "2026 ACTIVE")

if st.sidebar.button(T["btn_run"]):
    with st.spinner(T["running"]):
        try:
            # 構建結構化 Prompt 以便後續分頁顯示
            prompt = f"""
            Today: {datetime.now().strftime("%Y-%m-%d")}
            Task: AI Server BD Strategy Report (NVIDIA/AMD/Google/Microsoft focus).
            
            Strict Search Guidelines:
            - Global: Real-time trends of NVIDIA, AMD, Google, and Microsoft (AI chips, server demand, cloud Capex).
            - Japan: Local companies (Sakura, SoftBank, NTT) & government AI subsidies.
            - Taiwan: TSMC and ODM supply chain movements.
            - Mobile: AI Phone trends affecting data center demand.

            Format: You MUST separate the report into exactly three parts using these headers:
            [PART_1_NEWS]
            [PART_2_TECH]
            [PART_3_STRATEGY]
            
            - Identify business opportunities and provide actionable STRATEGY for each lead.
            - Entire output MUST be in {ui_lang}.
            - Professional tone, no email headers.
            """

            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            
            # --- 處理分頁顯示邏輯 ---
            full_text = response.text
            parts = {"NEWS": "", "TECH": "", "STRATEGY": ""}
            
            # 簡易解析邏輯
            if "[PART_1_NEWS]" in full_text and "[PART_2_TECH]" in full_text:
                parts["NEWS"] = full_text.split("[PART_1_NEWS]")[1].split("[PART_2_TECH]")[0]
                parts["TECH"] = full_text.split("[PART_2_TECH]")[1].split("[PART_3_STRATEGY]")[0]
                parts["STRATEGY"] = full_text.split("[PART_3_STRATEGY]")[1]
            else:
                parts["NEWS"] = full_text # 備援：若解析失敗則全部顯示在第一頁

            # 建立分頁標籤 (手機友善佈局)
            tab_news, tab_tech, tab_strategy = st.tabs(T["tabs"])
            
            with tab_news:
                st.markdown(parts["NEWS"])
                
            with tab_tech:
                st.markdown(parts["TECH"])
                
            with tab_strategy:
                st.success(T["summary_title"] if "summary_title" in T else "🎯 Recommended BD Strategies")
                st.markdown(parts["STRATEGY"])

        except Exception as e:
            st.error(f"Error: {e}")

# 底部署名與摺疊區塊
with st.expander("ℹ️ About this System"):
    st.write("2026 AI Intelligence Dashboard optimized for Mobile/PC. Powered by Gemini 2.5.")

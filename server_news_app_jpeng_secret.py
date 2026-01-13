import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 0. 多國語言介面定義
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "AI 伺服器市場動態監測",
        "sidebar_header": "設定與搜尋",
        "market_label": "關注市場",
        "ui_lang_label": "介面語言 (UI Language)",
        "output_lang_label": "報告輸出語言",
        "btn_run": "開始生成報告",
        "running": "正在搜尋當地新聞並分析中...",
        "success": "報告生成完成！",
        "error_key": "找不到 API 金鑰。請設定 GEMINI_API_KEY。",
        "markets": ["全球 (USA 來源)", "日本 (Local 來源)", "台灣供應鏈 (Local 來源)"]
    },
    "日本語": {
        "page_title": "AI サーバー市場動向モニタリング",
        "sidebar_header": "設定と検索",
        "market_label": "注目の市場",
        "ui_lang_label": "UI言語",
        "output_lang_label": "レポート出力言語",
        "btn_run": "レポート作成開始",
        "running": "各地のローカルニュースを検索し分析中...",
        "success": "レポートの作成が完了しました！",
        "error_key": "APIキーが見つかりません。GEMINI_API_KEYを設定してください。",
        "markets": ["グローバル (USAソース)", "日本 (ローカルソース)", "台湾サプライチェーン (ローカルソース)"]
    },
    "English": {
        "page_title": "AI Server Market Intelligence",
        "sidebar_header": "Settings & Search",
        "market_label": "Target Markets",
        "ui_lang_label": "UI Language",
        "output_lang_label": "Report Language",
        "btn_run": "Generate Report",
        "running": "Searching local news and analyzing...",
        "success": "Report generated successfully!",
        "error_key": "API Key not found. Please set GEMINI_API_KEY.",
        "markets": ["Global (USA Sources)", "Japan (Local Sources)", "Taiwan (Local Sources)"]
    }
}

# 1. 介面語系選擇 (放在最前面以驅動整個 GUI)
ui_lang = st.sidebar.radio("Select Interface Language", ["繁體中文", "日本語", "English"])
T = LANG_LABELS[ui_lang]

st.set_page_config(page_title=T["page_title"], layout="wide")
st.title(f"🌐 {T['page_title']}")

# 2. 安全讀取金鑰
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error(T["error_key"])
    st.stop()

# 3. 側邊欄設定
st.sidebar.divider()
st.sidebar.header(T["sidebar_header"])

selected_markets = st.sidebar.multiselect(
    T["market_label"], 
    T["markets"],
    default=[T["markets"][0], T["markets"][1]]
)

report_lang = st.sidebar.selectbox(
    T["output_lang_label"],
    ["繁體中文", "日本語", "English"]
)

if st.sidebar.button(T["btn_run"]):
    with st.spinner(T["running"]):
        try:
            # 建立針對地區來源的 Prompt
            prompt = f"""
            Task: Provide a deep-dive analysis of the AI server market (focusing on GPU servers, Blackwell, and Data Centers).
            
            Strict Search Guidelines:
            1. For '日本 (Local 來源)': You MUST search and prioritize local Japanese sources (e.g., Nikkei, ITmedia, PC Watch, and corporate press releases in Japan).
            2. For '台灣供應鏈 (Local 來源)': You MUST search and prioritize Taiwan-based tech news (e.g., Digitimes, MoneyDJ, TechNews.tw, Commercial Times).
            3. For '全球 (USA 來源)': You MUST search and prioritize USA-based industry news (e.g., Bloomberg, CNBC, TechCrunch, Next Platform).
            
            Target Markets to analyze: {', '.join(selected_markets)}
            
            Format Instructions:
            - DO NOT use email format (No 'Dear', 'Best regards', or email headers).
            - Use a professional market research report style with clear headings.
            - At the end of the report, provide a dedicated "SUMMARY" section highlighting key takeaways.
            - The entire report MUST be written in {report_lang}.
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

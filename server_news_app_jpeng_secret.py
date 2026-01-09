import streamlit as st
from google import genai
from google.genai import types

# 1. 網頁介面設定
st.set_page_config(page_title="全球伺服器市場分析", layout="wide")
st.title("🌐 全球 & 日本伺服器市場動態監測 (安全發布版)")

# 2. 安全讀取金鑰：從 Streamlit 雲端加密設定中讀取
# 部署後，請在 Streamlit Cloud 的 Advanced Settings -> Secrets 設定此金鑰
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("找不到 API 金鑰設定。請在 Streamlit Secrets 中設定 GEMINI_API_KEY。")
    st.stop()

# 3. 側邊欄：搜尋與語言設定
st.sidebar.header("搜尋與語系設定")
market_focus = st.sidebar.multiselect(
    "關注市場", 
    ["全球 (Global)", "日本 (Japan)", "台灣供應鏈 (Taiwan)"],
    default=["全球 (Global)", "日本 (Japan)"]
)

output_lang = st.sidebar.selectbox(
    "輸出報告語言",
    ["繁體中文 (Traditional Chinese)", "商務日文 (Business Japanese)", "商務英文 (Business English)"]
)

if st.sidebar.button("開始分析並生成報告"):
    with st.spinner(f'正在以 {output_lang} 分析伺服器市場動態...'):
        try:
            prompt = f"""
            請搜尋 2026 年關於 {', '.join(market_focus)} 伺服器市場（特別是 GPU Server、NVIDIA Blackwell 系列）的最新新聞。
            請以專業「市場開發經理」口吻，包含供應鏈趨勢、日本企業動態與業務開發機會。
            [重要]：請全程使用「{output_lang}」撰寫。
            """

            # 使用你帳號清單中確認可用的 gemini-2.5-flash
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())] 
                )
            )

            st.success(f"報告生成完成！")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"執行錯誤：{e}")

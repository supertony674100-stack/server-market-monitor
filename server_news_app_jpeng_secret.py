import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 
import time 

# ==========================================
# 1. 核心定義 (包含 Tony 專屬標籤)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "page_title": "2026 全球 AI 算力戰略監控中心",
        "market_label": "戰略關注領域 (24H 監控)",
        "btn_run": "執行深度戰略掃描",
        "btn_email": "📧 將今日報告寄送至我的 Email (tonyh@supermicro.com)",
        "running": "正在調用 Google Search 掃描供應鏈動態...",
        "success": "戰略報告生成完成！",
        "report_header": "🔍 2026 AI 算力與供應鏈即時戰略報告",
        "retry_msg": "⏳ 正在避開流量高峰 (快速重試)...",
        "markets": ["WW Giant Tech", "NVIDIA/AMD 戰略", "日本市場 (Sakura/SoftBank)", "台灣供應鏈 (液冷/網通)"]
    },
    "日本語": {
        "page_title": "2026 グローバル AI 算力戦略ナビゲーター",
        "market_label": "戦略的注力領域",
        "btn_run": "戦略報告を生成",
        "btn_email": "📧 レポートをメールで送信",
        "running": "日本・台湾市場データを深度分析中...",
        "success": "戦略分析が完了しました！",
        "report_header": "🔍 2026 グローバル AI 算力・サプライチェーン報告",
        "retry_msg": "⏳ 再試行中...",
        "markets": ["WWテック大手", "NVIDIA/AMD 戦略", "日本国内DC", "台灣サプライチェーン"]
    },
    "English": {
        "page_title": "2026 Global AI Strategy Navigator",
        "market_label": "Strategic Focus",
        "btn_run": "Generate Strategic Intelligence",
        "btn_email": "📧 Send Report to my Email",
        "running": "Deep scanning markets...",
        "success": "Intelligence Generated!",
        "report_header": "🔍 2026 Global AI & Supply Chain Strategic Report",
        "retry_msg": "⏳ Retrying...",
        "markets": ["WW Giant Tech", "NVIDIA/AMD Dynamics", "Japan DC Expansion", "Taiwan SC (Liquid Cooling)"]
    }
}

# --- 頁面初始化 ---
st.set_page_config(page_title="AI Strategy Navigator", layout="wide")
ui_lang = st.sidebar.radio("🌐 Language Selector", list(LANG_LABELS.keys()))
T = LANG_LABELS[ui_lang]

st.title(f"🚀 {T['page_title']}")
st.info("ℹ️ **系統狀態：24H 持續監控中**。已開啟 Google Search 深度檢索功能。")

# ==========================================
# 2. 環境與 API 設定 (Paid Tier 優化)
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key 缺失！請確保已在 Streamlit Secrets 設定 GEMINI_API_KEY。")
    st.stop()

st.sidebar.divider()
selected_markets = st.sidebar.multiselect(T["market_label"], T["markets"], default=T["markets"])

col1, col2, col3 = st.columns(3)
col1.metric("Current Time (CST)", current_tw_time.strftime("%Y-%m-%d %H:%M"))
col2.metric("Market Status", "2026 LIVE")
col3.metric("Service Tier", "Paid Tier Active")

# ==========================================
# 3. 戰略掃描與郵件發送邏輯
# ==========================================
if st.sidebar.button(T["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(T["running"]):
        
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 結合 Tony 關注的日本 DC 與台灣液冷/網通指令
                strategic_prompt = f"""
                Current Date: {report_date}. 
                Analysis Task: Strategic Supply Chain Intelligence for {ui_lang}.
                
                Mandatory Focus:
                1. **Japan Market**: 
                   - Investigate Sakura Internet's AI data center expansion and GPU procurement status.
                   - Monitor SoftBank's 2026 AI-RAN and large-scale DC development in Hokkaido.
                2. **Taiwan Supply Chain**:
                   - Track Liquid Cooling (AVC, Auras, Vertiv, Cooler Master) capacity for NVIDIA Blackwell.
                   - Track Networking updates (800G/1.6T switches, CPO adoption) for key networking players.
                3. **Global Context**: {', '.join(selected_markets)}.
                """

                # 使用 2.0-Flash 獲取最新即時搜尋結果
                response = client.models.generate_content(
                    model='gemini-2.0-flash', 
                    contents=strategic_prompt,
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                )
                full_text = response.text
                break
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    st.warning(f"{T['retry_msg']} (Attempt {attempt + 1})")
                    time.sleep(5) 
                else:
                    st.error(f"Execution Error: {e}")
                    st.stop()

        if full_text:
            st.header(T["report_header"])
            st.markdown(full_text)
            st.success(T["success"])

            # --- 郵件發送選項 (Option) ---
            st.divider()
            email_subject = f"AI Strategy Report - {report_date}"
            # 將報告內容前 1000 字編碼至郵件本文中
            email_body_preview = full_text[:1000].replace('\n', '%0D%0A')
            email_body = f"Hello Tony,%0D%0A%0D%0AThis is your AI Strategy Report for {report_date}.%0D%0A%0D%0A--- REPORT START ---%0D%0A{email_body_preview}...%0D%0A--- REPORT END ---%0D%0A%0D%0AGenerated by Gemini 2.0 Strategic Hub."
            
            mailto_link = f"mailto:tonyh@supermicro.com?subject={urllib.parse.quote(email_subject)}&body={email_body}"
            
            st.markdown(
                f'''
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6;">
                    <h4 style="margin-top: 0;">📬 戰略報告存檔選項</h4>
                    <p style="font-size: 14px; color: #555;">您可以點擊下方按鈕將此報告發送至您的 Supermicro 信箱以進行備份：</p>
                    <a href="{mailto_link}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px;">
                            {T["btn_email"]}
                        </button>
                    </a>
                </div>
                ''', 
                unsafe_allow_html=True
            )

st.sidebar.divider()
st.sidebar.caption(f"Last Intelligence Sync: {current_tw_time.strftime('%Y-%m-%d %H:%M:%S')}")

import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import urllib.parse
import pytz 
import time 

# ==========================================
# 0. 時區與快取設定
# ==========================================
tw_tz = pytz.timezone('Asia/Taipei')
current_tw_time = datetime.now(tw_tz)

# 使用 Streamlit 快取，避免重複點擊按鈕時觸發 429
@st.cache_data(ttl=3600)  # 快取 1 小時
def get_ai_intelligence(report_date, ui_lang, markets_str):
    # 此處邏輯移至下方按鈕觸發
    pass

# ==========================================
# 1. 多國語言定義 (縮短重試秒數)
# ==========================================
LANG_LABELS = {
    "繁體中文": {
        "retry_msg": "⚠️ 偵測到限制，等待 30 秒後自動重試...",
        "running": "情報抓取中...",
        "btn_run": "立即生成報告 (2026 穩定版)"
    },
    "日本語": {
        "retry_msg": "⚠️ 制限を検知。30秒後に再試行します...",
        "running": "情報分析中...",
        "btn_run": "レポートを生成"
    },
    "English": {
        "retry_msg": "⚠️ Rate limit. Retrying in 30s...",
        "running": "Generating...",
        "btn_run": "Generate Report"
    }
}
# 繼承之前的其他 Label...
# (為了簡潔，以下僅列出關鍵邏輯修改點)

# ... (UI 設定與 Sidebar 程式碼保持不變) ...

# ==========================================
# 4. 戰略情報生成邏輯 (優化重試與模型)
# ==========================================
if st.sidebar.button(LANG_LABELS[ui_lang]["btn_run"]):
    report_date = current_tw_time.strftime("%Y-%m-%d")
    with st.spinner(LANG_LABELS[ui_lang]["running"]):
        
        full_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                prompt = f"Today's Date: {report_date}. Task: AI Strategy Report for {ui_lang}..."
                
                # 關鍵修改 1：使用穩定性最高的 1.5-flash
                response = client.models.generate_content(
                    model='gemini-1.5-flash', 
                    contents=prompt,
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                )
                full_text = response.text
                break
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    # 關鍵修改 2：縮短等待時間至 30 秒 (剛好蓋過截圖中的 24s)
                    st.warning(f"{LANG_LABELS[ui_lang]['retry_msg']} ({attempt + 1}/{max_retries})")
                    time.sleep(30) 
                else:
                    st.error(f"Error: {e}")
                    st.stop()
        
        # ... (後續顯示與 Mail 邏輯保持不變) ...

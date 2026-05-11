import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

# 1. 頁面配置
st.set_page_config(page_title="ASCEM 系統維運治理看板", layout="wide", page_icon="🛡️")

# 2. 標題區
st.title("🛡️ 115年度系統維運治理儀表板")
st.markdown("報告人：**Axioma.alpha_V1** | 數據驅動維運管理")

# 3. 數據讀取邏輯 (Decoupling)
CSV_FILE = "work_log.csv"

@st.cache_data(ttl=600)
def load_data():
    if os.path.exists(CSV_FILE):
        try:
            # 支援 Excel 編輯過的中文編碼
            return pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        except Exception as e:
            st.error(f"讀取 CSV 錯誤: {e}")
            return pd.DataFrame()
    else:
        st.warning(f"⚠️ 找不到 {CSV_FILE}，請確保檔案位於根目錄。")
        return pd.DataFrame()

df = load_data()

# 4. 關鍵指標 (Metrics) - 呈現管理高度
if not df.empty:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("資安稽核 (05/07)", "預備中", "🔴")
    c2.metric("2FA 部署進度", "100%", "✅")
    c3.metric("本週官網更新", "2 筆", "↑ 參訪/論文")
    c4.metric("Talos|Titan Storage", "暫存 <70%", "380T ✅")

    st.divider()

    # 5. 進度追蹤表 (帶自動上色)
    st.subheader("📊 系統維運進度追蹤表")
    
    def highlight_status(val):
        return 'background-color: #D4EDDA' if val == '已完備' else 'background-color: #FFF3CD'

    # 使用 map 支援新版 Pandas
    styled_df = df.style.map(highlight_status, subset=['狀態'])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # 6. 顧問戰略觀察
    st.info("""
    **本週維運重點：**
    - **資安合規**：2FA 與 VPN 導入完成，NAS 擴充確保稽核日誌完整性。
    - **科研賦能**：CryoSPARC 環境優化完成，支援 Titan Krios Run 1 數據對接。
    """)

# 7. 側邊欄：功能與下載
st.sidebar.title("⏬ 報告與附件")
st.sidebar.markdown("[附件 1：稽核檢查表](https://docs.google.com/document/d/1lAtn1hm7oiO8cfsK4vQwrjdo0DQaKuvVF_xMVamLJ_g/edit)")

if not df.empty:
    csv_bytes = df.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("下載維運日誌 (CSV)", csv_bytes, "Work_Log.csv", "text/csv")
    
    if st.sidebar.button("產生預覽 PDF 報告"):
        st.sidebar.warning("中文 PDF 需載入字型，建議使用瀏覽器列印 (Cmd+P) 另存為 PDF。")

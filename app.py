import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="ASCEM 系統維運治理儀表板", layout="wide", page_icon="🛡️")

# 2. 標題與報告人 (已更正)
st.title("🛡️ 115年度系統維運治理儀表板")
st.markdown("報告人：**ASCEM IT 陳新博**") # 根據需求更正

# 3. 強化版數據讀取 (解決編碼報錯並支援動態配置)
CSV_FILE = "work_log.csv"

@st.cache_data(ttl=60) # 縮短緩存時間，讓更新更快反映
def load_data():
    if os.path.exists(CSV_FILE):
        try:
            # 優先嘗試 UTF-8 (包含 Excel 的 BOM)
            return pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        except UnicodeDecodeError:
            try:
                # 備案：嘗試台灣常見的 Big5 (cp950)
                return pd.read_csv(CSV_FILE, encoding='cp950')
            except:
                return pd.DataFrame()
    return pd.DataFrame()

df_full = load_data()

# --- 4. 動態解析設定 (讓狀態列、重點、附件可編輯) ---
# 過濾出「維運日誌」本體 (排除標記列)
if not df_full.empty:
    log_df = df_full[~df_full['領域'].isin(['管理指標', '重點摘要', '相關連結'])]
    
    # 提取「資安稽核」狀態
    audit_row = df_full[df_full['任務描述'] == '資安稽核']
    audit_status = audit_row['狀態'].values[0] if not audit_row.empty else "未定"
    audit_date = audit_row['日期'].values[0] if not audit_row.empty else "05/07"

    # 提取「本週維運重點」
    summary_rows = df_full[df_full['領域'] == '重點摘要']
    summary_text = "\n".join([f"- {row['任務描述']}" for _, row in summary_rows.iterrows()]) if not summary_rows.empty else "目前尚無重點摘要。"

    # 5. 狀態列 (Metrics)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"資安稽核 ({audit_date})", audit_status, "🔴" if "預備" in audit_status else "✅")
    c2.metric("2FA 部署進度", "100%", "✅")
    c3.metric("本週官網更新", "2 筆", "↑")
    c4.metric("NAS 總容量", "16TB", "Log Server")

    st.divider()

    # 6. 進度追蹤表
    st.subheader("📊 系統維運進度追蹤表")
    def highlight_status(val):
        return 'background-color: #D4EDDA' if val == '已完備' else 'background-color: #FFF3CD'
    
    st.dataframe(log_df.style.map(highlight_status, subset=['狀態']), use_container_width=True, hide_index=True)

    # 7. 本週維運重點 (可編輯區)
    st.subheader("🏛️ Daily Monitor | 本週維運重點")
    st.info(summary_text)

    # 8. 側邊欄：報告與附件 (可編輯區)
    st.sidebar.title("⏬ 報告與附件")
    link_rows = df_full[df_full['領域'] == '相關連結']
    if not link_rows.empty:
        for _, row in link_rows.iterrows():
            st.sidebar.markdown(f"[{row['任務描述']}]({row['備註']})")
    else:
        st.sidebar.write("尚無附件連結")
else:
    st.error("找不到 work_log.csv 或資料格式錯誤")

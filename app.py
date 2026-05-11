import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="ASCEM 系統維運治理儀表板", layout="wide", page_icon="🛡️")

# 2. 標題與報告人
st.title("🛡️ 115年度系統維運治理儀表板")
st.markdown("報告人：**ASCEM IT 陳新博**")

# 3. 數據讀取 (支援雙編碼相容與緩存)
CSV_FILE = "work_log.csv"

@st.cache_data(ttl=30) # 縮短緩存至30秒，方便快速看到更新
def load_data():
    if os.path.exists(CSV_FILE):
        for enc in ['utf-8-sig', 'cp950']:
            try:
                return pd.read_csv(CSV_FILE, encoding=enc)
            except:
                continue
    return pd.DataFrame()

df_full = load_data()

if not df_full.empty:
    # --- 4. 分流邏輯：將管理標籤與維運日誌分開 ---
    # 排除管理用途的特殊列
    log_df = df_full[~df_full['領域'].isin(['管理指標', '重點摘要', '相關連結'])].copy()
    
    # 提取：稽核狀態 (搜尋任務描述包含「資安稽核」的列)
    audit_row = df_full[df_full['任務描述'].str.contains('資安稽核', na=False)]
    audit_status = audit_row['狀態'].values[0] if not audit_row.empty else "未定"
    audit_date = audit_row['日期'].values[0] if not audit_row.empty else "05/07"

    # 5. 頂部狀態列 (Metrics)
    c1, c2, c3, c4 = st.columns(4)
    # 此處狀態會隨 CSV 中「資安稽核」那列的「狀態」與「日期」自動連動
    c1.metric(f"資安稽核 ({audit_date})", audit_status) 
    c2.metric("2FA 部署進度", "100%", "✅")
    c3.metric("本週官網更新", "2 筆", "↑")
    c4.metric("NAS 總容量", "16TB", "Log Server")

    st.divider()

    # 6. 系統維運進度追蹤表 (動態更新區)
    st.subheader("📊 系統維運進度追蹤表")
    def highlight_status(val):
        if val == '已完備': return 'background-color: #D4EDDA'
        if val == '進行中': return 'background-color: #FFF3CD'
        return ''
    
    # 顯示過濾後的純日誌內容
    st.dataframe(log_df.style.map(highlight_status, subset=['狀態']), use_container_width=True, hide_index=True)

    # 7. 本週維運重點 (動態從領域為「重點摘要」的列提取)
    st.subheader("🏛️ Daily Monitor | 本週維運重點")
    summary_rows = df_full[df_full['領域'] == '重點摘要']
    if not summary_rows.empty:
        for _, row in summary_rows.iterrows():
            st.write(f"· {row['任務描述']}")
    else:
        st.info("目前尚無重點摘要，請在 CSV 領域欄位填寫「重點摘要」。")

    # 8. 側邊欄：報告與附件相關連結 (動態從領域為「相關連結」的列提取)
    st.sidebar.title("⏬ 報告與附件")
    link_rows = df_full[df_full['領域'] == '相關連結']
    if not link_rows.empty:
        for _, row in link_rows.iterrows():
            # 任務描述為連結文字，備註為網址
            st.sidebar.markdown(f"[{row['任務描述']}]({row['備註']})")
    else:
        st.sidebar.write("尚無附件連結，請在 CSV 領域欄位填寫「相關連結」。")

else:
    st.error("讀取 work_log.csv 失敗，請確認檔案編碼與路徑。")

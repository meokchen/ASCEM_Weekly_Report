import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="ASCEM 系統維運治理儀表板", layout="wide", page_icon="🛡️")

# 2. 標題與報告人 (已更正)
st.title("🛡️ 115年度系統維運治理儀表板")
st.markdown("報告人：**ASCEM IT 陳新博**")

# 3. 數據讀取邏輯 (支援多種編碼與自動清洗)
CSV_FILE = "work_log.csv"

@st.cache_data(ttl=10)
def load_data():
    if os.path.exists(CSV_FILE):
        for enc in ['utf-8-sig', 'cp950', 'big5']:
            try:
                df = pd.read_csv(CSV_FILE, encoding=enc)
                # 清除全空行與欄位前後空白
                df = df.dropna(how='all').apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                return df
            except:
                continue
    return pd.DataFrame()

df_full = load_data()

if not df_full.empty:
    # --- 4. 關鍵數據過濾與分流 ---
    # A. 提取資安稽核狀態 (針對 5月7日 且 任務描述包含「稽核」)
    # 這裡採用更強大的搜尋邏輯，相容 5/7, 05/07, 5月7日
    audit_row = df_full[
        (df_full['日期'].str.contains('5.7|05.07|5月7日', na=False, regex=True)) & 
        (df_full['任務描述'].str.contains('稽核', na=False))
    ]
    
    if not audit_row.empty:
        audit_status = audit_row['狀態'].values[0]
        audit_date = "5月7日"
    else:
        # 備案：抓取最後一筆稽核紀錄
        last_audit = df_full[df_full['任務描述'].str.contains('稽核', na=False)].tail(1)
        audit_status = last_audit['狀態'].values[0] if not last_audit.empty else "未定"
        audit_date = last_audit['日期'].values[0] if not last_audit.empty else "5月7日"

    # 5. 頂部狀態列 (Metrics) - 修正為 5月7日
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"資安稽核 ({audit_date})", audit_status, delta="✅" if "結束" in audit_status or "完備" in audit_status else None)
    c2.metric("2FA 部署進度", "100%", "✅")
    c3.metric("本週官網更新", "2 筆", "↑")
    c4.metric("NAS 總容量", "16TB", "Log Server")

    st.divider()

    # 6. 系統維運進度追蹤表 (修正：顯示所有領域並同步 CSV)
    st.subheader("📊 系統維運進度追蹤表")
    
    # 排除管理標籤，確保表格內容與 CSV 同步
    log_df = df_full[~df_full['領域'].isin(['重點摘要', '相關連結'])].copy()
    
    def highlight_status(val):
        if val in ['已完備', '已結束']: return 'background-color: #D4EDDA'
        if val == '進行中': return 'background-color: #FFF3CD'
        return ''
    
    # 確保顯示所有核心欄位
    cols = ["日期", "領域", "類別", "任務描述", "狀態", "備註"]
    available_cols = [c for c in cols if c in log_df.columns]
    
    st.dataframe(
        log_df[available_cols].style.map(highlight_status, subset=['狀態'] if '狀態' in log_df.columns else []),
        use_container_width=True, 
        hide_index=True
    )

    # 7. 本週維運重點 (Daily Monitor) - 修復遺失問題
    st.subheader("🏛️ Daily Monitor | 本週維運重點")
    summary_rows = df_full[df_full['領域'].str.contains('重點|摘要', na=False)]
    if not summary_rows.empty:
        for _, row in summary_rows.iterrows():
            st.write(f"· {row['任務描述']}")
    else:
        st.info("💡 提醒：請在 CSV 的「領域」欄位填寫「重點摘要」來顯示此區塊。")

    # 8. 側邊欄：報告與附件 (相關連結) - 修復遺失問題
    st.sidebar.title("⏬ 報告與附件")
    link_rows = df_full[df_full['領域'].str.contains('連結|附件', na=False)]
    if not link_rows.empty:
        for _, row in link_rows.iterrows():
            st.sidebar.markdown(f"[{row['任務描述']}]({row['備註']})")
    else:
        st.sidebar.write("尚無附件連結")

else:
    st.error("讀取 work_log.csv 失敗，請確認檔案內容與編碼。")

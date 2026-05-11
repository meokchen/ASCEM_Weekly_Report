import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="ASCEM 系統維運治理儀表板", layout="wide", page_icon="🛡️")

# 2. 標題與報告人
st.title("🛡️ 115年度系統維運治理儀表板")
st.markdown("報告人：**ASCEM IT 陳新博**")

# 3. 數據讀取 (含自動清洗空白行)
CSV_FILE = "work_log.csv"

@st.cache_data(ttl=10)
def load_data():
    if os.path.exists(CSV_FILE):
        for enc in ['utf-8-sig', 'cp950']:
            try:
                # 讀取後立即剔除全空的行，避免出現 "None" 列
                df = pd.read_csv(CSV_FILE, encoding=enc).dropna(how='all')
                return df
            except:
                continue
    return pd.DataFrame()

df_full = load_data()

if not df_full.empty:
    # --- 4. 管理標籤過濾 ---
    # 確保表格只顯示日誌，並排除管理用途的標籤
    log_df = df_full[~df_full['領域'].isin(['重點摘要', '相關連結'])].copy()
    
    # 針對您要求的「資安稽核 (5月6日) 已結束」進行精確搜尋
    audit_row = df_full[df_full['任務描述'].str.contains('資安稽核', na=False) & (df_full['日期'] == '5月6日')]
    
    # 如果找不到 5/6 則抓取最新的稽核紀錄
    if audit_row.empty:
        audit_row = df_full[df_full['任務描述'].str.contains('資安稽核', na=False)]
        
    audit_status = "已結束" if not audit_row.empty else "未定"
    audit_date = audit_row['日期'].values[0] if not audit_row.empty else "5月6日"

    # 5. 頂部狀態列 (Metrics)
    c1, c2, c3, c4 = st.columns(4)
    # 修正顯示：明確指出 5月6日 已結束
    c1.metric(f"資安稽核 ({audit_date})", audit_status, delta="✅" if audit_status == "已結束" else None)
    c2.metric("2FA 部署進度", "100%", "✅")
    c3.metric("本週官網更新", "2 筆", "↑")
    c4.metric("NAS 總容量", "16TB", "Log Server")

    st.divider()

    # 6. 系統維運進度追蹤表 (呈現所有欄位)
    st.subheader("📊 系統維運進度追蹤表")
    def highlight_status(val):
        if val in ['已完備', '已結束']: return 'background-color: #D4EDDA'
        if val == '進行中': return 'background-color: #FFF3CD'
        return ''
    
    # 強制顯示完整欄位架構
    display_cols = ["日期", "領域", "類別", "任務描述", "狀態", "備註"]
    available_cols = [c for c in display_cols if c in log_df.columns]
    
    st.dataframe(
        log_df[available_cols].style.map(highlight_status, subset=['狀態'] if '狀態' in log_df.columns else []), 
        use_container_width=True, 
        hide_index=True
    )

    # 7. 重點摘要與側邊欄 (略，保持動態讀取邏輯)
    # ... 保持與之前一致的 Daily Monitor 與側邊欄連結代碼 ...

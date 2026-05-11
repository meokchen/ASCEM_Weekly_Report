import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="ASCEM 系統維運治理儀表板", layout="wide", page_icon="🛡️")

# 2. 標題與報告人
st.title("🛡️ 115年度系統維運治理儀表板")
st.markdown("報告人：**ASCEM IT 陳新博**")

# 3. 數據讀取與深度清洗
CSV_FILE = "work_log.csv"

@st.cache_data(ttl=5) # 縮短緩存時間以便即時看到 CSV 異動
def load_data():
    if os.path.exists(CSV_FILE):
        for enc in ['utf-8-sig', 'cp950', 'big5']:
            try:
                # 讀取並強制將所有欄位轉為字串，避免 None 或 NaN 顯示問題
                df = pd.read_csv(CSV_FILE, encoding=enc).fillna("")
                # 清除欄位名稱與內容的前後空白
                df.columns = [c.strip() for c in df.columns]
                df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                return df
            except:
                continue
    return pd.DataFrame()

df_full = load_data()

if not df_full.empty:
    # --- 4. 數據分流邏輯 ---
    # A. 提取「資安稽核」指標 (鎖定 5月7日)
    audit_mask = (df_full['任務描述'].str.contains('稽核', na=False)) & (df_full['日期'].str.contains('5月7日', na=False))
    audit_row = df_full[audit_mask]
    
    audit_status = audit_row['狀態'].values[0] if not audit_row.empty else "未定"
    audit_date = "5月7日"

    # B. 提取「重點摘要」
    summary_df = df_full[df_full['領域'] == '重點摘要']
    
    # C. 提取「相關連結」
    link_df = df_full[df_full['領域'] == '相關連結']

    # D. 過濾出「系統維運進度追蹤表」內容 (排除管理標籤)
    log_df = df_full[~df_full['領域'].isin(['重點摘要', '相關連結'])].copy()

    # 5. 頂部狀態列 (Metrics)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"資安稽核 ({audit_date})", audit_status, delta="✅" if audit_status == "已結束" else None)
    c2.metric("2FA 部署進度", "100%", "✅")
    c3.metric("本週官網更新", "2 筆", "↑")
    c4.metric("NAS 總容量", "16TB", "Log Server")

    st.divider()

    # 6. 📊 系統維運進度追蹤表 (完整顯示 6 個欄位)
    st.subheader("📊 系統維運進度追蹤表")
    
    def highlight_status(val):
        if val in ['已完備', '已結束']: return 'background-color: #D4EDDA'
        if val == '進行中': return 'background-color: #FFF3CD'
        return ''

    # 強制指定顯示順序，確保「備註」欄位一定出現
    display_cols = ["日期", "領域", "類別", "任務描述", "狀態", "備註"]
    # 只顯示 CSV 中確實存在的欄位，避免報錯
    valid_cols = [c for c in display_cols if c in log_df.columns]
    
    st.dataframe(
        log_df[valid_cols].style.map(highlight_status, subset=['狀態'] if '狀態' in log_df.columns else []),
        use_container_width=True,
        hide_index=True
    )

    # 7. 🏛️ Daily Monitor | 本週維運重點
    st.subheader("🏛️ Daily Monitor | 本週維運重點")
    if not summary_df.empty:
        for _, row in summary_df.iterrows():
            st.write(f"· {row['任務描述']}")
    else:
        st.info("💡 提醒：請確保 CSV 的「領域」欄位寫有『重點摘要』。")

    # 8. ⏬ 報告與附件 (相關連結)
    st.sidebar.title("⏬ 報告與附件")
    if not link_df.empty:
        for _, row in link_df.iterrows():
            # 連結名稱放在「任務描述」，網址放在「備註」
            st.sidebar.markdown(f"[{row['任務描述']}]({row['備註']})")
    else:
        st.sidebar.write("尚無附件連結")

else:
    st.error("無法讀取 work_log.csv，請確認檔案格式與 GitHub 上傳狀態。")

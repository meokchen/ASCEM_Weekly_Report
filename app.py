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

@st.cache_data(ttl=2) # 極短緩存，確保異動即時反映
def load_data():
    if os.path.exists(CSV_FILE):
        for enc in ['utf-8-sig', 'cp950', 'big5']:
            try:
                # 讀取資料並將所有內容轉為字串清洗空白
                df = pd.read_csv(CSV_FILE, encoding=enc).fillna("")
                df.columns = [c.strip() for c in df.columns]
                df = df.apply(lambda x: x.astype(str).str.strip() if x.dtype == "object" else x)
                return df.replace("nan", "")
            except:
                continue
    return pd.DataFrame()

df_full = load_data()

if not df_full.empty:
    # --- 4. 數據分流邏輯 (確保不互相干擾) ---
    
    # A. 提取「資安稽核」狀態 (針對 5月7日)
    audit_row = df_full[(df_full['任務描述'].str.contains('稽核', na=False)) & 
                        (df_full['日期'].str.contains('5月7日', na=False))]
    audit_status = audit_row['狀態'].values[0] if not audit_row.empty else "已結束"

    # B. 獨立提取「重點摘要」資料列
    summary_df = df_full[df_full['領域'].str.contains('重點|摘要', na=False)]
    
    # C. 獨立提取「相關連結」資料列
    link_df = df_full[df_full['領域'].str.contains('連結|附件', na=False)]

    # D. 獨立生成「系統維運進度追蹤表」內容 (排除管理用的特殊列)
    log_df = df_full[~df_full['領域'].str.contains('重點|摘要|連結|附件|指標', na=False)].copy()

    # 5. 頂部狀態列 (Metrics)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("資安稽核 (5月7日)", audit_status, delta="✅" if "結束" in audit_status else None)
    c2.metric("2FA 部署進度", "100%", "✅")
    c3.metric("本週官網更新", "2 筆", "↑")
    c4.metric("NAS 總容量", "16TB", "Log Server")

    st.divider()

    # 6. 📊 系統維運進度追蹤表 (強制顯示，不論摘要是否存在)
    st.subheader("📊 系統維運進度追蹤表")
    def highlight_status(val):
        if val in ['已完備', '已結束']: return 'background-color: #D4EDDA'
        if val == '進行中': return 'background-color: #FFF3CD'
        return ''

    # 指定顯示順序：日期, 領域, 類別, 任務描述, 狀態, 備註
    display_cols = ["日期", "領域", "類別", "任務描述", "狀態", "備註"]
    valid_cols = [c for c in display_cols if c in log_df.columns]
    
    # 即使 log_df 為空也要顯示欄位架構
    st.dataframe(
        log_df[valid_cols].style.map(highlight_status, subset=['狀態'] if '狀態' in log_df.columns else []),
        use_container_width=True,
        hide_index=True
    )

    # 7. 🏛️ Daily Monitor | 本週維運重點
    st.subheader("🏛️ Daily Monitor | 本週維運重點")
    if not summary_df.empty:
        for _, row in summary_df.iterrows():
            st.write(f"· {row['任務描述']}") # 顯示內容文字
    else:
        st.write("目前尚無重點摘要。")

    # 8. ⏬ 報告與附件 (側邊欄連結)
    st.sidebar.title("⏬ 報告與附件")
    if not link_df.empty:
        for _, row in link_df.iterrows():
            # 任務描述為文字，備註為 URL
            if "http" in str(row['備註']):
                st.sidebar.markdown(f"[{row['任務描述']}]({row['備註']})")
    else:
        st.sidebar.write("尚無附件連結")

else:
    st.error("讀取資料失敗，請確認 work_log.csv 是否已正確上傳且包含資料。")

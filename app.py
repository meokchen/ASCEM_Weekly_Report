import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="ASCEM 系統維運治理儀表板", layout="wide", page_icon="🛡️")

# 2. 標題與報告人
st.title("🛡️ 115年度系統維運治理儀表板")
st.markdown("報告人：**ASCEM IT 陳新博**")

# 3. 數據讀取與深度清洗 (確保無欄位被隱藏)
CSV_FILE = "work_log.csv"

@st.cache_data(ttl=2)
def load_data():
    if os.path.exists(CSV_FILE):
        for enc in ['utf-8-sig', 'cp950', 'big5']:
            try:
                # 讀取完整 CSV，不進行任何預先過濾
                df = pd.read_csv(CSV_FILE, encoding=enc).fillna("")
                # 清除欄位名稱空格
                df.columns = [c.strip() for c in df.columns]
                # 確保所有內容轉為字串並清洗
                df = df.apply(lambda x: x.astype(str).str.strip() if x.dtype == "object" else x)
                return df.replace("nan", "")
            except:
                continue
    return pd.DataFrame()

df_full = load_data()

if not df_full.empty:
    # --- 4. 數據提取 (獨立運作，不影響主表格) ---
    
    # A. 狀態列指標：鎖定 5月7日 的資安稽核
    audit_row = df_full[(df_full['日期'].str.contains('5月7日', na=False)) & 
                        (df_full['任務描述'].str.contains('稽核', na=False))]
    audit_status = audit_row['狀態'].values[0] if not audit_row.empty else "已結束"

    # B. 側邊欄：提取領域包含「連結」的列
    link_df = df_full[df_full['領域'].str.contains('連結', na=False)]
    
    # C. 下方重點：提取領域包含「重點」的列
    summary_df = df_full[df_full['領域'].str.contains('重點', na=False)]

    # 5. 頂部狀態列 (Metrics)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("資安稽核 (5月7日)", audit_status, delta="✅" if "結束" in audit_status else None)
    c2.metric("2FA 部署進度", "100%", "✅")
    c3.metric("本週官網更新", "2 筆", "↑")
    c4.metric("NAS 總容量", "16TB", "Log Server")

    st.divider()

    # 6. 📊 系統維運進度追蹤表 (修正：顯示全部 6 個欄位與所有行，絕不隱藏)
    st.subheader("📊 系統維運進度追蹤表")
    
    # 強制指定顯示所有 CSV 欄位順序
    display_cols = ["日期", "領域", "類別", "任務描述", "狀態", "備註"]
    
    def highlight_status(val):
        if val in ['已完備', '已結束']: return 'background-color: #D4EDDA'
        if val == '進行中': return 'background-color: #FFF3CD'
        return ''

    # 直接顯示 df_full，不進行任何行過濾，確保資料完整性
    st.dataframe(
        df_full[display_cols].style.map(highlight_status, subset=['狀態']),
        use_container_width=True,
        hide_index=True
    )

    # 7. 🏛️ Daily Monitor | 本週維運重點 (下方獨立顯示)
    st.subheader("🏛️ Daily Monitor | 本週維運重點")
    if not summary_df.empty:
        for _, row in summary_df.iterrows():
            st.write(f"· {row['任務描述']}")
    else:
        st.write("目前尚未在 CSV 標註重點摘要。")

    # 8. ⏬ 報告與附件 (左側獨立顯示)
    st.sidebar.title("⏬ 報告與附件")
    if not link_df.empty:
        for _, row in link_df.iterrows():
            # 任務描述為標題，備註為網址
            if "http" in str(row['備註']):
                st.sidebar.markdown(f"[{row['任務描述']}]({row['備註']})")
    else:
        st.sidebar.write("尚無附件連結")

else:
    st.error("讀取 work_log.csv 失敗，請確認檔案已正確上傳至 GitHub。")

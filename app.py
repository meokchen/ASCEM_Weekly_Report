import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="ASCEM-IT 工作日誌週報儀表板", layout="wide", page_icon="🛡️")

# 初始化 Session State 來儲存手動新增的連結
if 'custom_links' not in st.session_state:
    st.session_state.custom_links = []

# ==========================================
# 2. 左側面板：動態附件上傳與連結區
# ==========================================
with st.sidebar:
    st.title("⏬ 報告與附件")
    
    st.markdown("**📁 附件與數據更新區**")
    uploaded_files = st.file_uploader(
        "上傳工作日誌(CSV/XLSX) 或 參考附件(PDF/圖檔)", 
        accept_multiple_files=True,
        type=['csv', 'xlsx', 'pdf', 'png', 'jpg', 'jpeg']
    )
    
    # 將上傳的檔案分類
    data_files = []
    attachment_files = []
    
    if uploaded_files:
        for file in uploaded_files:
            if file.name.endswith(('.csv', '.xlsx')):
                data_files.append(file)
            else:
                attachment_files.append(file)
                
        st.success(f"✅ 已載入 {len(uploaded_files)} 個檔案")
        
        # 展示非數據類的參考附件 (PDF / 圖片)
        if attachment_files:
            st.markdown("---")
            st.markdown("**📎 參考附件預覽**")
            for file in attachment_files:
                file_size = round(file.size / 1024, 1)
                st.caption(f"📄 {file.name} ({file_size} KB)")
                if file.name.endswith(('.png', '.jpg', '.jpeg')):
                    st.image(file, use_container_width=True)

    st.divider()
    
    # 動態新增連結區
    st.markdown("**🔗 新增專案連結**")
    col1, col2 = st.columns([2, 1])
    with col1:
        new_url = st.text_input("貼上 URL 網址", placeholder="https://...", label_visibility="collapsed")
    with col2:
        new_name = st.text_input("顯示名稱", placeholder="自訂名稱", label_visibility="collapsed")
        
    if st.button("➕ 加入連結", use_container_width=True):
        if new_url:
            display_name = new_name if new_name else new_url
            st.session_state.custom_links.append({"name": display_name, "url": new_url})
            st.rerun() 

    st.divider()
    st.markdown("**📌 相關連結總覽**")


# ==========================================
# 3. 數據讀取與深度清洗
# ==========================================
CSV_FILE = "work_log.csv"

@st.cache_data(ttl=2)
def load_data(files):
    if files:
        for file in files:
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file).fillna("")
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file).fillna("")
                else:
                    continue
                
                df.columns = [c.strip() for c in df.columns]
                df = df.apply(lambda x: x.astype(str).str.strip() if x.dtype == "object" else x)
                return df.replace("nan", "")
            except Exception as e:
                st.sidebar.error(f"讀取數據檔失敗: {e}")
                
    if os.path.exists(CSV_FILE):
        for enc in ['utf-8-sig', 'cp950', 'big5']:
            try:
                df = pd.read_csv(CSV_FILE, encoding=enc).fillna("")
                df.columns = [c.strip() for c in df.columns]
                df = df.apply(lambda x: x.astype(str).str.strip() if x.dtype == "object" else x)
                return df.replace("nan", "")
            except:
                continue
    return pd.DataFrame()

df_full = load_data(data_files)

# 動態抓取完整週期
if not df_full.empty:
    valid_dates = [d for d in df_full['日期'].tolist() if d and "月" in str(d) and "日" in str(d)]
    if len(valid_dates) >= 1:
        start_date = valid_dates[0].replace("月", "/").replace("日", "")
        end_date = valid_dates[-1].replace("月", "/").replace("日", "")
        if end_date and end_date != start_date:
            week_range = f"{start_date}~{end_date}"
        else:
            week_range = f"{start_date}~5/8"
    else:
        week_range = "5/4~5/8"
else:
    week_range = "讀取中"


# ==========================================
# 4. 主視覺區：標題與中間區週報模式
# ==========================================
st.title("🛡️ ASCEM-IT 工作日誌週報儀表板")
st.markdown(f"報告人：**ASCEM IT 陳新博** | 統計週期：**{week_range}**")

if not df_full.empty:
    remark_col_name = '備註|建議事項' if '備註|建議事項' in df_full.columns else '備註'

    # ==========================================
    # 【重點修改區塊】：動態計算本週資安/稽核筆數
    # ==========================================
    # 判斷「類別」或「任務描述」中是否包含「資安」或「稽核」字眼
    is_audit = df_full['類別'].str.contains('資安|稽核', na=False) | df_full['任務描述'].str.contains('資安|稽核', na=False)
    audit_count = len(df_full[is_audit])

    # 獨立提取：相關連結與重點摘要
    link_df = df_full[df_full['領域'].str.contains('連結', na=False)]
    summary_df = df_full[df_full['領域'].str.contains('重點', na=False)]

    # --- 整合並顯示所有連結於左側面板 ---
    with st.sidebar:
        has_links = False
        for link in st.session_state.custom_links:
            st.markdown(f"🔗 [{link['name']}]({link['url']})")
            has_links = True
            
        if not link_df.empty:
            for _, row in link_df.iterrows():
                cell_value = str(row.get(remark_col_name, ''))
                if "http" in cell_value:
                    st.markdown(f"🔗 [{row['任務描述']}]({cell_value})")
                    has_links = True
                    
        if not has_links:
            st.write("尚無附件連結")

    # 狀態列 (Metrics)
    c1, c2, c3, c4, c5 = st.columns(5)
    
    # 這裡將標題改為「本週資安稽核」，並帶入動態算出的筆數
    c1.metric("本週資安稽核", f"{audit_count} 筆", delta="↑" if audit_count > 0 else None)
    
    c2.metric("2FA 部署進度", "100%", "✅")
    c3.metric("本週官網更新", "2 筆", "↑")
    c4.metric("Storage: Titan/Talos", "380T < 70% 佔用", "✅ 正常")
    c5.metric("NAS 總容量", "16TB", "Log Server")

    st.divider()

    # 📊 系統維運進度追蹤表
    st.subheader("📊 系統維運進度追蹤表")
    
    def highlight_status(val):
        if val in ['已完備', '已結束']: return 'background-color: #D4EDDA'
        if val == '進行中': return 'background-color: #FFF3CD'
        return ''

    display_cols = ["日期", "領域", "類別", "任務描述", "狀態", remark_col_name]
    st.dataframe(
        df_full[display_cols].style.map(highlight_status, subset=['狀態']),
        use_container_width=True,
        hide_index=True
    )

    # 🏛️ Daily Monitor | 本週維運重點
    st.subheader("🏛️ Daily Monitor | 本週維運重點")
    if not summary_df.empty:
        for _, row in summary_df.iterrows():
            st.write(f"· {row['任務描述']}")
    else:
        st.write("目前尚未在數據中標註重點摘要。")

else:
    st.error("目前讀取不到任何資料，請檢查伺服器上的檔案，或利用左側面板上傳新的工作日誌。")

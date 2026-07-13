import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="ASCEM-IT 工作日誌週報儀表板", layout="wide", page_icon="🛡️")

# 3. 數據讀取與深度清洗
CSV_FILE = "work_log.csv"

@st.cache_data(ttl=2)
def load_data():
    if os.path.exists(CSV_FILE):
        for enc in ['utf-8-sig', 'cp950', 'big5']:
            try:
                # 讀取完整 CSV
                df = pd.read_csv(CSV_FILE, encoding=enc).fillna("")
                df.columns = [c.strip() for c in df.columns]
                # 清洗內容空白，將內容全部轉為字串
                df = df.apply(lambda x: x.astype(str).str.strip() if x.dtype == "object" else x)
                return df.replace("nan", "")
            except:
                continue
    return pd.DataFrame()

df_full = load_data()

# --- 【精密修正】動態抓取完整週期 (確保正確顯示，不因摘要列斷開) ---
if not df_full.empty:
    # 提取所有非空的日期列，並排除掉標題或無效字串
    valid_dates = [d for d in df_full['日期'].tolist() if d and "月" in d and "日" in d]
    
    if len(valid_dates) >= 1:
        # 轉換格式：5月4日 -> 5/4
        start_date = valid_dates[0].replace("月", "/").replace("日", "")
        end_date = valid_dates[-1].replace("月", "/").replace("日", "")
        # 再次檢查 end_date 是否有效
        if end_date and end_date != start_date:
            week_range = f"{start_date}~{end_date}"
        else:
            week_range = f"{start_date}~5/8" # 強制補全備案
    else:
        week_range = "5/4~5/8"
else:
    week_range = "讀取中"

# 2. 標題與報告人資訊更新
st.title("🛡️ ASCEM-IT 工作日誌週報儀表板")
st.markdown(f"報告人：**ASCEM IT 陳新博** | 統計週期：**{week_range}**")

if not df_full.empty:
    # --- 4. 數據獨立提取 (不影響主表格) ---
    # A. 稽核狀態：鎖定 5月7日
    audit_row = df_full[(df_full['任務描述'].str.contains('稽核', na=False)) & (df_full['日期'].str.contains('5月7日', na=False))]
    audit_status = audit_row['狀態'].values[0] if not audit_row.empty else "已結束"

    # B. 獨立提取：相關連結與重點摘要
    link_df = df_full[df_full['領域'].str.contains('連結', na=False)]
    summary_df = df_full[df_full['領域'].str.contains('重點', na=False)]

    # 5. 狀態列 (Metrics) - 新增 Storage 指標
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(f"資安稽核 (5月7日)", audit_status, delta="✅" if "結束" in audit_status else None)
    c2.metric("2FA 部署進度", "100%", "✅")
    c3.metric("本週官網更新", "2 筆", "↑")
    c4.metric("Storage: Titan/Talos", "380T < 70% 佔用", "✅ 正常")
    c5.metric("NAS 總容量", "16TB", "Log Server")

    st.divider()

    # 6. 📊 系統維運進度追蹤表 (修正：顯示所有行與 6 個欄位，改用新版表格寬度參數)
    st.subheader("📊 系統維運進度追蹤表")
    
    def highlight_status(val):
        if val in ['已完備', '已結束']: return 'background-color: #D4EDDA'
        if val == '進行中': return 'background-color: #FFF3CD'
        return ''

    # 強制顯示所有 6 個欄位，並改用 width='stretch'
    display_cols = ["日期", "領域", "類別", "任務描述", "狀態", "備註"]
    st.dataframe(
        df_full[display_cols].style.map(highlight_status, subset=['狀態']),
        width='stretch',
        hide_index=True
    )

    # 7. 🏛️ Daily Monitor | 本週維運重點 (下方獨立顯示)
    st.subheader("🏛️ Daily Monitor | 本週維運重點")
    if not summary_df.empty:
        for _, row in summary_df.iterrows():
            st.write(f"· {row['任務描述']}")
    else:
        st.write("目前尚未在 CSV 中標註重點摘要。")

    # 8. ⏬ 報告與附件 (左側獨立顯示 & 修正圖片預覽相容性)
    st.sidebar.title("⏬ 報告與附件")
    
    # 處理原本程式碼後半段的檔案上傳與預覽逻辑
    # 這裡的 uploaded_files 與 attachment_files 變數需對應您前端的 st.file_uploader 邏輯
    if 'uploaded_files' in locals() or 'uploaded_files' in globals():
        st.success(f"✅ 已載入 {len(uploaded_files)} 個檔案")
        if attachment_files:
            st.markdown("---")
            st.markdown("**📎 參考附件預覽**")
            for file in attachment_files:
                file_size = round(file.size / 1024, 1)
                st.caption(f"📄 {file.name} ({file_size} KB)")
                if file.name.endswith(('.png', '.jpg', '.jpeg')):
                    # 【核心修正】：將舊版 use_container_width=True 改為新版 width='stretch'
                    st.image(file, width='stretch')

    if not link_df.empty:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**🔗 歷史維運連結**")
        for _, row in link_df.iterrows():
            if "http" in str(row['備註']):
                st.sidebar.markdown(f"[{row['任務描述']}]({row['備註']})")
    else:
        st.sidebar.write("尚無附件連結")

    st.divider()

    # 動態新增連結區
    st.markdown("**🔗 新增專案連結**")
    col1, col2 = st.columns([2, 1])
    with col1:
        new_url = st.text_input("貼上 URL 網址", placeholder="https://...", label_visibility="collapsed")
    with col2:
        new_name = st.text_input("顯示名稱", placeholder="自訂名稱", label_visibility="collapsed")

else:
    st.error("讀取資料失敗，請確認 work_log.csv 是否存在。")

import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="ASCEM-IT 工作日誌週報儀表板", layout="wide", page_icon="🛡️")

# 2. 數據讀取與深度清洗
CSV_FILE = "work_log.csv"

@st.cache_data(ttl=2)
def load_data():
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

df_full = load_data()

# --- 動態抓取完整週期 (確保正確顯示 5/4~5/8) ---
if not df_full.empty:
    valid_dates = [d for d in df_full['日期'].tolist() if d and "月" in d and "日" in d]
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
    week_range = "5/4~5/8"

# 3. 標題與報告人資訊
st.title("🛡️ ASCEM-IT 工作日誌週報儀表板")
st.markdown(f"報告人：**ASCEM IT 陳新博** | 統計週期：**{week_range}**")

if not df_full.empty:
    # --- 4. 數據獨立提取 ---
    audit_row = df_full[(df_full['任務描述'].str.contains('稽核', na=False)) & (df_full['日期'].str.contains('5月7日', na=False))]
    audit_status = audit_row['狀態'].values[0] if not audit_row.empty else "已結束"

    link_df = df_full[df_full['領域'].str.contains('連結', na=False)]
    summary_df = df_full[df_full['領域'].str.contains('重點', na=False)]

    # 5. 狀態列 (Metrics)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(f"資安稽核 (5月7日)", audit_status, delta="✅" if "結束" in audit_status else None)
    c2.metric("2FA 部署進度", "100%", "✅")
    c3.metric("本週官網更新", "2 筆", "↑")
    c4.metric("Storage: Titan/Talos", "380T < 70% 佔用", "✅ 正常")
    c5.metric("NAS 總容量", "16TB", "Log Server")

    st.divider()

    # 6. 📊 系統維運進度追蹤表 (【核心修復】移除 .style.map 確保原生不閃退)
    st.subheader("📊 系統維運進度追蹤表")
    
    display_cols = ["日期", "領域", "類別", "任務描述", "狀態", "備註|建議事項"]
    
    # 採用最穩定的純原生渲染，保證 6 欄與所有資料完整呈現
    st.dataframe(
        df_full[display_cols],
        width='stretch',
        hide_index=True
    )

    # 7. 🏛️ Daily Monitor | 本週維運重點
    st.subheader("🏛️ Daily Monitor | 本週維運重點")
    if not summary_df.empty:
        for _, row in summary_df.iterrows():
            st.write(f"· {row['任務描述']}")
    else:
        st.write("目前尚未在 CSV 中標註重點摘要。")

    # 8. ⏬ 報告與附件
    st.sidebar.title("⏬ 報告與附件")
    if not link_df.empty:
        st.sidebar.markdown("**🔗 歷史維運連結**")
        for _, row in link_df.iterrows():
            if "http" in str(row['備註']):
                st.sidebar.markdown(f"[{row['任務描述']}]({row['備註']})")
    else:
        st.sidebar.write("尚無附件連結")

else:
    st.error("讀取資料失敗，請確認 work_log.csv 是否存在。")

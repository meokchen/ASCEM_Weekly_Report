import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

# 1. 網頁配置
st.set_page_config(page_title="ASCEM_IT-工作日誌週報", layout="wide", page_icon="🛡️")

# 2. 標題與標頭
st.title("🛡️ ASCEM_IT-工作日誌週報儀表板")
st.markdown("報告人：**陳新博** | 統計週期：04/27 - 04/30")

# 3. 讀取資料
CSV_FILE = "work_log.csv"
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    st.error("找不到 work_log.csv")
    st.stop()

# 4. 頂部關鍵指標 (Metrics)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("資安稽核 (05/07)", "預備中", "🔴")
c2.metric("2FA 部署", "100%", "✅")
c3.metric("官網更新", "2 筆", "↑ 參訪/論文")
c4.metric("Talos | Titan Storage", "暫存 <70%", "↑ 380T (✅ 正常)")
c5.metric("📦 NAS 總容量 (Log Server)", "16TB")

st.divider()

# 5. 進度追蹤表
st.subheader("📊 系統維運進度追蹤表")

def highlight_status(val):
    color = 'background-color: #D4EDDA' if val == '已完備' else 'background-color: #FFF3CD'
    return color

# 這裡使用 map 修正新版 Pandas 報錯
styled_df = df.style.map(highlight_status, subset=['狀態'])
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# 6. 日常監控總結
st.subheader("🏛️ Daily Monitor | 日常監控(IT+資安+網管+CryoEM運算)")
st.info("""
**本週簡報重點：**
- **資安合規**：2FA 與 VPN 導入已將外部風險降至最低，NAS 擴充確保了稽核日誌的完整性。
- **科研賦能**：CryoSPARC v4.0+ 優化完成，目前 Titan Krios Run 1 數據連動++傳輸++編譯 | MotionCrr++穩定。
- **設施維運**：成功對接外賓參訪與最新學術發表，提升設施曝光度。
""")

# 7. 側邊欄：附件與導出
st.sidebar.title("⏬ 附件調閱")
st.sidebar.markdown("[附件 1：稽核檢查表](https://docs.google.com/document/d/1lAtn1hm7oiO8cfsK4vQwrjdo0DQaKuvVF_xMVamLJ_g/edit)")
st.sidebar.markdown("[附件 2：資安會議資料](https://csirt.its.sinica.edu.tw/projects/ismsarea/files)")

st.sidebar.divider()
st.sidebar.subheader("📄 報告導出")

# --- 方案 A: 導出 CSV (最穩定，保留圖表數據內容) ---
csv_data = df.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button(
    label="下載本週日誌 (CSV)",
    data=csv_data,
    file_name=f"Weekly_Report_0430.csv",
    mime="text/csv",
)

# --- 方案 B: 產生 PDF (修正報錯邏輯) ---
def create_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    # 這裡若無字型檔會略過中文，防止當機
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, "Weekly Maintenance Report - ASCEM", ln=True, align='C')
    pdf.ln(10)
    for index, row in dataframe.iterrows():
        # 只取日期與狀態避免編碼錯誤
        text = f"{row['日期']} | {row['領域']} | Status: {row['狀態']}"
        pdf.cell(190, 10, text.encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    return pdf.output(dest='S').encode('latin-1')

if st.sidebar.button("產生正式 PDF 報告"):
    try:
        pdf_out = create_pdf(df)
        st.sidebar.download_button("確認下載 PDF", pdf_out, "Report.pdf", "application/pdf")
    except Exception as e:
        st.sidebar.error("PDF 編碼受限，建議使用瀏覽器列印功能")

import streamlit as st
import pandas as pd
import os

# 1. 網頁基本設定
st.set_page_config(page_title="ASCEM_IT-工作日誌週報 (2026/04/27–04/30)儀表板", layout="wide", page_icon="🛡️")

# 2. 標題區
st.title("🛡️ ASCEM_IT-工作日誌週報儀表板")
st.markdown("報告人：**陳新博** | 統計週期：04/27 - 04/30")

# 3. 讀取資料
CSV_FILE = "work_log.csv"
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    st.error("找不到 work_log.csv，請確認檔案是否存在！")
    st.stop()

# 4. 頂部關鍵指標 (Metrics)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("資安稽核 (05/07)", "預備中", "🔴")
c2.metric("2FA 部署", "100%", "✅")
c3.metric("官網更新", "2 筆", "參訪/論文")
c4.metric(
    label="Talos | Titan Storage", 
    value="暫存 <70%", 
    delta="380T (✅ 正常)",
    help="包含EMData4 40T  暫存空間監控")
c5.metric(label="📦 NAS 總容量 (Log Server)",
    value="16TB")
st.divider()

# 5. 主要表格展示
# st.subheader("📊 系統維運進度追蹤表")
# 設定表格樣式：將「已完備」上色
# def highlight_status(val):
#    color = '#D4EDDA' if val == '已完備' else '#FFF3CD'
#    return f'background-color: {color}'
 #
 #           st.dataframe(df.style.applymap(highlight_status, subset=['狀態']), 
 #           use_container_width=True, 
 #           hide_index=True)

# --- 修正後的表格顯示程式碼 ---
st.subheader("📊 系統維運進度追蹤表")

# 檢查 DataFrame 是否有資料
if not df.empty:
    # 定義上色邏輯
    def highlight_status(val):
        color = 'background-color: #D4EDDA' if val == '已完備' else 'background-color: #FFF3CD'
        return color

    # 注意：這裡將 applymap 改為 map
    styled_df = df.style.map(highlight_status, subset=['狀態'])
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
else:
    st.write("目前尚無資料紀錄。")

# 6. Daily Monitor｜日常監控( IT+資安+網管+CyroEM運算)：
st.divider()
st.subheader("🏛️ Daily Monitor｜日常監控(IT+資安+網管+CyroEM運算)")
st.info("""
**本週簡報重點：**
- **資安合規**：2FA 與 VPN 導入已將外部風險降至最低，NAS 擴充確保了稽核日誌的完整性。
- **科研賦能**：CryoSPARC v4.0+ 優化完成，目前 Titan Krios Run 1 數據連動++傳輸＋編譯｜MotionCrr+穩定。
- **設施維運**：成功對接外賓參訪與最新學術發表，提升設施曝光度。
""")

# 7. 側邊欄檔案調閱
st.sidebar.title("⏬ 附件調閱")
st.sidebar.markdown("[附件 1：稽核檢查表](https://docs.google.com/document/d/1lAtn1hm7oiO8cfsK4vQwrjdo0DQaKuvVF_xMVamLJ_g/edit?tab=t.0)")
st.sidebar.markdown("[附件 2：資安會議資料](https://csirt.its.sinica.edu.tw/projects/ismsarea/files)")

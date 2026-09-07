import streamlit as st
import pandas as pd
import os
import re

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

# --- 【智慧修正 1】動態正向排序週期 (修復 9/04~8/31 反轉問題) ---
def parse_week_range(df):
    if df.empty or '日期' not in df.columns:
        return "8/31~9/4"
    date_tuples = []
    for d in df['日期']:
        m = re.search(r'(\d+)月(\d+)日?', str(d))
        if m:
            date_tuples.append((int(m.group(1)), int(m.group(2))))
    if not date_tuples:
        return "8/31~9/4"
    # 按月份、日期從小到大排序
    date_tuples = sorted(date_tuples, key=lambda x: (x[0], x[1]))
    start_d, end_d = date_tuples[0], date_tuples[-1]
    return f"{start_d[0]}/{start_d[1]}~{end_d[0]}/{end_d[1]}"

week_range = parse_week_range(df_full)

# 3. 標題與報告人資訊
st.title("🛡️ ASCEM-IT 工作日誌週報儀表板")
st.markdown(f"報告人：**ASCEM IT 陳新博** | 統計週期：**{week_range}**")

if not df_full.empty:
    # 尋找備註欄位名稱（相容「備註」與「備註/建議事項」）
    remark_col = next((c for c in df_full.columns if '備註' in c or '建議' in c), "備註")

    # --- 【智慧修正 2】自動辨識官網更新與分類 ---
    # 只要任務描述或領域含「官網」，自動歸類為官網更新
    web_mask = df_full['任務描述'].str.contains('官網', na=False) | df_full['領域'].str.contains('官網', na=False)
    web_count = int(web_mask.sum())

    # 連結篩選：領域含連結 或 任務為官網發布
    link_mask = df_full['領域'].str.contains('連結', na=False) | web_mask
    link_df = df_full[link_mask]

    # 重點摘要：排除已歸類至官網更新的項目，避免重複
    summary_mask = df_full['領域'].str.contains('重點', na=False) & (~web_mask)
    summary_df = df_full[summary_mask]

    # 4. 頂部狀態列 (Metrics)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("資安稽核 (5月7日)", "已結束", delta="✅")
    c2.metric("2FA 部署進度", "100%", "✅")
    # 動態計算本週官網更新筆數
    c3.metric("本週官網更新", f"{web_count} 筆", "↑" if web_count > 0 else None)
    c4.metric("Storage: Titan/Talos", "380T < 70% 佔用", "✅ 正常")
    c5.metric("NAS 總容量", "16TB", "Log Server")

    st.divider()

    # 5. 📊 系統維運進度追蹤表 (完整顯示 6 欄，維持原汁原味)
    st.subheader("📊 系統維運進度追蹤表")
    base_cols = [c for c in ["日期", "領域", "類別", "任務描述", "狀態"] if c in df_full.columns]
    if remark_col in df_full.columns and remark_col not in base_cols:
        base_cols.append(remark_col)

    st.dataframe(
        df_full[base_cols],
        width='stretch',
        hide_index=True
    )

    # 6. 🏛️ Daily Monitor | 本週維運重點
    st.subheader("🏛️ Daily Monitor | 本週維運重點")
    if not summary_df.empty:
        for _, row in summary_df.iterrows():
            st.write(f"· {row['任務描述']}")
    else:
        st.write("目前尚未在 CSV 中標註重點摘要。")

    # 7. ⏬ 報告與附件 (側邊欄智慧連結產生器)
    st.sidebar.title("⏬ 報告與附件")
    if not link_df.empty:
        for _, row in link_df.iterrows():
            title = row['任務描述']
            raw_remark = str(row.get(remark_col, ""))
            
            # 若備註包含 http 網址則直接採用，否則預設導向 ASCEM 官方網站
            if "http" in raw_remark:
                # 提取網址
                url_match = re.search(r'(https?://[^\s]+)', raw_remark)
                url = url_match.group(1) if url_match else raw_remark
            else:
                url = "https://cryoem.project.sinica.edu.tw/"
            
            st.sidebar.markdown(f"[{title}]({url})")
            # 若備註中有論文資訊或說明文字，以附註形式呈現
            if raw_remark and not raw_remark.startswith("http"):
                st.sidebar.caption(f"📝 {raw_remark}")
    else:
        st.sidebar.write("尚無附件連結")

else:
    st.error("讀取資料失敗，請確認 work_log.csv 是否存在。")

import streamlit as st
import pandas as pd

# ==========================================
# 1. 網頁基本設定
# ==========================================
st.set_page_config(
    page_title="ASCEM 週報數據監控面板",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. 左側面板：相關連結與附件 (隨時更新)
# ==========================================
with st.sidebar:
    st.header("🔗 相關連結與附件")
    
    # 固定的重要專案參考連結
    st.markdown("""
    **重點專案連結**
    * [次世代智慧醫療基礎設施評估簡報 (共用雲端)](#)
    * [生醫資訊科技與 AI 賦能應用手冊](#)
    ---
    """)
    
    # 動態附件上傳區 (可供使用者隨時丟入新檔案更新數據)
    st.markdown("**附件與數據更新區**")
    uploaded_files = st.file_uploader(
        "上傳最新數據或參考文件 (支援 CSV, XLSX, PDF)", 
        accept_multiple_files=True,
        type=['csv', 'xlsx', 'pdf']
    )
    
    # 顯示目前上傳的檔案狀態
    if uploaded_files:
        st.success(f"✅ 已載入 {len(uploaded_files)} 個檔案")
        for file in uploaded_files:
            file_size = round(file.size / 1024, 1)
            st.caption(f"📄 {file.name} ({file_size} KB)")
    
    st.write("---")


# ==========================================
# 3. 資料讀取功能 (含防錯機制)
# ==========================================
@st.cache_data
def load_data(uploaded_files=None):
    """
    此處為資料讀取邏輯。
    如果使用者在左側上傳了新的 CSV/XLSX，則優先採用上傳的數據；
    否則，請在此讀取您原有的預設本地檔案 (例如週報原始資料)。
    """
    # 狀況 A：如果使用者有透過左側面板上傳最新數據檔
    if uploaded_files:
        for file in uploaded_files:
            if file.name.endswith('.csv'):
                return pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                return pd.read_excel(file)
                
    # 狀況 B：預設本地資料讀取 (請將 'your_default_data.csv' 替換為您實際的本地路徑)
    try:
        # return pd.read_csv("your_default_data.csv")
        
        # --- 為了確保程式碼直接覆蓋後能跑通，以下先提供一組預設模擬數據 ---
        mock_data = {
            '日期': ['5月15日', '5月16日', '5月17日', '5月18日', '5月19日', '5月20日', '5月21日', '5月22日'],
            '指標A': [102, 115, 118, 125, 130, 142, 138, 145],
            '指標B': [85, 88, 92, 90, 94, 98, 96, 101]
        }
        return pd.DataFrame(mock_data)
    except Exception as e:
        st.error(f"預設資料載入失敗: {e}")
        return None

# 執行讀取主資料表
df_full = load_data(uploaded_files)


# ==========================================
# 4. 關鍵資料處理與防護機制 (修正 KeyError)
# ==========================================
if df_full is not None:
    
    # 【關鍵修正】自動清除所有欄位名稱前後的空白字元，防止 '日期 ' 這種隱藏錯誤
    df_full.columns = df_full.columns.str.strip()
    
    # 安全檢查：確保 '日期' 欄位真的存在，才執行後續邏輯
    if '日期' in df_full.columns:
        
        # 第 31 行原始核心邏輯 (加入 str(d) 轉型防護以確保字串比對安全)
        valid_dates = [d for d in df_full['日期'].tolist() if d and "月" in str(d) and "日" in str(d)]
        
        # ==========================================
        # 5. 主頁面儀表板視覺化呈現
        # ==========================================
        st.title("📊 ASCEM 週報數據監控面板")
        st.subheader("統計週期：5/15 ~ 5/22")
        
        # 頁面頂部指標卡片展示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="📅 有效統計天數", value=f"{len(valid_dates)} 天")
        with col2:
            val_a = df_full['指標A'].iloc[-1] if '指標A' in df_full.columns else "N/A"
            st.metric(label="📈 指標 A 最新數值", value=val_a)
        with col3:
            val_b = df_full['指標B'].iloc[-1] if '指標B' in df_full.columns else "N/A"
            st.metric(label="📉 指標 B 最新數值", value=val_b)
            
        st.write("---")
        
        # 數據走勢圖表
        st.markdown("### 📈 週報指標走勢趨勢")
        if '指標A' in df_full.columns and '指標B' in df_full.columns:
            st.line_chart(df_full.set_index('日期')[['指標A', '指標B']])
        else:
            st.line_chart(df_full.set_index('日期'))
            
        # 完整資料表格檢視
        st.markdown("### 📋 原始數據明細")
        st.dataframe(df_full, use_container_width=True)
        
    else:
        # 如果新推送的資料還是找不到 '日期' 欄位，呈現清晰的 Debug 提示畫面
        st.error("❌ 錯誤：目前的資料表中找不到名為 『日期』 的欄位！")
        st.warning(f"🔍 偵測到目前您檔案內實際包含的欄位名稱為： {df_full.columns.tolist()}")
        st.info("💡 解決辦法：請確認您更新的 Excel/CSV 檔案第一列標題，是否有拼錯字或不小心轉換成英文 (如 Date)。")
else:
    st.error("無法成功載入數據，請確認資料來源路徑或上傳正確的檔案格式。")

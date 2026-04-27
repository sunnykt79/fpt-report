import pandas as pd
import datetime
import io

def load_data(file):
    try:
        # Reset file pointer to ensure we read from the beginning
        file.seek(0)
        # Đọc dữ liệu trực tiếp từ file object với engine openpyxl
        # Việc sử dụng file object trực tiếp thường ổn định hơn trên Streamlit Cloud
        xls = pd.ExcelFile(file, engine='openpyxl')
        
        # Load Internet sheet
        df_internet = pd.read_excel(
            xls, 
            sheet_name="Internet", 
            usecols="J,O,P,Q,R,T,Y,AA",
            names=["Hop_dong", "Ngay_tao", "Ngay_online", "Ngay_huy", "Sale", "Xa_Phuong", "Tra_truoc", "Hinh_thuc_TT"]
        )
        
        # Load Pay sheet
        df_pay = pd.read_excel(
            xls, 
            sheet_name="Pay", 
            usecols="H,L",
            names=["Phan_loai", "Hop_dong_Pay"]
        )

        # Preprocessing Data
        # Ensure datetime formats
        df_internet['Ngay_tao'] = pd.to_datetime(df_internet['Ngay_tao'], errors='coerce')
        df_internet['Ngay_online'] = pd.to_datetime(df_internet['Ngay_online'], errors='coerce')
        df_internet['Ngay_huy'] = pd.to_datetime(df_internet['Ngay_huy'], errors='coerce')
        
        # Handle Xa_Phuong (Region)
        df_internet['Xa_Phuong'] = df_internet['Xa_Phuong'].fillna("Khác")
        df_internet['Xa_Phuong'] = df_internet['Xa_Phuong'].replace(["Không xác định", "", " "], "Khác")
        
        # Handle Tra_truoc (Prepaid)
        df_internet['Tra_truoc'] = pd.to_numeric(df_internet['Tra_truoc'], errors='coerce').fillna(0)
        
        # Merge with Pay sheet to identify Combo
        df_merged = pd.merge(df_internet, df_pay, left_on='Hop_dong', right_on='Hop_dong_Pay', how='left')
        
        # Combo is defined as contract existing in both Internet and Pay
        df_merged['Is_Combo'] = df_merged['Hop_dong_Pay'].notna()
        
        return df_merged
    except Exception as e:
        raise Exception(f"Lỗi khi đọc dữ liệu: {e}")

def get_date_range(df):
    if df['Ngay_tao'].notna().any():
        min_date = df['Ngay_tao'].min().date()
        max_date = df['Ngay_tao'].max().date()
        return min_date, max_date
    return datetime.date.today(), datetime.date.today()

def filter_data(df, start_date, end_date, selected_sales):
    mask = (df['Ngay_tao'].dt.date >= start_date) & (df['Ngay_tao'].dt.date <= end_date)
    filtered_df = df.loc[mask]
    
    if selected_sales and "Tất cả" not in selected_sales:
        filtered_df = filtered_df[filtered_df['Sale'].isin(selected_sales)]
        
    return filtered_df

def calculate_metrics(df):
    total_pttb = len(df)
    if total_pttb == 0:
        return {
            "total_pttb": 0, "combo": 0, "vvip": 0, "vvip_count": 0, "vip_count": 0,
            "online_rate": 0, "cancel_rate": 0, "avg_deploy_days": 0
        }
    
    combo_count = df['Is_Combo'].sum()
    
    # V.Vip / Vip count - Corrected logic
    phan_loai = df['Phan_loai'].astype(str).str.upper()
    vvip_count = phan_loai.str.contains(r'V\.VIP', regex=True).sum()
    # Vip count: matches VIP but not preceded by V.
    vip_count = phan_loai.str.contains(r'(?<!V\.)VIP', regex=True).sum()
    
    # Online Rate
    online_count = df['Ngay_online'].notna().sum()
    online_rate = (online_count / total_pttb) * 100
    
    # Cancel Rate (Hủy TSD)
    cancel_count = df['Ngay_huy'].notna().sum()
    cancel_rate = (cancel_count / total_pttb) * 100
    
    # Avg Deploy Days
    deployed_df = df[df['Ngay_online'].notna() & df['Ngay_tao'].notna()].copy()
    if not deployed_df.empty:
        deployed_df['Deploy_Days'] = (deployed_df['Ngay_online'] - deployed_df['Ngay_tao']).dt.days
        # Avoid negative days in case of dirty data
        avg_deploy_days = deployed_df[deployed_df['Deploy_Days'] >= 0]['Deploy_Days'].mean()
        if pd.isna(avg_deploy_days):
            avg_deploy_days = 0
    else:
        avg_deploy_days = 0
        
    return {
        "total_pttb": total_pttb,
        "combo": int(combo_count),
        "vvip": f"{int(vvip_count)} / {int(vip_count)}",
        "vvip_count": int(vvip_count),
        "vip_count": int(vip_count),
        "online_rate": online_rate,
        "cancel_rate": cancel_rate,
        "avg_deploy_days": avg_deploy_days
    }

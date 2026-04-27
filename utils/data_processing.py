import datetime

import pandas as pd


INTERNET_USECOLS = "E,J,O,P,Q,R,T,Y,AA"
INTERNET_COLUMNS = [
    "Phong",
    "Hop_dong",
    "Ngay_tao",
    "Ngay_online",
    "Ngay_huy",
    "Sale",
    "Xa_Phuong",
    "Tra_truoc",
    "Hinh_thuc_TT",
]

PAY_USECOLS = "H,L,T"
PAY_COLUMNS = ["Phan_loai", "Hop_dong_Pay", "Pay_Sale"]


def _read_internet_sheet(source, sheet_name=0):
    return pd.read_excel(
        source,
        sheet_name=sheet_name,
        usecols=INTERNET_USECOLS,
        names=INTERNET_COLUMNS,
    )


def _read_pay_sheet(source, sheet_name=0):
    return pd.read_excel(
        source,
        sheet_name=sheet_name,
        usecols=PAY_USECOLS,
        names=PAY_COLUMNS,
    )


def _prepare_data(df_internet, df_pay):
    df_internet["Ngay_tao"] = pd.to_datetime(df_internet["Ngay_tao"], errors="coerce")
    df_internet["Ngay_online"] = pd.to_datetime(df_internet["Ngay_online"], errors="coerce")
    df_internet["Ngay_huy"] = pd.to_datetime(df_internet["Ngay_huy"], errors="coerce")

    # Source column T is still used as the reporting area after the district-level change.
    df_internet["Phong"] = df_internet["Phong"].fillna("Khác")
    df_internet["Phong"] = df_internet["Phong"].replace(["Không xác định", "", " "], "Khác")
    df_internet["Xa_Phuong"] = df_internet["Xa_Phuong"].fillna("Khác")
    df_internet["Xa_Phuong"] = df_internet["Xa_Phuong"].replace(["Không xác định", "", " "], "Khác")

    df_internet["Tra_truoc"] = pd.to_numeric(df_internet["Tra_truoc"], errors="coerce").fillna(0)

    df_merged = pd.merge(df_internet, df_pay, left_on="Hop_dong", right_on="Hop_dong_Pay", how="left")
    df_merged["Is_Combo"] = df_merged["Hop_dong_Pay"].notna()

    return df_merged


def load_data(file):
    return load_data_from_workbook(file)


def load_data_from_workbook(file):
    try:
        file.seek(0)
        xls = pd.ExcelFile(file, engine="openpyxl")
        df_internet = _read_internet_sheet(xls, sheet_name="Internet")
        df_pay = _read_pay_sheet(xls, sheet_name="Pay")
        return _prepare_data(df_internet, df_pay)
    except Exception as e:
        raise Exception(f"Lỗi khi đọc dữ liệu: {e}")


def load_data_from_separate_files(internet_file, pay_file):
    try:
        internet_file.seek(0)
        pay_file.seek(0)
        df_internet = _read_internet_sheet(internet_file)
        df_pay = _read_pay_sheet(pay_file)
        return _prepare_data(df_internet, df_pay)
    except Exception as e:
        raise Exception(f"Lỗi khi đọc dữ liệu: {e}")


def get_date_range(df):
    if df["Ngay_tao"].notna().any():
        min_date = df["Ngay_tao"].min().date()
        max_date = df["Ngay_tao"].max().date()
        return min_date, max_date
    return datetime.date.today(), datetime.date.today()


def filter_data(df, start_date, end_date, selected_sales):
    mask = (df["Ngay_tao"].dt.date >= start_date) & (df["Ngay_tao"].dt.date <= end_date)
    filtered_df = df.loc[mask]

    if selected_sales and "Tất cả" not in selected_sales:
        filtered_df = filtered_df[filtered_df["Sale"].isin(selected_sales)]

    return filtered_df


def calculate_metrics(df):
    total_pttb = len(df)
    if total_pttb == 0:
        return {
            "total_pttb": 0,
            "combo": 0,
            "vvip": 0,
            "vvip_count": 0,
            "vip_count": 0,
            "online_rate": 0,
            "cancel_rate": 0,
            "avg_deploy_days": 0,
        }

    combo_count = df["Is_Combo"].sum()

    phan_loai = df["Phan_loai"].astype(str).str.upper()
    vvip_count = phan_loai.str.contains(r"V\.VIP", regex=True).sum()
    vip_count = phan_loai.str.contains(r"(?<!V\.)VIP", regex=True).sum()

    online_count = df["Ngay_online"].notna().sum()
    online_rate = (online_count / total_pttb) * 100

    cancel_count = df["Ngay_huy"].notna().sum()
    cancel_rate = (cancel_count / total_pttb) * 100

    deployed_df = df[df["Ngay_online"].notna() & df["Ngay_tao"].notna()].copy()
    if not deployed_df.empty:
        deployed_df["Deploy_Days"] = (deployed_df["Ngay_online"] - deployed_df["Ngay_tao"]).dt.days
        avg_deploy_days = deployed_df[deployed_df["Deploy_Days"] >= 0]["Deploy_Days"].mean()
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
        "avg_deploy_days": avg_deploy_days,
    }

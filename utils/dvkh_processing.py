import datetime

import pandas as pd


DVKH_COLUMNS = {
    "contract": "Hợp đồng",
    "months_used": "Số tháng sử dụng",
    "payment_method": "Phương thức thanh toán",
    "payment_form": "Hình thức thanh toán",
    "region": "Quận (Lắp đặt)",
    "collector": "Nhân viên thu",
    "payment_date": "Ngày thanh toán",
    "assignee": "Nhân viên phân công",
}


def _clean_text(series, default="Khác"):
    cleaned = series.fillna("").astype(str).str.strip()
    cleaned = cleaned.str.replace(r"^_+\s*", "", regex=True).str.strip()
    return cleaned.replace("", default)


def load_dvkh_data(file):
    try:
        file.seek(0)
        df = pd.read_excel(file, sheet_name=0)
        return prepare_dvkh_data(df)
    except Exception as e:
        raise Exception(f"Lỗi khi đọc dữ liệu DVKH: {e}")


def prepare_dvkh_data(df):
    missing_cols = [col for col in DVKH_COLUMNS.values() if col not in df.columns]
    if missing_cols:
        raise Exception(f"File DVKH thiếu cột: {', '.join(missing_cols)}")

    prepared = df.copy()
    prepared["Ngay_thanh_toan"] = pd.to_datetime(
        prepared[DVKH_COLUMNS["payment_date"]],
        dayfirst=True,
        errors="coerce",
    )
    prepared["Nhan_vien_thu"] = _clean_text(prepared[DVKH_COLUMNS["collector"]])
    prepared["Nhan_vien_phan_cong"] = _clean_text(prepared[DVKH_COLUMNS["assignee"]])
    prepared["Phuong_thuc_TT"] = _clean_text(prepared[DVKH_COLUMNS["payment_method"]])
    prepared["Hinh_thuc_TT_DVKH"] = _clean_text(prepared[DVKH_COLUMNS["payment_form"]])
    prepared["Khu_vuc_DVKH"] = _clean_text(prepared[DVKH_COLUMNS["region"]])
    prepared["So_thang_su_dung"] = pd.to_numeric(
        prepared[DVKH_COLUMNS["months_used"]],
        errors="coerce",
    ).fillna(0)
    prepared["Da_thu"] = prepared["Ngay_thanh_toan"].notna()
    return prepared


def get_dvkh_date_range(df):
    if df["Ngay_thanh_toan"].notna().any():
        return df["Ngay_thanh_toan"].min().date(), df["Ngay_thanh_toan"].max().date()
    today = datetime.date.today()
    return today, today


def filter_dvkh_data(df, start_date, end_date, selected_collectors, selected_regions):
    paid_in_range = (
        df["Ngay_thanh_toan"].notna()
        & (df["Ngay_thanh_toan"].dt.date >= start_date)
        & (df["Ngay_thanh_toan"].dt.date <= end_date)
    )
    unpaid_rows = df["Ngay_thanh_toan"].isna()
    filtered_df = df.loc[paid_in_range | unpaid_rows].copy()

    if selected_collectors and "Tất cả" not in selected_collectors:
        filtered_df = filtered_df[filtered_df["Nhan_vien_thu"].isin(selected_collectors)]

    if selected_regions and "Tất cả" not in selected_regions:
        filtered_df = filtered_df[filtered_df["Khu_vuc_DVKH"].isin(selected_regions)]

    return filtered_df


def calculate_dvkh_metrics(df):
    total_bill = len(df)
    collected_bill = int(df["Da_thu"].sum()) if total_bill else 0
    outstanding_bill = total_bill - collected_bill
    collected_rate = (collected_bill / total_bill * 100) if total_bill else 0

    return {
        "total_bill": total_bill,
        "collected_bill": collected_bill,
        "outstanding_bill": outstanding_bill,
        "collected_rate": collected_rate,
        "payment_methods": int(df.loc[df["Da_thu"], "Phuong_thuc_TT"].nunique()) if total_bill else 0,
        "payment_forms": int(df.loc[df["Da_thu"], "Hinh_thuc_TT_DVKH"].nunique()) if total_bill else 0,
    }

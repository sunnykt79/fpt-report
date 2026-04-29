import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def _horizontal_yaxis_order(sort_ascending):
    return "total descending" if sort_ascending else "total ascending"


def _rank_limited(data, sort_by, top_n, sort_ascending=False):
    return data.sort_values(sort_by, ascending=sort_ascending).head(top_n)


def plot_status_pie(df, sort_ascending=False):
    # Cơ cấu trạng thái (Online / Hủy / Đang chờ)
    # Online: Ngay_online not null
    # Hủy: Ngay_huy not null (but not online)
    # Đang chờ: Both are null
    
    # We create a new column for status
    def get_status(row):
        if pd.notna(row['Ngay_online']):
            return 'Online'
        elif pd.notna(row['Ngay_huy']):
            return 'Hủy'
        else:
            return 'Đang chờ'
            
    if len(df) == 0:
        return px.pie(title="Không có dữ liệu")
        
    status_series = df.apply(get_status, axis=1)
    status_counts = status_series.value_counts().reset_index()
    status_counts.columns = ['Trạng thái', 'Số lượng']
    status_counts = status_counts.sort_values('Số lượng', ascending=sort_ascending)
    
    fig = px.pie(
        status_counts, 
        values='Số lượng', 
        names='Trạng thái', 
        title='Cơ cấu trạng thái Hợp đồng',
        color='Trạng thái',
        color_discrete_map={'Online': '#28a745', 'Hủy': '#dc3545', 'Đang chờ': '#ffc107'},
        hole=0.4
    )
    fig.update_traces(sort=False)
    return fig

def _plot_rate_ranking(
    df,
    group_col,
    date_col,
    title,
    group_label,
    rate_label,
    top_n=20,
    color_scale='Greens',
    sort_ascending=False,
):
    if len(df) == 0 or group_col not in df.columns or date_col not in df.columns:
        return px.bar(title="Không có dữ liệu")

    group_values = df[group_col].fillna("Khác").astype(str).str.strip()
    group_values = group_values.replace("", "Khác")

    grouped = (
        df.assign(
            _group=group_values,
            _hit=df[date_col].notna(),
        )
        .groupby("_group", dropna=False)
        .agg(Tong_PTTB=("_hit", "size"), So_luong=("_hit", "sum"))
        .reset_index()
    )
    grouped["Ty_le"] = grouped["So_luong"] / grouped["Tong_PTTB"] * 100
    grouped = grouped.sort_values(
        ["Ty_le", "So_luong", "Tong_PTTB"],
        ascending=sort_ascending,
    ).head(top_n)
    grouped["Nhan_hien_thi"] = grouped.apply(
        lambda row: f"{row['Ty_le']:.1f}% ({int(row['So_luong'])}/{int(row['Tong_PTTB'])})",
        axis=1,
    )

    fig = px.bar(
        grouped,
        y="_group",
        x="Ty_le",
        orientation="h",
        title=title,
        text="Nhan_hien_thi",
        color="Ty_le",
        color_continuous_scale=color_scale,
        labels={
            "_group": group_label,
            "Ty_le": rate_label,
            "Nhan_hien_thi": rate_label,
        },
        hover_data={
            "_group": False,
            "Ty_le": ":.1f",
            "So_luong": True,
            "Tong_PTTB": True,
            "Nhan_hien_thi": False,
        },
    )
    fig.update_layout(
        template="plotly_white",
        height=430,
        margin={"l": 145, "r": 95, "t": 58, "b": 58},
        yaxis={"categoryorder": _horizontal_yaxis_order(sort_ascending), "automargin": True},
        coloraxis_showscale=False,
        font={"size": 11},
        title={"font": {"size": 15}},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(tickfont={"size": 10})
    fig.update_xaxes(tickfont={"size": 10}, title_font={"size": 12})
    fig.update_xaxes(range=[0, max(105, grouped["Ty_le"].max() * 1.15 if len(grouped) else 100)])
    return fig

def plot_department_online_rate_ranking(df, top_n=10, sort_ascending=False):
    return _plot_rate_ranking(
        df,
        "Phong",
        "Ngay_online",
        f"Tỷ lệ online theo phòng (Top {top_n})",
        "Phong",
        "Tỷ lệ online (%)",
        top_n=top_n,
        color_scale="Greens",
        sort_ascending=sort_ascending,
    )

def plot_employee_online_rate_ranking(df, top_n=10, sort_ascending=False):
    return _plot_rate_ranking(
        df,
        "Sale",
        "Ngay_online",
        f"Xếp hạng nhân sự theo tỷ lệ online (Top {top_n})",
        "Nhân sự",
        "Tỷ lệ online (%)",
        top_n=top_n,
        color_scale="Greens",
        sort_ascending=sort_ascending,
    )

def plot_department_cancel_rate_ranking(df, top_n=10, sort_ascending=False):
    return _plot_rate_ranking(
        df,
        "Phong",
        "Ngay_huy",
        f"Tỷ lệ hủy TSD theo phòng (Top {top_n})",
        "Phong",
        "Tỷ lệ hủy TSD (%)",
        top_n=top_n,
        color_scale="Reds",
        sort_ascending=sort_ascending,
    )

def plot_employee_cancel_rate_ranking(df, top_n=10, sort_ascending=False):
    return _plot_rate_ranking(
        df,
        "Sale",
        "Ngay_huy",
        f"Xếp hạng nhân sự theo tỷ lệ hủy TSD (Top {top_n})",
        "Nhân sự",
        "Tỷ lệ hủy TSD (%)",
        top_n=top_n,
        color_scale="Reds",
        sort_ascending=sort_ascending,
    )

def plot_top_regions_bar(df, top_n=10, sort_ascending=False):
    if len(df) == 0:
        return px.bar(title="Không có dữ liệu")
        
    region_counts = df['Xa_Phuong'].value_counts().reset_index()
    region_counts.columns = ['Xã/Phường', 'Số lượng']
    region_counts = _rank_limited(region_counts, 'Số lượng', top_n, sort_ascending)
    
    fig = px.bar(
        region_counts, 
        y='Xã/Phường', 
        x='Số lượng', 
        orientation='h',
        title=f'Top {top_n} Xã/Phường theo sản lượng',
        text='Số lượng',
        color='Số lượng',
        color_continuous_scale='Blues'
    )
    fig.update_layout(yaxis={'categoryorder': _horizontal_yaxis_order(sort_ascending)})
    return fig

def plot_avg_deploy_by_region(df, top_n=10, sort_ascending=False):
    deployed_df = df[df['Ngay_online'].notna() & df['Ngay_tao'].notna()].copy()
    if len(deployed_df) == 0:
        return px.bar(title="Không có dữ liệu thời gian triển khai")
        
    deployed_df['Deploy_Days'] = (deployed_df['Ngay_online'] - deployed_df['Ngay_tao']).dt.days
    deployed_df = deployed_df[deployed_df['Deploy_Days'] >= 0]
    
    avg_days = deployed_df.groupby('Xa_Phuong')['Deploy_Days'].mean().reset_index()
    avg_days_top = _rank_limited(avg_days, 'Deploy_Days', top_n, sort_ascending)
    
    fig = px.bar(
        avg_days_top, 
        x='Xa_Phuong', 
        y='Deploy_Days',
        title=f'Hiệu suất triển khai trung bình (Top {top_n} Khu vực)',
        labels={'Deploy_Days': 'Ngày triển khai TB', 'Xa_Phuong': 'Khu vực'},
        text=avg_days_top['Deploy_Days'].round(1),
        color='Deploy_Days',
        color_continuous_scale='Oranges'
    )
    return fig

def plot_prepaid_stacked_bar(df, top_n=10, sort_ascending=False):
    if len(df) == 0:
        return px.bar(title="Không có dữ liệu")
        
    # Get regions by volume in the selected sort direction.
    top_regions = df['Xa_Phuong'].value_counts().reset_index()
    top_regions.columns = ['Xa_Phuong', 'Số lượng']
    top_regions = _rank_limited(top_regions, 'Số lượng', top_n, sort_ascending)
    top_regions = top_regions['Xa_Phuong']
    df_top = df[df['Xa_Phuong'].isin(top_regions)].copy()

    prepaid_order = [
        "Trả sau (Từng tháng)",
        "1 tháng",
        "3 tháng",
        "6 tháng",
        "13 tháng (1 năm)",
    ]
    prepaid_colors = {
        "Trả sau (Từng tháng)": "#4E79A7",
        "1 tháng": "#59A14F",
        "3 tháng": "#F28E2B",
        "6 tháng": "#E15759",
        "13 tháng (1 năm)": "#B07AA1",
    }
    
    # Clean up Tra_truoc and Map values
    def map_prepaid(val):
        try:
            v = int(float(val))
            if v == 0: return "Trả sau (Từng tháng)"
            if v == 3: return "3 tháng"
            if v == 6: return "6 tháng"
            if v == 13: return "13 tháng (1 năm)"
            return f"{v} tháng"
        except:
            return str(val)
            
    df_top['Tra_truoc'] = df_top['Tra_truoc'].apply(map_prepaid)
    
    grouped = df_top.groupby(['Xa_Phuong', 'Tra_truoc']).size().reset_index(name='Số lượng')
    
    fig = px.bar(
        grouped, 
        x='Xa_Phuong', 
        y='Số lượng', 
        color='Tra_truoc',
        title=f'Tỷ lệ trả trước theo khu vực (Top {top_n})',
        barmode='stack',
        category_orders={
            'Xa_Phuong': list(top_regions),
            'Tra_truoc': prepaid_order,
        },
        color_discrete_map=prepaid_colors,
        labels={
            'Xa_Phuong': 'Khu vực',
            'Tra_truoc': 'Trả trước',
            'Số lượng': 'Số lượng',
        },
    )
    fig.update_layout(
        template='plotly_white',
        legend_title_text='Trả trước',
    )
    fig.update_traces(marker_line_color='white', marker_line_width=0.5)
    return fig

def plot_department_pttb_bar(df, sort_ascending=False):
    if len(df) == 0 or 'Phong' not in df.columns:
        return px.bar(title="Không có dữ liệu phòng")

    department_counts = df['Phong'].fillna("Khác").value_counts().reset_index()
    department_counts.columns = ['Phòng', 'Số PTTB']
    department_counts = department_counts.sort_values('Số PTTB', ascending=sort_ascending)

    fig = px.bar(
        department_counts,
        y='Phòng',
        x='Số PTTB',
        orientation='h',
        title='Đóng góp PTTB theo phòng',
        text='Số PTTB',
        color='Số PTTB',
        color_continuous_scale='Blues',
        labels={'Phòng': 'Phòng', 'Số PTTB': 'Số PTTB'},
    )
    fig.update_layout(
        template='plotly_white',
        yaxis={'categoryorder': _horizontal_yaxis_order(sort_ascending)},
        coloraxis_showscale=False,
    )
    return fig

def plot_employee_product_contribution(df, top_n=20, sort_ascending=False):
    if len(df) == 0:
        return px.bar(title="Không có dữ liệu nhân sự")

    net_counts = (
        df['Sale']
        .fillna("Khác")
        .value_counts()
        .rename_axis('Nhan_su')
        .reset_index(name='PTTB Net')
    )

    pay_sale = df['Pay_Sale'] if 'Pay_Sale' in df.columns else df['Sale']
    pay_person = pay_sale.fillna(df['Sale']).fillna("Khác")
    phan_loai = df['Phan_loai'].astype(str).str.upper()
    tv_mask = phan_loai.str.contains('VIP', regex=False, na=False)
    vvip_mask = phan_loai.str.contains(r'V\.VIP', regex=True, na=False)

    tv_counts = (
        pay_person[tv_mask]
        .value_counts()
        .rename_axis('Nhan_su')
        .reset_index(name='PTTB Truyền hình')
    )
    vvip_counts = (
        pay_person[vvip_mask]
        .value_counts()
        .rename_axis('Nhan_su')
        .reset_index(name='PTTB V.Vip')
    )

    summary = net_counts.merge(tv_counts, on='Nhan_su', how='outer').merge(vvip_counts, on='Nhan_su', how='outer')
    summary = summary.fillna(0)
    for col in ['PTTB Net', 'PTTB Truyền hình', 'PTTB V.Vip']:
        summary[col] = summary[col].astype(int)

    summary['Tổng đóng góp'] = summary[['PTTB Net', 'PTTB Truyền hình', 'PTTB V.Vip']].sum(axis=1)
    summary = _rank_limited(summary, 'Tổng đóng góp', top_n, sort_ascending)

    chart_data = summary.melt(
        id_vars='Nhan_su',
        value_vars=['PTTB Net', 'PTTB Truyền hình', 'PTTB V.Vip'],
        var_name='Loại PTTB',
        value_name='Số PTTB',
    )

    fig = px.bar(
        chart_data,
        x='Nhan_su',
        y='Số PTTB',
        color='Loại PTTB',
        barmode='group',
        title=f'Đóng góp PTTB Net, Truyền hình và V.Vip theo nhân sự (Top {top_n})',
        text='Số PTTB',
        category_orders={'Nhan_su': list(summary['Nhan_su'])},
        color_discrete_map={
            'PTTB Net': '#4E79A7',
            'PTTB Truyền hình': '#F28E2B',
            'PTTB V.Vip': '#E15759',
        },
        labels={'Nhan_su': 'Nhân sự', 'Số PTTB': 'Số PTTB'},
    )
    fig.update_layout(template='plotly_white', legend_title_text='Loại PTTB')
    fig.update_xaxes(tickangle=-35)
    return fig


def plot_dvkh_bill_status(df, sort_ascending=False):
    if len(df) == 0:
        return px.pie(title="Không có dữ liệu DVKH")

    status_counts = pd.DataFrame(
        {
            "Trạng thái": ["Đã thu", "Tồn"],
            "Số lượng": [int(df["Da_thu"].sum()), int((~df["Da_thu"]).sum())],
        }
    )
    status_counts = status_counts.sort_values("Số lượng", ascending=sort_ascending)

    fig = px.pie(
        status_counts,
        values="Số lượng",
        names="Trạng thái",
        title="Cơ cấu bill thu / tồn",
        color="Trạng thái",
        color_discrete_map={"Đã thu": "#28a745", "Tồn": "#dc3545"},
        hole=0.4,
    )
    fig.update_traces(sort=False)
    return fig


def plot_dvkh_collector_ranking(df, top_n=10, sort_ascending=False):
    if len(df) == 0:
        return px.bar(title="Không có dữ liệu nhân sự thu bill")

    collected_df = df[df["Da_thu"]]
    if len(collected_df) == 0:
        return px.bar(title="Không có dữ liệu bill đã thu")

    collector_counts = collected_df["Nhan_vien_thu"].value_counts().reset_index()
    collector_counts.columns = ["Nhân sự", "Số bill thu"]
    collector_counts = _rank_limited(collector_counts, "Số bill thu", top_n, sort_ascending)

    fig = px.bar(
        collector_counts,
        y="Nhân sự",
        x="Số bill thu",
        orientation="h",
        title=f"Xếp hạng nhân sự thu bill (Top {top_n})",
        text="Số bill thu",
        color="Số bill thu",
        color_continuous_scale="Greens",
    )
    fig.update_layout(
        template="plotly_white",
        height=430,
        margin={"l": 145, "r": 70, "t": 58, "b": 58},
        yaxis={"categoryorder": _horizontal_yaxis_order(sort_ascending), "automargin": True},
        coloraxis_showscale=False,
        font={"size": 11},
        title={"font": {"size": 15}},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    return fig


def plot_dvkh_outstanding_by_collector(df, top_n=10, sort_ascending=False):
    if len(df) == 0:
        return px.bar(title="Không có dữ liệu bill tồn")

    outstanding_df = df[~df["Da_thu"]]
    if len(outstanding_df) == 0:
        return px.bar(title="Không có bill tồn")

    collector_counts = outstanding_df["Nhan_vien_thu"].value_counts().reset_index()
    collector_counts.columns = ["Nhân sự", "Số bill tồn"]
    collector_counts = _rank_limited(collector_counts, "Số bill tồn", top_n, sort_ascending)

    fig = px.bar(
        collector_counts,
        y="Nhân sự",
        x="Số bill tồn",
        orientation="h",
        title=f"Xếp hạng nhân sự còn bill tồn (Top {top_n})",
        text="Số bill tồn",
        color="Số bill tồn",
        color_continuous_scale="Reds",
    )
    fig.update_layout(
        template="plotly_white",
        height=430,
        margin={"l": 145, "r": 70, "t": 58, "b": 58},
        yaxis={"categoryorder": _horizontal_yaxis_order(sort_ascending), "automargin": True},
        coloraxis_showscale=False,
        font={"size": 11},
        title={"font": {"size": 15}},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    return fig


def plot_dvkh_payment_method(df, top_n=10, sort_ascending=False):
    if len(df) == 0:
        return px.bar(title="Không có dữ liệu phương thức thanh toán")

    collected_df = df[df["Da_thu"]]
    method_counts = collected_df["Phuong_thuc_TT"].value_counts().reset_index()
    method_counts.columns = ["Phương thức", "Số bill"]
    method_counts = _rank_limited(method_counts, "Số bill", top_n, sort_ascending)

    fig = px.bar(
        method_counts,
        y="Phương thức",
        x="Số bill",
        orientation="h",
        title=f"Phương thức thu bill (Top {top_n})",
        text="Số bill",
        color="Số bill",
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        template="plotly_white",
        yaxis={"categoryorder": _horizontal_yaxis_order(sort_ascending), "automargin": True},
        coloraxis_showscale=False,
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    return fig


def plot_dvkh_payment_form(df, top_n=10, sort_ascending=False):
    if len(df) == 0:
        return px.bar(title="Không có dữ liệu hình thức thanh toán")

    collected_df = df[df["Da_thu"]]
    form_counts = collected_df["Hinh_thuc_TT_DVKH"].value_counts().reset_index()
    form_counts.columns = ["Hình thức", "Số bill"]
    form_counts = _rank_limited(form_counts, "Số bill", top_n, sort_ascending)

    fig = px.bar(
        form_counts,
        y="Hình thức",
        x="Số bill",
        orientation="h",
        title=f"Hình thức thu bill (Top {top_n})",
        text="Số bill",
        color="Số bill",
        color_continuous_scale="Purples",
    )
    fig.update_layout(
        template="plotly_white",
        yaxis={"categoryorder": _horizontal_yaxis_order(sort_ascending), "automargin": True},
        coloraxis_showscale=False,
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    return fig


def plot_dvkh_region_collection_rate(df, top_n=10, sort_ascending=False):
    if len(df) == 0:
        return px.bar(title="Không có dữ liệu xã/phường")

    grouped = (
        df.groupby("Khu_vuc_DVKH", dropna=False)
        .agg(Tong_bill=("Da_thu", "size"), Bill_thu=("Da_thu", "sum"))
        .reset_index()
    )
    grouped["Ty_le_thu"] = grouped["Bill_thu"] / grouped["Tong_bill"] * 100
    grouped = _rank_limited(
        grouped,
        ["Ty_le_thu", "Bill_thu", "Tong_bill"],
        top_n,
        sort_ascending,
    )
    grouped["Nhan_hien_thi"] = grouped.apply(
        lambda row: f"{row['Ty_le_thu']:.1f}% ({int(row['Bill_thu'])}/{int(row['Tong_bill'])})",
        axis=1,
    )

    fig = px.bar(
        grouped,
        y="Khu_vuc_DVKH",
        x="Ty_le_thu",
        orientation="h",
        title=f"Xếp hạng xã/phường theo tỷ lệ thu bill (Top {top_n})",
        text="Nhan_hien_thi",
        color="Ty_le_thu",
        color_continuous_scale="Greens",
        labels={
            "Khu_vuc_DVKH": "Xã/Phường",
            "Ty_le_thu": "Tỷ lệ thu bill (%)",
            "Nhan_hien_thi": "Tỷ lệ thu bill",
        },
        hover_data={
            "Khu_vuc_DVKH": False,
            "Ty_le_thu": ":.1f",
            "Bill_thu": True,
            "Tong_bill": True,
            "Nhan_hien_thi": False,
        },
    )
    fig.update_layout(
        template="plotly_white",
        yaxis={"categoryorder": _horizontal_yaxis_order(sort_ascending), "automargin": True},
        coloraxis_showscale=False,
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(range=[0, max(105, grouped["Ty_le_thu"].max() * 1.15 if len(grouped) else 100)])
    return fig

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_status_pie(df):
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
    
    fig = px.pie(
        status_counts, 
        values='Số lượng', 
        names='Trạng thái', 
        title='Cơ cấu trạng thái Hợp đồng',
        color='Trạng thái',
        color_discrete_map={'Online': '#28a745', 'Hủy': '#dc3545', 'Đang chờ': '#ffc107'},
        hole=0.4
    )
    return fig

def _plot_rate_ranking(df, group_col, date_col, title, group_label, rate_label, top_n=20, color_scale='Greens'):
    if len(df) == 0 or group_col not in df.columns or date_col not in df.columns:
        return px.bar(title="Không có dữ liệu")

    grouped = (
        df.assign(
            _group=df[group_col].fillna("Khác"),
            _hit=df[date_col].notna(),
        )
        .groupby("_group", dropna=False)
        .agg(Tong_PTTB=("_hit", "size"), So_luong=("_hit", "sum"))
        .reset_index()
    )
    grouped["Ty_le"] = grouped["So_luong"] / grouped["Tong_PTTB"] * 100
    grouped = grouped.sort_values(["Ty_le", "So_luong", "Tong_PTTB"], ascending=False).head(top_n)
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
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(range=[0, max(105, grouped["Ty_le"].max() * 1.15 if len(grouped) else 100)])
    return fig

def plot_department_online_rate_ranking(df, top_n=20):
    return _plot_rate_ranking(
        df,
        "Phong",
        "Ngay_online",
        f"Tỷ lệ online theo phòng (Top {top_n})",
        "Phong",
        "Tỷ lệ online (%)",
        top_n=top_n,
        color_scale="Greens",
    )

def plot_employee_online_rate_ranking(df, top_n=20):
    return _plot_rate_ranking(
        df,
        "Sale",
        "Ngay_online",
        f"Xếp hạng nhân sự theo tỷ lệ online (Top {top_n})",
        "Nhân sự",
        "Tỷ lệ online (%)",
        top_n=top_n,
        color_scale="Greens",
    )

def plot_department_cancel_rate_ranking(df, top_n=20):
    return _plot_rate_ranking(
        df,
        "Phong",
        "Ngay_huy",
        f"Tỷ lệ hủy TSD theo phòng (Top {top_n})",
        "Phong",
        "Tỷ lệ hủy TSD (%)",
        top_n=top_n,
        color_scale="Reds",
    )

def plot_employee_cancel_rate_ranking(df, top_n=20):
    return _plot_rate_ranking(
        df,
        "Sale",
        "Ngay_huy",
        f"Xếp hạng nhân sự theo tỷ lệ hủy TSD (Top {top_n})",
        "Nhân sự",
        "Tỷ lệ hủy TSD (%)",
        top_n=top_n,
        color_scale="Reds",
    )

def plot_top_regions_bar(df, top_n=10):
    if len(df) == 0:
        return px.bar(title="Không có dữ liệu")
        
    region_counts = df['Xa_Phuong'].value_counts().nlargest(top_n).reset_index()
    region_counts.columns = ['Xã/Phường', 'Số lượng']
    
    fig = px.bar(
        region_counts, 
        y='Xã/Phường', 
        x='Số lượng', 
        orientation='h',
        title=f'Top {top_n} Xã/Phường có sản lượng cao nhất',
        text='Số lượng',
        color='Số lượng',
        color_continuous_scale='Blues'
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

def plot_avg_deploy_by_region(df, top_n=10):
    deployed_df = df[df['Ngay_online'].notna() & df['Ngay_tao'].notna()].copy()
    if len(deployed_df) == 0:
        return px.bar(title="Không có dữ liệu thời gian triển khai")
        
    deployed_df['Deploy_Days'] = (deployed_df['Ngay_online'] - deployed_df['Ngay_tao']).dt.days
    deployed_df = deployed_df[deployed_df['Deploy_Days'] >= 0]
    
    avg_days = deployed_df.groupby('Xa_Phuong')['Deploy_Days'].mean().reset_index()
    # Lấy top N xã phường có sản lượng cao nhất để xem thời gian trung bình của chúng
    top_regions = df['Xa_Phuong'].value_counts().nlargest(top_n).index
    avg_days_top = avg_days[avg_days['Xa_Phuong'].isin(top_regions)].sort_values('Deploy_Days', ascending=False)
    
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

def plot_prepaid_stacked_bar(df, top_n=10):
    if len(df) == 0:
        return px.bar(title="Không có dữ liệu")
        
    # Get top regions by volume
    top_regions = df['Xa_Phuong'].value_counts().nlargest(top_n).index
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

def plot_department_pttb_bar(df):
    if len(df) == 0 or 'Phong' not in df.columns:
        return px.bar(title="Không có dữ liệu phòng")

    department_counts = df['Phong'].fillna("Khác").value_counts().reset_index()
    department_counts.columns = ['Phòng', 'Số PTTB']

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
        yaxis={'categoryorder': 'total ascending'},
        coloraxis_showscale=False,
    )
    return fig

def plot_employee_product_contribution(df, top_n=20):
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
    summary = summary.sort_values('Tổng đóng góp', ascending=False).head(top_n)

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

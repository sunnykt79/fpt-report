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
    df_top = df[df['Xa_Phuong'].isin(top_regions)]
    
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
        barmode='stack'
    )
    return fig

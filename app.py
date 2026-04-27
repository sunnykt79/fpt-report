import streamlit as st
import pandas as pd
from utils.data_processing import load_data, get_date_range, filter_data, calculate_metrics
from utils.charts import plot_status_pie, plot_top_regions_bar, plot_avg_deploy_by_region, plot_prepaid_stacked_bar
from utils.export_word import create_word_report
from utils.export_pdf import create_pdf_report
from utils.export_pptx import create_pptx_report

st.set_page_config(page_title="FPT Telecom Sales Reporting", layout="wide", page_icon="📊")

st.title("📊 FPT Telecom Sales Reporting Dashboard (FSRD)")

# Phase 1: Input & Tiền xử lý
uploaded_file = st.sidebar.file_uploader("Upload file Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        with st.spinner('Đang xử lý dữ liệu...'):
            df = load_data(uploaded_file)
            
        min_date, max_date = get_date_range(df)
        
        # Sidebar Filters
        st.sidebar.header("Bộ lọc")
        start_date = st.sidebar.date_input("Từ ngày", min_value=min_date, max_value=max_date, value=min_date)
        end_date = st.sidebar.date_input("Đến ngày", min_value=min_date, max_value=max_date, value=max_date)
        
        # Sales Filter
        sales_list = ["Tất cả"] + list(df['Sale'].dropna().unique())
        selected_sales = st.sidebar.multiselect("Nhân viên Sale", options=sales_list, default=["Tất cả"])
        
        # Lọc dữ liệu
        filtered_df = filter_data(df, start_date, end_date, selected_sales)
        metrics = calculate_metrics(filtered_df)
        
        # Phase 2: Dashboard trực quan
        st.markdown(f"### Dữ liệu từ `{start_date}` đến `{end_date}`")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        col1.metric("Tổng PTTB", metrics["total_pttb"])
        col2.metric("Combo", metrics["combo"])
        col3.metric("V.Vip | Vip", metrics["vvip"])
        col4.metric("Tỷ lệ Online", f"{metrics['online_rate']:.1f}%")
        
        # Cảnh báo Hủy TSD > 15%
        cancel_color = "normal" if metrics['cancel_rate'] <= 15 else "inverse"
        col5.metric("Tỷ lệ Hủy TSD", f"{metrics['cancel_rate']:.1f}%", 
                    delta="Cảnh báo!" if metrics['cancel_rate'] > 15 else None,
                    delta_color=cancel_color)
                    
        col6.metric("Triển khai TB", f"{metrics['avg_deploy_days']:.1f} ngày")
        
        st.markdown("---")
        
        # Tạo biểu đồ và lưu vào biến
        fig_pie = plot_status_pie(filtered_df)
        fig_bar_region = plot_top_regions_bar(filtered_df)
        fig_bar_deploy = plot_avg_deploy_by_region(filtered_df)
        fig_stack_prepaid = plot_prepaid_stacked_bar(filtered_df)
        
        figs = [fig_pie, fig_bar_region, fig_bar_deploy, fig_stack_prepaid]
        
        # Render biểu đồ lên Dashboard
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.plotly_chart(fig_pie, use_container_width=True)
        with row1_col2:
            st.plotly_chart(fig_bar_region, use_container_width=True)
            
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.plotly_chart(fig_bar_deploy, use_container_width=True)
        with row2_col2:
            st.plotly_chart(fig_stack_prepaid, use_container_width=True)
            
        # Phase 3: Kết xuất báo cáo (Export)
        st.sidebar.header("Xuất Báo Cáo")
        
        word_buffer = create_word_report(metrics, start_date, end_date, figs)
        st.sidebar.download_button(
            label="📄 Tải Word (.docx)",
            data=word_buffer,
            file_name="Bao_Cao_FPT.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        pdf_buffer = create_pdf_report(metrics, start_date, end_date, figs)
        st.sidebar.download_button(
            label="📕 Tải PDF",
            data=pdf_buffer,
            file_name="Bao_Cao_FPT.pdf",
            mime="application/pdf"
        )
        
        pptx_buffer = create_pptx_report(metrics, start_date, end_date, figs)
        st.sidebar.download_button(
            label="📊 Tải PowerPoint (.pptx)",
            data=pptx_buffer,
            file_name="Bao_Cao_FPT.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
    except Exception as e:
        st.error(f"Đã xảy ra lỗi khi xử lý dữ liệu: {e}")

else:
    st.info("Vui lòng upload file Excel để bắt đầu.")

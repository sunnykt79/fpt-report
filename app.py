import streamlit as st

from utils.charts import (
    plot_avg_deploy_by_region,
    plot_department_pttb_bar,
    plot_employee_product_contribution,
    plot_prepaid_stacked_bar,
    plot_status_pie,
    plot_top_regions_bar,
)
from utils.data_processing import (
    calculate_metrics,
    filter_data,
    get_date_range,
    load_data_from_separate_files,
    load_data_from_workbook,
)
from utils.export_pdf import create_pdf_report
from utils.export_pptx import create_pptx_report
from utils.export_word import create_word_report


st.set_page_config(page_title="FPT Telecom Sales Reporting", layout="wide", page_icon="📊")

st.title("📊 FPT Telecom Sales Reporting Dashboard (FSRD)")


def load_uploaded_data():
    st.sidebar.header("Nhập dữ liệu")
    import_mode = st.sidebar.radio(
        "Kiểu import",
        ["File tổng hợp", "File Internet + Pay riêng"],
        horizontal=False,
    )

    if import_mode == "File tổng hợp":
        uploaded_file = st.sidebar.file_uploader(
            "Upload file Excel tổng hợp (.xlsx)",
            type=["xlsx"],
            help="File cần có 2 sheet: Internet và Pay.",
        )
        if uploaded_file is None:
            return None

        with st.spinner("Đang xử lý dữ liệu..."):
            return load_data_from_workbook(uploaded_file)

    internet_file = st.sidebar.file_uploader(
        "Upload file Internet/NET (.xlsx)",
        type=["xlsx"],
        key="internet_file",
    )
    pay_file = st.sidebar.file_uploader(
        "Upload file Pay/Truyền hình (.xlsx)",
        type=["xlsx"],
        key="pay_file",
    )

    if internet_file is None or pay_file is None:
        return None

    with st.spinner("Đang xử lý dữ liệu từ 2 file riêng..."):
        return load_data_from_separate_files(internet_file, pay_file)


try:
    df = load_uploaded_data()

    if df is None:
        st.info("Vui lòng upload file Excel để bắt đầu.")
        st.stop()

    min_date, max_date = get_date_range(df)

    st.sidebar.header("Bộ lọc")
    start_date = st.sidebar.date_input("Từ ngày", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.sidebar.date_input("Đến ngày", min_value=min_date, max_value=max_date, value=max_date)

    sales_list = ["Tất cả"] + list(df["Sale"].dropna().unique())
    selected_sales = st.sidebar.multiselect("Nhân viên Sale", options=sales_list, default=["Tất cả"])

    filtered_df = filter_data(df, start_date, end_date, selected_sales)
    metrics = calculate_metrics(filtered_df)

    st.markdown(f"### Dữ liệu từ `{start_date}` đến `{end_date}`")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Tổng PTTB", metrics["total_pttb"])
    col2.metric("Combo", metrics["combo"])
    col3.metric("V.Vip | Vip", metrics["vvip"])
    col4.metric("Tỷ lệ Online", f"{metrics['online_rate']:.1f}%")

    cancel_color = "normal" if metrics["cancel_rate"] <= 15 else "inverse"
    col5.metric(
        "Tỷ lệ Hủy TSD",
        f"{metrics['cancel_rate']:.1f}%",
        delta="Cảnh báo!" if metrics["cancel_rate"] > 15 else None,
        delta_color=cancel_color,
    )

    col6.metric("Triển khai TB", f"{metrics['avg_deploy_days']:.1f} ngày")

    st.markdown("---")

    fig_pie = plot_status_pie(filtered_df)
    fig_bar_region = plot_top_regions_bar(filtered_df)
    fig_bar_deploy = plot_avg_deploy_by_region(filtered_df)
    fig_stack_prepaid = plot_prepaid_stacked_bar(filtered_df)
    fig_department = plot_department_pttb_bar(filtered_df)
    fig_employee = plot_employee_product_contribution(filtered_df)

    figs = [fig_pie, fig_bar_region, fig_bar_deploy, fig_stack_prepaid, fig_department, fig_employee]

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

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        st.plotly_chart(fig_department, use_container_width=True)
    with row3_col2:
        st.plotly_chart(fig_employee, use_container_width=True)

    st.sidebar.header("Xuất Báo Cáo")

    word_buffer = create_word_report(metrics, start_date, end_date, figs)
    st.sidebar.download_button(
        label="📄 Tải Word (.docx)",
        data=word_buffer,
        file_name="Bao_Cao_FPT.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    pdf_buffer = create_pdf_report(metrics, start_date, end_date, figs)
    st.sidebar.download_button(
        label="📕 Tải PDF",
        data=pdf_buffer,
        file_name="Bao_Cao_FPT.pdf",
        mime="application/pdf",
    )

    pptx_buffer = create_pptx_report(metrics, start_date, end_date, figs)
    st.sidebar.download_button(
        label="📊 Tải PowerPoint (.pptx)",
        data=pptx_buffer,
        file_name="Bao_Cao_FPT.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )

except Exception as e:
    st.error(f"Đã xảy ra lỗi khi xử lý dữ liệu: {e}")

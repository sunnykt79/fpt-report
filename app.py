import streamlit as st

from utils.charts import (
    plot_avg_deploy_by_region,
    plot_department_cancel_rate_ranking,
    plot_department_online_rate_ranking,
    plot_department_pttb_bar,
    plot_dvkh_bill_status,
    plot_dvkh_collector_ranking,
    plot_dvkh_outstanding_by_collector,
    plot_dvkh_payment_form,
    plot_dvkh_payment_method,
    plot_dvkh_region_collection_rate,
    plot_employee_cancel_rate_ranking,
    plot_employee_online_rate_ranking,
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
from utils.dvkh_processing import (
    calculate_dvkh_metrics,
    filter_dvkh_data,
    get_dvkh_date_range,
    load_dvkh_data,
)
from utils.export_pdf import create_pdf_report
from utils.export_pptx import create_pptx_report
from utils.export_word import create_word_report


st.set_page_config(page_title="FPT Telecom Reporting", layout="wide", page_icon="📊")

st.title("📊 FPT Telecom Reporting Dashboard")

st.markdown(
    """
    <style>
    div[data-testid="stHorizontalBlock"] {
        gap: 1.25rem;
    }
    div[data-testid="stPlotlyChart"] {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_uploaded_sales_data():
    st.sidebar.header("Nhập dữ liệu bán hàng")
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
            key="sales_workbook",
        )
        if uploaded_file is None:
            return None

        with st.spinner("Đang xử lý dữ liệu bán hàng..."):
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


def load_uploaded_dvkh_data():
    st.sidebar.header("Nhập dữ liệu DVKH")
    uploaded_file = st.sidebar.file_uploader(
        "Upload file bill DVKH (.xlsx)",
        type=["xlsx"],
        help="File cần có các cột: Hợp đồng, Ngày thanh toán, Nhân viên thu, Nhân viên phân công, Phương thức thanh toán, Hình thức thanh toán.",
        key="dvkh_file",
    )
    if uploaded_file is None:
        return None

    with st.spinner("Đang xử lý dữ liệu DVKH..."):
        return load_dvkh_data(uploaded_file)


def get_sort_ascending():
    chart_sort_order = st.sidebar.radio(
        "Sắp xếp chart",
        ["Cao đến thấp", "Thấp đến cao"],
        horizontal=False,
    )
    return chart_sort_order == "Thấp đến cao"


def render_sales_report():
    df = load_uploaded_sales_data()

    if df is None:
        st.info("Vui lòng upload file Excel bán hàng để bắt đầu.")
        st.stop()

    min_date, max_date = get_date_range(df)

    st.sidebar.header("Bộ lọc bán hàng")
    start_date = st.sidebar.date_input("Từ ngày", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.sidebar.date_input("Đến ngày", min_value=min_date, max_value=max_date, value=max_date)

    sales_list = ["Tất cả"] + list(df["Sale"].dropna().unique())
    selected_sales = st.sidebar.multiselect("Nhân viên Sale", options=sales_list, default=["Tất cả"])
    sort_ascending = get_sort_ascending()

    filtered_df = filter_data(df, start_date, end_date, selected_sales)
    metrics = calculate_metrics(filtered_df)

    st.markdown(f"### Báo cáo bán hàng từ `{start_date}` đến `{end_date}`")

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

    fig_pie = plot_status_pie(filtered_df, sort_ascending=sort_ascending)
    fig_bar_region = plot_top_regions_bar(filtered_df, sort_ascending=sort_ascending)
    fig_bar_deploy = plot_avg_deploy_by_region(filtered_df, sort_ascending=sort_ascending)
    fig_stack_prepaid = plot_prepaid_stacked_bar(filtered_df, sort_ascending=sort_ascending)
    fig_department = plot_department_pttb_bar(filtered_df, sort_ascending=sort_ascending)
    fig_employee = plot_employee_product_contribution(filtered_df, sort_ascending=sort_ascending)
    fig_department_online = plot_department_online_rate_ranking(filtered_df, sort_ascending=sort_ascending)
    fig_employee_online = plot_employee_online_rate_ranking(filtered_df, sort_ascending=sort_ascending)
    fig_department_cancel = plot_department_cancel_rate_ranking(filtered_df, sort_ascending=sort_ascending)
    fig_employee_cancel = plot_employee_cancel_rate_ranking(filtered_df, sort_ascending=sort_ascending)

    figs = [
        fig_pie,
        fig_bar_region,
        fig_bar_deploy,
        fig_stack_prepaid,
        fig_department,
        fig_employee,
        fig_department_online,
        fig_employee_online,
        fig_department_cancel,
        fig_employee_cancel,
    ]

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

    row4_col1, row4_col2 = st.columns(2)
    with row4_col1:
        st.plotly_chart(fig_department_online, use_container_width=True)
    with row4_col2:
        st.plotly_chart(fig_employee_online, use_container_width=True)

    row5_col1, row5_col2 = st.columns(2)
    with row5_col1:
        st.plotly_chart(fig_department_cancel, use_container_width=True)
    with row5_col2:
        st.plotly_chart(fig_employee_cancel, use_container_width=True)

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


def render_dvkh_report():
    df = load_uploaded_dvkh_data()

    if df is None:
        st.info("Vui lòng upload file Excel DVKH để bắt đầu.")
        st.stop()

    min_date, max_date = get_dvkh_date_range(df)

    st.sidebar.header("Bộ lọc DVKH")
    start_date = st.sidebar.date_input("Từ ngày", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.sidebar.date_input("Đến ngày", min_value=min_date, max_value=max_date, value=max_date)

    collector_list = ["Tất cả"] + list(df["Nhan_vien_thu"].dropna().sort_values().unique())
    selected_collectors = st.sidebar.multiselect("Nhân viên thu", options=collector_list, default=["Tất cả"])

    region_list = ["Tất cả"] + list(df["Khu_vuc_DVKH"].dropna().sort_values().unique())
    selected_regions = st.sidebar.multiselect("Khu vực", options=region_list, default=["Tất cả"])
    sort_ascending = get_sort_ascending()

    filtered_df = filter_dvkh_data(df, start_date, end_date, selected_collectors, selected_regions)
    metrics = calculate_dvkh_metrics(filtered_df)

    st.markdown(f"### Báo cáo DVKH từ `{start_date}` đến `{end_date}`")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Tổng bill", metrics["total_bill"])
    col2.metric("Bill đã thu", metrics["collected_bill"])
    col3.metric("Bill tồn", metrics["outstanding_bill"])
    col4.metric("Tỷ lệ thu", f"{metrics['collected_rate']:.1f}%")
    col5.metric("PTTT | HTTT", f"{metrics['payment_methods']} | {metrics['payment_forms']}")

    st.caption("Bill tồn được tính là các dòng chưa có Ngày thanh toán. Khi lọc ngày, bill đã thu lọc theo ngày thanh toán; bill tồn chưa có ngày vẫn được giữ để theo dõi.")
    st.markdown("---")

    fig_status = plot_dvkh_bill_status(filtered_df, sort_ascending=sort_ascending)
    fig_collector = plot_dvkh_collector_ranking(filtered_df, sort_ascending=sort_ascending)
    fig_outstanding = plot_dvkh_outstanding_by_collector(filtered_df, sort_ascending=sort_ascending)
    fig_method = plot_dvkh_payment_method(filtered_df, sort_ascending=sort_ascending)
    fig_form = plot_dvkh_payment_form(filtered_df, sort_ascending=sort_ascending)
    fig_region_rate = plot_dvkh_region_collection_rate(filtered_df, sort_ascending=sort_ascending)

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.plotly_chart(fig_status, use_container_width=True)
    with row1_col2:
        st.plotly_chart(fig_collector, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.plotly_chart(fig_outstanding, use_container_width=True)
    with row2_col2:
        st.plotly_chart(fig_method, use_container_width=True)

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        st.plotly_chart(fig_form, use_container_width=True)
    with row3_col2:
        st.plotly_chart(fig_region_rate, use_container_width=True)


try:
    report_mode = st.sidebar.selectbox(
        "Menu báo cáo",
        ["Báo cáo bán hàng", "Báo cáo DVKH"],
    )

    if report_mode == "Báo cáo bán hàng":
        render_sales_report()
    else:
        render_dvkh_report()

except Exception as e:
    st.error(f"Đã xảy ra lỗi khi xử lý dữ liệu: {e}")

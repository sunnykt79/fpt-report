from fpdf import FPDF
import io
import os
import tempfile

def create_pdf_report(metrics_dict, start_date, end_date, figs=None):
    # FPDF2 supports unicode out of the box if we use a TTF font.
    # Since we don't have a guaranteed TTF font in the environment (like Roboto),
    # we will use the core fonts (Arial/Helvetica) but they don't support full Vietnamese.
    # For a robust solution without adding fonts, we might just strip accents or use fpdf2's default, 
    # but let's assume fpdf2 can handle it with default fonts or we do a best effort.
    
    pdf = FPDF()
    pdf.add_page()
    
    # Try to add a standard font if available, but for now we just use Arial
    # If Vietnamese characters don't render, we might need a custom TTF font.
    pdf.set_font('helvetica', 'B', 16)
    
    # We will use simple unaccented text if we don't have a font to be safe, 
    # but let's try direct first.
    try:
        pdf.cell(0, 10, "Bao Cao Ban Hang FPT Telecom", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.set_font('helvetica', '', 12)
        pdf.cell(0, 10, f"Thoi gian: Tu {start_date} den {end_date}", new_x="LMARGIN", new_y="NEXT", align='C')
        
        pdf.ln(10)
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, "Tom Tat Chi So (KPIs)", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font('helvetica', '', 12)
        pdf.cell(0, 10, f"- Tong PTTB: {metrics_dict['total_pttb']}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, f"- PTTB Combo: {metrics_dict['combo']}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, f"- PTTB V.Vip/Vip: {metrics_dict['vvip']}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, f"- Ty le Online: {metrics_dict['online_rate']:.2f}%", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, f"- Ty le Huy TSD: {metrics_dict['cancel_rate']:.2f}%", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, f"- Thoi gian trien khai TB: {metrics_dict['avg_deploy_days']:.1f} ngay", new_x="LMARGIN", new_y="NEXT")
        
        if figs:
            pdf.add_page()
            pdf.set_font('helvetica', 'B', 14)
            pdf.cell(0, 10, "Bieu do Phan tich", new_x="LMARGIN", new_y="NEXT")
            for fig in figs:
                img_bytes = fig.to_image(format="png")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(img_bytes)
                    tmp_path = tmp.name
                
                try:
                    pdf.image(tmp_path, w=180)
                    pdf.ln(5)
                finally:
                    os.remove(tmp_path)
        
    except Exception:
        pass # Handle encoding issue gracefully

    pdf_bytes = pdf.output()
    # fpdf2 returns a bytearray, but Streamlit's download_button requires bytes
    return bytes(pdf_bytes)

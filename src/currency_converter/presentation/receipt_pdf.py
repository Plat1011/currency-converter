from __future__ import annotations

from datetime import datetime
from io import BytesIO
from uuid import uuid4

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def _money_line(label: str, value: str) -> str:
    return f"{label:<12}{value:>18}"


def build_receipt_pdf(
    *,
    amount: float,
    from_currency: str,
    to_currency: str,
    rate: float,
    result: float,
) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(80 * mm, 120 * mm))
    pdf.setTitle("currency-converter-receipt")

    y = 112 * mm
    line_height = 5.5 * mm

    pdf.setFont("Courier-Bold", 12)
    pdf.drawCentredString(40 * mm, y, "CASH RECEIPT")
    y -= line_height

    pdf.setFont("Courier", 9)
    pdf.drawCentredString(40 * mm, y, "Currency Converter POS")
    y -= line_height

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    receipt_no = uuid4().hex[:10].upper()

    pdf.drawString(8 * mm, y, f"Receipt: {receipt_no}")
    y -= line_height
    pdf.drawString(8 * mm, y, f"Date:    {timestamp}")
    y -= line_height

    pdf.line(8 * mm, y, 72 * mm, y)
    y -= line_height

    pdf.drawString(8 * mm, y, _money_line("Amount", f"{amount:.2f} {from_currency}"))
    y -= line_height
    pdf.drawString(8 * mm, y, _money_line("Rate", f"{rate:.4f}"))
    y -= line_height
    pdf.drawString(8 * mm, y, _money_line("Result", f"{result:.2f} {to_currency}"))
    y -= line_height
    pdf.drawString(8 * mm, y, _money_line("Route", f"{from_currency} -> {to_currency}"))
    y -= line_height

    pdf.line(8 * mm, y, 72 * mm, y)
    y -= line_height

    pdf.setFont("Courier-Bold", 10)
    pdf.drawString(8 * mm, y, _money_line("TOTAL", f"{result:.2f} {to_currency}"))
    y -= line_height * 1.5

    pdf.setFont("Courier", 9)
    pdf.drawCentredString(40 * mm, y, "Thank you for your conversion")

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()

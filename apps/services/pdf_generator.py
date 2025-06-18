from io import BytesIO
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import datetime


def generate_receipt_pdf(vehicle, entry_time, exit_time, amount):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica", 12)
    p.drawString(100, 800, f"Jarima Maydoni Qabul Kvittansiyasi")
    p.drawString(100, 780, f"Avtomobil raqami: {vehicle.plate_number}")
    p.drawString(100, 760, f"Kirish vaqti: {entry_time}")
    p.drawString(100, 740, f"Chiqish vaqti: {exit_time}")
    p.drawString(100, 720, f"To‘lov summasi: {amount} so‘m")

    p.drawString(100, 700, f"Sana: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    p.drawString(100, 680, f"Imzo: ________________")

    p.showPage()
    p.save()

    buffer.seek(0)
    file_content = ContentFile(buffer.getvalue())
    file_name = f"receipts/{vehicle.plate_number}_{datetime.datetime.now().timestamp()}.pdf"
    file_path = default_storage.save(file_name, file_content)

    return file_path

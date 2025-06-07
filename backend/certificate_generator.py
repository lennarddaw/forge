from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import hashlib
import qrcode
from io import BytesIO
import os

def generate_certificate(name, course, date, issuer, output_path):
    # 1. Erstelle Hash für Verifikation
    data_string = f"{name}|{course}|{issuer}|{date}"
    cert_hash = hashlib.sha256(data_string.encode()).hexdigest()

    # 2. Erstelle QR-Code
    verification_url = f"https://opencertify.org/verify/{cert_hash}"
    qr = qrcode.make(verification_url)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_img = ImageReader(qr_buffer)

    # 3. PDF erzeugen
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 100, "ZERTIFIKAT")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 150, f"Hiermit wird bestätigt, dass")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 180, name)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 210, f"am Kurs „{course}“ erfolgreich teilgenommen hat.")
    c.drawCentredString(width/2, height - 240, f"Datum: {date}")
    c.drawCentredString(width/2, height - 260, f"Ausgestellt von: {issuer}")

    c.setFont("Helvetica", 8)
    c.drawString(40, 80, f"Verifikationscode: {cert_hash[:32]}...")
    c.drawImage(qr_img, width - 140, 40, width=100, height=100)

    c.showPage()
    c.save()

    return cert_hash

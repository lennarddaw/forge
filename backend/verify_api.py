from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import re
import hashlib
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import qrcode

app = FastAPI(title="OpenCertify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verzeichnisse & Datenbank-Pfad
DB_PATH    = "backend/verify_db.json"
OUTPUT_DIR = "output"
UPLOAD_DIR = "uploads"
SIGNED_DIR = "signed"
for d in (OUTPUT_DIR, UPLOAD_DIR, SIGNED_DIR, os.path.dirname(DB_PATH)):
    os.makedirs(d, exist_ok=True)

@app.post("/sign-pdf")
async def sign_uploaded_pdf(file: UploadFile = File(...)):
    # 1. Datei speichern
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    content = await file.read()
    with open(file_location, "wb") as f:
        f.write(content)

    # 2. Hash berechnen
    cert_hash = hashlib.sha256(content).hexdigest()

    # 3. Signaturseite generieren
    sig_buffer = BytesIO()
    c = canvas.Canvas(sig_buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 700, "OpenCertify Signature")
    c.setFont("Helvetica", 10)
    c.drawString(100, 680, f"Verifikationscode: {cert_hash}")
    c.drawString(100, 660, f"QR-Link: http://127.0.0.1:8000/verify/{cert_hash}")
    c.showPage()
    c.save()
    sig_buffer.seek(0)

    # 4. Original-PDF + Signaturseite zusammenführen
    original = PdfReader(file_location)
    sig_pdf  = PdfReader(sig_buffer)
    writer   = PdfWriter()
    for page in original.pages:
        writer.add_page(page)
    writer.add_page(sig_pdf.pages[0])

    output_path = os.path.join(SIGNED_DIR, f"signed_{file.filename}")
    with open(output_path, "wb") as out_f:
        writer.write(out_f)

    # 5. Hash in DB speichern
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        db = {}
    db[cert_hash] = {"source": file.filename, "signed": True}
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

    # 6. Die signierte PDF zurückliefern
    return FileResponse(output_path, media_type="application/pdf", filename=f"signed_{file.filename}")

@app.post("/verify-pdf")
async def verify_uploaded_pdf(file: UploadFile = File(...)):
    # 1. Datei einlesen
    content = await file.read()
    try:
        reader = PdfReader(BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Keine gültige PDF")

    if len(reader.pages) < 1:
        return JSONResponse(status_code=400, content={"valid": False, "message": "PDF enthält keine Seiten."})

    # 2. Signaturseite (letzte Seite) auslesen
    last_page = reader.pages[-1]
    text = last_page.extract_text() or ""

    # 3. Hash mittels Regex extrahieren
    match = re.search(r"Verifikationscode:\s*([0-9a-f]{64})", text)
    if not match:
        return JSONResponse(status_code=400, content={"valid": False, "message": "Signatur-Code nicht gefunden."})
    cert_hash = match.group(1)

    # 4. In verify_db.json nachschlagen
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Verifikationsdatenbank nicht gefunden.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Verifikationsdatenbank fehlerhaft formatiert.")

    if cert_hash in db:
        return {"valid": True, "data": db[cert_hash]}
    else:
        return {"valid": False, "message": "Zertifikat nicht in der Datenbank."}

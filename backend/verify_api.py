from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.certificate_generator import generate_certificate
import json, os, hashlib
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO

app = FastAPI(title="OpenCertify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "backend/verify_db.json"
OUTPUT_DIR = "output"
UPLOAD_DIR = "uploads"
SIGNED_DIR = "signed"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SIGNED_DIR, exist_ok=True)

class CertData(BaseModel):
    name: str
    course: str
    date: str
    issuer: str

@app.post("/generate")
def generate(cert: CertData):
    filename = cert.name.replace(" ", "_") + ".pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)

    hash_code = generate_certificate(cert.name, cert.course, cert.date, cert.issuer, output_path)

    try:
        with open(DB_PATH, "r") as f:
            db = json.load(f)
    except:
        db = {}

    db[hash_code] = cert.dict()

    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=4)

    return {
        "status": "ok",
        "hash": hash_code,
        "pdf": f"/download/{filename}"
    }

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf', filename=filename)
    return JSONResponse(status_code=404, content={"error": "Datei nicht gefunden"})

@app.get("/verify/{hash_code}")
def verify_certificate(hash_code: str):
    if not os.path.exists(DB_PATH):
        return JSONResponse(status_code=500, content={"error": "Verifikationsdatenbank nicht gefunden."})

    with open(DB_PATH, "r") as f:
        try:
            db = json.load(f)
        except json.JSONDecodeError:
            return JSONResponse(status_code=500, content={"error": "Verifikationsdatenbank beschädigt."})

    if hash_code in db:
        return {"valid": True, "data": db[hash_code]}
    else:
        return {"valid": False, "message": "Zertifikat nicht gefunden oder ungültig."}

@app.post("/sign-pdf")
async def sign_uploaded_pdf(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    cert_hash = hashlib.sha256(content).hexdigest()

    # Signaturseite generieren
    sig_buffer = BytesIO()
    c = canvas.Canvas(sig_buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 700, "OpenCertify Signature")
    c.setFont("Helvetica", 10)
    c.drawString(100, 680, f"Verifikationscode: {cert_hash}")
    c.drawString(100, 660, f"QR-Link: https://opencertify.org/verify/{cert_hash}")
    c.save()
    sig_buffer.seek(0)

    # Neues PDF erzeugen
    output_path = os.path.join(SIGNED_DIR, f"signed_{file.filename}")
    original = PdfReader(file_location)
    sig_pdf = PdfReader(sig_buffer)
    writer = PdfWriter()

    for page in original.pages:
        writer.add_page(page)
    writer.add_page(sig_pdf.pages[0])

    with open(output_path, "wb") as out_f:
        writer.write(out_f)

    # ✅ Speichere Hash in verify_db.json
    try:
        with open(DB_PATH, "r") as f:
            db = json.load(f)
    except:
        db = {}

    db[cert_hash] = {
        "source": file.filename,
        "signed": True
    }

    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=4)

    return FileResponse(output_path, media_type="application/pdf", filename=f"signed_{file.filename}")

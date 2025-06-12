from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

import json
import os
import hashlib
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter

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
UPLOAD_DIR = "uploads"
SIGNED_DIR = "signed"
for d in (UPLOAD_DIR, SIGNED_DIR, os.path.dirname(DB_PATH)):
    os.makedirs(d, exist_ok=True)

@app.post("/sign-pdf")
async def sign_uploaded_pdf(file: UploadFile = File(...)):
    # 1. PDF-Inhalt lesen
    content = await file.read()
    # 2. SHA256-Hash berechnen
    cert_hash = hashlib.sha256(content).hexdigest()

    # 3. PDF öffnen und alle Seiten übernehmen
    try:
        reader = PdfReader(BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Keine gültige PDF")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    # 4. Hash als unsichtbares Metadatum hinzufügen
    metadata = reader.metadata or {}
    metadata.update({"/CertHash": cert_hash})
    writer.add_metadata(metadata)

    # 5. Ergebnis speichern
    output_path = os.path.join(SIGNED_DIR, f"signed_{file.filename}")
    with open(output_path, "wb") as out_f:
        writer.write(out_f)

    # 6. Hash in DB speichern
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        db = {}
    db[cert_hash] = {"source": file.filename, "signed": True}
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

    # 7. Signierte Datei zurückliefern
    return FileResponse(output_path, media_type="application/pdf", filename=f"signed_{file.filename}")

@app.post("/verify-pdf")
async def verify_uploaded_pdf(file: UploadFile = File(...)):
    # 1. PDF-Inhalt lesen
    content = await file.read()
    try:
        reader = PdfReader(BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Keine gültige PDF")

    # 2. Metadaten auslesen
    metadata = reader.metadata or {}
    cert_hash = metadata.get("/CertHash")
    if not cert_hash:
        return JSONResponse(status_code=400, content={"valid": False, "message": "Signatur-Metadatum nicht gefunden."})

    # 3. In DB nachschlagen
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

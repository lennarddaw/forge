from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import json
import os
import hashlib # wichtig für SHA256-Hashing
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter

app = FastAPI(title="Forge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # notwendig da manchmal blockiert
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH= "backend/verify_db.json"

@app.post("/sign-pdf")
async def sign_uploaded_pdf(file: UploadFile = File(...)):
    content = await file.read()
    cert_hash = hashlib.sha256(content).hexdigest()

# Bisherigen Content lesen
    try:
        reader = PdfReader(BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Keine gültige PDF")

# Sette Writer
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)


    metadata = reader.metadata or {} #lesen
    metadata.update({"/CertHash": cert_hash}) # ändern
    writer.add_metadata(metadata) # Gebe dem Writer Bescheid

# BytesIO-Stream im RAM
    output_stream = BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)

# Datenbankeintrag
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        db = {}

    db[cert_hash] = {
        "source": file.filename,
        "signed": True
    }

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

    return StreamingResponse(
        output_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=signed_{file.filename}"
        }
    )



@app.post("/verify-pdf") # POST-Endpoint
async def verify_uploaded_pdf(file: UploadFile = File(...)):
    content = await file.read() # Wieder warten auf content und lesen
    try:
        reader = PdfReader(BytesIO(content)) # Binärinhalt in ein lesbares PDF
    except Exception:
        raise HTTPException(status_code=400, detail="Keine gültige PDF")

    metadata = reader.metadata or {} # alles wie in POST /sign-pdf
    cert_hash = metadata.get("/CertHash")
    if not cert_hash:
        return JSONResponse(status_code=400, content={"valid": False, "message": "Signatur-Metadatum nicht gefunden."})

    try: # Checke hier noch die DB, kann ja auch an ihr legen
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
    # Untescheidung, wenn DB nicht defekt, irgendwo Fehler beim Upload :)

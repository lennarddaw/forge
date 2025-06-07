from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.certificate_generator import generate_certificate
import json, os

app = FastAPI(title="OpenCertify API")

# ✅ CORS aktivieren (für lokale Tests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion: hier domain setzen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "backend/verify_db.json"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

    # Update DB
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
        return {
            "valid": True,
            "data": db[hash_code]
        }
    else:
        return {
            "valid": False,
            "message": "Zertifikat nicht gefunden oder ungültig."
        }

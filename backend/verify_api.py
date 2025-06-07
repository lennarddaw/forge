from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import os

app = FastAPI(title="OpenCertify Verification API")

DB_PATH = "backend/verify_db.json"

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

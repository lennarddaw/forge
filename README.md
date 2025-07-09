# Forge

**Forge** ist ein leichtgewichtiges Open-Source-Projekt zur PDF-Signierung und -Verifikation auf Basis von SHA256-Hashwerten. Statt klassischer digitaler Signaturen wird der Hash als Metadatum (`/CertHash`) in die PDF eingebettet und serverseitig in einer JSON-Datenbank gespeichert.

## Features

- Hashbasierte Signierung von PDF-Dateien (keine Speicherung auf dem Server)
- Verifikation über `/verify-pdf` anhand des eingebetteten Metadaten-Hashes
- JSON-Register (`verify_db.json`) zur Verwaltung registrierter Dokumente
- Kein Speichern von PDF-Dateien im Projektverzeichnis
- FastAPI-Backend mit einfacher REST-Schnittstelle

## Projektstruktur

```
forge/
├── backend/
│   ├── __init__.py
│   ├── verify_api.py         # Signier- und Verifikationslogik (FastAPI)
│   ├── verify_db.json        # Hash-basierte Signaturdatenbank
├── frontend/                 # Optional: UI (nicht enthalten)
├── venv/                     # Virtuelle Umgebung
├── requirements.txt          # Abhängigkeiten
├── start.bat                 # Lokaler Startbefehl (optional)
└── README.md
```

## API-Endpunkte

### 🔏 `/sign-pdf` – PDF signieren
- **Methode:** `POST`
- **Eingabe:** `multipart/form-data` mit PDF-Datei
- **Ausgabe:** Direkt-Download der signierten Datei (mit eingebettetem Hash)
- **Verhalten:** PDF wird **nicht gespeichert**, nur in RAM verarbeitet

### 🔍 `/verify-pdf` – PDF verifizieren
- **Methode:** `POST`
- **Eingabe:** PDF-Datei
- **Ausgabe:** JSON mit `valid: true/false` und ggf. Eintragsdaten

## Schnellstart

### 1. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 2. Server starten
```bash
uvicorn backend.verify_api:app --reload
```

### 3. API testen
z. B. mit [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

## Sicherheitshinweis

Die Signatur basiert **ausschließlich auf SHA256-Hashing und Metadatenmanipulation**. Es handelt sich **nicht um eine kryptographisch sichere digitale Signatur**. Eine Erweiterung mit X.509-Zertifikaten oder PKCS#7 wäre möglich.

## Lizenz

MIT License – frei nutzbar, veränderbar und verbreitbar.

# Forge

**OpenCertify** is a lightweight, open-source certificate generator that creates verifiable PDF certificates with embedded QR codes and SHA256 hashes. Ideal for online courses, hackathons, or internal training programs.

## Features

- Generate custom PDF certificates
- Embed SHA256-based verification codes
- Optional QR codes linking to verification endpoints
- Minimal frontend interface (HTML/CSS)
- Simple backend with Python (no login required)

## Project Structure

```
backend/
├── app.py                   # Main runner
├── certificate_generator.py # PDF + QR generation
├── utils.py                 # Hash verification
├── verify_db.json           # Optional hash registry
└── templates/
    └── template.html        # (Optional future use)

frontend/
├── index.html               # Basic UI
└── styles.css               # Styling

output/                      # Final certificate PDFs
README.md
requirements.txt
```

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the script
```bash
python backend/app.py
```

### 3. Output
A certificate PDF will be created in the `/output` folder with an embedded QR code and verification hash.

## License

MIT License – free to use, modify, and distribute.

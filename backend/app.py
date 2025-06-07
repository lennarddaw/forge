from certificate_generator import generate_certificate
import os

# Beispieldaten
name = "Anna Müller"
course = "Einführung in Künstliche Intelligenz"
date = "06.06.2025"
issuer = "Lennard Gross – OpenCertify"

# Ausgabeordner sicherstellen
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Zertifikat erzeugen
output_file = os.path.join(output_dir, f"{name.replace(' ', '_')}.pdf")
hash_code = generate_certificate(name, course, date, issuer, output_file)

# Erfolgsmeldung
print(f"✅ Zertifikat erstellt: {output_file}")
print(f"🔐 Verifikationscode: {hash_code}")
print(f"🔗 Verifikationslink: https://opencertify.org/verify/{hash_code}")

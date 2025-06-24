import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from certificate_generator import generate_certificate
import os
import json

name = ""
course = ""
date = ""
issuer = ""
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, f"{name.replace(' ', '_')}.pdf")
hash_code = generate_certificate(name, course, date, issuer, output_file)

db_path = "backend/verify_db.json"

if not os.path.exists(db_path) or os.stat(db_path).st_size == 0:
    db = {}
else:
    with open(db_path, "r") as f:
        db = json.load(f)


db[hash_code] = {
    "name": name,
    "course": course,
    "date": date,
    "issuer": issuer
}

with open(db_path, "w") as f:
    json.dump(db, f, indent=4)

print(f" Zertifikat erstellt: {output_file}")
print(f" Verifikationscode: {hash_code}")
print(f" Verifikationslink: https://opencertify.org/verify/{hash_code}")

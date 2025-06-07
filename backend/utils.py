import hashlib

def verify_certificate(file_path, expected_hash):
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
    actual_hash = hashlib.sha256(pdf_bytes).hexdigest()

    return actual_hash == expected_hash

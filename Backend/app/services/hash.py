import hashlib

def get_image_hash(image_bytes: bytes) -> str:
    """Generate SHA256 hash for image bytes to ensure integrity."""
    return hashlib.sha256(image_bytes).hexdigest()

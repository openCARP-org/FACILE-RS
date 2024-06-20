import hashlib


def get_sha256(file_path):
    """
    Get the SHA256 checksum of a file.
    """
    m = hashlib.sha256()
    m.update(file_path.read_text().encode())
    return m.hexdigest()


def get_sha512(file_path):
    """
    Get the SHA512 checksum of a file.
    """
    m = hashlib.sha512()
    m.update(file_path.read_text().encode())
    return m.hexdigest()

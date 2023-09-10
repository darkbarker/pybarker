import hashlib


def md5sum(content: bytes) -> str:
    """ get md5 sum hex-lowercase """
    return hashlib.md5(content).hexdigest().lower()

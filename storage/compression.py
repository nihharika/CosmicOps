import zlib

def compress(data: bytes):
    return zlib.compress(data, level=9)

def decompress(data: bytes):
    return zlib.decompress(data)
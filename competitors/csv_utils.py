def decode_csv_bytes(raw: bytes) -> str:
    """
    Decode an uploaded CSV's raw bytes, tolerating the encodings real-world
    files actually show up in - not just UTF-8. Excel's "CSV (Comma
    delimited)" export on Windows writes cp1252, not UTF-8, so a smart quote
    or curly apostrophe typed in Excel/Word becomes a byte (e.g. 0x92) that
    strict UTF-8 decoding rejects outright.
    """
    for encoding in ('utf-8-sig', 'cp1252'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    # latin-1 maps every byte to a character, so it never raises - guaranteed
    # fallback so an upload never hard-fails on encoding alone.
    return raw.decode('latin-1')

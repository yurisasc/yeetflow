import re
from pathlib import Path
from urllib.parse import quote


def sanitize_filename(filename: str) -> tuple[str, str]:
    """
    Sanitize filename for Content-Disposition header to prevent header injection.

    Returns a tuple of (ascii_safe_filename, utf8_encoded_filename).
    """
    if not filename:
        return "file", "file"

    # Remove path components to prevent directory traversal
    filename = Path(filename).name

    # Strip CR/LF and other control characters
    filename = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", filename)

    # Create ASCII-safe version by replacing non-ASCII characters
    ascii_safe = re.sub(r"[^\x20-\x7e]", "_", filename)

    # If ASCII-safe version is empty or starts with a dot, provide a fallback
    if not ascii_safe or ascii_safe.startswith("."):
        ascii_safe = "file"

    # URL-encode the UTF-8 filename for RFC5987 compliance
    utf8_encoded = quote(filename.encode("utf-8"), safe="")

    return ascii_safe, utf8_encoded

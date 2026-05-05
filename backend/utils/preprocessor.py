import re
import unicodedata


def preprocess_text(text: str, max_length: int = 512) -> str:
    """Normaliza texto antes de enviarlo al tokenizador."""
    normalized = unicodedata.normalize("NFC", text)
    without_control_chars = "".join(
        char for char in normalized if unicodedata.category(char)[0] != "C"
    )
    collapsed = re.sub(r"\s+", " ", without_control_chars).strip()
    return collapsed[:max_length]


from pathlib import Path


def read_text(path: str) -> dict:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    return {"path": str(file_path), "text": text}


def write_text(path: str, text: str) -> dict:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text, encoding="utf-8")
    return {"path": str(file_path), "bytes": len(text.encode("utf-8"))}

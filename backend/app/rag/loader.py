from pathlib import Path

import pymupdf


def load_document(path: str) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(path)

    suffix = file_path.suffix.lower()

    if suffix == ".txt":
        return file_path.read_text(encoding="utf-8").strip()

    if suffix == ".pdf":
        document = pymupdf.open(path)

        try:
            pages = [page.get_text() for page in document]
            return "\n".join(pages).strip()
        finally:
            document.close()

    raise ValueError(f"Unsupported document type: {suffix}")
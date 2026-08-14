from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from app.rag.service import rag_service

router = APIRouter(prefix="/rag", tags=["RAG"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Filename required")

    extension = Path(file.filename).suffix.lower()

    if extension not in {".txt", ".pdf"}:
        raise HTTPException(
            400,
            "Only TXT and PDF files are supported",
        )

    destination = UPLOAD_DIR / file.filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return rag_service.ingest(str(destination))


@router.get("/query")
async def query_rag(q: str):
    return await rag_service.answer(q)
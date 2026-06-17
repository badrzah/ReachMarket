import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
import asyncpg

from backend.app.db.connection import get_db_tenant
from backend.app.services import knowledge_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

ALLOWED_TYPES = {"pitch_deck", "case_study", "brand_guide", "competitor_analysis", "other"}


@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    conn: asyncpg.Connection = Depends(get_db_tenant),
):
    """Upload a PDF or DOCX document for knowledge ingestion."""
    if doc_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid doc_type. Must be one of: {', '.join(ALLOWED_TYPES)}",
        )

    if not file.filename or not file.filename.lower().endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or DOCX.")

    content = await file.read()
    company_id = request.state.company_id

    try:
        result = await knowledge_service.ingest_document(
            conn, content, file.filename, company_id, doc_type
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Knowledge ingestion failed: %s", exc)
        raise HTTPException(status_code=422, detail=f"Extraction failed: {str(exc)}")


@router.get("/")
async def list_documents(
    request: Request,
    conn: asyncpg.Connection = Depends(get_db_tenant),
):
    """List all knowledge documents for the current company."""
    rows = await conn.fetch(
        """SELECT id, company_id, filename, doc_type, status, chunk_count, created_at
           FROM knowledge_documents
           ORDER BY created_at DESC"""
    )
    documents = []
    for row in rows:
        documents.append({
            "id": str(row["id"]),
            "filename": row["filename"],
            "doc_type": row["doc_type"],
            "status": row["status"],
            "chunk_count": row["chunk_count"],
            "created_at": row["created_at"].isoformat(),
        })
    return {"documents": documents, "total": len(documents)}


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    request: Request,
    conn: asyncpg.Connection = Depends(get_db_tenant),
):
    """Delete a knowledge document and its chunks."""
    result = await conn.execute(
        "DELETE FROM knowledge_documents WHERE id = $1",
        uuid.UUID(document_id),
    )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted"}

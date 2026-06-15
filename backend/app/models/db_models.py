from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Company:
    id: UUID
    name: str
    plan: str = "free"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class User:
    id: UUID
    company_id: UUID
    email: str
    hashed_password: str
    role: str = "member"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Session:
    id: UUID
    user_id: UUID
    company_id: UUID
    refresh_token: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class KnowledgeDocument:
    id: UUID
    company_id: UUID
    filename: str
    doc_type: str
    status: str = "pending"
    s3_key: Optional[str] = None
    chunk_count: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DocumentChunk:
    id: UUID
    document_id: UUID
    company_id: UUID
    namespace: str
    chunk_index: int
    content: str
    embedding: Optional[list[float]] = None
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Strategy:
    id: UUID
    company_id: UUID
    user_id: UUID
    session_id: UUID
    status: str = "generating"
    payload: Optional[dict] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentAssetDB:
    id: UUID
    company_id: UUID
    strategy_id: Optional[UUID]
    content_type: str
    title: str
    body: str
    validation_status: str = "pending"
    brand_alignment_score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CompanyMemory:
    id: UUID
    company_id: UUID
    key: str
    value: dict
    updated_at: datetime = field(default_factory=datetime.utcnow)

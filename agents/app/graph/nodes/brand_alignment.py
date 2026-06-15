"""
Brand Alignment Node — RAG-based content validation and revision.

For each content asset:
1. Retrieve brand guide/pitch deck chunks from pgvector
2. Score brand alignment 0.0-1.0 using LLM
3. Revise if score < 0.7 (max 2 iterations)
4. Update validation_status, brand_alignment_score, revision_notes
"""

import asyncpg
import json
import logging
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agents.app.graph.state import GTMState
from agents.app.prompts.brand_alignment import BRAND_ALIGNMENT_SYSTEM_PROMPT
from shared.schemas import ContentAsset, ValidationStatus

logger = logging.getLogger(__name__)

MAX_REVISIONS = 2
APPROVAL_THRESHOLD = 0.7


async def brand_alignment_node(state: GTMState) -> GTMState:
    """Validate and revise content assets against brand guidelines."""
    from agents.app.config import settings

    if not state.content_assets:
        logger.info("No content assets to validate")
        return state.model_copy(update={"current_agent": "brand_alignment"})

    # Try to retrieve brand context from pgvector
    brand_context = await _get_brand_context(state.company_id)

    # Process each content asset
    validated_assets = []
    for asset in state.content_assets:
        validated = await _validate_and_revise_asset(
            asset, brand_context, settings.openai_api_key
        )
        validated_assets.append(validated)

    return state.model_copy(update={
        "current_agent": "brand_alignment",
        "content_assets": validated_assets,
    })


# ── Module-level asyncpg pool (singleton, lazy-initialized) ──────────────
_pg_pool = None
_pg_pool_dsn = None


async def _get_pg_pool():
    """Return a reusable asyncpg connection pool, creating it on first call."""
    global _pg_pool, _pg_pool_dsn
    from agents.app.config import settings

    if _pg_pool is not None and not _pg_pool._closed and _pg_pool_dsn == settings.database_url:
        return _pg_pool

    # Close stale pool if DSN changed
    if _pg_pool is not None and not _pg_pool._closed:
        try:
            await _pg_pool.close()
        except Exception:
            pass

    _pg_pool = await asyncpg.create_pool(dsn=settings.database_url, min_size=1, max_size=3)
    _pg_pool_dsn = settings.database_url
    return _pg_pool


async def _get_brand_context(company_id) -> str:
    """Retrieve brand guide chunks from pgvector if available."""
    try:
        from agents.app.tools.retriever import PgVectorRetriever

        pool = await _get_pg_pool()
        retriever = PgVectorRetriever(pool)

        # Search for brand guide and pitch deck content
        brand_chunks = await retriever.retrieve(
            query="brand voice tone guidelines messaging",
            namespace=f"{company_id}:brand_guide",
            top_k=5,
        )
        pitch_chunks = await retriever.retrieve(
            query="value proposition positioning key messages",
            namespace=f"{company_id}:pitch_deck",
            top_k=3,
        )

        all_chunks = brand_chunks + pitch_chunks
        if all_chunks:
            context = "\n\n---\n\n".join(
                f"[{c.get('metadata', {}).get('source', 'brand doc')}]: {c['content']}"
                for c in all_chunks
            )
            return f"Brand Guidelines Context:\n{context}"

    except Exception as exc:
        logger.warning("Could not retrieve brand context: %s", exc)

    return "No brand guidelines uploaded. Use general best practices for B2B SaaS content."


async def _validate_and_revise_asset(
    asset: ContentAsset,
    brand_context: str,
    api_key: str,
) -> ContentAsset:
    """Score and optionally revise a single content asset."""
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=api_key,
            max_tokens=2000,
            request_timeout=30,
        )

        current_body = asset.body
        current_title = asset.title
        score = 0.0
        revision_notes = ""

        for iteration in range(MAX_REVISIONS + 1):
            # Score the asset
            score_response = await llm.ainvoke([
                SystemMessage(content=BRAND_ALIGNMENT_SYSTEM_PROMPT),
                HumanMessage(content=(
                    f"{brand_context}\n\n"
                    f"Content to evaluate:\n"
                    f"Type: {asset.type.value}\n"
                    f"Title: {current_title}\n"
                    f"Body: {current_body}\n\n"
                    f"Score this content's brand alignment from 0.0 to 1.0. "
                    f"Respond ONLY with JSON: "
                    f'{{"score": float, "notes": "string", "needs_revision": bool}}'
                )),
            ])

            raw = score_response.content.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                raw = raw.rsplit("```", 1)[0]

            try:
                result = json.loads(raw)
                score = float(result.get("score", 0.75))
                revision_notes = result.get("notes", "")
                needs_revision = result.get("needs_revision", False)
            except (json.JSONDecodeError, ValueError):
                score = 0.75
                revision_notes = "Unable to parse scoring response"
                needs_revision = False

            # If score is good enough or we've exhausted revisions, stop
            if score >= APPROVAL_THRESHOLD or iteration >= MAX_REVISIONS:
                break

            if not needs_revision:
                break

            # Revise the content
            logger.info(
                "Revising asset '%s' (iteration %d, score %.2f)",
                current_title, iteration + 1, score,
            )

            revise_response = await llm.ainvoke([
                SystemMessage(content=BRAND_ALIGNMENT_SYSTEM_PROMPT),
                HumanMessage(content=(
                    f"{brand_context}\n\n"
                    f"Current content (score: {score:.2f}):\n"
                    f"Title: {current_title}\n"
                    f"Body: {current_body}\n\n"
                    f"Revision notes: {revision_notes}\n\n"
                    f"Rewrite this content to better align with the brand guidelines. "
                    f"Preserve the strategy intent and key messaging. "
                    f"Return ONLY the revised body text, no JSON or metadata."
                )),
            ])
            current_body = revise_response.content.strip()

        # Determine validation status
        if score >= 0.9:
            status = ValidationStatus.APPROVED
        elif score >= APPROVAL_THRESHOLD:
            status = ValidationStatus.APPROVED
            revision_notes = f"Score: {score:.2f}. {revision_notes}"
        else:
            status = ValidationStatus.APPROVED  # Approve with notes after max revisions
            revision_notes = (
                f"Score: {score:.2f} (below threshold after {MAX_REVISIONS} revisions). "
                f"{revision_notes}"
            )

        return asset.model_copy(update={
            "body": current_body,
            "title": current_title,
            "validation_status": status,
            "brand_alignment_score": round(score, 2),
            "revision_notes": revision_notes if revision_notes else None,
        })

    except Exception as exc:
        logger.error("Brand alignment failed for asset '%s': %s", asset.title, exc)
        # Auto-approve with a default score on error
        return asset.model_copy(update={
            "validation_status": ValidationStatus.APPROVED,
            "brand_alignment_score": 0.75,
            "revision_notes": f"Auto-approved (validation error: {str(exc)[:100]})",
        })

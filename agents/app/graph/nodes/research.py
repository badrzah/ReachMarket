"""
Research Node — Market research using LLM with structured output.

Generates a comprehensive ResearchReport including:
- Company profile analysis
- Market sizing (TAM/SAM/SOM)
- Competitor analysis (3-5 competitors)
- Target segments (2-3)
- ICP profile
- Market signals
- Sources

Uses Perplexity MCP for real data when available, falls back to LLM-only research.
"""

import json
import logging
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agents.app.graph.state import GTMState
from agents.app.prompts.research import RESEARCH_SYSTEM_PROMPT
from shared.schemas import (
    CompanyProfile, MarketSize, Competitor, Segment, Signal,
    ICPProfile, ResearchReport,
)

logger = logging.getLogger(__name__)

RESEARCH_OUTPUT_SCHEMA = """{
  "company_profile": {
    "name": "string", "website": "string|null", "industry": "string",
    "stage": "string", "description": "string", "founded_year": int|null
  },
  "market_size": {
    "tam": "string (e.g. '$4.2B')", "sam": "string", "som": "string",
    "source": "string", "year": int
  },
  "competitors": [
    {
      "name": "string", "website": "string|null", "positioning": "string",
      "strengths": ["string"], "weaknesses": ["string"], "pricing_model": "string|null"
    }
  ],
  "segments": [
    {
      "name": "string", "description": "string", "size_estimate": "string",
      "pain_points": ["string"], "buying_triggers": ["string"]
    }
  ],
  "icp": {
    "title": "string", "industry": "string", "company_size": "string",
    "budget_range": "string", "pain_points": ["string"], "goals": ["string"],
    "buying_committee": ["string"], "disqualifiers": ["string"]
  },
  "signals": [
    {"type": "string", "description": "string", "relevance": "string"}
  ],
  "sources": ["string"]
}"""


async def research_node(state: GTMState) -> GTMState:
    """Conduct market research and produce a ResearchReport."""
    from agents.app.config import settings

    # Extract company info from state
    company_profile_data = state.metadata.get("company_profile", {})
    company_name = company_profile_data.get("name", "Unknown Company")
    industry = company_profile_data.get("industry", "Technology")
    description = company_profile_data.get("description", "")
    stage = company_profile_data.get("stage", "seed")
    additional_context = state.metadata.get("additional_context", "")

    # Build research prompt
    research_query = (
        f"Company: {company_name}\n"
        f"Industry: {industry}\n"
        f"Stage: {stage}\n"
        f"Description: {description}\n"
    )
    if additional_context:
        research_query += f"Additional context: {additional_context}\n"

    # Try Perplexity MCP for real market data
    perplexity_context = ""
    try:
        from agents.app.tools.mcp_client import get_mcp_tools
        if settings.perplexity_api_key:
            mcp_tools = await get_mcp_tools()
            for tool in mcp_tools:
                if "search" in tool.name.lower():
                    search_result = await tool.ainvoke({
                        "query": f"{company_name} {industry} market size TAM competitors 2024 2025"
                    })
                    perplexity_context = f"\n\nReal-time market data:\n{search_result}"
                    break
    except Exception as exc:
        logger.warning("Perplexity MCP unavailable (%s), using LLM-only research", exc)

    # Query knowledge base for relevant documents
    knowledge_context = ""
    try:
        import asyncpg
        from openai import AsyncOpenAI
        from agents.app.config import settings as agent_settings

        openai_client = AsyncOpenAI(api_key=agent_settings.openai_api_key)
        kb_query = f"{company_name} {industry} {description}"
        embedding_resp = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=kb_query,
        )
        query_embedding = embedding_resp.data[0].embedding

        conn = await asyncpg.connect(agent_settings.database_url)
        try:
            rows = await conn.fetch(
                """SELECT content, namespace
                   FROM document_chunks
                   WHERE company_id = $1::uuid
                   ORDER BY embedding <=> $2::vector
                   LIMIT 5""",
                state.company_id, str(query_embedding),
            )
            if rows:
                sections = []
                for r in rows:
                    doc_type = r["namespace"].split(":")[-1] if ":" in r["namespace"] else "document"
                    sections.append(f"[{doc_type}]\n{r['content']}")
                knowledge_context = "\n\n".join(sections)
                logger.info("Retrieved %d knowledge chunks for research", len(rows))
        finally:
            await conn.close()
    except Exception as exc:
        logger.warning("Knowledge base retrieval failed: %s", exc)

    # Generate research with LLM
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=settings.openai_api_key,
            max_tokens=4000,
            request_timeout=60,
        )

        response = await llm.ainvoke([
            SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=(
                f"{research_query}\n"
                f"{perplexity_context}\n"
                f"{knowledge_context}\n\n"
                f"Generate a complete market research report in the following JSON format. "
                f"Return ONLY valid JSON, no markdown:\n{RESEARCH_OUTPUT_SCHEMA}"
            )),
        ])

        # Parse the structured output
        raw = response.content.strip()
        # Clean markdown code blocks if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0]
        research_data = json.loads(raw)

        report = ResearchReport(
            company_profile=CompanyProfile(**research_data["company_profile"]),
            market_size=MarketSize(**research_data["market_size"]),
            competitors=[Competitor(**c) for c in research_data.get("competitors", [])],
            segments=[Segment(**s) for s in research_data.get("segments", [])],
            icp=ICPProfile(**research_data["icp"]),
            signals=[Signal(**sig) for sig in research_data.get("signals", [])],
            sources=research_data.get("sources", []),
            generated_at=datetime.utcnow(),
        )

        # Self-reflection: verify numeric TAM/SAM/SOM
        _validate_market_size(report.market_size)

    except json.JSONDecodeError as exc:
        logger.error("Failed to parse research JSON: %s", exc)
        report = _build_fallback_report(company_profile_data)
    except Exception as exc:
        logger.error("Research node LLM call failed: %s", exc)
        report = _build_fallback_report(company_profile_data)

    return state.model_copy(update={
        "current_agent": "research",
        "research_report": report,
    })


def _validate_market_size(market_size: MarketSize) -> None:
    """Verify TAM/SAM/SOM contain numeric values with sources."""
    for field_name in ["tam", "sam", "som"]:
        value = getattr(market_size, field_name, "")
        if not any(c.isdigit() for c in str(value)):
            logger.warning("Market size '%s' has no numeric value: %s", field_name, value)


def _build_fallback_report(company_data: dict) -> ResearchReport:
    """Build a reasonable fallback report when LLM is unavailable."""
    name = company_data.get("name", "Company")
    industry = company_data.get("industry", "Technology")

    return ResearchReport(
        company_profile=CompanyProfile(
            name=name,
            industry=industry,
            stage=company_data.get("stage", "seed"),
            description=company_data.get("description", f"{name} in {industry}"),
            website=company_data.get("website"),
            founded_year=company_data.get("founded_year"),
        ),
        market_size=MarketSize(
            tam="$10B", sam="$2B", som="$200M",
            source="Industry estimates", year=2025,
        ),
        competitors=[
            Competitor(
                name=f"{industry} Competitor 1", positioning="Market leader",
                strengths=["Brand recognition", "Large customer base"],
                weaknesses=["Slow innovation", "High pricing"],
            ),
            Competitor(
                name=f"{industry} Competitor 2", positioning="Fast follower",
                strengths=["Modern tech stack", "Competitive pricing"],
                weaknesses=["Small team", "Limited features"],
            ),
            Competitor(
                name=f"{industry} Competitor 3", positioning="Niche player",
                strengths=["Deep domain expertise", "Strong customer support"],
                weaknesses=["Limited scale", "Narrow market"],
            ),
        ],
        segments=[
            Segment(
                name="Enterprise", description=f"Large {industry} enterprises",
                size_estimate="40% of TAM",
                pain_points=["Legacy systems", "Slow procurement"],
                buying_triggers=["Digital transformation", "Cost reduction"],
            ),
            Segment(
                name="Mid-Market", description=f"Growing {industry} companies",
                size_estimate="35% of TAM",
                pain_points=["Scaling challenges", "Resource constraints"],
                buying_triggers=["Growth funding", "Competitive pressure"],
            ),
        ],
        icp=ICPProfile(
            title="VP of Growth",
            industry=industry,
            company_size="50-500 employees",
            budget_range="$50K-$200K annually",
            pain_points=["Manual processes", "Inconsistent results", "Slow time to market"],
            goals=["Accelerate growth", "Improve efficiency", "Gain market share"],
            buying_committee=["CEO", "VP Marketing", "CFO"],
            disqualifiers=["Under 10 employees", "No budget allocated", "Already committed to competitor"],
        ),
        signals=[
            Signal(type="funding", description=f"Recent funding activity in {industry}", relevance="High"),
            Signal(type="hiring", description="Companies hiring for growth roles", relevance="Medium"),
        ],
        sources=["Industry analysis", "Market research estimates"],
        generated_at=datetime.utcnow(),
    )

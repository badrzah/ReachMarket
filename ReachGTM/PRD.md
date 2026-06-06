# ReachGTM — Product Requirements Document

**Version:** 1.0  
**Date:** 2026-06-06  
**Status:** Draft  
**Author:** Architecture Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Goals & Success Metrics](#3-goals--success-metrics)
4. [Target Users](#4-target-users)
5. [Framework Decision](#5-framework-decision-langgraph-vs-openai-agents-sdk)
6. [System Architecture](#6-system-architecture)
7. [Agent Architecture & Responsibilities](#7-agent-architecture--responsibilities)
8. [Skills Integration](#8-skills-integration-pm-skills--coldiq-gtm-skills)
9. [RAG / Knowledge Base Design](#9-rag--knowledge-base-design)
10. [Memory Architecture](#10-memory-architecture)
11. [MCP Tools Integration](#11-mcp-tools-integration)
12. [API Design](#12-api-design-fastapi)
13. [Frontend Design](#13-frontend-design-nextjs)
14. [Data Models](#14-data-models-postgresql)
15. [Deployment Architecture](#15-deployment-architecture-aws)
16. [Multi-Tenancy Architecture](#16-multi-tenancy-architecture)
17. [MVP vs Full Product Scope](#17-mvp-vs-full-product-scope)
18. [Non-Functional Requirements](#18-non-functional-requirements)
19. [Security & Compliance](#19-security--compliance)
20. [Open Questions & Assumptions](#20-open-questions--assumptions)
21. [Glossary](#21-glossary)

---

## 1. Executive Summary

**ReachGTM** is an AI-powered, multi-agent Go-To-Market Strategy platform. It ingests a company's knowledge base (product docs, brand guidelines, past campaigns), performs autonomous market and competitor research, synthesizes a structured GTM strategy (positioning, ICP, messaging, channel mix), and generates execution-ready content assets (cold emails, LinkedIn posts, blog outlines, ad copy) — all grounded in the company's voice and positioning.

The system is built as a **supervised multi-agent pipeline** on **LangGraph**, backed by a **multi-page Next.js** web application and **FastAPI** backend, with **PostgreSQL + pgvector** for persistent memory and knowledge retrieval, and **MCP tools** for live market intelligence. The frontend is a full product with dedicated workspaces for Research, Strategy, Content Studio, and Knowledge Base — not a chatbot interface.

It converts two curated skill repositories into agent capabilities:
- **pm-skills** (68 PM skills) → Strategic planning layer (ICP, positioning, GTM strategy)
- **ColdIQ GTM Skills** (7 orchestrators, 52 sub-skills) → Execution layer (cold email, LinkedIn, signals)

---

## 2. Problem Statement

### Current State

Marketing and growth teams launching products or entering new markets face a fragmented, slow, and inconsistent GTM workflow:

| Pain | Detail |
|------|--------|
| **Fragmented research** | Teams manually scan competitors, review reports, and interview customers across disconnected tools |
| **Generic strategy** | Templates and AI tools produce generic output not grounded in company-specific context |
| **Slow turnaround** | Research → strategy → content pipeline takes days to weeks per campaign |
| **Messaging drift** | Inconsistent tone and positioning across channels and team members |
| **Limited scale** | Manual content production cannot keep up with multi-channel demand |
| **No unified pipeline** | Existing tools address isolated steps; nothing connects research → strategy → execution |

### What Existing Tools Don't Do

- **ChatGPT / Claude**: Generate content but have no company memory, no research capability, no strategic framework
- **Jasper / Copy.ai**: Template-based content; no market research or strategic layer
- **HubSpot AI**: CRM-integrated but not strategy-generating; no competitive intelligence
- **Notion AI**: Document assistance; not an agent pipeline
- **Apollo / Clay**: Outbound data; no strategy or content generation

### The Gap

No tool currently connects: **Company Knowledge → Market Research → GTM Strategy → Content Execution** in a single, iterative, company-specific pipeline.

---

## 3. Goals & Success Metrics

### Product Goals

1. Reduce GTM planning cycle from weeks to hours
2. Produce strategy outputs that are grounded in company context (not generic)
3. Enable consistent, on-brand multi-channel content at scale
4. Support iterative refinement through conversation

### OKRs (MVP — Q1 post-launch)

**Objective: Deliver an AI GTM agent that replaces the initial research + strategy phase**

| Key Result | Target | Measurement |
|------------|--------|-------------|
| Strategy generation time | < 30 minutes end-to-end | System timestamps |
| User satisfaction with output quality | > 4.0 / 5.0 | In-app rating |
| Content assets generated per session | ≥ 5 assets | DB count |
| Brand alignment score (human review) | > 80% "on-brand" | Manual audit |
| Agent task completion rate | > 90% without error | LangSmith traces |

### Success Metrics (6 months post-launch)

- 100 active companies onboarded
- Average 3+ sessions per company per week
- < 15% churn at 90 days
- > 50 NPS

---

## 4. Target Users

### Primary Personas

**Persona 1: The Growth-Stage Startup Founder**
- Role: CEO / Founder at a 5-30 person B2B SaaS company
- Problem: Has product-market fit signals but no dedicated marketing hire; needs a GTM plan fast
- Goal: Launch into a new vertical or market segment in < 4 weeks
- Frustration: Generic templates; no time to do deep research

**Persona 2: The Product Marketing Manager**
- Role: PMM at a 50-500 person company
- Problem: Supports 3-5 product launches per year; bottlenecked on research and content
- Goal: Produce consistent, high-quality strategy docs and content briefs faster
- Frustration: Messaging drift between teams; inability to scale content production

**Persona 3: The Agency Growth Strategist**
- Role: Consultant or agency lead managing 5-15 client accounts
- Problem: Needs to produce GTM strategy and execution assets for multiple clients with different contexts
- Goal: Reduce per-client research and strategy time by 60%
- Frustration: Switching contexts; maintaining client voice; manual content factories

### Secondary Users

- Content writers (consume content briefs from the agent)
- Sales reps (consume ICP profiles, battlecards, email sequences)
- Executives (consume strategy summaries and roadmaps)

---

## 5. Framework Decision: LangGraph vs OpenAI Agents SDK

### Decision: **LangGraph** (v1.0.8)

### Evaluation Matrix

| Criterion | LangGraph | OpenAI Agents SDK | Weight |
|-----------|-----------|-------------------|--------|
| MCP tool support | Native, production-ready | Native, less mature | High |
| Multi-agent orchestration | Graph-based, explicit, debuggable | Handoff-based, simpler | High |
| Parallel agent execution | First-class via `Send` | More complex to coordinate | High |
| State / memory management | Built-in PostgreSQL checkpointing | Manual configuration required | High |
| RAG integration | Mature (pgvector, Pinecone, Qdrant) | Custom tool composition | High |
| Streaming to frontend | 5 modes, SSE + WebSocket native | SSE/WebSocket, simpler | Medium |
| Python SDK stability | v1.0.8, production-stable, LTS policy | v0.2.8, pre-1.0, active breaking changes | High |
| FastAPI compatibility | Excellent, native async | Good | Medium |
| AWS deployment patterns | 3 proven patterns (ECS, EKS, BYOC) | Custom, fewer examples | Medium |
| GTM-specific examples | Yes (deepagents/examples) | No | Low |
| Observability | LangSmith (mature) | OpenAI dashboard (newer) | Medium |
| **Total fit score** | **9/10** | **6/10** | |

### Key Rationale

1. **Complex workflow requirement**: Research → Strategy → Content → Brand Validation is a multi-step, stateful workflow with conditional branching (e.g., if research quality is low, re-search before strategy). LangGraph's graph model handles this explicitly and debuggably.

2. **Parallel execution**: Research Agent and Content Agent can run concurrently while Strategy Agent synthesizes. LangGraph's `Send` primitive handles this natively; OpenAI SDK requires manual coordination.

3. **State persistence**: Between sessions (long-term company memory) and within sessions (multi-step workflow state) both require PostgreSQL checkpointing. LangGraph provides this out of the box via `langgraph-checkpoint-postgres`.

4. **MCP integration**: `langchain-mcp-adapters` converts any MCP tool to a LangGraph node tool with one line. This gives us Perplexity, Databar, CRM integrations automatically.

5. **Production maturity**: LangGraph v1.0 carries a no-breaking-changes-until-v2.0 LTS commitment. OpenAI Agents SDK had major breaking changes in April 2026 and is still pre-1.0.

### When to Reconsider

Revisit OpenAI Agents SDK if:
- The workflow becomes purely sequential with no parallel agents
- The team wants to exclusively use OpenAI-hosted tools and minimize infrastructure
- Kubernetes operational overhead becomes a bottleneck

---

## 6. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                          │
│                    Next.js 16 (App Router)                      │
│  Dashboard │ Research │ Strategy │ Content Studio │ Knowledge   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS / SSE / WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                          API LAYER                               │
│                  FastAPI 0.128 (Python 3.11)                     │
│     /chat  │  /strategy  │  /content  │  /knowledge  │  /auth   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Internal API
┌──────────────────────────▼──────────────────────────────────────┐
│                     AGENT ORCHESTRATION                          │
│                   LangGraph 1.0.8 (Python)                       │
│                                                                  │
│  ┌────────────┐    ┌──────────────┐    ┌───────────────────┐    │
│  │Orchestrator│───▶│ Research     │    │ Strategy Agent    │    │
│  │ (Supervisor│    │ Agent        │    │ (GTM Framework)   │    │
│  │  Agent)   │    │ (Market Intel│    │                   │    │
│  └────────────┘    └──────┬───────┘    └────────┬──────────┘    │
│        │                  │                     │               │
│        │           ┌──────▼───────┐    ┌────────▼──────────┐   │
│        └──────────▶│ Content      │    │ Brand Alignment   │   │
│                    │ Agent        │    │ Agent             │   │
│                    │ (Copywriting)│    │ (RAG Validation)  │   │
│                    └──────────────┘    └───────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
    ┌──────────────────────┼──────────────────────────┐
    │                      │                          │
┌───▼────────┐   ┌─────────▼──────────┐   ┌──────────▼───────┐
│ PostgreSQL │   │ pgvector (embedded  │   │ Redis            │
│ (RDS)      │   │ in PostgreSQL)      │   │ (ElastiCache)    │
│ Long-term  │   │ Vector Embeddings   │   │ Session Cache    │
│ memory,    │   │ Company Docs        │   │ Short-term       │
│ LangGraph  │   │ RAG Retrieval       │   │ memory           │
│ checkpoints│   └────────────────────┘   └──────────────────┘
└────────────┘
        │
┌───────▼─────────────────────────────────────────────────────────┐
│                        MCP TOOL LAYER                            │
│  Perplexity │ Databar │ Attio/HubSpot │ Smartlead │ Web Fetch   │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | Next.js | 16.1.6 | Multi-page web application (App Router) |
| Data Fetching | TanStack Query | 5.x | Server state, caching, SSE stream hooks |
| API | FastAPI | 0.128.0 | REST + SSE API gateway |
| Orchestration | LangGraph | 1.0.8 | Multi-agent graph orchestration |
| LLM (default) | OpenAI gpt-4o-mini / gpt-5.4-mini | latest | Agent reasoning; **must support tool calling and agent handoffs** — verify on OpenAI model page before pinning |
| Embeddings | OpenAI text-embedding-3-small | latest | Document and query embeddings (mini-tier cost efficiency) |
| Database | PostgreSQL | 16 | Persistent storage, LangGraph checkpoints |
| Vector DB | pgvector | 0.8.2 | Embedded in PostgreSQL, HNSW index |
| Cache | Redis | 7.x | Session state, API caching |
| MCP | langchain-mcp-adapters | 0.1+ | MCP tool integration |
| Container | Docker | 25+ | Service packaging |
| Orchestration | AWS ECS Fargate (MVP) / EKS (scale) | latest | Container deployment |
| Monitoring | LangSmith Cloud + CloudWatch | latest | Agent tracing, system metrics |

> **LLM Note:** Use the latest OpenAI mini model that supports **parallel tool calling** and **multi-step agent handoffs**. As of June 2026, confirm whether `gpt-5.4-mini` or `gpt-4o-mini` is the correct ID. Test with a tool-calling smoke test before committing. Fall back to `gpt-4.1` for any agent that fails tool invocations with the mini model.

---

## 7. Agent Architecture & Responsibilities

### Agent Graph Topology

```
User Input
    │
    ▼
┌──────────────────────────────────────────────────────┐
│               ORCHESTRATOR AGENT                      │
│  - Parses user intent                                 │
│  - Routes to appropriate sub-agents                   │
│  - Manages workflow state                             │
│  - Returns synthesized response                       │
└──────────┬───────────────────────────────────────────┘
           │
     ┌─────┴──────────────────────────────────┐
     │              │                         │
     ▼              ▼                         ▼
┌─────────┐  ┌─────────────┐        ┌────────────────┐
│RESEARCH │  │ STRATEGY    │        │BRAND ALIGNMENT │
│AGENT    │  │ AGENT       │        │AGENT           │
│         │  │             │        │                │
│ Tools:  │  │ Skills:     │        │ RAG over:      │
│Perplexity│  │ GTM Strategy│        │ Company docs   │
│Databar  │  │ ICP         │        │ Brand guidelines│
│Web Fetch│  │ Positioning │        │ Past campaigns │
│Attio MCP│  │ Value Prop  │        │                │
│         │  │ Battlecard  │        │ Validates ALL  │
│Output:  │  │ Growth Loops│        │ outputs before │
│Market   │  │             │        │ delivery       │
│report   │  │Output:      │        │                │
│Competitor│  │ GTM strategy│        │Output:         │
│analysis │  │ document    │        │ Aligned/revised│
│ICP data │  └──────┬──────┘        │ content        │
└────┬────┘         │               └───────┬────────┘
     │              │                       │
     └──────────────┤                       │
                    ▼                       │
           ┌────────────────┐               │
           │ CONTENT AGENT  │               │
           │                │               │
           │ Skills:        │               │
           │ Cold Email     │               │
           │ LinkedIn Posts │               │
           │ Blog Outline   │               │
           │ Ad Copy        │◄──────────────┘
           │ Email Sequence │  (Brand check
           │                │   applied here)
           │ Output:        │
           │ Content assets │
           └────────────────┘
```

### Agent Specifications

#### Orchestrator Agent

**Role:** Supervisor that routes requests, manages multi-step workflow, and synthesizes final outputs.

**Inputs:** User message, session state, company profile  
**Outputs:** Workflow plan + final synthesized response  
**LangGraph Pattern:** `StateGraph` with conditional edges  

**Decision Logic:**
- "What do you know about our market?" → Research Agent
- "Create a GTM strategy for our new product" → Research Agent → Strategy Agent → Brand Alignment Agent
- "Write cold email sequences" → (if ICP exists) → Content Agent → Brand Alignment Agent
- "Revise the messaging" → Strategy Agent → Brand Alignment Agent

**State managed:**
```python
class GTMState(TypedDict):
    messages: list[AnyMessage]
    company_profile: CompanyProfile
    session_objective: str
    research_report: ResearchReport | None
    gtm_strategy: GTMStrategy | None
    content_assets: list[ContentAsset]
    brand_validation_status: str
```

---

#### Research Agent

**Role:** Autonomous market intelligence gatherer. Performs web research, competitor analysis, trend identification, and prospect sourcing.

**Inputs:** Company profile, target market, research query  
**Outputs:** `ResearchReport` (structured JSON with market data, competitor analysis, ICP signals)

**MCP Tools Used:**
- `perplexity-mcp` — Real-time web search and research synthesis
- `databar-mcp` — B2B data enrichment, company/people lookup
- `fetch-mcp` — Raw web content fetching and HTML-to-markdown parsing
- `attio-mcp` or `hubspot-mcp` — Pull existing CRM data for context

**Skills Applied (from pm-skills):**
- `pm-market-research:competitor-analysis` — Structured competitive analysis framework
- `pm-market-research:market-sizing` — TAM/SAM/SOM calculation
- `pm-market-research:market-segments` — Segment identification
- `pm-market-research:user-personas` — Persona development from research

**Skills Applied (from ColdIQ):**
- `Signal Sourcer` — Buying signal identification (job changes, funding, hiring)
- `List Building: define-ICP` → `source-companies` → `find-contacts` → `qualify-accounts`

**Output Schema:**
```python
class ResearchReport(BaseModel):
    market_size: MarketSize          # TAM, SAM, SOM
    competitors: list[Competitor]    # Name, positioning, strengths, weaknesses
    target_segments: list[Segment]   # Segment name, size, characteristics
    buying_signals: list[Signal]     # Signal type, timing window, action
    icp_hypothesis: ICPProfile       # Firmographic + psychographic profile
    sources: list[str]               # URLs and data sources
```

---

#### Strategy Agent

**Role:** GTM strategy synthesizer. Takes research output and company context to produce a structured, actionable GTM strategy.

**Inputs:** `ResearchReport`, `CompanyProfile`, session objective  
**Outputs:** `GTMStrategy` document (structured JSON + human-readable markdown)

**Skills Applied (from pm-skills — core):**
- `pm-go-to-market:gtm-strategy` — 6-part GTM framework
- `pm-go-to-market:beachhead-segment` — First market selection
- `pm-go-to-market:ideal-customer-profile` — ICP refinement
- `pm-go-to-market:competitive-battlecard` — Competitive positioning
- `pm-go-to-market:growth-loops` — Sustainable growth flywheel
- `pm-go-to-market:gtm-motions` — Inbound vs outbound vs product-led
- `pm-marketing-growth:value-prop-statements` — Core value propositions
- `pm-marketing-growth:positioning-ideas` — Positioning options
- `pm-marketing-growth:north-star-metric` — Single metric that matters
- `pm-product-strategy:value-proposition` — JTBD-grounded value prop

**Output Schema:**
```python
class GTMStrategy(BaseModel):
    beachhead_segment: Segment           # Recommended first market
    icp: ICPProfile                      # Refined ICP
    positioning_statement: str           # One-sentence positioning
    value_propositions: list[ValueProp]  # 3-5 value props by persona
    channel_mix: list[Channel]           # Recommended channels + rationale
    gtm_motion: str                      # PLG / Sales-led / Marketing-led
    messaging_pillars: list[str]         # 3 core messaging themes
    battlecard: CompetitiveBattlecard    # vs. top 3 competitors
    north_star_metric: str               # Primary success metric
    growth_loops: list[GrowthLoop]       # Flywheel mechanics
    90_day_plan: list[Milestone]         # Phased execution plan
```

---

#### Content Agent

**Role:** Generates execution-ready content assets grounded in strategy and company voice.

**Inputs:** `GTMStrategy`, `CompanyProfile`, content type request, target persona  
**Outputs:** `list[ContentAsset]` (structured content with copy, metadata, variants)

**Skills Applied (from ColdIQ — core):**
- `Cold Email: ATL/BTL messaging` — Above/below-the-line cold email approach
- `Cold Email: first-touch` — Personalized cold email templates
- `Cold Email: subject-lines` — Subject line optimization
- `Cold Email: email-sequence (4-email)` — Full sequence design
- `LinkedIn Content: hooks` — 210-char hook formulas (AIDA, PAS, BAB)
- `LinkedIn Content: storytelling` — Long-form narrative frameworks
- `LinkedIn Content: CTAs` — Call-to-action design
- `Personalization: 6-bucket framework` — Context-aware personalization
- `Sales Triggers: 137+ triggers` — Signal-based message customization
- `Email Copywriting: 5 frameworks` — AIDA, PAS, BAB, Storytelling, Problem-Agitate-Solve

**Content Types Supported:**
| Type | Description | Output |
|------|-------------|--------|
| Cold Email | 1-4 email sequences, ATL/BTL | Full email copy + subject lines + A/B variants |
| LinkedIn Post | Organic content | Post copy + hook + CTA + hashtags |
| Blog Outline | SEO-informed blog post | H1, H2s, intro, key points, CTA |
| Ad Copy | LinkedIn Ads, Google Ads | Headline + body + CTA + audience targeting |
| Email Newsletter | Nurture sequences | Subject + body + CTA + segmentation rules |
| Sales Battlecard | One-pager for sales reps | Vs. competitor comparison + talk tracks |

**Content Asset Schema:**
```python
class ContentAsset(BaseModel):
    type: ContentType
    title: str
    copy: str                    # Primary copy
    variants: list[str]          # A/B test variants
    target_persona: str
    trigger_used: str | None     # ColdIQ signal trigger applied
    personalization_bucket: str  # ColdIQ 6-bucket classification
    expected_metrics: dict       # e.g., {"reply_rate": "25-30%"}
```

---

#### Brand Alignment Agent

**Role:** Quality gate that validates all strategy and content outputs against the company's knowledge base. Ensures voice, tone, positioning, and factual consistency.

**Inputs:** Any agent output + company knowledge base (via RAG)  
**Outputs:** Validation result (pass/flag/revise) + revised content if needed

**RAG Sources Queried:**
- Product descriptions and feature documentation
- Brand guidelines (voice, tone, prohibited phrases)
- Past campaigns and approved messaging
- Company positioning documents

**Validation Checks:**
1. Tone consistency (matches brand voice guidelines)
2. Factual accuracy (claims match product documentation)
3. Positioning alignment (consistent with approved positioning)
4. Prohibited content (flags competitor comparisons, unsubstantiated claims)
5. Legal/compliance signals (flags regulatory language)

**LangGraph Pattern:** Self-reflection loop — if validation fails, agent revises and re-validates (max 2 iterations before escalating to user).

---

## 8. Skills Integration: pm-skills + ColdIQ GTM Skills

### Integration Strategy

Both skill repositories encode **framework-driven, structured methodologies** as prompt templates. They are converted to **agent system prompts and tool definitions** in LangGraph.

### Conversion Pattern

```python
# Each skill becomes a structured prompt template
# Example: pm-go-to-market:gtm-strategy → GTM Strategy Tool

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

GTM_STRATEGY_PROMPT = """
You are a GTM strategy expert applying the following framework:

## GTM Strategy Framework (pm-skills)
1. Beachhead Segment Selection
2. ICP Definition
3. Channel Mix (inbound/outbound/PLG)
4. Messaging Pillars
5. GTM Motion Selection
6. 90-Day Execution Plan

## Company Context
{company_profile}

## Research Findings
{research_report}

Generate a structured GTM strategy following this framework exactly.
Return as JSON matching the GTMStrategy schema.
"""

@tool
def generate_gtm_strategy(company_profile: str, research_report: str) -> GTMStrategy:
    """Generate a complete GTM strategy using the pm-skills framework."""
    ...
```

### Skill-to-Agent Mapping

| Skill Source | Skill Name | Target Agent | Implementation |
|-------------|-----------|-------------|----------------|
| pm-go-to-market | gtm-strategy | Strategy | System prompt framework |
| pm-go-to-market | beachhead-segment | Strategy | Tool: `select_beachhead` |
| pm-go-to-market | ideal-customer-profile | Research + Strategy | Tool: `build_icp` |
| pm-go-to-market | competitive-battlecard | Research + Strategy | Tool: `generate_battlecard` |
| pm-go-to-market | growth-loops | Strategy | Tool: `design_growth_loops` |
| pm-go-to-market | gtm-motions | Strategy | Tool: `select_gtm_motion` |
| pm-market-research | competitor-analysis | Research | Tool: `analyze_competitors` |
| pm-market-research | user-personas | Research | Tool: `build_personas` |
| pm-market-research | market-sizing | Research | Tool: `calculate_market_size` |
| pm-market-research | market-segments | Research | Tool: `identify_segments` |
| pm-marketing-growth | value-prop-statements | Strategy | Tool: `generate_value_props` |
| pm-marketing-growth | positioning-ideas | Strategy | Tool: `generate_positioning` |
| pm-marketing-growth | north-star-metric | Strategy | Tool: `define_north_star` |
| ColdIQ | cold-email (7 sub-skills) | Content | System prompt + templates |
| ColdIQ | linkedin-content (7 sub-skills) | Content | System prompt + templates |
| ColdIQ | signal-sourcer (9 sub-skills) | Research | Tool: `identify_buying_signals` |
| ColdIQ | list-building (6 sub-skills) | Research | Tool: `build_target_list` |
| ColdIQ | personalization (4 sub-skills) | Content | Tool: `apply_personalization` |
| ColdIQ | email-copywriting (7 skills) | Content | System prompt + 34 templates |
| ColdIQ | sales-triggers (137+ triggers) | Content + Research | Vector-indexed lookup |

### Sales Triggers as Vector Index

The 137+ ColdIQ sales triggers are indexed in pgvector. When the Content Agent needs to personalize a message, it:
1. Receives the target account context (funding round, hiring activity, job change, etc.)
2. Queries vector index: `SELECT trigger, action FROM sales_triggers ORDER BY embedding <-> query_embedding LIMIT 3`
3. Applies top matching trigger framework to the content

---

## 9. RAG / Knowledge Base Design

### Knowledge Sources

| Source Type | Format | Update Frequency | Storage |
|-------------|--------|-----------------|---------|
| Product documentation | PDF, Markdown, DOCX | On upload | pgvector |
| Brand guidelines | PDF, Markdown | On upload | pgvector |
| Past campaigns | PDF, Markdown, JSON | On upload | pgvector |
| Competitor research | Auto-generated | Per session | pgvector (TTL: 7 days) |
| Market research | Auto-generated | Per session | pgvector (TTL: 30 days) |
| ColdIQ Sales Triggers | Pre-indexed Markdown | Static | pgvector |
| pm-skills Frameworks | Pre-indexed Markdown | Static | pgvector |

### Chunking Strategy

- **Company documents**: 512-token chunks, 50-token overlap, paragraph-aware splitting
- **Research outputs**: 256-token chunks (denser, more specific)
- **Framework content**: Full framework sections (1,000-2,000 tokens, no split)
- **Sales triggers**: One trigger per vector entry

### Embedding Model

- **OpenAI text-embedding-3-large** (3,072 dimensions, reduced to 1,536 for storage efficiency)
- Index type: **HNSW** with cosine distance (`vector_cosine_ops`)
- At 1M vectors, pgvector HNSW matches Pinecone query performance

### Retrieval Strategy

```python
class RAGRetriever:
    def retrieve(self, query: str, namespace: str, top_k: int = 5) -> list[Document]:
        # 1. Embed query
        # 2. Filter by namespace (company_id + doc_type)
        # 3. HNSW similarity search
        # 4. MMR (Maximal Marginal Relevance) reranking for diversity
        # 5. Return top_k documents
```

**Namespaces:**
- `{company_id}:product` — Product docs
- `{company_id}:brand` — Brand guidelines  
- `{company_id}:campaigns` — Past campaigns
- `{company_id}:research` — Cached research
- `global:skills:pm` — pm-skills frameworks
- `global:skills:coldiq` — ColdIQ frameworks and triggers

---

## 10. Memory Architecture

### Memory Hierarchy

```
┌─────────────────────────────────────────────┐
│           LONG-TERM MEMORY (PostgreSQL)      │
│  Company profile, brand guidelines,          │
│  past strategies, user preferences,          │
│  generated assets history                    │
│  LangGraph checkpoints (cross-session)       │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         SESSION MEMORY (Redis TTL: 24h)      │
│  Current campaign objective                  │
│  Active strategy draft                       │
│  Selected market/segment                     │
│  Intermediate agent outputs                  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          IN-GRAPH STATE (LangGraph)          │
│  Current message thread                      │
│  Active workflow step                        │
│  Retrieved documents (RAG context)           │
│  Agent handoff state                         │
└─────────────────────────────────────────────┘
```

### Long-Term Memory Schema

```python
class CompanyMemory(BaseModel):
    company_id: str
    profile: CompanyProfile            # Core company data
    brand_voice: BrandVoice            # Tone, style, prohibited terms
    past_strategies: list[GTMStrategy] # Historical strategies
    preferred_channels: list[str]      # User-confirmed channel preferences
    content_assets: list[ContentAsset] # All generated content
    user_preferences: dict             # UI and agent behavior preferences
    created_at: datetime
    updated_at: datetime
```

### LangGraph Checkpoint Strategy

- Checkpoint at every node completion (Research, Strategy, Content, Brand)
- Store in PostgreSQL via `langgraph-checkpoint-postgres`
- Enable session resumption: user can continue a strategy from where they left off
- TTL: 90 days for active companies, 365 days for paid tiers

---

## 11. MCP Tools Integration

### Selected MCP Servers

| MCP Server | Category | Agent Consumer | Key Capability |
|-----------|---------|---------------|----------------|
| **Perplexity MCP** | Web Research | Research Agent | Real-time market research, competitor intel |
| **Databar MCP** | Data Enrichment | Research Agent | 100+ provider aggregation, lead enrichment |
| **Fetch MCP** (official) | Web Content | Research Agent | HTML-to-markdown, competitor website scraping |
| **Attio MCP** | CRM | Research Agent | Pull existing customer data from CRM |
| **HubSpot MCP** | CRM (enterprise) | Research Agent | Mid-market CRM integration |
| **Smartlead MCP** | Email Outreach | Content Agent | Send campaign sequences from agent |
| **Git MCP** (official) | Version Control | Content Agent | Store and version content assets |

### Integration Pattern

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_client = MultiServerMCPClient({
    "perplexity": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-perplexity"],
        "env": {"PERPLEXITY_API_KEY": settings.PERPLEXITY_API_KEY},
        "transport": "stdio"
    },
    "databar": {
        "url": "https://api.databar.ai/mcp",
        "transport": "http",
        "headers": {"Authorization": f"Bearer {settings.DATABAR_API_KEY}"}
    },
    "attio": {
        "url": "https://mcp.attio.com",
        "transport": "streamable_http",
        "headers": {"Authorization": f"Bearer {settings.ATTIO_API_KEY}"}
    }
})

# All MCP tools auto-registered as LangGraph tools
tools = await mcp_client.get_tools()
```

### MCP Tool Authorization

- Per-company MCP credentials stored encrypted in PostgreSQL
- Tool access controlled by company subscription tier
- Rate limiting per tool per company enforced at FastAPI layer

---

## 12. API Design (FastAPI)

### Base URL: `/api/v1`

### Core Endpoints

#### Chat / Agent

```
POST /chat
  Body: { message: str, session_id: str, company_id: str }
  Response: SSE stream of agent events
  Auth: Bearer JWT

GET /sessions/{session_id}
  Response: Full session state including all agent outputs
  Auth: Bearer JWT

DELETE /sessions/{session_id}
  Response: 204 No Content
```

#### Strategy

```
GET /strategy/{company_id}/latest
  Response: Most recent GTMStrategy document

GET /strategy/{company_id}/history
  Response: List of past strategies (paginated)

POST /strategy/{company_id}/generate
  Body: { objective: str, segment: str | null }
  Response: SSE stream → final GTMStrategy JSON
```

#### Content

```
POST /content/generate
  Body: { type: ContentType, strategy_id: str, persona: str, trigger: str | null }
  Response: SSE stream → ContentAsset JSON

GET /content/{company_id}
  Response: Content library (paginated, filterable by type/date)

PUT /content/{asset_id}
  Body: { copy: str, approved: bool }
  Response: Updated ContentAsset
```

#### Knowledge Base

```
POST /knowledge/{company_id}/upload
  Body: multipart/form-data (PDF, DOCX, MD)
  Response: { document_id: str, chunks_indexed: int }

GET /knowledge/{company_id}
  Response: List of indexed documents

DELETE /knowledge/{company_id}/{document_id}
  Response: 204 No Content
```

#### Auth

```
POST /auth/login
  Body: { email: str, password: str }
  Response: { access_token: str, refresh_token: str }

POST /auth/register
  Body: { email: str, password: str, company_name: str }
  Response: { company_id: str, access_token: str }

POST /auth/refresh
  Body: { refresh_token: str }
  Response: { access_token: str }

POST /auth/invite
  Auth: Bearer JWT (role = owner | admin)
  Body: { email: str, role: str }
  Response: { invite_link: str }

POST /auth/accept-invite
  Body: { token: str, password: str }
  Response: { access_token: str }
```

### SSE Streaming Protocol

All long-running endpoints stream Server-Sent Events:

```
event: agent_start
data: {"agent": "research", "status": "running"}

event: agent_progress
data: {"agent": "research", "step": "competitor_analysis", "message": "Analyzing 3 competitors..."}

event: agent_output
data: {"agent": "research", "output": {...ResearchReport...}}

event: agent_complete
data: {"agent": "strategy", "output": {...GTMStrategy...}}

event: error
data: {"code": "RESEARCH_TIMEOUT", "message": "Research timed out after 30s"}

event: done
data: {"session_id": "...", "total_time_ms": 45000}
```

---

## 13. Frontend Design (Next.js)

### Tech Stack

- Next.js 16.1.6 (App Router, RSC)
- React 19.2
- TypeScript 5.3
- Tailwind CSS + shadcn/ui
- TanStack Query 5.x (server state, cache, SSE)
- Zustand (client UI state)
- Native `EventSource` API (SSE consumption for agent streams)

### Application Structure

ReachGTM is a **full-featured multi-page web application**, not a chatbot. The agent pipeline (Research → Strategy → Content → Brand) is triggered from dedicated workspaces and surfaces results in structured, interactive views.

```
/                           Redirect → /dashboard (or landing if unauthenticated)
/auth/login
/auth/register              Company onboarding wizard (profile + first doc upload)

/dashboard                  Home: KPI cards, recent activity, quick actions
/research                   Research workspace: trigger + view market reports
/research/{id}              Research report detail: market, competitors, ICP, signals
/strategy                   Strategy list: all GTM strategies, versioned
/strategy/new               Strategy builder: select research → configure → generate (SSE)
/strategy/{id}              Strategy detail: ICP, positioning, battlecard, 90-day plan
/content                    Content library: filter by type, persona, approval status
/content/create             Content studio: select strategy + type → generate (SSE)
/content/{id}               Asset editor: copy, variants, approve/reject
/knowledge                  Knowledge base: upload docs, view indexed files, status
/agent                      Agent console: run full pipeline, live graph progress view
/settings                   Company profile, API keys, team (Phase 2), subscription
```

### Page Designs

#### `/dashboard` — Home Dashboard

```
┌──────────────────────────────────────────────────────────────┐
│ ReachGTM    [Research] [Strategy] [Content] [Knowledge]  [⚙] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │Strategies│  │ Research │  │ Content  │  │ Knowledge  │  │
│  │    3     │  │ Reports  │  │ Assets   │  │  12 docs   │  │
│  │ created  │  │    5     │  │   24     │  │  indexed   │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│                                                              │
│  QUICK ACTIONS                                               │
│  [+ New Research]  [+ Build Strategy]  [+ Create Content]   │
│                                                              │
│  RECENT ACTIVITY                                             │
│  ● Strategy "Q3 SaaS Launch" generated — 2h ago             │
│  ● 8 cold emails created for "VP Eng" persona — 4h ago       │
│  ● Research report: "AI DevTools market" — yesterday         │
│                                                              │
│  ACTIVE STRATEGY                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Q3 SaaS Launch GTM v2                                  │ │
│  │ Beachhead: Series A SaaS, 50-200 emp                   │ │
│  │ Motion: Product-led + outbound SDR                     │ │
│  │ North Star: Activated teams in 14 days   [View →]      │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

#### `/research` — Research Workspace

```
┌──────────────────────────────────────────────────────────────┐
│ Research                                    [+ New Research]  │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────┐  ┌──────────────────────┐  │
│  │ NEW RESEARCH                 │  │ RECENT REPORTS       │  │
│  │ Market / Competitors         │  │                      │  │
│  │ ┌──────────────────────────┐ │  │ AI DevTools market   │  │
│  │ │ Target market or query   │ │  │ 2 days ago  [View]   │  │
│  │ └──────────────────────────┘ │  │                      │  │
│  │ [Run Research Agent ▶]       │  │ B2B SaaS competitors │  │
│  │                              │  │ 5 days ago  [View]   │  │
│  │ AGENT PROGRESS (live SSE)    │  │                      │  │
│  │ ✓ Perplexity search          │  │ Fintech segments     │  │
│  │ ✓ Competitor analysis        │  │ 1 week ago  [View]   │  │
│  │ ● ICP hypothesis...          │  │                      │  │
│  └──────────────────────────────┘  └──────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

#### `/research/{id}` — Research Report Detail

Structured view with tabs:
- **Market Overview**: TAM/SAM/SOM cards, growth rate, key trends
- **Competitors**: Table (name, positioning, strengths, weaknesses, ICP overlap)
- **Segments**: Cards per target segment with size + characteristics
- **ICP Hypothesis**: Firmographic + psychographic profile card
- **Buying Signals**: Table of signals (type, trigger, timing window, recommended action)
- Actions: `[Export PDF]` `[Use to Build Strategy →]`

#### `/strategy/new` — Strategy Builder

```
┌──────────────────────────────────────────────────────────────┐
│ Build GTM Strategy                                           │
├──────────────────────────────────────────────────────────────┤
│  Step 1: Select Research Base                                │
│  ○ AI DevTools market (2 days ago)                           │
│  ○ B2B SaaS competitors (5 days ago)                         │
│  ○ Skip — generate from company profile only                 │
│                                                              │
│  Step 2: Configure                                           │
│  Objective: [______________________________]                 │
│  Target segment (optional): [_______________]                │
│                                                              │
│  [Generate Strategy ▶]                                       │
│                                                              │
│  AGENT PROGRESS                                              │
│  ✓ Research Agent — loading context                          │
│  ● Strategy Agent — synthesizing ICP...                      │
│  ○ Brand Alignment Agent                                     │
└──────────────────────────────────────────────────────────────┘
```

#### `/strategy/{id}` — Strategy Detail

Full structured view with sections:
- **Header**: Title, version, created date, GTM motion badge, `[Regenerate]` `[Export]`
- **ICP Card**: Firmographic profile, decision-maker titles, buying triggers
- **Positioning**: Statement + 3 messaging pillars
- **Value Propositions**: Cards per persona (problem → solution → outcome)
- **Channel Mix**: Recommended channels with rationale + priority rank
- **Competitive Battlecard**: vs. top 3 competitors (us vs. them table + talk tracks)
- **Growth Loops**: Flywheel diagram (text-based)
- **90-Day Plan**: Timeline view with milestones per phase
- **Actions**: `[Create Content from This Strategy]` `[Compare to v1]`

#### `/content` — Content Library

```
┌──────────────────────────────────────────────────────────────┐
│ Content Library                           [+ Create Content]  │
├──────────────────────────────────────────────────────────────┤
│ Filter: [All Types ▼]  [All Personas ▼]  [All Status ▼]      │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐  │
│  │ Cold Email      │ │ Cold Email      │ │ LinkedIn Post │  │
│  │ 4-email seq     │ │ First touch     │ │ Hook + story  │  │
│  │ VP Eng persona  │ │ CTO persona     │ │ Series A ICP  │  │
│  │ ✓ Approved      │ │ ⏳ Pending       │ │ ✓ Approved    │  │
│  │ [Edit] [Copy]   │ │ [Review]        │ │ [Edit] [Copy] │  │
│  └─────────────────┘ └─────────────────┘ └───────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

#### `/content/create` — Content Studio

```
┌──────────────────────────────────────────────────────────────┐
│ Content Studio                                               │
├──────────────────────────────────────────────────────────────┤
│  Strategy: [Q3 SaaS Launch GTM v2 ▼]                        │
│  Content Type: [Cold Email Sequence ▼]                       │
│  Target Persona: [VP Engineering ▼]                          │
│  Sales Trigger (optional): [Recent funding round ▼]          │
│                                                              │
│  [Generate ▶]                                                │
│                                                              │
│  ════════════════════════════════════════════════════════    │
│  GENERATED OUTPUT (live stream)                              │
│                                                              │
│  Email 1 — First Touch                                       │
│  Subject: [streaming...]                                     │
│  Body: [streaming...]                                        │
│                                                              │
│  [A/B Variant] [Approve] [Reject] [Save to Library]         │
└──────────────────────────────────────────────────────────────┘
```

#### `/knowledge` — Knowledge Base

```
┌──────────────────────────────────────────────────────────────┐
│ Knowledge Base                                               │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Drop files here or click to upload                   │  │
│  │  Supported: PDF, DOCX, MD (max 50MB)                  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  INDEXED DOCUMENTS                                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ brand-guidelines.pdf     │ brand    │ 47 chunks  │ ✓ │   │
│  │ product-overview.docx    │ product  │ 83 chunks  │ ✓ │   │
│  │ past-campaign-q2.md      │ campaign │ processing │ ⏳ │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

#### `/agent` — Agent Console

Full-pipeline trigger with real-time multi-agent graph view:
- Select objective + research base
- Trigger full Research → Strategy → Content → Brand pipeline
- Live status per agent node (pending / running / complete / error)
- Expandable output per agent as it completes
- Session saved automatically; resumes on refresh via LangGraph checkpoint

### SSE Integration Pattern (no Vercel AI SDK)

```typescript
// hooks/useAgentStream.ts
export function useAgentStream(sessionId: string) {
  const [events, setEvents] = useState<AgentEvent[]>([])

  useEffect(() => {
    const source = new EventSource(`/api/v1/agent/stream/${sessionId}`)
    source.addEventListener('agent_progress', (e) => {
      setEvents(prev => [...prev, JSON.parse(e.data)])
    })
    source.addEventListener('done', () => source.close())
    source.onerror = () => source.close()
    return () => source.close()
  }, [sessionId])

  return events
}
```

### Key UX Patterns

1. **Structured workspaces**: Each pipeline stage (Research, Strategy, Content) has its own dedicated page — not collapsed into chat
2. **Live agent progress**: SSE-streamed step-by-step status on any generation page, no polling
3. **Approval workflow**: All generated content requires explicit approve/reject before export
4. **Version history**: Strategies are versioned; users can compare v1 vs v2
5. **Cross-page continuity**: Research → "Use for Strategy" → "Create Content from Strategy" flow links pages together
6. **Knowledge base indicator**: Global header shows indexed doc count + health status

---

## 14. Data Models (PostgreSQL)

### Core Tables

```sql
-- Companies
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    size_range VARCHAR(50),         -- "1-10", "11-50", "51-200", etc.
    subscription_tier VARCHAR(50),  -- "free", "starter", "pro", "enterprise"
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',  -- "owner", "admin", "member"
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sessions (LangGraph conversation threads)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    objective TEXT,
    status VARCHAR(50) DEFAULT 'active',  -- "active", "completed", "archived"
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Strategies
CREATE TABLE strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id),
    version INTEGER DEFAULT 1,
    beachhead_segment JSONB,
    icp JSONB,
    positioning_statement TEXT,
    value_propositions JSONB,
    channel_mix JSONB,
    gtm_motion VARCHAR(100),
    messaging_pillars JSONB,
    battlecard JSONB,
    north_star_metric TEXT,
    growth_loops JSONB,
    ninety_day_plan JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Content Assets
CREATE TABLE content_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id),
    strategy_id UUID REFERENCES strategies(id),
    type VARCHAR(100),               -- "cold_email", "linkedin_post", "blog_outline", etc.
    title VARCHAR(255),
    copy TEXT NOT NULL,
    variants JSONB,                  -- A/B variants
    target_persona VARCHAR(255),
    trigger_used VARCHAR(255),
    personalization_bucket VARCHAR(100),
    expected_metrics JSONB,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Knowledge Documents
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    doc_type VARCHAR(100),           -- "product", "brand", "campaign", "research"
    chunks_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'processing',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector Embeddings (pgvector)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id),
    namespace VARCHAR(255),          -- "{company_id}:{doc_type}"
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast similarity search
CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Company Memory (long-term)
CREATE TABLE company_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID UNIQUE REFERENCES companies(id) ON DELETE CASCADE,
    brand_voice JSONB,
    preferred_channels JSONB,
    user_preferences JSONB,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 15. Deployment Architecture (AWS)

### MVP Deployment (ECS Fargate)

```
┌────────────────────────────────────────────────────────────┐
│                         AWS VPC                             │
│                                                            │
│  ┌─────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │Route 53 │───▶│ CloudFront   │───▶│   ALB (HTTPS)    │  │
│  └─────────┘    │ (CDN)        │    └────────┬─────────┘  │
│                 └──────────────┘             │            │
│                                    ┌─────────┴──────────┐ │
│                                    │   ECS Fargate       │ │
│                                    │                     │ │
│                                    │  ┌───────────────┐  │ │
│                                    │  │ Next.js       │  │ │
│                                    │  │ (port 3000)   │  │ │
│                                    │  └───────────────┘  │ │
│                                    │  ┌───────────────┐  │ │
│                                    │  │ FastAPI       │  │ │
│                                    │  │ (port 8000)   │  │ │
│                                    │  └───────────────┘  │ │
│                                    │  ┌───────────────┐  │ │
│                                    │  │ LangGraph     │  │ │
│                                    │  │ Service       │  │ │
│                                    │  │ (port 8001)   │  │ │
│                                    │  └───────────────┘  │ │
│                                    └─────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Data Layer (Private Subnet)             │  │
│  │                                                      │  │
│  │  ┌─────────────────┐    ┌─────────────────────────┐  │  │
│  │  │ RDS PostgreSQL  │    │ ElastiCache Redis        │  │  │
│  │  │ 16 + pgvector   │    │ (Session cache)         │  │  │
│  │  │ (db.t3.medium)  │    │ (cache.t3.micro)        │  │  │
│  │  └─────────────────┘    └─────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ S3           │  │ Secrets      │  │ CloudWatch      │  │
│  │ (doc upload) │  │ Manager      │  │ (logs + alerts) │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Scale-Up Path (EKS — when needed)

Trigger for EKS migration:
- > 50 concurrent users, or
- Need for independent auto-scaling per agent type, or
- Service mesh requirement for agent-to-agent security

EKS addition:
- Istio service mesh for agent communication security
- HPA (Horizontal Pod Autoscaler) per agent service
- ArgoCD for GitOps deployments

### Docker Compose (Local Development)

```yaml
version: "3.9"
services:
  nextjs:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000

  fastapi:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/reachgtm
      REDIS_URL: redis://redis:6379
      LANGGRAPH_URL: http://langgraph:8001
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on: [db, redis, langgraph]

  langgraph:
    build: ./agents
    ports: ["8001:8001"]
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/reachgtm
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      LANGSMITH_API_KEY: ${LANGSMITH_API_KEY}
    depends_on: [db, redis]

  db:
    image: pgvector/pgvector:pg16
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: reachgtm
      POSTGRES_PASSWORD: password
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

---

## 16. Multi-Tenancy Architecture

### Tenancy Model

One company = one tenant. All users belong to exactly one company. Infrastructure is shared; data is isolated.

| Concept | Implementation |
|---------|---------------|
| Tenant | `companies` table row |
| User | `users` table row with `company_id` FK |
| Isolation | Row-Level Security (RLS) in PostgreSQL |
| Scope | Every table carries `company_id`; every query filters by it |

**This is shared-schema multi-tenancy — NOT per-tenant databases.** A single PostgreSQL instance serves all tenants. Isolation is enforced at the row level by RLS policies, not by schema separation.

### Isolation Strategy

```sql
-- RLS enabled on every tenant-scoped table
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_memory ENABLE ROW LEVEL SECURITY;

-- Policy pattern (same on all tables)
CREATE POLICY tenant_isolation ON sessions
    USING (company_id = current_setting('app.current_company_id')::uuid);
```

FastAPI sets `app.current_company_id` from the authenticated JWT before every query. No query can touch another tenant's rows — the DB enforces it, not the application layer.

**Additional isolation layers:**

| Layer | Mechanism |
|-------|-----------|
| Vector store | Namespace prefix `{company_id}:{doc_type}` on every `document_chunks` row |
| Redis | Key prefix `company:{company_id}:` on all session keys |
| MCP credentials | Per-company, encrypted at rest (AES-256), never shared across tenants |
| LangGraph checkpoints | Scoped to `session_id`; sessions always reference `company_id` |
| Rate limiting | Enforced per `company_id` at FastAPI middleware before any agent is invoked |

### Tenant Creation Flow

Registration creates the company and its first user in a single transaction:

```
POST /auth/register
  Body: { email, password, company_name }

  1. INSERT INTO companies (name) → company_id
  2. INSERT INTO users (company_id, email, password_hash, role='owner')
  3. INSERT INTO company_memory (company_id) → blank profile
  4. Return: { company_id, access_token }
```

The registering user is always assigned `role = 'owner'`. Only one owner per company.

### User Invite Flow

Owners and admins can add users to their existing company:

```
POST /auth/invite
  Auth: Bearer JWT (role = owner | admin)
  Body: { email, role }   -- role = "admin" | "member"

  1. Generate signed invite token (JWT, TTL 48h, carries company_id + role)
  2. Send invite email with link: /auth/accept-invite?token=<token>

GET /auth/accept-invite?token=<token>
  1. Validate token (not expired, signature valid)
  2. Show registration form pre-filled with email

POST /auth/accept-invite
  Body: { token, password }
  1. Decode token → company_id, role, email
  2. INSERT INTO users (company_id, email, password_hash, role)
  3. Return: { access_token }  -- user is now in the tenant
```

The invited user joins the existing company — no new company is created. The `company_id` comes from the invite token, not from user input.

### RLS Enforcement in FastAPI

```python
# middleware/tenant.py
async def set_tenant_context(request: Request, call_next):
    token = extract_jwt(request)
    company_id = token.get("company_id")
    async with db.transaction():
        await db.execute(
            f"SET LOCAL app.current_company_id = '{company_id}'"
        )
        response = await call_next(request)
    return response
```

This runs before every request. No handler needs to manually filter by `company_id` — the DB rejects cross-tenant access automatically.

---

## 17. MVP vs Full Product Scope

### MVP (Phase 1 — 8-12 weeks)

**Goal:** Prove that the Research → Strategy → Content pipeline works end-to-end for a single user with a single company profile.

**In Scope:**
- [ ] Company onboarding: profile creation + document upload (PDF, DOCX, MD)
- [ ] Knowledge base: RAG over company documents (pgvector)
- [ ] Research Agent: Perplexity MCP for market research
- [ ] Strategy Agent: GTM strategy generation (ICP, positioning, channels, value props)
- [ ] Content Agent: Cold email sequences + LinkedIn posts
- [ ] Brand Alignment Agent: Validation pass on all outputs
- [ ] Chat interface: Streaming responses, artifact cards
- [ ] Content library: Save and manage generated assets
- [ ] Single-user, single-company (no team collaboration)
- [ ] LangSmith tracing for debugging

**Out of Scope (MVP):**
- Team collaboration and roles
- CRM integrations (HubSpot, Attio, Salesforce)
- Smartlead campaign sending
- Blog post full generation (outline only)
- Ad copy generation
- Analytics and performance tracking
- Billing and subscription management
- Multi-company for agencies

### Phase 2 (weeks 4-8 post-MVP)

- Team collaboration (multi-user per company)
- Blog post full generation and ad copy (LinkedIn + Google)
- Built-in lead/contact management (standalone — no external CRM dependency)
- Campaign performance tracking and analytics dashboard
- Agency multi-company workspace
- Databar MCP for prospect enrichment
- Subscription billing (Stripe)
- Export to PDF/DOCX

### Phase 3 (future — on demand)

- External CRM integrations (HubSpot, Attio, Salesforce) — offered as optional connectors, not core
- Smartlead MCP: agent-triggered email send
- Signal Sourcer: real-time buying signal monitoring
- Campaign automation: content → internal CRM → send pipeline
- Full EKS migration for scale

> **CRM Strategy Decision:** ReachGTM will be a **standalone service** with its own contact and lead management. External CRM integrations (HubSpot, Attio, Salesforce) are optional Phase 3 connectors for teams that already have a CRM. This keeps the MVP and Phase 2 lean and avoids coupling to third-party data models.

### MVP Timeline (2-3 weeks, team of 4 AI-assisted engineers)

| Week | Focus | Deliverable |
|------|-------|-------------|
| Week 1 | Backend: FastAPI + LangGraph + Research + Strategy Agents + PostgreSQL + pgvector | Working Research → Strategy pipeline (API only) |
| Week 2 | Frontend: Next.js chat UI + streaming + Content Agent + Brand Alignment Agent | End-to-end working agent in chat UI |
| Week 3 | Polish + Knowledge Base upload + LangSmith tracing + Docker Compose + deploy to AWS ECS | Deployed, shareable MVP |

**Team task split suggestion:**
- **Yousef**: Architecture lead, LangGraph agent graph, orchestration
- **Nawaf**: FastAPI backend, database models, API endpoints
- **Bader**: Next.js frontend, streaming chat UI, content library
- **Abdulrahem**: RAG pipeline, pgvector setup, MCP tool integrations

---

## 18. Non-Functional Requirements

| Category | Requirement | Target |
|----------|-------------|--------|
| **Latency** | First token to frontend | < 3 seconds |
| **Latency** | Full strategy generation | < 60 seconds |
| **Latency** | Content asset generation | < 15 seconds |
| **Throughput** | Concurrent sessions (MVP) | 20 simultaneous |
| **Throughput** | Concurrent sessions (scale) | 500+ |
| **Availability** | Uptime SLA | 99.5% (MVP), 99.9% (enterprise) |
| **Data retention** | Session data | 90 days (free), 365 days (paid) |
| **Search latency** | RAG retrieval (top-5) | < 100ms at 1M vectors |
| **API response** | Non-streaming endpoints | < 500ms p95 |
| **File upload** | Max document size | 50 MB per file |
| **Streaming** | SSE connection timeout | 120 seconds |

---

## 19. Security & Compliance

### Data Isolation

- All company data namespaced by `company_id` in every table and vector namespace
- Row-level security (RLS) enforced in PostgreSQL
- Redis keys prefixed with `company:{company_id}:`

### Authentication & Authorization

- JWT-based auth (access token: 15min TTL, refresh token: 30 days)
- Role-based access control: `owner`, `admin`, `member`
- API keys for programmatic access (future)

### Secrets Management

- All API keys (OpenAI, Perplexity, Databar, etc.) stored in AWS Secrets Manager
- Company-provided MCP credentials encrypted at rest (AES-256)
- Never logged or exposed in LangSmith traces (redacted)

### Data Privacy

- Company documents processed in-memory; only embeddings + chunks stored
- No cross-company data leakage (namespace isolation in vector DB)
- GDPR-compliant: data deletion cascade on company deletion
- SOC 2 Type II roadmap for enterprise tier

### LLM Data Handling

- OpenAI API calls use `user` parameter for audit trail
- Option to use AWS Bedrock (Anthropic Claude) for in-VPC inference (no data leaving AWS)
- No training data opt-in by default

---

## 20. Open Questions & Assumptions

### Assumptions Made

| Assumption | Rationale |
|-----------|-----------|
| OpenAI GPT-4.1 as default LLM | User was evaluating OpenAI Agents SDK; configurable in settings |
| PostgreSQL + pgvector as single vector store | Reduces operational complexity vs. separate vector DB; scales to 1M+ vectors |
| ECS Fargate for MVP | Lower ops overhead than EKS; EKS path clear for scale |
| Shared-schema multi-tenancy | Each company's data isolated by RLS on shared infrastructure |
| English-first | International language support deferred to Phase 3 |

### Decisions Confirmed

| Decision | Choice | Notes |
|----------|--------|-------|
| LLM provider | OpenAI mini model (gpt-5.4-mini or latest mini) | Confirm tool-calling support before pinning version |
| Observability | LangSmith Cloud | MVP — self-host if data residency required later |
| CRM | Standalone — no external CRM | Optional connectors in Phase 3 |
| Timeline | 2-3 weeks MVP | Team of 4 AI-assisted engineers |
| Multi-tenancy | Shared schema + RLS | Not per-tenant databases |

### Remaining Open Question

| Question | Impact | Recommended Decision |
|----------|--------|---------------------|
| Billing model: usage-based or seat-based? | Revenue model | Recommend: seat-based with usage caps (simpler at MVP) |

---

## 21. Glossary

| Term | Definition |
|------|-----------|
| **GTM** | Go-To-Market — the strategy and execution plan for launching a product into a market |
| **ICP** | Ideal Customer Profile — firmographic + psychographic definition of the best-fit buyer |
| **Beachhead Segment** | The initial, most-winnable market segment to focus GTM resources on |
| **RAG** | Retrieval-Augmented Generation — enhancing LLM outputs with retrieved documents |
| **MCP** | Model Context Protocol — standard for connecting AI agents to external tools |
| **LangGraph** | LangChain's graph-based multi-agent orchestration framework |
| **pgvector** | PostgreSQL extension for storing and querying vector embeddings |
| **SSE** | Server-Sent Events — HTTP streaming protocol for real-time frontend updates |
| **LangSmith** | LangChain's observability platform for tracing agent reasoning |
| **ATL/BTL** | Above/Below The Line — ColdIQ's framework for different cold email messaging angles |
| **HNSW** | Hierarchical Navigable Small World — the indexing algorithm used for fast vector search |
| **GTM Motion** | The go-to-market approach: Product-Led Growth, Sales-Led, Marketing-Led, or hybrid |
| **Checkpoint** | LangGraph's mechanism for persisting agent state to PostgreSQL between steps |
| **RLS** | Row-Level Security — PostgreSQL feature that enforces data isolation at the row level |
| **Tenant** | A company and all its users, sharing infrastructure but with isolated data |

---

*This PRD was researched and authored using pm-skills and ColdIQ GTM Skills repositories, LangGraph documentation, and current (June 2026) best practices for multi-agent AI systems.*

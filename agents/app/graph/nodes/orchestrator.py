"""
Orchestrator Node — Intelligent routing based on session state.

Analyzes the current GTMState and routes to the appropriate sub-agent:
- No research_report → route to Research
- Has research but no strategy → route to Strategy
- Has strategy → route to Content (and then Brand Alignment)
"""

import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agents.app.graph.state import GTMState
from agents.app.prompts.orchestrator import ORCHESTRATOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


async def orchestrator_node(state: GTMState) -> GTMState:
    """Analyze state and determine routing. The actual routing edge is in graph.py."""
    from agents.app.config import settings

    # Determine what we have and what we need
    has_research = state.research_report is not None
    has_strategy = state.gtm_strategy is not None
    has_content = len(state.content_assets) > 0

    # Build routing reasoning
    if not has_research:
        routing = "research"
        reason = "No research report exists. Starting with market research."
    elif not has_strategy:
        routing = "strategy"
        reason = "Research complete. Proceeding to GTM strategy generation."
    elif not has_content:
        routing = "content"
        reason = "Strategy exists. Generating content assets."
    else:
        routing = "content"
        reason = "Strategy and research exist. Generating additional content."

    # Use LLM to add context-aware reasoning if available
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=settings.openai_api_key,
            max_tokens=200,
            request_timeout=15,
        )

        # Handle both dict-format messages and LangChain message objects.
        # The LangGraph `add_messages` reducer may convert raw dicts into
        # LangChain message instances (HumanMessage, AIMessage, etc.).
        user_messages = []
        for m in state.messages:
            if isinstance(m, dict) and m.get("role") == "user":
                user_messages.append(m.get("content", ""))
            elif hasattr(m, "type") and m.type == "human":
                # LangChain HumanMessage
                user_messages.append(m.content)
            elif hasattr(m, "__class__") and m.__class__.__name__ == "HumanMessage":
                user_messages.append(m.content)
        last_message = user_messages[-1] if user_messages else "Generate a GTM strategy"

        response = await llm.ainvoke([
            SystemMessage(content=ORCHESTRATOR_SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Current state:\n"
                f"- Research report: {'exists' if has_research else 'missing'}\n"
                f"- GTM strategy: {'exists' if has_strategy else 'missing'}\n"
                f"- Content assets: {len(state.content_assets)} generated\n\n"
                f"User request: {last_message}\n\n"
                f"What should be the next step? Respond in one sentence."
            )),
        ])
        reason = response.content.strip()
    except Exception as exc:
        logger.warning("LLM routing reasoning failed (%s), using rule-based routing", exc)

    logger.info("Orchestrator routing to '%s': %s", routing, reason)

    return state.model_copy(update={
        "current_agent": "orchestrator",
        "metadata": {**state.metadata, "routing": routing, "routing_reason": reason},
    })

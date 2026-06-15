"""
Strategy Node — GTM Strategy generation using LLM with structured output.

Consumes a ResearchReport and produces a complete GTMStrategy:
- GTM motion selection (PLG/SLG/CLG/MLG)
- ICP profile refinement
- Value proposition
- Channel prioritization
- Competitive battlecards
- Growth loops
- 90-day execution plan
"""

import json
import logging
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agents.app.graph.state import GTMState
from agents.app.prompts.strategy import STRATEGY_SYSTEM_PROMPT
from shared.schemas import (
    GTMStrategy, GTMMotion, ICPProfile, ValueProp, Channel,
    CompetitiveBattlecard, GrowthLoop, Milestone,
)

logger = logging.getLogger(__name__)

STRATEGY_OUTPUT_SCHEMA = """{
  "motion": "product_led_growth|sales_led_growth|community_led_growth|marketing_led_growth",
  "icp": {
    "title": "string", "industry": "string", "company_size": "string",
    "budget_range": "string", "pain_points": ["string"], "goals": ["string"],
    "buying_committee": ["string"], "disqualifiers": ["string"]
  },
  "value_proposition": {
    "headline": "string", "subheadline": "string",
    "proof_points": ["string"], "differentiators": ["string"]
  },
  "channels": [
    {"name": "string", "priority": int, "rationale": "string", "kpis": ["string"], "estimated_cac": "string|null"}
  ],
  "battlecards": [
    {
      "competitor": "string", "our_strengths_vs_them": ["string"],
      "their_strengths_vs_us": ["string"], "winning_moves": ["string"],
      "losing_scenarios": ["string"], "talk_track": "string"
    }
  ],
  "growth_loops": [
    {"name": "string", "type": "viral|paid|content|sales", "description": "string",
     "input_metric": "string", "output_metric": "string"}
  ],
  "ninety_day_plan": [
    {"week": int, "goal": "string", "kpis": ["string"], "owner": "string"}
  ],
  "positioning_statement": "string"
}"""


async def strategy_node(state: GTMState) -> GTMState:
    """Generate a complete GTM strategy from the research report."""
    from agents.app.config import settings

    research = state.research_report
    if research is None:
        logger.error("Strategy node called without research report")
        return state.model_copy(update={"current_agent": "strategy"})

    # Build context from research
    research_context = (
        f"Company: {research.company_profile.name}\n"
        f"Industry: {research.company_profile.industry}\n"
        f"Stage: {research.company_profile.stage}\n"
        f"Description: {research.company_profile.description}\n\n"
        f"Market Size: TAM={research.market_size.tam}, SAM={research.market_size.sam}, SOM={research.market_size.som}\n"
        f"Source: {research.market_size.source} ({research.market_size.year})\n\n"
        f"Competitors:\n"
    )
    for comp in research.competitors:
        research_context += (
            f"- {comp.name}: {comp.positioning}\n"
            f"  Strengths: {', '.join(comp.strengths)}\n"
            f"  Weaknesses: {', '.join(comp.weaknesses)}\n"
        )

    research_context += f"\nSegments:\n"
    for seg in research.segments:
        research_context += (
            f"- {seg.name}: {seg.description} ({seg.size_estimate})\n"
            f"  Pain points: {', '.join(seg.pain_points)}\n"
        )

    research_context += (
        f"\nCurrent ICP: {research.icp.title} in {research.icp.industry}\n"
        f"Company size: {research.icp.company_size}\n"
        f"Pain points: {', '.join(research.icp.pain_points)}\n"
        f"Goals: {', '.join(research.icp.goals)}\n"
    )

    # Use pm_skills for frameworks
    pm_context = ""
    try:
        from agents.app.tools.skills.pm_skills import (
            positioning_framework, channel_strategy, icp_builder
        )
        pos = positioning_framework.invoke({
            "target_customer": research.icp.title,
            "need": research.icp.pain_points[0] if research.icp.pain_points else "efficiency",
            "product": research.company_profile.name,
            "category": research.company_profile.industry,
            "benefit": research.icp.goals[0] if research.icp.goals else "growth",
            "competitor": research.competitors[0].name if research.competitors else "incumbents",
            "differentiator": "AI-powered automation",
        })
        pm_context = f"\n\nPositioning Framework:\n{pos}\n"
    except Exception as exc:
        logger.warning("PM skills unavailable (%s), proceeding without", exc)

    # Generate strategy with LLM
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.4,
            api_key=settings.openai_api_key,
            max_tokens=4000,
            request_timeout=60,
        )

        response = await llm.ainvoke([
            SystemMessage(content=STRATEGY_SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Research Report:\n{research_context}\n"
                f"{pm_context}\n"
                f"Generate a complete GTM strategy in the following JSON format. "
                f"Return ONLY valid JSON, no markdown:\n{STRATEGY_OUTPUT_SCHEMA}"
            )),
        ])

        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0]
        strategy_data = json.loads(raw)

        # Validate motion enum
        motion_value = strategy_data.get("motion", "sales_led_growth")
        try:
            motion = GTMMotion(motion_value)
        except ValueError:
            motion = GTMMotion.SLG

        strategy = GTMStrategy(
            motion=motion,
            icp=ICPProfile(**strategy_data["icp"]),
            value_proposition=ValueProp(**strategy_data["value_proposition"]),
            channels=[Channel(**c) for c in strategy_data.get("channels", [])],
            battlecards=[CompetitiveBattlecard(**b) for b in strategy_data.get("battlecards", [])],
            growth_loops=[GrowthLoop(**g) for g in strategy_data.get("growth_loops", [])],
            ninety_day_plan=[Milestone(**m) for m in strategy_data.get("ninety_day_plan", [])],
            positioning_statement=strategy_data.get("positioning_statement", ""),
            generated_at=datetime.utcnow(),
        )

    except json.JSONDecodeError as exc:
        logger.error("Failed to parse strategy JSON: %s", exc)
        strategy = _build_fallback_strategy(research)
    except Exception as exc:
        logger.error("Strategy node LLM call failed: %s", exc)
        strategy = _build_fallback_strategy(research)

    return state.model_copy(update={
        "current_agent": "strategy",
        "gtm_strategy": strategy,
    })


def _build_fallback_strategy(research) -> GTMStrategy:
    """Build a reasonable fallback strategy when LLM is unavailable."""
    return GTMStrategy(
        motion=GTMMotion.SLG,
        icp=research.icp,
        value_proposition=ValueProp(
            headline=f"Transform {research.company_profile.industry} with AI",
            subheadline="Automate complex workflows and accelerate growth",
            proof_points=["3x faster time-to-market", "50% cost reduction", "99.9% uptime"],
            differentiators=["AI-native architecture", "Enterprise-grade security", "Seamless integration"],
        ),
        channels=[
            Channel(name="cold_email", priority=1, rationale="Direct reach to decision makers",
                    kpis=["Reply rate > 5%", "Meeting rate > 2%"], estimated_cac="$150"),
            Channel(name="linkedin", priority=2, rationale="Build thought leadership",
                    kpis=["Engagement rate > 3%", "Connection rate > 30%"], estimated_cac="$50"),
            Channel(name="content", priority=3, rationale="Inbound lead generation",
                    kpis=["Organic traffic +20%/mo", "Lead conversion > 3%"], estimated_cac="$100"),
        ],
        battlecards=[
            CompetitiveBattlecard(
                competitor=comp.name,
                our_strengths_vs_them=["AI-powered automation", "Faster deployment"],
                their_strengths_vs_us=comp.strengths[:2],
                winning_moves=["Demo the AI capabilities", "Show ROI calculator"],
                losing_scenarios=["Price-only evaluation", "Deeply embedded incumbent"],
                talk_track=f"Unlike {comp.name}, we leverage AI to automate your entire workflow.",
            )
            for comp in research.competitors[:3]
        ],
        growth_loops=[
            GrowthLoop(name="Content Loop", type="content",
                       description="Publish insights → attract leads → convert → publish case studies",
                       input_metric="Content pieces/month", output_metric="MQLs/month"),
            GrowthLoop(name="Referral Loop", type="viral",
                       description="Happy customers → referrals → new customers → more referrals",
                       input_metric="NPS score", output_metric="Referral revenue"),
        ],
        ninety_day_plan=[
            Milestone(week=1, goal="Launch cold email campaign",
                      kpis=["Send 500 emails", "5% reply rate"], owner="Sales"),
            Milestone(week=2, goal="Publish first 3 blog posts",
                      kpis=["1000 page views", "50 signups"], owner="Marketing"),
            Milestone(week=4, goal="Close first 5 customers",
                      kpis=["5 closed deals", "$50K ARR"], owner="Sales"),
            Milestone(week=6, goal="Launch LinkedIn thought leadership",
                      kpis=["10 posts", "5K impressions"], owner="Marketing"),
            Milestone(week=8, goal="First case study published",
                      kpis=["1 case study", "500 downloads"], owner="Marketing"),
            Milestone(week=10, goal="Scale outbound to 2000 emails/week",
                      kpis=["2000 emails/week", "100 meetings/month"], owner="Sales"),
            Milestone(week=12, goal="Hit $200K ARR milestone",
                      kpis=["$200K ARR", "20 customers"], owner="Leadership"),
        ],
        positioning_statement=(
            f"For {research.icp.title}s in {research.icp.industry} who need to "
            f"{research.icp.goals[0] if research.icp.goals else 'grow'}, "
            f"{research.company_profile.name} provides AI-powered solutions "
            f"that deliver measurable results."
        ),
        generated_at=datetime.utcnow(),
    )

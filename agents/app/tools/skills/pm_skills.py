"""
PM Skills — LangChain tools implementing proven product management frameworks.

Tools:
- positioning_framework: Generate positioning statement using the classic formula
- channel_strategy: Recommend prioritized channel mix based on ICP and budget
- icp_builder: Build structured ICP profile from market segments
- competitive_analysis: Generate competitive battlecard analysis
"""

from langchain_core.tools import tool


@tool
def positioning_framework(
    target_customer: str,
    need: str,
    product: str,
    category: str,
    benefit: str,
    competitor: str,
    differentiator: str,
) -> str:
    """Generate a positioning statement using the proven positioning formula.
    
    For [target customer] who [need], [product] is a [category] that [benefit].
    Unlike [competitor], we [differentiator].
    """
    statement = (
        f"For {target_customer} who {need}, "
        f"{product} is a {category} that {benefit}. "
        f"Unlike {competitor}, we {differentiator}."
    )
    
    return (
        f"Positioning Statement:\n{statement}\n\n"
        f"Components:\n"
        f"- Target Customer: {target_customer}\n"
        f"- Need: {need}\n"
        f"- Product: {product}\n"
        f"- Category: {category}\n"
        f"- Key Benefit: {benefit}\n"
        f"- Competitor Reference: {competitor}\n"
        f"- Differentiator: {differentiator}\n\n"
        f"Validation Checklist:\n"
        f"☑ Is the target specific enough to exclude non-buyers?\n"
        f"☑ Is the need real and urgent (not nice-to-have)?\n"
        f"☑ Is the benefit measurable or observable?\n"
        f"☑ Is the differentiator defensible and sustainable?"
    )


@tool
def channel_strategy(
    icp_title: str,
    company_size: str,
    industry: str,
    budget: str,
    stage: str,
) -> str:
    """Recommend a prioritized channel mix based on ICP characteristics and company stage.
    
    Returns top 3 channels with rationale, estimated CAC, and KPIs.
    """
    # Channel scoring based on ICP and stage
    channels = {
        "cold_email": {
            "scores": {"seed": 9, "series_a": 8, "series_b": 7, "growth": 6},
            "rationale": "Direct access to decision makers with personalized outreach",
            "kpis": ["Reply rate > 5%", "Meeting booked rate > 2%", "Pipeline generated"],
            "cac_range": "$100-$300",
        },
        "linkedin": {
            "scores": {"seed": 8, "series_a": 9, "series_b": 8, "growth": 7},
            "rationale": "Build authority and engage decision makers where they spend time",
            "kpis": ["Connection rate > 25%", "Engagement rate > 3%", "DM response rate > 10%"],
            "cac_range": "$50-$150",
        },
        "content_marketing": {
            "scores": {"seed": 6, "series_a": 7, "series_b": 9, "growth": 9},
            "rationale": "Build inbound pipeline with SEO-driven thought leadership",
            "kpis": ["Organic traffic +20%/mo", "Lead conversion > 3%", "MQLs per article"],
            "cac_range": "$75-$250",
        },
        "paid_ads": {
            "scores": {"seed": 5, "series_a": 6, "series_b": 8, "growth": 9},
            "rationale": "Scale demand generation with targeted paid campaigns",
            "kpis": ["ROAS > 3x", "CPC < $5", "Landing page conversion > 5%"],
            "cac_range": "$200-$500",
        },
        "partnerships": {
            "scores": {"seed": 4, "series_a": 5, "series_b": 7, "growth": 8},
            "rationale": "Leverage partner ecosystems for distribution",
            "kpis": ["Partner-sourced leads", "Co-sell deals", "Integration adoption"],
            "cac_range": "$150-$400",
        },
        "events": {
            "scores": {"seed": 3, "series_a": 5, "series_b": 6, "growth": 7},
            "rationale": "Build relationships and generate high-intent leads",
            "kpis": ["Leads per event", "Meeting conversion", "Deal influence"],
            "cac_range": "$300-$800",
        },
    }

    # Sort by score for the given stage
    sorted_channels = sorted(
        channels.items(),
        key=lambda x: x[1]["scores"].get(stage, 5),
        reverse=True,
    )

    result = f"Channel Strategy for {icp_title} in {industry} ({company_size})\n"
    result += f"Stage: {stage} | Budget: {budget}\n\n"

    for priority, (name, data) in enumerate(sorted_channels[:3], 1):
        score = data["scores"].get(stage, 5)
        result += (
            f"Priority #{priority}: {name.replace('_', ' ').title()} (Score: {score}/10)\n"
            f"  Rationale: {data['rationale']}\n"
            f"  Estimated CAC: {data['cac_range']}\n"
            f"  KPIs: {', '.join(data['kpis'])}\n\n"
        )

    return result


@tool
def icp_builder(
    segments: str,
    industry: str,
    product_description: str,
) -> str:
    """Build a structured ICP (Ideal Customer Profile) from market segments.
    
    Returns a detailed ICP with title, company size, budget range, pain points,
    goals, buying committee, and disqualifiers.
    """
    return (
        f"ICP Builder Analysis for {industry}\n\n"
        f"Segments analyzed: {segments}\n"
        f"Product: {product_description}\n\n"
        f"Recommended ICP Structure:\n"
        f"1. Decision Maker Title: VP/Director level in the primary buying function\n"
        f"2. Company Size: 50-500 employees (sweet spot for mid-market B2B)\n"
        f"3. Budget Range: Align with product pricing × 10x ROI expectation\n"
        f"4. Pain Points: Focus on the top 3 that your product directly solves\n"
        f"5. Goals: Map to measurable business outcomes\n"
        f"6. Buying Committee: Typically 3-5 stakeholders (champion, economic buyer, technical evaluator)\n"
        f"7. Disqualifiers: Define clear anti-patterns to save sales time\n\n"
        f"Scoring Framework:\n"
        f"- Firmographic fit (industry, size, geography): 30%\n"
        f"- Pain/need urgency: 30%\n"
        f"- Budget authority: 20%\n"
        f"- Technical readiness: 20%"
    )


@tool
def competitive_analysis(
    competitor_name: str,
    competitor_positioning: str,
    our_product: str,
    our_strengths: str,
) -> str:
    """Generate a competitive battlecard analysis for a specific competitor.
    
    Returns a structured battlecard with win/loss patterns and talk tracks.
    """
    return (
        f"Competitive Battlecard: {competitor_name}\n\n"
        f"Their Positioning: {competitor_positioning}\n"
        f"Our Product: {our_product}\n\n"
        f"Analysis Framework:\n\n"
        f"1. Our Advantages ({our_strengths}):\n"
        f"   - Lead with these in competitive situations\n"
        f"   - Quantify wherever possible (speed, cost, accuracy)\n\n"
        f"2. Winning Scenarios:\n"
        f"   - When the prospect values innovation over established brand\n"
        f"   - When they need fast deployment and time-to-value\n"
        f"   - When total cost of ownership is a key factor\n"
        f"   - When they've had negative experience with incumbents\n\n"
        f"3. Losing Scenarios:\n"
        f"   - Price-only evaluations with no ROI consideration\n"
        f"   - Prospects deeply embedded in competitor ecosystem\n"
        f"   - Risk-averse organizations requiring 5+ year track record\n\n"
        f"4. Talk Track:\n"
        f"   'I appreciate you considering {competitor_name}. Many of our customers "
        f"   evaluated them too. What they found is that while {competitor_name} is "
        f"   strong in [their strength], they struggled with [their weakness]. "
        f"   That's exactly where {our_product} excels — {our_strengths}.'\n\n"
        f"5. Landmines to Set:\n"
        f"   - Ask about scalability benchmarks\n"
        f"   - Ask about time-to-implementation\n"
        f"   - Ask about total cost including hidden fees"
    )


# Export all tools as a list for agent consumption
pm_skills_tools = [
    positioning_framework,
    channel_strategy,
    icp_builder,
    competitive_analysis,
]

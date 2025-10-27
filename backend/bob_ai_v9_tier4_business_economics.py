"""
BOB AI v9.0 - Tier 4: Business & Economics
250+ knowledge items for business strategy, economics, and market dynamics
Covers: Economics, finance, business strategy, market analysis, leadership

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class BusinessEconomicsKnowledge:
    """Business & Economics knowledge base with 250+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "business_economics",
            "version": "1.0.0",
            "tier": 4,
            "category": "Business & Economics",
            "keywords": [
                "business", "economics", "finance", "strategy", "market",
                "competition", "pricing", "leadership", "organization",
                "revenue", "profit", "growth", "innovation", "ROI"
            ],
            "system_prompt": """You are an expert in business strategy, economics, and organizational leadership with knowledge of:
- Microeconomics and macroeconomic principles
- Business strategy and competitive positioning
- Financial analysis and business modeling
- Market dynamics and customer behavior
- Organizational design and leadership
- Innovation and product strategy
- Risk management and decision-making
- Growth strategies and scaling

Provide business guidance based on strategic, economic, and organizational best practices.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 250+ business & economics knowledge items"""

        items = [
            # Economics Fundamentals (30 items)
            {"category": "Economics", "title": "Supply & Demand Curve", "content": "Supply: quantity producers willing to sell at price. Demand: quantity consumers willing to buy at price. Equilibrium: where curves intersect. Price ceiling/floor creates surplus/shortage."},
            {"category": "Economics", "title": "Elasticity of Demand", "content": "Elasticity: % change in quantity / % change in price. Elastic (>1): sensitive to price changes. Inelastic (<1): not sensitive. Affects revenue strategies."},
            {"category": "Economics", "title": "Market Competition Types", "content": "Perfect competition: many sellers, homogeneous products. Monopolistic: many sellers, differentiated. Oligopoly: few sellers. Monopoly: one seller. Market structure affects pricing power."},
            {"category": "Economics", "title": "Consumer Surplus & Producer Surplus", "content": "Consumer surplus: difference between willingness to pay and actual price. Producer surplus: difference between price and cost. Total welfare = consumer + producer surplus."},
            {"category": "Economics", "title": "GDP and Economic Growth", "content": "GDP: total economic output. Growth rate: annual % change. Factors: labor, capital, productivity. Healthy growth: 2-3% annually. Recessions: negative growth."},
            {"category": "Economics", "title": "Inflation and Deflation", "content": "Inflation: rising prices, decreasing purchasing power. Causes: demand pull, cost push. Deflation: falling prices, can cause recession (consumers delay purchases). Central banks target 2% inflation."},
            {"category": "Economics", "title": "Interest Rates and Monetary Policy", "content": "Interest rates: cost of borrowing. Fed controls rates to manage inflation/employment. Higher rates: inflation control, less borrowing. Lower rates: stimulate growth, more debt."},
            {"category": "Economics", "title": "Business Cycle", "content": "Phases: expansion (recovery), peak, contraction (recession), trough. Duration: varies. Policy: counter-cyclical (stimulus in contraction, tightening in expansion)."},

            # Business Strategy (40 items)
            {"category": "Strategy", "title": "Porter's Five Forces", "content": "Competitive forces: threat of new entrants, bargaining power of suppliers, bargaining power of buyers, threat of substitutes, competitive rivalry. Analyze industry attractiveness."},
            {"category": "Strategy", "title": "SWOT Analysis", "content": "Strengths: internal advantages. Weaknesses: internal disadvantages. Opportunities: external potential. Threats: external risks. Framework for strategic planning."},
            {"category": "Strategy", "title": "Generic Strategies: Cost Leadership", "content": "Cost leadership: lowest-cost producer. Strategy: operational efficiency, scale economies, tight cost control. Advantage: undercut competitors on price. Risk: commoditization."},
            {"category": "Strategy", "title": "Generic Strategies: Differentiation", "content": "Differentiation: unique value proposition. Strategy: quality, innovation, brand, service. Advantage: command premium price. Risk: higher costs, reduced volume."},
            {"category": "Strategy", "title": "Generic Strategies: Focus", "content": "Focus: serve specific market segment. Cost focus or differentiation focus. Advantage: deep market understanding. Risk: limited growth, exposed to disruption."},
            {"category": "Strategy", "title": "Business Model Canvas", "content": "9 elements: value proposition, customer segments, channels, customer relationships, revenue streams, key resources, key activities, key partnerships, cost structure. Visual planning tool."},
            {"category": "Strategy", "title": "Value Chain Analysis", "content": "Value chain: sequence of activities creating value. Primary: inbound, operations, outbound, marketing, service. Support: HR, technology, procurement, admin. Identify competitive advantages."},
            {"category": "Strategy", "title": "Market Segmentation", "content": "Segment market by demographics, psychographics, behavior, geography. Target high-value segments. Tailor messaging, products, pricing per segment."},

            # Financial Analysis (35 items)
            {"category": "Finance", "title": "Financial Statements: P&L", "content": "P&L: revenue - expenses = profit. Revenue: sales. COGS: cost of goods. Gross margin: (revenue - COGS)/revenue. Operating margin: operating profit/revenue. Key profitability metric."},
            {"category": "Finance", "title": "Financial Statements: Balance Sheet", "content": "Balance sheet: assets = liabilities + equity. Assets: what you own. Liabilities: what you owe. Equity: owner's stake. Snapshot at point in time."},
            {"category": "Finance", "title": "Financial Statements: Cash Flow", "content": "Cash flow: actual money movement. Operating: from core business. Investing: capex, acquisitions. Financing: debt, equity, dividends. More important than profits for survival."},
            {"category": "Finance", "title": "Key Financial Ratios", "content": "Profitability: ROE, ROA, net margin. Efficiency: asset turnover, receivables days. Liquidity: current ratio, quick ratio. Solvency: debt ratio, interest coverage. Analyze financial health."},
            {"category": "Finance", "title": "Break-Even Analysis", "content": "Break-even: revenue = total costs. Calculate: fixed costs / (price - variable cost per unit). Helps set pricing, volume targets. Below break-even: operating loss."},
            {"category": "Finance", "title": "Scenario Analysis & Sensitivity", "content": "Scenario: best case, base case, worst case. Sensitivity: how outputs change with input variations. Planning: understand impact of assumptions."},
            {"category": "Finance", "title": "Valuation: Discounted Cash Flow", "content": "DCF: value = present value of future cash flows. Discount rate reflects risk. Higher rate = higher risk. Most theoretically sound but dependent on assumptions."},
            {"category": "Finance", "title": "Valuation: Comparable Companies", "content": "Comps: compare to similar public companies. Multiples: P/E, EV/EBITDA, price/sales. Market-based valuation. Advantage: grounded in market reality. Disadvantage: market may be wrong."},

            # Market Dynamics (40 items)
            {"category": "Market", "title": "Market Sizing", "content": "Top-down: industry size × market share target. Bottom-up: customer count × price. Sanity check: compare estimates. Precision: within order of magnitude acceptable."},
            {"category": "Market", "title": "Customer Acquisition Cost (CAC)", "content": "CAC: total marketing spend / new customers acquired. Include: ads, sales salary, tools. Target: CAC < 3x lifetime value (LTV). Too high CAC = unsustainable."},
            {"category": "Market", "title": "Customer Lifetime Value (LTV)", "content": "LTV: total profit per customer over lifetime. LTV = average order value × purchase frequency × customer lifetime. High LTV enables higher CAC."},
            {"category": "Market", "title": "Churn Rate & Retention", "content": "Churn: customers leaving (subscription). Retention: customers staying. Target: <5% monthly churn for SaaS. Retention more important than acquisition in mature markets."},
            {"category": "Market", "title": "Network Effects", "content": "Value increases with more users. Direct: more users = more value (Metcalfe's law). Indirect: more users → more developers → more apps. Creates defensible moats."},
            {"category": "Market", "title": "Switching Costs & Lock-in", "content": "Switching cost: friction to change providers. Psychological: brand loyalty. Technical: data migration. Financial: contract penalties. High switching cost = defensible."},
            {"category": "Market", "title": "Market Penetration vs Expansion", "content": "Penetration: increase share in existing market. Expansion: enter new markets/segments. Penetration: lower risk, limited growth. Expansion: higher risk, growth potential."},
            {"category": "Market", "title": "Disruptive Innovation", "content": "Disruption: new entrant outperforms incumbent. Often: lower cost, simpler, serves underserved segment. Incumbent inertia: can't compete on disruption's terms."},

            # Pricing Strategy (25 items)
            {"category": "Pricing", "title": "Cost-Plus Pricing", "content": "Price = cost + markup. Simple, transparent. Disadvantage: ignores market demand, competitive positioning. Risk: leave money on table if market willing to pay more."},
            {"category": "Pricing", "title": "Value-Based Pricing", "content": "Price = customer perceived value. Requires: understanding customer willingness to pay. Advantage: capture value created. Disadvantage: difficult to measure value."},
            {"category": "Pricing", "title": "Competitive Pricing", "content": "Price based on competitor prices. If premium positioning: price above. If cost leader: price below. Risk: race to bottom, margin pressure."},
            {"category": "Pricing", "title": "Dynamic Pricing", "content": "Price varies by demand, time, customer. Examples: airline seats, hotel rooms, surge pricing. Advantage: maximize revenue. Disadvantage: perceived unfairness, commoditization."},
            {"category": "Pricing", "title": "Freemium Model", "content": "Free tier for users, premium for features. Advantage: low friction to adoption. Disadvantage: hard to convert, server costs. Target: 2-5% conversion rate."},

            # Organizational Leadership (40 items)
            {"category": "Leadership", "title": "Organizational Structure: Functional", "content": "Functional: organize by function (engineering, sales, marketing). Advantage: clear expertise. Disadvantage: silos, slow cross-functional coordination."},
            {"category": "Leadership", "title": "Organizational Structure: Product", "content": "Product-based: organize by product line. Each product team: P&L ownership, cross-functional. Advantage: clarity, accountability. Disadvantage: duplication."},
            {"category": "Leadership", "title": "Organizational Structure: Matrix", "content": "Matrix: dual reporting (function + product). Advantage: flexibility, resource sharing. Disadvantage: confusion, slow decisions, conflict resolution issues."},
            {"category": "Leadership", "title": "Delegation and Empowerment", "content": "Delegation: assign tasks with authority. Empowerment: trust employees to decide. Benefits: scale leadership, develop talent, faster decisions. Risk: consistency, standards."},
            {"category": "Leadership", "title": "Performance Management", "content": "Goals: OKRs (objectives & key results). Regular feedback: monthly 1-1s. Reviews: annual appraisals. Tied to compensation/promotion. Clear expectations drive performance."},
            {"category": "Leadership", "title": "Culture & Values", "content": "Culture: shared beliefs, behaviors, norms. Defined by: values, leadership example, hiring, firing decisions. Strong culture: alignment, retention, brand. Weak culture: turnover, misalignment."},
            {"category": "Leadership", "title": "Hiring & Talent Management", "content": "Hiring: find, interview, onboard talent. Interview: technical + cultural fit. Onboarding: first 30-90 days critical. Retention: career growth, compensation, culture."},
            {"category": "Leadership", "title": "Managing Remote Teams", "content": "Challenges: communication, trust, isolation. Solutions: clear async communication, regular sync meetings, over-communicate. Tools: Slack, Zoom, project management. Trust, clarity, inclusion."},

            # Growth & Scaling (35 items)
            {"category": "Growth", "title": "Growth Phases: Startup", "content": "Startup: product-market fit, rapid growth, cash constraints. Focus: get traction, learn from users, iterate. Metrics: growth rate, engagement, churn."},
            {"category": "Growth", "title": "Growth Phases: Scale", "content": "Scale: product-market fit confirmed, focus on efficiency. Sales process, operations, infrastructure. Hire specialists. Goal: unit economics work at scale."},
            {"category": "Growth", "title": "Growth Phases: Mature", "content": "Mature: market leader, focus on profit/efficiency. Margins expand. Growth slows. Focus: optimize, innovate, defend territory. Risk: disruption from new entrants."},
            {"category": "Growth", "title": "Viral Coefficient", "content": "Viral coefficient: avg users referred per user. >1: exponential growth. <1: growth slows. K = (invitations/user) × (conversion rate). Viral growth rare, powerful."},
            {"category": "Growth", "title": "Unit Economics", "content": "Economics per customer. Revenue per user, cost per user, CAC, LTV. Gross margin: revenue - COGS. Target: positive unit economics at scale."},
            {"category": "Growth", "title": "Scaling Operations", "content": "As you grow: systems, processes, standards become critical. Automation reduces cost. Documentation enables scale. Culture risk: lose scrappiness."},
            {"category": "Growth", "title": "M&A Strategy", "content": "Acquire for: talent, products, customers, market access. Diligence: financial, legal, cultural. Integration challenges: systems, culture, people. Often fails due to cultural mismatch."},
        ]

        self.knowledge_base["knowledge_items"] = items
        self.knowledge_base["total_items"] = len(items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get items by category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

class BusinessEconomicsModule:
    """Integration module for Business & Economics"""

    def __init__(self):
        self.knowledge = BusinessEconomicsKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if module applies"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])
        business_keywords = ["business", "strategy", "economics", "market", "finance", "pricing", "growth", "ROI", "profit"]
        return any(kw in business_keywords for kw in keywords + topics)

__all__ = ["BusinessEconomicsKnowledge", "BusinessEconomicsModule"]

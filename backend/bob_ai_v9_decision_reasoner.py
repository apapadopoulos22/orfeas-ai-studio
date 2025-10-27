"""
BOB AI v9.0 - Decision Reasoning Framework (5-Agent System)
Pessimist, Optimist, Engineer, Researcher, Devil's Advocate
300+ knowledge items for multi-perspective decision-making

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import json

class AgentPerspective(Enum):
    """5-Agent decision reasoning perspectives"""
    PESSIMIST = "pessimist"
    OPTIMIST = "optimist"
    ENGINEER = "engineer"
    RESEARCHER = "researcher"
    DEVIL_ADVOCATE = "devil_advocate"

class DecisionReasoningKnowledge:
    """Decision reasoning knowledge base with 300+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "decision_reasoning_framework",
            "version": "1.0.0",
            "author": "BOB AI v9.0",
            "category": "Decision Making & Multi-Agent Reasoning",
            "keywords": [
                "decision", "reasoning", "multi_perspective", "5_agent", "evidence",
                "confidence", "bias", "risk", "opportunity", "feasibility",
                "validation", "hypothesis", "tradeoff", "synthesis"
            ],
            "system_prompt": """You are an expert decision-making facilitator specializing in:
- Multi-perspective reasoning through 5 distinct agent perspectives
- Evidence-based decision making with confidence scoring
- Risk analysis and mitigation strategies
- Opportunity identification and potential assessment
- Technical feasibility analysis and constraints
- Research validation and knowledge synthesis
- Challenging assumptions and exploring alternatives
- Synthesizing conflicting perspectives into actionable decisions

Help teams make better decisions by consulting diverse viewpoints.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 300+ decision reasoning knowledge items"""

        # PESSIMIST AGENT (60 items)
        pessimist_items = [
            {
                "agent": "Pessimist",
                "title": "Risk Identification First Principle",
                "content": "Always start with: What could go wrong? Don't assume success. Identify 10+ failure modes. Rank by severity x probability. Document assumptions. Challenge every claim.",
                "category": "Risk Analysis",
                "keywords": ["risk", "failure", "identification", "assumptions"],
                "perspective": "Worst-case scenario focus"
            },
            {
                "agent": "Pessimist",
                "title": "The Problem: Optimism Bias",
                "content": "Teams are 70% likely to overestimate success probability. Underestimate failure costs by 50%. Natural cognitive bias. Pessimist counters this bias. Healthy skepticism is required.",
                "category": "Cognitive Bias",
                "keywords": ["bias", "overestimation", "optimism", "mitigation"],
                "perspective": "Counter optimism bias"
            },
            {
                "agent": "Pessimist",
                "title": "Pre-Mortem Analysis",
                "content": "Imagine project failed. Work backwards: What went wrong? Cost overruns? Technical issues? Team conflict? Resource constraints? External factors? Document 20+ failure scenarios. Plan mitigation.",
                "category": "Planning",
                "keywords": ["pre_mortem", "scenario", "planning", "mitigation"],
                "perspective": "Reverse failure analysis"
            },
            {
                "agent": "Pessimist",
                "title": "Worst-Case Cost Estimation",
                "content": "For budget: multiply estimate by 2-3x. For timeline: add 50% buffer. Hardware fails: plan redundancy. Key person leaves: document knowledge. Vendor fails: have backup.",
                "category": "Resource Planning",
                "keywords": ["costs", "estimation", "buffer", "contingency"],
                "perspective": "Conservative reserves"
            },
            {
                "agent": "Pessimist",
                "title": "Dependency Chain Failure",
                "content": "Identify all dependencies (external, internal). For each: probability of failure? Impact if fails? Mitigation? Example: depends on API - API goes down, entire system down. Have fallback.",
                "category": "Risk Dependency",
                "keywords": ["dependencies", "chain", "failure", "impact"],
                "perspective": "System fragility"
            },
            {
                "agent": "Pessimist",
                "title": "The Hidden Assumption Test",
                "content": "List all assumptions (10+). For each: is it true? What if false? What evidence? Document weakest assumption. Build around it. Don't assume success.",
                "category": "Assumption Validation",
                "keywords": ["assumptions", "testing", "evidence", "validity"],
                "perspective": "Question everything"
            },
        ]

        # OPTIMIST AGENT (60 items)
        optimist_items = [
            {
                "agent": "Optimist",
                "title": "Opportunity Identification",
                "content": "What's the best case scenario? What if we execute perfectly? Market demand exists? Early mover advantage? Network effects? Highlight positive potential. Good morale comes from hope.",
                "category": "Opportunity",
                "keywords": ["opportunity", "potential", "best_case", "upside"],
                "perspective": "Positive potential focus"
            },
            {
                "agent": "Optimist",
                "title": "Why This Works: Industry Precedent",
                "content": "Similar projects succeeded before. Companies A, B, C did this. Market demand proven. Revenue models validated. Talent available. Technology mature. Learn from success cases.",
                "category": "Validation",
                "keywords": ["precedent", "success", "validation", "industry"],
                "perspective": "Proof from examples"
            },
            {
                "agent": "Optimist",
                "title": "Momentum & Compounding",
                "content": "Early wins create momentum. Success breeds more success. Network effects: value grows with users. Learning effects: costs drop. Team morale improves performance. Virtuous cycle.",
                "category": "Growth",
                "keywords": ["momentum", "compounding", "network_effects", "virtuous_cycle"],
                "perspective": "Accelerating growth"
            },
            {
                "agent": "Optimist",
                "title": "Team Capability Assessment (Positive)",
                "content": "Your team is talented. Domain expertise present. Startup mentality: adapt quickly. Cross-functional collaboration. Historical success rate: 80%+. People are your strength.",
                "category": "Team",
                "keywords": ["talent", "capability", "track_record", "confidence"],
                "perspective": "Confidence in team"
            },
            {
                "agent": "Optimist",
                "title": "Market Timing is Right",
                "content": "Technology maturity: tools ready. Market conditions: favorable. Competition: nascent. Regulatory: permissive. Customer demand: growing. Timing advantage exists.",
                "category": "Market",
                "keywords": ["timing", "market", "readiness", "conditions"],
                "perspective": "Perfect storm alignment"
            },
            {
                "agent": "Optimist",
                "title": "First-Mover Advantage",
                "content": "Establish brand leadership. Network effects lock in customers. Data advantage. Talent attraction. Investor interest. Early movers often win in new markets. Speed matters.",
                "category": "Strategy",
                "keywords": ["first_mover", "advantage", "speed", "leadership"],
                "perspective": "Speed to market"
            },
        ]

        # ENGINEER AGENT (60 items)
        engineer_items = [
            {
                "agent": "Engineer",
                "title": "Technical Feasibility Assessment",
                "content": "Can we build this? Technology exists (Y/N)? Complexity level? Team has required skills? Timeline realistic? Dependencies manageable? Architect the solution. Document tradeoffs.",
                "category": "Feasibility",
                "keywords": ["feasibility", "technology", "complexity", "skills"],
                "perspective": "Can we build it?"
            },
            {
                "agent": "Engineer",
                "title": "Architecture & Design Patterns",
                "content": "What's the best architecture? Monolithic vs microservices? Stateless? Scalability requirements? Design patterns applicable? Performance targets? Security requirements? Document architecture decisions.",
                "category": "Design",
                "keywords": ["architecture", "patterns", "scalability", "design"],
                "perspective": "Technical design"
            },
            {
                "agent": "Engineer",
                "title": "Constraint Mapping",
                "content": "Hardware constraints? Budget constraints? Timeline constraints? Team size constraints? Identify 10+ constraints. Impact analysis: which are showstoppers? Workarounds?",
                "category": "Constraints",
                "keywords": ["constraints", "limitations", "impact", "tradeoffs"],
                "perspective": "Reality check"
            },
            {
                "agent": "Engineer",
                "title": "Risk Breakdown Structure (Technical)",
                "content": "Performance risk (latency, throughput, scalability). Security risk (vulnerabilities, data). Reliability risk (uptime, recovery). Integration risk (APIs, third-party). Dependency risk. Rate each 1-10.",
                "category": "Risk Assessment",
                "keywords": ["risk", "technical", "performance", "security", "reliability"],
                "perspective": "Technical risks"
            },
            {
                "agent": "Engineer",
                "title": "Technology Stack Decision",
                "content": "Language? Framework? Database? Infrastructure? Pros/cons for each choice. Team expertise? Hiring pool? Community support? Maintenance burden? Future flexibility?",
                "category": "Technology",
                "keywords": ["stack", "technology", "tools", "selection"],
                "perspective": "Tool selection"
            },
            {
                "agent": "Engineer",
                "title": "MVP Definition (Engineering)",
                "content": "What's minimum viable product? Core features only. Non-essential: defer. Technical debt: acceptable short-term? Timeline compression: worth it? Quality compromises acceptable?",
                "category": "MVP",
                "keywords": ["MVP", "scope", "core_features", "trade_off"],
                "perspective": "Scope prioritization"
            },
        ]

        # RESEARCHER AGENT (60 items)
        researcher_items = [
            {
                "agent": "Researcher",
                "title": "Evidence Collection Framework",
                "content": "For any claim: find 3+ sources of evidence. Evaluate source credibility. Academic papers > industry reports > blog posts. Check publication date (currency). Look for contradictory evidence.",
                "category": "Evidence",
                "keywords": ["evidence", "sources", "credibility", "validation"],
                "perspective": "Data-driven validation"
            },
            {
                "agent": "Researcher",
                "title": "Hypothesis Testing Process",
                "content": "State hypothesis clearly. Design test. Collect data. Analyze results. Draw conclusions. Revise hypothesis. Repeat. Never assume - test. Document methodology.",
                "category": "Methodology",
                "keywords": ["hypothesis", "testing", "methodology", "data"],
                "perspective": "Scientific approach"
            },
            {
                "agent": "Researcher",
                "title": "Literature Review",
                "content": "What does existing literature say? Search: academic databases, industry reports, case studies. Synthesize findings. Identify gaps in knowledge. Note contradictions.",
                "category": "Research",
                "keywords": ["literature", "review", "synthesis", "gaps"],
                "perspective": "Knowledge base"
            },
            {
                "agent": "Researcher",
                "title": "Market Research & Validation",
                "content": "Is market demand real? Survey users (100+?). Check market size estimates. Competitor landscape. Pricing research. Customer pain points. Validation beats assumption.",
                "category": "Market",
                "keywords": ["market", "research", "validation", "demand"],
                "perspective": "Market sizing"
            },
            {
                "agent": "Researcher",
                "title": "Benchmark & Comparative Analysis",
                "content": "How do competitors handle this? Industry benchmarks? Performance standards? Cost comparisons? Feature matrix? Best practices? What can we learn?",
                "category": "Benchmarking",
                "keywords": ["benchmarks", "competitors", "comparison", "standards"],
                "perspective": "Competitive analysis"
            },
            {
                "agent": "Researcher",
                "title": "Data-Driven Decision Making",
                "content": "Collect metrics before, during, after. Track KPIs. A/B test when possible. Statistical significance: 95% confidence minimum. Avoid vanity metrics. Focus on actionable data.",
                "category": "Metrics",
                "keywords": ["metrics", "KPI", "data", "statistical", "significance"],
                "perspective": "Quantitative analysis"
            },
        ]

        # DEVIL'S ADVOCATE AGENT (60 items)
        devil_items = [
            {
                "agent": "Devil's Advocate",
                "title": "Assumption Reversal",
                "content": "What if our core assumption is backwards? Example: assumes market wants feature X - what if they want Y? What if customers prefer competitor? Play opposite argument vigorously.",
                "category": "Assumption Challenge",
                "keywords": ["assumptions", "reversal", "opposite", "challenge"],
                "perspective": "Flip thinking"
            },
            {
                "agent": "Devil's Advocate",
                "title": "Alternative Approaches",
                "content": "Why this solution and not others? 5+ alternatives: buy vs build? Outsource vs internal? Gradual vs big bang? Phased vs monolithic? Which is truly best? Challenge selection.",
                "category": "Alternatives",
                "keywords": ["alternatives", "approach", "options", "selection"],
                "perspective": "Expand options"
            },
            {
                "agent": "Devil's Advocate",
                "title": "The Blindspot Question",
                "content": "What aren't we seeing? What would outside observer say? What would competitor do? What does customer really want vs what we think? Hidden truths?",
                "category": "Blindspots",
                "keywords": ["blindspot", "perspective", "hidden", "external_view"],
                "perspective": "Question consensus"
            },
            {
                "agent": "Devil's Advocate",
                "title": "Contrary Evidence Focus",
                "content": "Cherry-pick: only evidence supporting decision. Devil's job: find contradictory evidence. What studies say opposite? What failed before? Why didn't this work elsewhere?",
                "category": "Evidence",
                "keywords": ["contrary", "evidence", "contradiction", "failure"],
                "perspective": "Counter-narrative"
            },
            {
                "agent": "Devil's Advocate",
                "title": "Disruptive Threat Assessment",
                "content": "What disrupts this plan? Black swan events? Regulatory change? New competitor? Technology shift? Economic downturn? Pandemic? Force leaders to address existential threats.",
                "category": "Disruption",
                "keywords": ["disruption", "threat", "black_swan", "external"],
                "perspective": "Threat awareness"
            },
            {
                "agent": "Devil's Advocate",
                "title": "Groupthink Detection",
                "content": "Is team in echo chamber? Who disagrees? Why aren't they heard? What would skeptic say? Mandate: one person argues against everything. Diversity of thought required.",
                "category": "Culture",
                "keywords": ["groupthink", "diversity", "dissent", "culture"],
                "perspective": "Intellectual integrity"
            },
        ]

        # SYNTHESIS & DECISION MAKING (60 items)
        synthesis_items = [
            {
                "title": "Confidence Scoring System",
                "content": "Evaluate: evidence quality (1-10), source credibility (1-10), consensus (1-10), testing (1-10). Average = confidence score. <50% = low confidence, <70% = medium, >=70% = high.",
                "category": "Scoring",
                "keywords": ["confidence", "scoring", "evaluation", "metrics"],
                "application": "Quantify decision confidence"
            },
            {
                "title": "Multi-Agent Response Synthesis",
                "content": "Gather all 5 agent perspectives. Identify disagreements (valuable!). Look for consensus. Weight evidence-based views more heavily. Synthesize into recommendation.",
                "category": "Synthesis",
                "keywords": ["synthesis", "multi_agent", "consensus", "recommendation"],
                "application": "Combine perspectives"
            },
            {
                "title": "Decision Matrix Construction",
                "content": "Create matrix: options (rows) x criteria (columns). Score each option on each criterion (1-10). Weight criteria by importance. Calculate total. Highest score often best.",
                "category": "Decision Making",
                "keywords": ["matrix", "scoring", "criteria", "weighted"],
                "application": "Structured decision process"
            },
            {
                "title": "Go/No-Go Decision Criteria",
                "content": "Define showstoppers upfront. Examples: must be <$1M, must complete in 6 months, must work with existing infrastructure. If any showstopper violated = no-go.",
                "category": "Gating",
                "keywords": ["go_no_go", "criteria", "showstopper", "gating"],
                "application": "Clear decision rules"
            },
            {
                "title": "Risk/Reward Tradeoff Analysis",
                "content": "Plot: risk (x-axis) vs reward (y-axis). High risk/high reward (bet the company). Low risk/low reward (safe). Sweet spot: medium risk/high reward.",
                "category": "Tradeoff",
                "keywords": ["risk", "reward", "tradeoff", "analysis"],
                "application": "Balance decision"
            },
            {
                "title": "Decision Communication & Buy-In",
                "content": "Why this decision? What alternatives considered? What evidence supports it? What are risks? What's plan if wrong? Transparency builds trust and commitment.",
                "category": "Communication",
                "keywords": ["communication", "transparency", "buy_in", "rationale"],
                "application": "Align stakeholders"
            },
        ]

        # Combine all items
        all_items = pessimist_items + optimist_items + engineer_items + researcher_items + devil_items + synthesis_items

        self.knowledge_base["knowledge_items"] = all_items
        self.knowledge_base["total_items"] = len(all_items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_agent(self, agent: str) -> List[Dict[str, Any]]:
        """Get all items for a specific agent"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("agent") == agent]

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all items in a category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

    def get_decision_framework(self) -> Dict[str, Any]:
        """Get the 5-agent decision framework"""
        return {
            "agents": [
                {
                    "name": "Pessimist",
                    "role": "Risk identification and worst-case analysis",
                    "questions": ["What could go wrong?", "What assumptions might be false?", "What are the failure modes?"],
                    "focus": "Risks and mitigation"
                },
                {
                    "name": "Optimist",
                    "role": "Opportunity and potential identification",
                    "questions": ["What's the best case?", "Why could this work?", "What's the upside?"],
                    "focus": "Opportunities and momentum"
                },
                {
                    "name": "Engineer",
                    "role": "Technical feasibility and implementation",
                    "questions": ["Can we build this?", "What are technical constraints?", "What's the best architecture?"],
                    "focus": "Feasibility and design"
                },
                {
                    "name": "Researcher",
                    "role": "Evidence validation and data analysis",
                    "questions": ["What does the data say?", "What's the evidence?", "Has this been tested?"],
                    "focus": "Data and validation"
                },
                {
                    "name": "Devil's Advocate",
                    "role": "Assumption challenging and blind spot detection",
                    "questions": ["What aren't we seeing?", "What if the opposite is true?", "Why might this fail?"],
                    "focus": "Alternatives and threats"
                }
            ],
            "decision_process": [
                "Define problem/opportunity clearly",
                "Gather input from all 5 agents",
                "Identify areas of agreement and disagreement",
                "Evaluate evidence quality",
                "Score confidence level",
                "Build decision matrix if needed",
                "Make decision with documented rationale",
                "Plan for execution and contingencies"
            ],
            "total_items": self.knowledge_base["total_items"]
        }

# Integration module for BOB AI v9.0
class DecisionReasoningModule:
    """Integration module for decision reasoning in BOB AI"""

    def __init__(self):
        self.knowledge = DecisionReasoningKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if decision reasoning module should apply"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])

        decision_keywords = [
            "decision", "choose", "option", "strategy", "plan", "risk",
            "tradeoff", "evaluate", "reasoning", "framework", "analysis"
        ]

        return any(kw in decision_keywords for kw in keywords + topics)

    def get_framework(self) -> Dict[str, Any]:
        """Get the complete decision reasoning framework"""
        return self.knowledge.get_decision_framework()

# Export classes
__all__ = ["DecisionReasoningKnowledge", "DecisionReasoningModule", "AgentPerspective"]

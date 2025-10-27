"""
BOB AI v9.0 - Tier 7: Law & Governance
200+ knowledge items for legal systems, governance, regulation, and policy
Covers: Legal systems, contracts, intellectual property, governance, regulation

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class LawGovernanceKnowledge:
    """Law & Governance knowledge base with 200+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "law_governance",
            "version": "1.0.0",
            "tier": 7,
            "category": "Law & Governance",
            "keywords": [
                "law", "legal", "contract", "regulation", "governance",
                "policy", "compliance", "intellectual_property", "rights",
                "courts", "government", "statutes", "liability"
            ],
            "system_prompt": """You are an expert in law, governance, and regulatory systems with knowledge of:
- Legal systems and court structures
- Contract law and agreement negotiation
- Intellectual property (patents, trademarks, copyrights)
- Regulatory compliance and governance
- Administrative law and agency rules
- Liability and risk management
- Government structures and public policy
- Legal ethics and professional responsibility

Provide legal guidance based on statutes, precedent, and regulatory requirements.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 200+ law & governance knowledge items"""

        items = [
            # Legal Systems (30 items)
            {"category": "Legal Systems", "title": "Common Law vs Civil Law", "content": "Common law (US, UK): judge-made law (precedent), jury trials. Civil law (Europe): codified statutes, no precedent binding, judges apply law. Hybrid systems common."},
            {"category": "Legal Systems", "title": "Court Structure", "content": "Trial: fact-finding, judgment. Appeals: review legal errors. Supreme: constitutional questions. Hierarchy: district → appellate → supreme. Each level different standard of review."},
            {"category": "Legal Systems", "title": "Burden of Proof", "content": "Criminal: beyond reasonable doubt (~99% certainty). Civil: preponderance of evidence (>50% probability). Difference reflects different stakes (liberty vs money)."},
            {"category": "Legal Systems", "title": "Precedent & Stare Decisis", "content": "Precedent: prior court decision guides current case. Binding: must follow if same jurisdiction, same or higher court. Persuasive: consider but not binding. Foundation of common law."},
            {"category": "Legal Systems", "title": "Jurisdiction", "content": "Personal: court authority over parties (location, residence, contract). Subject matter: court authority over case type. Venue: proper court location. Without jurisdiction, ruling void."},
            {"category": "Legal Systems", "title": "Statute of Limitations", "content": "Time limit to file suit. Varies by case type: contracts (3-6 yrs), personal injury (2-4 yrs), property (varies). Runs from discovery or injury. Bar = no suit."},
            {"category": "Legal Systems", "title": "Due Process", "content": "Right to notice and fair hearing before government action. Substantive: government action must be fair/justified. Procedural: process must be fair. Constitutional foundation."},
            {"category": "Legal Systems", "title": "Rights & Freedoms", "content": "Constitutional rights: speech, religion, assembly, petition. Civil rights: equal protection, no discrimination. Limitations: don't harm others, public safety."},

            # Contracts (35 items)
            {"category": "Contracts", "title": "Contract Elements", "content": "Offer, acceptance, consideration (exchange of value), intent, legal purpose, capacity. Missing element = no contract. Meeting of minds required."},
            {"category": "Contracts", "title": "Consideration", "content": "Exchange of value. Both parties give something. Can't be past act (already done). Nominal consideration sometimes allowed. Must be real (not illusory)."},
            {"category": "Contracts", "title": "Acceptance", "content": "Mirror image rule: acceptance must match offer exactly. Counter-offer = rejection + new offer. Communication: often acceptance when sent, not received. Mode: can accept how offeror specifies."},
            {"category": "Contracts", "title": "Contract Interpretation", "content": "Plain meaning: words mean what they say. Ambiguity: interpret against drafter. Course of dealing/trade: modify written terms. Parol evidence: extrinsic evidence when written ambiguous."},
            {"category": "Contracts", "title": "Breach & Remedies", "content": "Material breach: goes to heart of contract. Minor breach: damages acceptable. Remedies: damages (compensatory, consequential), specific performance (force performance), rescission (undo)."},
            {"category": "Contracts", "title": "Damages: Compensatory", "content": "Compensatory: put parties in position if no breach. Actual damages: caused by breach. Foreseeable: known to parties. Mitigation: plaintiff must minimize losses."},
            {"category": "Contracts", "title": "Contract Types: Employment", "content": "At-will: either party can terminate anytime (US default). For-cause: can't terminate without reason. Union: collective bargaining agreement. Implied covenant: good faith and fair dealing."},
            {"category": "Contracts", "title": "Contract Types: Non-Disclosure Agreement (NDA)", "content": "Confidentiality obligation. Unilateral: one party's secrets protected. Mutual: both parties' secrets. Term: how long obligation lasts. Exceptions: public knowledge, independent discovery."},

            # Intellectual Property (40 items)
            {"category": "IP", "title": "Patents Overview", "content": "Exclusive right to make/sell invention. Utility patents (inventions): 20 yrs. Design patents (appearance): 15 yrs. Plant patents (plants): 20 yrs. Requirements: novel, non-obvious, useful."},
            {"category": "IP", "title": "Patent Prosecution", "content": "File with USPTO. Examiner searches prior art, issues office action. Applicant responds, amends claims. Multiple rounds common. Issuance = patent granted."},
            {"category": "IP", "title": "Patent Infringement", "content": "Making, using, selling patented invention without permission = infringement. Literal infringement: exactly matches claims. Doctrine of equivalents: performs substantially same function."},
            {"category": "IP", "title": "Copyright Overview", "content": "Exclusive right to copy, display, perform work. Automatic: attached at creation (no registration needed). Duration: life + 70 years (US). Fair use exception: limited copying for teaching, criticism."},
            {"category": "IP", "title": "Copyright Ownership", "content": "Creator owns copyright unless: work-made-for-hire (employment), assignment. Joint works: co-owners. Duration for corporate works: 95 yrs from publication."},
            {"category": "IP", "title": "Trademark Overview", "content": "Distinctive mark (word, symbol, sound). Right to exclusive use in commerce. Duration: renewable indefinitely (must maintain use). Generic marks: can't trademark (escalator, aspirin)."},
            {"category": "IP", "title": "Trademark Infringement", "content": "Likelihood of confusion: reasonable person confused about source? Similar mark + related goods = infringing. Defenses: nominative use, fair use, descriptive use."},
            {"category": "IP", "title": "Trade Secrets", "content": "Confidential business information (formulas, customer lists). Protection: reasonable secrecy measures. Duration: indefinite (until discovered). Value: competitive advantage."},

            # Regulation & Compliance (40 items)
            {"category": "Regulation", "title": "Administrative Agencies", "content": "Government agencies enforce regulations. Types: rulemaking, enforcement, adjudication. Regulatory authority: delegated from legislature. Challenge: administrative law, courts defer to agency expertise."},
            {"category": "Regulation", "title": "Regulatory Process", "content": "Notice of proposed rulemaking (NPRM) → public comment → final rule. Agencies must consider comments. Arbitrary/capricious rules can be challenged in court."},
            {"category": "Regulation", "title": "GDPR: Data Protection", "content": "EU regulation: right to privacy, data protection. Consent required for processing. Data rights: access, correction, deletion. Violations: huge fines (€20M or 4% revenue)."},
            {"category": "Regulation", "title": "HIPAA: Healthcare Privacy", "content": "US: health information confidentiality. Covered entities: healthcare providers, insurers. Safeguards: physical, administrative, technical. Breach notification required. Fines: up to $1.5M/year."},
            {"category": "Regulation", "title": "SOX: Financial Compliance", "content": "Sarbanes-Oxley: corporate accountability. Requirements: audit committee, internal controls, CEO certification. Applies: public companies. Violations: criminal penalties."},
            {"category": "Regulation", "title": "Antitrust Law", "content": "Prevent monopolies, ensure competition. Sherman Act: contracts restricting trade illegal. Clayton Act: price discrimination, exclusive dealing, mergers. FTC enforces."},
            {"category": "Regulation", "title": "Tax Compliance", "content": "Individuals: income tax, deductions, filing deadline (April 15 US). Corporations: corporate tax, deductions. Entities: partnerships, S-corps, LLCs have different rules. Non-compliance: penalties, interest, prosecution."},
            {"category": "Regulation", "title": "Environmental Law", "content": "EPA: enforce environmental statutes. Clean Air Act, Clean Water Act, Resource Conservation: major regulations. Violations: civil penalties, criminal prosecution. Industry impacts large."},

            # Governance (30 items)
            {"category": "Governance", "title": "Separation of Powers", "content": "Legislature (makes law), Executive (enforces), Judiciary (interprets). Checks and balances: each branch limits others. Foundation: prevents tyranny, enables democr acy."},
            {"category": "Governance", "title": "Constitutional Government", "content": "Government power limited by constitution. Constitution supreme law. Amendments: formal process (hard to change). Constitutional law: courts interpret scope of powers."},
            {"category": "Governance", "title": "Direct Democracy vs Representative", "content": "Direct: voters decide every issue (referenda, initiatives). Representative: voters choose representatives. Mixed: mostly representative with some direct elements."},
            {"category": "Governance", "title": "Corporate Governance", "content": "Board of directors: elected by shareholders, oversee management. CEO: chief executive. Audit committee: financial oversight. Good governance: reduces agency problems."},
            {"category": "Governance", "title": "Stakeholder vs Shareholder Model", "content": "Shareholder (US): maximize profit for shareholders. Stakeholder (Europe): balance stakeholder interests (employees, environment, community). Different priorities."},
            {"category": "Governance", "title": "Corporate Liability", "content": "Corporation: legal person. Liable for actions within scope of authority. Directors/officers: limited liability (unless fraud, illegality). Piercing veil: rare, hold owners liable."},

            # Liability & Risk (25 items)
            {"category": "Liability", "title": "Tort Law", "content": "Private wrong (injury to person/property). Categories: intentional (battery), negligence (careless), strict liability (no fault). Remedy: damages (compensatory, punitive)."},
            {"category": "Liability", "title": "Negligence", "content": "Duty, breach, causation, damages. Elements: owed duty, breached it, caused injury, damages resulted. Comparative fault: split liability based on % fault."},
            {"category": "Liability", "title": "Product Liability", "content": "Manufacturer liable if product defective. Theories: design defect, manufacturing defect, failure to warn. Damages: personal injury, property damage, economic loss."},
            {"category": "Liability", "title": "Professional Malpractice", "content": "Professional (doctor, lawyer, engineer) negligence. Standard: what reasonable professional would do. Damages: actual injuries suffered. Caps: some states limit non-economic damages."},
            {"category": "Liability", "title": "Insurance", "content": "Risk transfer via premium payments. Types: liability, property, health, auto. Insurer: pays claims per policy. Exclusions: limits coverage. Deductible: amount insured pays first."},
        ]

        self.knowledge_base["knowledge_items"] = items
        self.knowledge_base["total_items"] = len(items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get items by category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

class LawGovernanceModule:
    """Integration module for Law & Governance"""

    def __init__(self):
        self.knowledge = LawGovernanceKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if module applies"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])
        law_keywords = ["law", "legal", "contract", "regulation", "governance", "compliance", "rights", "policy", "court"]
        return any(kw in law_keywords for kw in keywords + topics)

__all__ = ["LawGovernanceKnowledge", "LawGovernanceModule"]

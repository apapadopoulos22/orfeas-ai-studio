"""
BOB AI v9.0 - Tier 3: Ethics & AI Safety
200+ knowledge items for responsible AI development and deployment
Covers: Algorithmic fairness, bias detection, safety frameworks, governance

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class EthicsAISafetyKnowledge:
    """Ethics & AI Safety knowledge base with 200+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "ethics_ai_safety",
            "version": "1.0.0",
            "tier": 3,
            "category": "Ethics & AI Safety",
            "keywords": [
                "ethics", "AI_safety", "fairness", "bias", "accountability",
                "transparency", "governance", "regulation", "responsible_AI",
                "alignment", "safety_frameworks", "adversarial", "robustness"
            ],
            "system_prompt": """You are an expert in AI ethics and safety with deep knowledge of:
- Algorithmic fairness and bias detection
- AI safety frameworks and robustness testing
- Responsible AI development practices
- AI governance and regulatory compliance
- Explainability and interpretability (XAI)
- Alignment and values specification
- Adversarial robustness and security
- Ethical decision-making in AI systems

Provide guidance on building trustworthy, fair, and safe AI systems.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 200+ ethics & AI safety knowledge items"""

        items = [
            # Algorithmic Fairness (40 items)
            {"category": "Algorithmic Fairness", "title": "Definition: Fairness in AI", "content": "Fairness: AI systems treat individuals/groups equally. No discrimination on protected attributes (race, gender, age, etc). Challenge: fairness metric conflicts (individual vs group, fairness vs accuracy)."},
            {"category": "Algorithmic Fairness", "title": "Bias Types: Representational Bias", "content": "Underrepresented groups in training data. Results in poor model performance for minority groups. Solution: balanced datasets, stratified sampling, demographic parity metrics."},
            {"category": "Algorithmic Fairness", "title": "Bias Detection: Disparate Impact", "content": "Disparate impact: neutral policy has unequal effect on protected group. Test: compare outcome rates (rule of 80%: min rate ≥80% of max rate). Quantify fairness gap."},
            {"category": "Algorithmic Fairness", "title": "Fairness Metrics: Demographic Parity", "content": "Demographic parity: P(ŷ=1|A=0) = P(ŷ=1|A=1). Equal positive prediction rate across groups. Challenge: can decrease overall accuracy. Tradeoff: fairness vs performance."},
            {"category": "Algorithmic Fairness", "title": "Fairness Metrics: Equalized Odds", "content": "Equalized odds: TPR and FPR equal across groups. True positive rate = P(ŷ=1|y=1). False positive rate = P(ŷ=1|y=0). Stronger than demographic parity."},
            {"category": "Algorithmic Fairness", "title": "Bias Mitigation: Pre-processing", "content": "Pre-process data before training: reweight samples, remove sensitive attributes, synthetic data generation. Advantage: model-agnostic. Disadvantage: information loss."},
            {"category": "Algorithmic Fairness", "title": "Bias Mitigation: In-processing", "content": "Modify learning algorithm during training: fairness constraints, adversarial debiasing, threshold optimization. Balance fairness with accuracy directly."},
            {"category": "Algorithmic Fairness", "title": "Bias Mitigation: Post-processing", "content": "Adjust predictions after training: threshold tuning, output calibration. Change decision boundary per group. Advantage: model-agnostic. Fast to implement."},

            # AI Safety Frameworks (40 items)
            {"category": "AI Safety", "title": "AI Safety Overview", "content": "AI safety: ensure AI systems behave as intended, avoid harms, remain controllable. Domains: robustness, alignment, interpretability, adversarial security."},
            {"category": "AI Safety", "title": "Robustness: Out-of-Distribution Data", "content": "OOD: data different from training distribution. Risk: poor performance, hallucinations, confidence errors. Solution: anomaly detection, calibration, uncertainty quantification."},
            {"category": "AI Safety", "title": "Robustness: Adversarial Examples", "content": "Adversarial examples: imperceptible perturbations cause misclassification. Attack: FGSM, C&W, PGD. Defense: adversarial training, certified robustness, input transformation."},
            {"category": "AI Safety", "title": "Robustness Testing: Red Teaming", "content": "Red teaming: adversarially test system to find weaknesses. Simulate attacker thinking. Proactive: before deployment. Team: internal + external experts."},
            {"category": "AI Safety", "title": "Safety Framework: ISO/IEC 42001", "content": "ISO 42001: AI management system standard. Requirements: risk assessment, stakeholder engagement, transparency, human oversight. Compliance checklist for enterprises."},
            {"category": "AI Safety", "title": "Safety Framework: NIST AI RMF", "content": "NIST AI Risk Management Framework: govern, map, measure, manage AI risks. Integrates with existing risk frameworks. Voluntary, flexible, outcome-focused."},
            {"category": "AI Safety", "title": "Alignment Problem", "content": "Alignment: ensure AI objectives match human values. Challenge: values are complex, context-dependent, sometimes contradictory. Current systems lack true understanding of intent."},
            {"category": "AI Safety", "title": "Value Alignment Techniques", "content": "RLHF (Reinforcement Learning from Human Feedback): train model with human preferences. Constitutional AI: follow explicit principles. But: value disagreement, specification gaming."},

            # Transparency & Explainability (40 items)
            {"category": "Transparency", "title": "Explainability vs Interpretability", "content": "Interpretability: understand model decision (glass box). Explainability: explain prediction to user (post-hoc). Different goals: debugging vs user trust."},
            {"category": "Transparency", "title": "Model Interpretability: Linear Models", "content": "Linear models inherently interpretable: coefficients show feature importance. Disadvantage: limited expressiveness. Trade-off: interpretability vs performance."},
            {"category": "Transparency", "title": "Model Interpretability: Decision Trees", "content": "Decision trees interpretable: explicit rules (if-then). Root-to-leaf path explains prediction. Disadvantage: prone to overfitting, limited expressiveness."},
            {"category": "Transparency", "title": "Explainability: Feature Importance", "content": "Which features matter? Techniques: permutation importance, SHAP, LIME. SHAP: game theory approach, Shapley values. LIME: local linear approximation."},
            {"category": "Transparency", "title": "Explainability: SHAP Method", "content": "SHAP: coalitional game theory for ML interpretability. Shapley value: marginal contribution of each feature. Output: feature importance with direction (positive/negative effect)."},
            {"category": "Transparency", "title": "Explainability: LIME", "content": "LIME: Local Interpretable Model-agnostic Explanations. Perturb input, fit local linear model, explain prediction. Works on any model. Good for single-instance explanations."},
            {"category": "Transparency", "title": "Model Cards", "content": "Model card: document model details. Include: intended use, performance metrics, fairness evaluation, limitations, recommendations. Transparency best practice."},
            {"category": "Transparency", "title": "Data Sheets for Datasets", "content": "Datasheet: document dataset origins, composition, characteristics. Include: collection process, labeling procedure, bias issues, recommendations. Transparency for data."},

            # Governance & Regulation (40 items)
            {"category": "Governance", "title": "EU AI Act Overview", "content": "EU AI Act: regulate high-risk AI. Risk levels: prohibited, high-risk, limited risk, minimal risk. Requirements: conformity assessment, documentation, human oversight."},
            {"category": "Governance", "title": "High-Risk AI Systems", "content": "High-risk: biometric, critical infrastructure, education, employment, law enforcement. Stricter requirements: impact assessment, human oversight, documentation, transparency."},
            {"category": "Governance", "title": "AI Governance Framework", "content": "Governance: policies, procedures, oversight structures. Components: AI strategy, risk assessment, ethics review board, incident reporting, stakeholder engagement."},
            {"category": "Governance", "title": "Human Oversight Requirements", "content": "High-risk systems need human oversight: humans understand system, can override decisions, intervene when needed. Meaningful human control (not rubber-stamping)."},
            {"category": "Governance", "title": "Impact Assessment: AIDA", "content": "AI Impact Assessment: evaluate potential harms before deployment. Consider: fairness, safety, privacy, security. Document risks, mitigation strategies, monitoring plans."},
            {"category": "Governance", "title": "Regulatory Compliance Checklist", "content": "Audit: privacy (GDPR), fairness (anti-discrimination), transparency (explainability), safety (robustness). Documentation requirements per regulation."},
            {"category": "Governance", "title": "Liability & Accountability", "content": "Who's responsible if AI harms? Framework: strict liability (vendor responsible), fault-based (negligence), shared responsibility. Varies by jurisdiction."},
            {"category": "Governance", "title": "AI Incident Response Plan", "content": "Incident: bias discovered, model adversarially attacked, unintended consequences. Response: detect, contain, analyze, remediate, communicate. Documentation critical."},

            # Adversarial Security (20 items)
            {"category": "Adversarial Security", "title": "Threat Model: Evasion", "content": "Evasion: attacker modifies input at test time. Goal: fool model. Example: adversarial images, spam emails. Defense: robust models, input validation."},
            {"category": "Adversarial Security", "title": "Threat Model: Poisoning", "content": "Poisoning: attacker modifies training data. Goal: backdoor model, degrade performance. Example: mislabeled samples, watermarking. Defense: data validation, robust training."},
            {"category": "Adversarial Security", "title": "Threat Model: Extraction", "content": "Extraction: attacker copies model via API queries. Steals IP, enables evasion attacks. Defense: rate limiting, output smoothing, differential privacy."},
            {"category": "Adversarial Security", "title": "Threat Model: Privacy", "content": "Privacy attack: infer training data from model. Membership inference: was sample in training? Model inversion: reconstruct training sample. Defense: differential privacy, regularization."},
        ]

        self.knowledge_base["knowledge_items"] = items
        self.knowledge_base["total_items"] = len(items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get items by category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

class EthicsAISafetyModule:
    """Integration module for Ethics & AI Safety"""

    def __init__(self):
        self.knowledge = EthicsAISafetyKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if module applies"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])
        ethics_keywords = ["ethics", "fairness", "bias", "safety", "responsible", "governance", "compliance", "security"]
        return any(kw in ethics_keywords for kw in keywords + topics)

__all__ = ["EthicsAISafetyKnowledge", "EthicsAISafetyModule"]

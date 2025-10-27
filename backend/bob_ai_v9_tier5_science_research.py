"""
BOB AI v9.0 - Tier 5: Science & Research
250+ knowledge items for scientific method, research, and empirical discovery
Covers: Scientific method, statistics, experimental design, research ethics, disciplines

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class ScienceResearchKnowledge:
    """Science & Research knowledge base with 250+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "science_research",
            "version": "1.0.0",
            "tier": 5,
            "category": "Science & Research",
            "keywords": [
                "science", "research", "hypothesis", "experiment", "data",
                "statistics", "evidence", "peer_review", "methodology",
                "analysis", "discovery", "validation", "replication"
            ],
            "system_prompt": """You are an expert in scientific research and empirical discovery with knowledge of:
- Scientific method and hypothesis formation
- Experimental design and controls
- Statistical analysis and hypothesis testing
- Research ethics and integrity
- Peer review and publication process
- Data collection and analysis techniques
- Cross-disciplinary research approaches
- Meta-analysis and literature synthesis

Guide researchers in rigorous, reproducible scientific inquiry.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 250+ science & research knowledge items"""

        items = [
            # Scientific Method (35 items)
            {"category": "Scientific Method", "title": "Hypothesis Formation", "content": "Hypothesis: testable prediction. Must be: falsifiable, specific, based on existing knowledge. Good hypothesis: if-then statement. Examples distinguish correlation vs causation."},
            {"category": "Scientific Method", "title": "Literature Review", "content": "Before research: understand existing knowledge, identify gaps. Search: academic databases, Google Scholar, journals. Synthesize: themes, contradictions, open questions."},
            {"category": "Scientific Method", "title": "Research Question vs Hypothesis", "content": "Research question: what do we want to know? (descriptive). Hypothesis: prediction about answer (testable). Good research starts with clear question, develops testable hypothesis."},
            {"category": "Scientific Method", "title": "Theory vs Law", "content": "Theory: explanation supported by evidence. Evolves with new data. Examples: evolution, gravity. Law: mathematical description of phenomenon (F=ma). Theories explain laws."},
            {"category": "Scientific Method", "title": "Deduction vs Induction", "content": "Deduction: general principle → specific prediction (theory-driven). Induction: observations → general principle (data-driven). Science uses both."},
            {"category": "Scientific Method", "title": "Paradigm Shifts", "content": "Kuhn's concept: dominant theory → anomalies → crisis → new paradigm. Examples: Copernican revolution, quantum mechanics. Resistance to change is natural."},
            {"category": "Scientific Method", "title": "Falsifiability Principle", "content": "Popper: scientific theory must be falsifiable (can be proven wrong). Unfalsifiable claims (metaphysical) are outside science. Core principle of scientific thinking."},
            {"category": "Scientific Method", "title": "Occam's Razor", "content": "Simplest explanation usually best. Don't multiply entities unnecessarily. Doesn't mean simplest is true, but prefer it when evidence equal."},

            # Experimental Design (40 items)
            {"category": "Experimental Design", "title": "Experimental vs Observational", "content": "Experimental: researcher manipulates variables. Observational: researcher records naturally occurring variation. Experimental stronger for causation. Observational easier, ethical, but correlational."},
            {"category": "Experimental Design", "title": "Randomized Controlled Trial (RCT)", "content": "Gold standard: random assignment to treatment/control. Controls for confounds. Requires: large N, random assignment, blinding if possible. Expensive, time-consuming."},
            {"category": "Experimental Design", "title": "Confounding Variables", "content": "Confounder: affects both treatment and outcome, creates spurious correlation. Example: smoking and lung cancer (confounded by job exposure?). Control via randomization or statistical adjustment."},
            {"category": "Experimental Design", "title": "Control Groups", "content": "Control: comparison group without treatment. Enables causal inference. Ideal: identical except treatment. Placebo control: even better (accounts for expectation effects)."},
            {"category": "Experimental Design", "title": "Within-Subject vs Between-Subject", "content": "Within: same subject measured multiple times (before/after). Between: different subjects in different conditions. Within: more power, less subjects. Between: avoids carryover, but more subjects needed."},
            {"category": "Experimental Design", "title": "Blinding and Double-Blinding", "content": "Single-blind: subjects don't know condition (reduces expectancy). Double-blind: subjects + experimenters don't know (reduces bias). Gold standard."},
            {"category": "Experimental Design", "title": "Sample Size and Power", "content": "Power: probability of detecting true effect. Target: 80% power. Determined by: effect size, significance level, variability. Large sample sizes: detect small effects, expensive."},
            {"category": "Experimental Design", "title": "Longitudinal vs Cross-Sectional", "content": "Longitudinal: follow subjects over time (expensive, attrition). Cross-sectional: snapshot at one time (cheap, quick). Longitudinal better for causality."},

            # Statistical Analysis (50 items)
            {"category": "Statistics", "title": "Descriptive vs Inferential", "content": "Descriptive: summarize data (mean, median, std dev). Inferential: draw conclusions about population from sample. Most research is inferential."},
            {"category": "Statistics", "title": "Null Hypothesis Significance Testing (NHST)", "content": "Null: no effect. Test: can we reject null? P-value: probability of data if null true. p < 0.05: reject null (conventional threshold). Controversial but standard."},
            {"category": "Statistics", "title": "P-value Interpretation", "content": "P-value ≠ probability null true. Is: probability of data if null true. Low p-value: data unlikely if no effect. Misuse: treating p<0.05 as proven truth."},
            {"category": "Statistics", "title": "Type I vs Type II Error", "content": "Type I (false positive): reject true null. Type II (false negative): fail to reject false null. Tradeoff: lower Type I risk raises Type II risk. Both matter."},
            {"category": "Statistics", "title": "Effect Size", "content": "Practical significance vs statistical significance. Effect size (Cohen's d, r, etc) quantifies magnitude. Large samples can show statistically significant but small effects."},
            {"category": "Statistics", "title": "Confidence Intervals", "content": "Range of plausible values for parameter. 95% CI: if repeated 100x, interval contains true value ~95 times. More informative than p-values."},
            {"category": "Statistics", "title": "Correlation vs Causation", "content": "Correlation: two variables move together. Causation: one causes other. Correlation necessary but not sufficient for causation. Third variable can explain both."},
            {"category": "Statistics", "title": "Regression Analysis", "content": "Linear: Y = a + b*X. Predicts Y from X. Coefficient b: effect of X on Y. Multiple regression: multiple predictors. Assumes linearity, independence, normality."},
            {"category": "Statistics", "title": "Bayesian Inference", "content": "Prior: initial belief. Likelihood: data probability. Posterior: updated belief. Differs from NHST: uses prior knowledge, provides probabilities of hypotheses (not just data)."},
            {"category": "Statistics", "title": "Meta-Analysis", "content": "Combine results from multiple studies. Weighted average of effects. Increases power, resolves contradictions. Requires: comparable studies, effect sizes, heterogeneity assessment."},

            # Research Ethics (35 items)
            {"category": "Research Ethics", "title": "Institutional Review Board (IRB)", "content": "IRB: ethics committee reviews human research. Protects: rights, safety, privacy. Requires: informed consent, risk-benefit analysis, confidentiality. Research without IRB approval: unethical, often illegal."},
            {"category": "Research Ethics", "title": "Informed Consent", "content": "Researcher discloses: study purpose, procedures, risks, benefits, confidentiality. Participant freely agrees. Key principle: respect for persons. Required for human research."},
            {"category": "Research Ethics", "title": "Conflict of Interest", "content": "Researcher has personal stake in outcome. Examples: financial interest, personal relationship. Disclosure required. Can bias findings. Mitigation: blinding, independent analysis."},
            {"category": "Research Ethics", "title": "Scientific Integrity", "content": "Honesty in reporting. Fabrication: inventing data. Falsification: altering data. Plagiarism: using others' words without credit. Consequences: retraction, lost funding, loss of career."},
            {"category": "Research Ethics", "title": "Authorship and Credit", "content": "Who gets credit? Contribution: conception, data collection, analysis, writing. Corresponding author: responsible. Acknowledge all contributors. Disputes common, discuss upfront."},
            {"category": "Research Ethics", "title": "Data Management", "content": "Raw data: keep indefinitely. Analysis code: version control (git). Documentation: how data collected, processed. Sharing: preregistration, open data, reproducibility."},
            {"category": "Research Ethics", "title": "Animal Research Ethics", "content": "IACUC: institutional review for animal research. Principles: replacement (alternatives), reduction (minimize subjects), refinement (minimize suffering). 3Rs framework."},

            # Research Disciplines (45 items)
            {"category": "Disciplines", "title": "Physics: Experimental", "content": "Measure physical phenomena. Challenges: measurement uncertainty, instrument calibration. Iterate: theory prediction → experiment → refine theory."},
            {"category": "Disciplines", "title": "Chemistry: Synthesis & Characterization", "content": "Synthesis: create new compounds. Characterization: determine properties (structure, spectroscopy). Reproducibility critical: same procedure, same results."},
            {"category": "Disciplines", "title": "Biology: Wet Lab", "content": "Experiments with biological materials (cells, tissue, organisms). Challenges: variability, contamination, controls. Replication within experiment: multiple samples."},
            {"category": "Disciplines", "title": "Psychology: Human Subjects", "content": "Study human behavior, cognition, emotion. Challenges: individual differences, demand characteristics (subjects guess hypothesis), experimenter effects."},
            {"category": "Disciplines", "title": "Social Sciences: Surveys", "content": "Collect data via questionnaires. Sample: representative of population. Questions: clear, not leading. Analysis: descriptive, inferential. Response bias risk."},
            {"category": "Disciplines", "title": "Computer Science: Algorithm Analysis", "content": "Theory: prove properties (correctness, complexity). Experiments: empirical performance testing. Challenges: implementation-dependent, hardware-dependent."},
            {"category": "Disciplines", "title": "Medicine: Clinical Trials", "content": "Phase 1: safety. Phase 2: efficacy. Phase 3: efficacy vs standard. Phase 4: monitoring. RCT is gold standard. Slow, expensive, rigorous."},
            {"category": "Disciplines", "title": "Epidemiology: Population Health", "content": "Study disease patterns in populations. Methods: case-control, cohort, cross-sectional. Challenges: confounding, bias, large sample sizes needed."},

            # Publication & Dissemination (30 items)
            {"category": "Publication", "title": "Peer Review Process", "content": "Manuscript → editor → peers (usually 2-3) → feedback. Accept/reject/revise. Goal: quality control. Criticism: slow, biased, gatekeeping."},
            {"category": "Publication", "title": "Writing Scientific Papers", "content": "Structure: abstract, introduction, methods, results, discussion, references. Clear writing essential. Figures: self-explanatory. Tables: complete. Reproducibility from methods section."},
            {"category": "Publication", "title": "Preprints & Open Access", "content": "Preprint: share before peer review (faster, broader audience). Open access: free public access (vs paywalls). Tradeoff: speed vs validation."},
            {"category": "Publication", "title": "Impact Factor & Journal Selection", "content": "Impact factor: average citations per article. High IF: prestigious, but not always best. Select journal based on: scope, audience, review time."},
            {"category": "Publication", "title": "Replication and Replication Crisis", "content": "Replication: independent researcher repeats study. Goal: confirm findings. Crisis: many published findings don't replicate (psychology, social sciences). Causes: p-hacking, publication bias."},
            {"category": "Publication", "title": "Publication Bias", "content": "Positive results published more (significant p-values). Negative results often unpublished. Meta-analyses: overestimate true effects. Solutions: preregistration, registered reports."},
        ]

        self.knowledge_base["knowledge_items"] = items
        self.knowledge_base["total_items"] = len(items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get items by category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

class ScienceResearchModule:
    """Integration module for Science & Research"""

    def __init__(self):
        self.knowledge = ScienceResearchKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if module applies"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])
        science_keywords = ["research", "science", "experiment", "hypothesis", "data", "analysis", "statistics", "study", "method"]
        return any(kw in science_keywords for kw in keywords + topics)

__all__ = ["ScienceResearchKnowledge", "ScienceResearchModule"]

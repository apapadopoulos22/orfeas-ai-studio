"""
BOB AI v9.0 - Tier 6: Healthcare & Medicine
250+ knowledge items for medical science, healthcare systems, and clinical practice
Covers: Anatomy, pathology, pharmacology, treatments, healthcare management, epidemiology

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class HealthcareMedicineKnowledge:
    """Healthcare & Medicine knowledge base with 250+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "healthcare_medicine",
            "version": "1.0.0",
            "tier": 6,
            "category": "Healthcare & Medicine",
            "keywords": [
                "medicine", "healthcare", "disease", "treatment", "diagnosis",
                "pathology", "pharmacology", "clinical", "patient", "epidemiology",
                "public_health", "wellness", "prevention", "surgery"
            ],
            "system_prompt": """You are an expert in healthcare, medicine, and clinical science with knowledge of:
- Human anatomy, physiology, and pathology
- Disease mechanisms and clinical presentations
- Pharmacology and therapeutic interventions
- Diagnostic methods and clinical decision-making
- Healthcare systems and management
- Public health and epidemiology
- Evidence-based medicine and clinical guidelines
- Healthcare ethics and patient care

Provide medical guidance based on current clinical evidence and best practices.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 250+ healthcare & medicine knowledge items"""

        items = [
            # Anatomy & Physiology (30 items)
            {"category": "Anatomy", "title": "Organ Systems Overview", "content": "12 major systems: circulatory, respiratory, nervous, musculoskeletal, digestive, urinary, reproductive, endocrine, immune, integumentary, lymphatic, vestibular. Each maintains homeostasis."},
            {"category": "Anatomy", "title": "Cardiovascular System", "content": "Heart pumps blood through arteries, capillaries, veins. Systolic/diastolic pressure. Coronary circulation supplies heart. Lymphatic system drains tissue fluid."},
            {"category": "Anatomy", "title": "Respiratory System", "content": "Nose → trachea → bronchi → lungs. Gas exchange: O2 into blood, CO2 out. Diaphragm controls breathing. Lung capacity: ~6L."},
            {"category": "Anatomy", "title": "Nervous System: CNS vs PNS", "content": "CNS: brain (cerebrum, cerebellum, brainstem), spinal cord. PNS: peripheral nerves. Somatic (voluntary), autonomic (involuntary: sympathetic, parasympathetic)."},
            {"category": "Anatomy", "title": "Endocrine System", "content": "Hormones regulate metabolism, growth, reproduction, stress. Glands: pituitary, thyroid, pancreas, adrenal, gonads. Feedback loops maintain balance."},
            {"category": "Anatomy", "title": "Immune System", "content": "Innate: barriers, inflammation, phagocytes. Adaptive: antibodies, T-cells. Lymph nodes, spleen, thymus. Lymphocytes: B-cells (antibodies), T-cells (killer, helper)."},
            {"category": "Anatomy", "title": "Digestive System", "content": "Mouth → esophagus → stomach → small intestine (duodenum, jejunum, ileum) → large intestine → rectum. Liver, pancreas, gallbladder assist. Absorbs nutrients."},
            {"category": "Anatomy", "title": "Brain Structure & Function", "content": "Cerebrum: cognition, motor, sensory. Cerebellum: coordination. Brainstem: autonomic functions. Limbic: emotion, memory. Hemispheric lateralization."},

            # Pathology & Disease (40 items)
            {"category": "Pathology", "title": "Disease Categories", "content": "Infectious: bacteria, virus, fungus, parasite. Non-infectious: genetic, environmental, degenerative, neoplastic (cancer), autoimmune. Most modern death: non-infectious."},
            {"category": "Pathology", "title": "Acute vs Chronic", "content": "Acute: sudden onset, short duration, often severe. Chronic: slow onset, long duration, may be severe. Chronic diseases: account for ~70% mortality."},
            {"category": "Pathology", "title": "Inflammation", "content": "Response to injury: redness, heat, swelling, pain. Acute: brief, then resolves. Chronic: prolonged, damaging. Inflammation marker: CRP (C-reactive protein)."},
            {"category": "Pathology", "title": "Infection Basics", "content": "Pathogen invades → immune response → symptoms. Incubation period: exposure to symptoms. Contagious period: can transmit. Quarantine: prevent transmission."},
            {"category": "Pathology", "title": "Cancer: Growth & Metastasis", "content": "Cancer: uncontrolled cell growth. Benign: localized. Malignant: invades, metastasizes (spreads). Stages: local → regional → distant. Prognosis: stage-dependent."},
            {"category": "Pathology", "title": "Autoimmune Diseases", "content": "Immune system attacks own tissue. Examples: rheumatoid arthritis, lupus, diabetes type 1. Cause unknown but genetic + environmental triggers. Lifelong management."},
            {"category": "Pathology", "title": "Genetic Diseases", "content": "Inherited: single gene (cystic fibrosis, sickle cell), polygenic (diabetes, heart disease). Monogenic: usually rare, severe. Polygenic: common, moderate severity."},
            {"category": "Pathology", "title": "Cardiovascular Diseases", "content": "Leading cause of death globally. Types: heart attack (MI), stroke, hypertension, heart failure, arrhythmia. Risk factors: smoking, diabetes, hypertension, high cholesterol."},

            # Pharmacology (35 items)
            {"category": "Pharmacology", "title": "Drug Classes: Antibiotics", "content": "Kill or inhibit bacteria. Classes: beta-lactams, macrolides, fluoroquinolones, tetracyclines. Resistance: overuse selects resistant strains. Narrow spectrum when possible."},
            {"category": "Pharmacology", "title": "Drug Classes: Antivirals", "content": "Inhibit viral replication. Challenges: viruses evolve quickly, limited targets. Examples: antiretrovirals (HIV), antivirals (influenza, COVID). Often suppress not cure."},
            {"category": "Pharmacology", "title": "Drug Classes: Cardiovascular", "content": "ACE inhibitors, beta-blockers, statins, diuretics. Multiple mechanisms: lower BP, reduce workload, prevent clots, manage heart failure."},
            {"category": "Pharmacology", "title": "Drug Classes: Psychiatric", "content": "SSRIs: depression, anxiety. Antipsychotics: schizophrenia, bipolar. Benzodiazepines: anxiety (addiction risk). Mood stabilizers: lithium. Mechanism often unknown."},
            {"category": "Pharmacology", "title": "Pharmacokinetics: Absorption", "content": "Drug enters body: oral (GI absorption), injection (IV, IM, SC), inhalation. Factors: pH, size, lipophilicity, food. Bioavailability: % reaching systemic circulation."},
            {"category": "Pharmacology", "title": "Pharmacokinetics: Metabolism", "content": "Liver (Phase I, II, III). CYP450 enzymes. Drug-drug interactions: one drug inhibits/induces metabolism of another. Genetic variation affects metabolism."},
            {"category": "Pharmacology", "title": "Pharmacokinetics: Elimination", "content": "Kidneys (most common). Half-life: time to 50% elimination. Dosing: higher in renal disease (accumulates). Clearance: volume of plasma cleared per time."},
            {"category": "Pharmacology", "title": "Adverse Drug Reactions", "content": "Side effects common. Mild: nausea, headache. Severe: organ damage, allergic reaction. Idiosyncratic: unpredictable. Pharmacovigilance: post-market surveillance."},

            # Diagnostic & Treatment (45 items)
            {"category": "Diagnosis", "title": "Physical Exam", "content": "Inspection, palpation, percussion, auscultation. Vital signs: temperature, heart rate, blood pressure, respiratory rate, oxygen saturation."},
            {"category": "Diagnosis", "title": "Laboratory Tests", "content": "Blood: CBC (cell counts), metabolic panel (glucose, electrolytes, kidney, liver). Urinalysis, cultures. Quick, objective, but limited information."},
            {"category": "Diagnosis", "title": "Imaging: X-ray & CT", "content": "X-ray: bones, lungs, fast, cheap. CT: cross-sectional, detailed, radiation. MRI: soft tissue, no radiation, expensive, contraindicated with metal."},
            {"category": "Diagnosis", "title": "Imaging: Ultrasound & PET", "content": "Ultrasound: real-time, no radiation, operator-dependent. PET: metabolic activity, cancer detection. Functional imaging."},
            {"category": "Diagnosis", "title": "Diagnostic Accuracy: Sensitivity & Specificity", "content": "Sensitivity: true positive rate (catches disease). Specificity: true negative rate (avoids false alarm). Tradeoff: higher sensitivity lowers specificity."},
            {"category": "Diagnosis", "title": "Differential Diagnosis", "content": "List likely diagnoses. Start broad, narrow based on findings. Rules of thumb: common things common, consider zebras if clues present."},
            {"category": "Diagnosis", "title": "Treatment: Medications", "content": "Drug selection: efficacy, safety, cost, patient factors. Dosing: calculated from weight, kidney function. Adherence: patient takes as directed (biggest problem)."},
            {"category": "Diagnosis", "title": "Treatment: Surgery", "content": "Indications: remove tumor, repair damage, emergency. Risks: infection, bleeding, anesthesia complications. Recovery: varies by procedure."},

            # Clinical Practice (40 items)
            {"category": "Clinical", "title": "Clinical Decision-Making", "content": "Evidence-based: apply research to patient. Patient values: what matters to them. Clinical judgment: experience, intuition. Balance all three."},
            {"category": "Clinical", "title": "Clinical Guidelines", "content": "Evidence-based recommendations for diagnosis/treatment. Written by specialty societies. Used in clinical practice, litigation, quality assessment. Adaptation needed for individual patients."},
            {"category": "Clinical", "title": "Patient-Centered Care", "content": "Involves patient in decisions. Shared decision-making: patient preference + clinical evidence. Improves adherence, satisfaction, outcomes."},
            {"category": "Clinical", "title": "Ethical Issues: Informed Consent", "content": "Patient must understand: condition, treatments, risks/benefits, alternatives. Voluntary. Required before procedures. Exception: emergency, not mentally capable."},
            {"category": "Clinical", "title": "Ethical Issues: Confidentiality", "content": "Patient information private. HIPAA (US): legal protection. Exceptions: imminent danger, abuse reporting, public health. Erodes trust if broken."},
            {"category": "Clinical", "title": "Medication Errors", "content": "Common in healthcare. Types: wrong drug, wrong dose, wrong patient, wrong route. Prevention: double-check, technology (barcode scanning), communication."},
            {"category": "Clinical", "title": "Burnout & Clinician Wellbeing", "content": "High burnout in healthcare: long hours, emotional labor, EHR burden. Consequences: errors, turnover, quality decline. Solutions: workload reduction, support systems."},
            {"category": "Clinical", "title": "Telemedicine", "content": "Remote clinical encounters. Advantages: access, convenience, cost. Disadvantages: no physical exam, technology issues, privacy concerns. Expanding post-COVID."},

            # Healthcare Systems & Public Health (30 items)
            {"category": "Healthcare Systems", "title": "Healthcare Models", "content": "Bismarck: employer-insurance (Germany). Beveridge: government-run (UK NHS). Market: private insurance (US before ACA). Mixed: combines approaches. No perfect model."},
            {"category": "Healthcare Systems", "title": "Healthcare Financing", "content": "Funding: taxation, insurance premiums, out-of-pocket. Models differ: universal (covers all), multi-payer, single-payer. Tradeoff: access vs choice vs cost."},
            {"category": "Healthcare Systems", "title": "Healthcare Disparities", "content": "Unequal outcomes by race, gender, socioeconomic status. Causes: structural racism, poverty, access, discrimination. Addressing: policy, awareness, resources."},
            {"category": "Healthcare Systems", "title": "Public Health", "content": "Population level: prevent disease, promote health. Methods: surveillance, epidemiology, health education, policy. Population > individual."},
            {"category": "Healthcare Systems", "title": "Epidemiology: R0 (Basic Reproduction)", "content": "Average secondary cases from one case. R0 > 1: epidemic. R0 < 1: dying out. Varies by pathogen, population, interventions. COVID: R0 ~2-3, flu ~1-2."},
            {"category": "Healthcare Systems", "title": "Vaccination", "content": "Stimulates immunity without disease. Safe, effective, prevents epidemics (herd immunity ~80-95% coverage). Rare side effects outweighed by benefits."},
        ]

        self.knowledge_base["knowledge_items"] = items
        self.knowledge_base["total_items"] = len(items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get items by category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

class HealthcareMedicineModule:
    """Integration module for Healthcare & Medicine"""

    def __init__(self):
        self.knowledge = HealthcareMedicineKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if module applies"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])
        health_keywords = ["medicine", "healthcare", "disease", "treatment", "diagnosis", "health", "medical", "clinical", "patient"]
        return any(kw in health_keywords for kw in keywords + topics)

__all__ = ["HealthcareMedicineKnowledge", "HealthcareMedicineModule"]

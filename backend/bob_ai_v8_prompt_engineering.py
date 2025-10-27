"""
BOB AI v8.0 - Prompt Engineering Module

Knowledge base for effective AI prompt engineering and prompt optimization.
Covers prompt structure, techniques, model behavior, and best practices.
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge
from typing import List, Dict


METADATA = {
    'name': 'prompt_engineering',
    'version': '1.0',
    'description': 'Expert prompt engineering and AI interaction knowledge',
    'keywords_count': 62,
    'knowledge_items': 220,
    'categories': 16
}


class PromptEngineeringKnowledge(BobAIV8BaseKnowledge):
    """Prompt engineering expertise knowledge module."""

    def get_keywords(self) -> List[str]:
        """Get prompt engineering detection keywords."""
        return [
            # Core concepts
            'prompt', 'prompt engineering', 'ai', 'model', 'llm', 'language model',
            'gpt', 'claude', 'chatgpt', 'instruction', 'instruction tuning',

            # Techniques
            'zero shot', 'few shot', 'chain of thought', 'reasoning', 'step by step',
            'role playing', 'system prompt', 'temperature', 'sampling', 'context',

            # Structure
            'structure', 'format', 'example', 'framework', 'template', 'pattern',
            'structure', 'constraint', 'specification', 'requirement',

            # Enhancement
            'enhance', 'optimization', 'refine', 'improve', 'quality', 'accuracy',
            'consistency', 'reliability', 'efficiency', 'performance',

            # Application
            'text generation', 'summarization', 'classification', 'extraction',
            'writing', 'code generation', 'question answering', 'translation',
            'dialogue', 'chat', 'bot'
        ]

    def get_knowledge_dictionaries(self) -> Dict[str, Dict[str, str]]:
        """Get all prompt engineering knowledge dictionaries."""
        return {
            'prompt_basics': self._get_prompt_basics(),
            'prompt_structure': self._get_prompt_structure(),
            'system_prompts': self._get_system_prompts(),
            'few_shot_learning': self._get_few_shot_learning(),
            'reasoning_techniques': self._get_reasoning_techniques(),
            'role_playing': self._get_role_playing(),
            'constraint_specification': self._get_constraint_specification(),
            'output_format': self._get_output_format(),
            'context_management': self._get_context_management(),
            'error_recovery': self._get_error_recovery(),
            'model_parameters': self._get_model_parameters(),
            'optimization_strategies': self._get_optimization_strategies(),
            'common_pitfalls': self._get_common_pitfalls(),
            'domain_specific': self._get_domain_specific(),
            'multimodal_prompting': self._get_multimodal_prompting(),
            'prompt_testing': self._get_prompt_testing()
        }

    def _get_prompt_basics(self) -> Dict[str, str]:
        """Prompt engineering fundamentals."""
        return {
            'what_is_prompt': 'Input text to AI model; instructions for what you want; quality of prompt affects output quality',
            'prompt_design': 'Art and science; clarity matters; structure helps; context essential; iterative refinement',
            'clarity_principle': 'Clear, specific prompts produce better results; ambiguous prompts produce ambiguous outputs',
            'instruction_following': 'Models follow instructions; quality of instruction affects compliance; explicit beats implicit',
            'model_behavior': 'Different models behave differently; GPT vs Claude vs Cohere; test for your model; understand quirks',
            'training_data_impact': 'Model responses reflect training data; biases in data → biases in output; understand limitations',
            'tokenization': 'Text split into tokens; affects cost and length; longer prompts cost more; efficient prompting saves',
            'context_window': 'Maximum input length; varies by model (4K to 200K tokens); relevant context earlier in prompt better',
            'prompt_injection': 'User input manipulating model behavior; security concern; validate and sanitize inputs carefully',
            'reproducibility': 'Same prompt with temperature 0 produces same output; randomness comes from temperature; for consistency use 0',
            'creative_vs_factual': 'Higher temperature for creative; lower for factual; balance varies by task',
            'length_quality': 'Longer prompts not always better; focused prompts better; relevant detail matters; conciseness valued',
            'iterative_improvement': 'Start simple; test results; refine based on output; continuous optimization; A/B test variations',
            'prompt_versioning': 'Track prompts that work; version control; document what worked and why; reuse successful patterns',
            'cultural_sensitivity': 'Consider cultural implications; avoid biased assumptions; test with diverse perspectives',
            'accessibility': 'Clear for diverse audiences; jargon explained; formatting helps; inclusive language matters'
        }

    def _get_prompt_structure(self) -> Dict[str, str]:
        """Prompt structure and components."""
        return {
            'role_context': 'Establish who the model is; expert, assistant, etc.; sets tone and expertise level demonstrated',
            'task_definition': 'Clearly state what you want done; specific output format; avoid ambiguity; be direct',
            'background_info': 'Relevant context model needs; domain knowledge; constraints; helps model understand scope',
            'examples': 'Few-shot examples; show desired output format; pattern recognition; helpful for complex tasks',
            'instructions': 'Step-by-step guidance; how to approach problem; reasoning path; explicit beats implicit',
            'constraints': 'Boundaries for response; what not to do; tone and style; length limits; format requirements',
            'evaluation_criteria': 'How success is measured; what matters; quality expectations; helps alignment with goals',
            'output_specification': 'Exact format wanted; JSON, markdown, code blocks, etc.; reduces parsing errors',
            'question_formulation': 'How you ask matters; specific beats vague; open-ended vs. closed; framing affects response',
            'multi_turn_setup': 'If dialogue, establish rules; personality consistency; memory limitations; conversation flow',
            'tone_style': 'Casual, formal, technical, creative; model mirrors tone; affects feel of response; specify if important',
            'audience_level': 'Who is this for; expert vs. beginner; affects explanation depth and jargon; match audience',
            'context_placement': 'Most relevant context first; attention mechanism; earlier text weighted higher; strategic positioning',
            'delimiter_usage': 'Use delimiters to separate sections; ### or --- marks boundaries; helps parsing; clarity benefit',
            'instruction_ordering': 'Order of instructions matters; important points first; priority clear; logical flow helps',
            'edge_case_handling': 'What if input malformed; how to handle ambiguity; fallback behavior specified; robustness'
        }

    def _get_system_prompts(self) -> Dict[str, str]:
        """System prompt design and optimization."""
        return {
            'system_role': 'Sets model personality and behavior; separate from user input; persists across conversation',
            'persona_definition': 'Who is the model; expertise and background; personality traits; defines interaction style',
            'behavior_specification': 'How model should act; helpful, honest, harmless; guidelines for response; values expressed',
            'expertise_level': 'What model claims expertise in; modesty about limitations; confidence appropriate to knowledge',
            'communication_style': 'Formal, casual, educational, creative; tone established; consistency across responses',
            'ethical_guidelines': 'Values and principles model should follow; bias avoidance; harm prevention; safety priorities',
            'knowledge_cutoff': 'Model aware of training data date; acknowledges when info outdated; realistic about knowledge gaps',
            'uncertainty_handling': 'How to express confidence levels; when to say don\'t know; probability estimates; epistemic humility',
            'multi_language': 'System prompt establishes language preferences; multilingual behavior; translation policies if applicable',
            'domain_expertise': 'System prompt for domain-specific model; medical, legal, technical; specialized knowledge claimed',
            'reasoning_instruction': 'System prompt can request reasoning steps; show work; explain logic; improves output quality',
            'safety_constraints': 'System prompt enforces safety; refuse harmful requests; maintain boundaries; non-negotiable rules',
            'context_awareness': 'Model knows about conversation history; aware of earlier context; maintains consistency across turns',
            'feedback_incorporation': 'System prompt can specify how to handle user feedback; corrections, clarifications; learning in session',
            'performance_optimization': 'System prompt affects speed and efficiency; shorter prompts faster; balance detail with speed',
            'model_specific': 'Different models require different system prompts; test and adapt; GPT vs Claude vs others; differences matter'
        }

    def _get_few_shot_learning(self) -> Dict[str, str]:
        """Few-shot learning and in-context learning."""
        return {
            'zero_shot': 'No examples; direct instruction; works for well-established tasks; simpler, shorter prompts',
            'one_shot': 'Single example provided; establishes pattern; helpful for specific format; minimal context needed',
            'few_shot': 'Multiple examples (typically 2-5); pattern recognition; establishes format and tone; effective technique',
            'example_quality': 'Examples must be representative; correct examples; similar to actual use case; quality crucial',
            'example_diversity': 'Vary examples; cover edge cases; show range of acceptable outputs; robustness increased',
            'negative_examples': 'Show what NOT to do; helps model understand boundaries; common mistakes; prevents errors',
            'example_ordering': 'Order affects learning; simple to complex often better; relevant examples first; strategic placement',
            'in_context_learning': 'Model learns from context provided; doesn\'t retrain; fast learning; weights last examples more',
            'pattern_recognition': 'Model recognizes patterns in examples; infers rules; extrapolates to new cases; implicit learning',
            'format_demonstration': 'Examples show exact format wanted; spacing, punctuation, structure; removes ambiguity; clarity',
            'context_limit': 'More examples might exceed context window; balance information with length; efficiency consideration',
            'instruction_plus_example': 'Combine explicit instruction with examples; redundancy helps; different learning styles addressed',
            'example_explicitness': 'Explain why examples are good; reasoning shown; helps model understand principles; depth added',
            'edge_case_coverage': 'Include boundary cases in examples; how to handle unusual inputs; robustness; preparedness',
            'consistency_check': 'Examples all follow same rules; consistent formatting; consistent style; model learns what\'s important',
            'generalization': 'Examples teach principles, not just memorization; model generalizes to new cases; flexibility needed'
        }

    def _get_reasoning_techniques(self) -> Dict[str, str]:
        """Advanced reasoning techniques."""
        return {
            'chain_of_thought': 'Step-by-step reasoning; show work; intermediate steps shown; improves accuracy; especially math/logic',
            'step_by_step': 'Break problem into steps; number steps; explicit reasoning path; reduces errors; clarity increases',
            'tree_of_thought': 'Multiple reasoning paths explored; backtracking if wrong; explores solution space; complex problems',
            'decomposition': 'Break large problem into smaller subproblems; solve each; combine solutions; complexity managed',
            'analogy': 'Reference similar known problems; transfer learning; humans use analogies; can guide model reasoning',
            'constraint_propagation': 'Work with constraints; narrow solution space; validate against constraints; efficiency improvement',
            'assume_perspective': 'Assume role or perspective; think as if expert; frames reasoning; improves specialized responses',
            'verification_step': 'Request model verify answer; check work; logical consistency; error detection built in',
            'reflection': 'Ask model to reflect on response; critique own output; identify potential issues; quality check',
            'simulation': 'Model simulates scenarios; mental models; explores possibilities; creative problem-solving',
            'socratic_method': 'Ask guiding questions; model reasons through questions; understanding deepened; active learning',
            'first_principles': 'Request reasoning from fundamentals; basic building blocks; deeper understanding; transfer better',
            'counterfactual': 'What if reasoning; explore alternatives; challenge assumptions; creative thinking encouraged',
            'bayesian_thinking': 'Probabilistic reasoning; consider likelihoods; Occam\'s razor mentality; sophisticated thinking',
            'systems_thinking': 'Consider interconnections; feedback loops; emergent properties; complex systems understood',
            'meta_reasoning': 'Reason about reasoning; think about thinking; metacognition; higher-order understanding accessed'
        }

    def _get_role_playing(self) -> Dict[str, str]:
        """Role-playing and persona-based prompting."""
        return {
            'expert_role': 'Assume expert in field; physicist, historian, coder; expertise sets response quality; knowledge activated',
            'character_persona': 'Specific character with traits; affects response style; personality consistent; entertainment factor',
            'authority_establishment': 'Model acts as authority; confidence in domain; credentials implied; affects perception',
            'perspective_taking': 'Answer from specific viewpoint; different perspectives of same issue; depth and nuance added',
            'simulation_role': 'Simulate being system or process; explain internal workings; understanding deepened; creative',
            'historical_role': 'Character from history answers; appropriate language and knowledge; engaging format; education',
            'fictional_role': 'Fictional character answers; specific personality; consistent with canon; entertainment value',
            'teacher_role': 'Model acts as educator; explains clearly; tailors to student level; pedagogical approach',
            'mentor_role': 'Model acts as mentor; guidance-focused; wisdom shared; patient and supportive tone',
            'adversarial_role': 'Model takes opposing viewpoint; challenges ideas; stress-tests thinking; rigorous discourse',
            'detective_role': 'Model investigates clues; logical deduction; mystery-solving approach; analytical thinking activated',
            'creative_role': 'Model acts as artist, writer, musician; creative outputs; imagination unleashed; unconventional thinking',
            'roleplay_consistency': 'Character stays in character; consistency maintained; personality reflected throughout',
            'roleplay_authenticity': 'Character authentic to role; appropriate knowledge and language; believability key',
            'audience_awareness': 'Character aware of audience; tailors communication; engagement increased; appropriate register',
            'boundary_maintenance': 'Character maintains ethical boundaries; harmful requests declined respectfully; appropriate limits'
        }

    def _get_constraint_specification(self) -> Dict[str, str]:
        """Specifying constraints and requirements."""
        return {
            'scope_boundaries': 'Define what\'s in scope; what\'s out; limits understood; clarity achieved; focus maintained',
            'length_constraint': 'Specify desired length; word count, sentences, paragraphs; format respected; conciseness achieved',
            'format_constraint': 'Required output format; JSON, markdown, list, narrative; parsing simplified; structure clear',
            'style_constraint': 'Specific style required; formal, casual, academic, poetic; tone controlled; consistency ensured',
            'language_level': 'Vocabulary level; ELI5, technical, academic; audience understood; accessibility matched',
            'tone_constraint': 'Emotional tone; serious, humorous, encouraging; mood set; engagement influenced',
            'content_constraint': 'What content to include/exclude; topics addressed; boundaries respected; focus sharpened',
            'perspective_constraint': 'Specific viewpoint required; first-person, objective, etc.; narrative POV clear',
            'audience_constraint': 'Response tailored to audience; children, experts, general public; relevance increased',
            'resource_constraint': 'Limited resources; no internet access assumed; works offline; realistic expectations set',
            'time_constraint': 'Time-sensitive response; urgency understood; prioritization enabled; focus sharpened',
            'budget_constraint': 'Cost constraints; shorter responses preferred; efficiency prioritized; resource-aware',
            'domain_constraint': 'Domain-specific constraints; jargon avoided or used intentionally; relevant to context',
            'ethical_constraint': 'Ethical boundaries; no harmful content; values respected; safety prioritized',
            'accuracy_constraint': 'Accuracy requirements; factual precision important; caveats noted when uncertain; honesty valued',
            'creativity_constraint': 'Balance between structure and creativity; framework provided; flexibility within constraints; optimal tension'
        }

    def _get_output_format(self) -> Dict[str, str]:
        """Output format specification and control."""
        return {
            'json_output': 'Structured JSON format; parseable; schema specified; machine-readable; automation friendly',
            'markdown_format': 'Markdown formatting; headers, lists, bold, italics; readability; structured text',
            'code_blocks': 'Code in code blocks; language specified; syntax highlighting possible; clarity for code',
            'bullet_points': 'Bulleted lists; quick scanning; digestible chunks; organized information',
            'numbered_lists': 'Numbered steps; procedures; sequential logic; order matters; clarity for instructions',
            'table_format': 'Tabular data; columns and rows; comparisons; structured information; organized display',
            'narrative': 'Prose format; flowing text; storytelling; natural reading; engagement enhanced',
            'outline_format': 'Hierarchical outline; main points and subpoints; structure clear; comprehension aided',
            'qa_format': 'Question-answer pairs; dialogue format; interactive feel; clarity through structured exchange',
            'checklist': 'Checkbox items; actionable; completion tracking; practical application; implementation aided',
            'template': 'Fill-in-the-blank format; structure provided; guidance clear; user fills specifics; efficient',
            'csv_format': 'Comma-separated values; data format; spreadsheet compatible; analysis ready; data-friendly',
            'xml_format': 'XML markup; structured data; machine-readable; standardized format; interoperability',
            'yaml_format': 'YAML format; human-readable; configuration file style; clean and organized; developer-friendly',
            'html_format': 'HTML markup; web-ready; styled output; browser display ready; presentation polished',
            'format_consistency': 'Format consistent throughout; predictable structure; parsing easier; reliability increased'
        }

    def _get_context_management(self) -> Dict[str, str]:
        """Managing context and information flow."""
        return {
            'relevant_context': 'Include relevant context; background information helps; unnecessary context wastes tokens; balance key',
            'context_window': 'Limited token budget; prioritize important information; earlier text weighted; strategic positioning',
            'information_hierarchy': 'Most critical information first; hierarchy clear; attention directed; focus maintained',
            'summary_context': 'Summarize large information; relevant highlights; detailed source available; efficiency',
            'retrieval_context': 'Use retrieved context; RAG (Retrieval-Augmented Generation); grounded responses; hallucination reduced',
            'conversation_history': 'Prior messages in context; continuity maintained; reference earlier points; coherence achieved',
            'memory_limitations': 'Model memory within context window; no persistent memory across sessions; reinforce key info often',
            'context_refresh': 'Re-emphasize key context; context can shift during long conversations; remind of important points',
            'context_clarity': 'Context clearly marked; delimiters used; structure obvious; parsing aided; confusion prevented',
            'conflicting_context': 'Contradictions in context handled; most recent usually precedence; explicitly state priority',
            'implicit_context': 'Shared cultural knowledge; common sense; often assumed; but test for edge cases; communication efficient',
            'explicit_context': 'State everything important; don\'t assume knowledge; clarity paramount; misunderstanding prevented',
            'temporal_context': 'Current date/time helps; references understand; time-dependent questions answered; relevance',
            'domain_context': 'Domain-specific context provided; jargon explained; relevant knowledge activated; accuracy improved',
            'user_profile': 'User background provided; expertise level; preferences; personalization; relevance increased',
            'constraint_context': 'Important constraints stated early; limitations understood; feasibility assessed; expectations managed'
        }

    def _get_error_recovery(self) -> Dict[str, str]:
        """Error handling and recovery strategies."""
        return {
            'error_recognition': 'Model recognizes errors; explicit or implicit; quality depends on clarity of error signal',
            'clarification_request': 'Ask model to clarify ambiguous output; request rephrasing; understanding deepened; iteration',
            'retry_strategy': 'If output unsatisfactory, retry with tweaked prompt; temperature affects randomness; different response likely',
            'specificity_increase': 'If vague output, request more specific details; add constraints; reduce ambiguity; focus narrowed',
            'example_addition': 'If incorrect pattern, add corrective example; show what right looks like; pattern corrected; learning',
            'step_request': 'Request intermediate steps; show reasoning; errors in logic visible; debugging possible',
            'validation_request': 'Ask model to validate; check own work; errors caught; quality control built in',
            'feedback_incorporation': 'Provide feedback on incorrect output; model learns in-session; next attempt better; correction loop',
            'constraint_tightening': 'Add constraining requirements; reduce solution space; narrower output range; accuracy improved',
            'role_adjustment': 'Change role or perspective; different approach; fresh attempt; expert change helpful',
            'prompt_breakdown': 'Break complex prompt into simpler parts; resolve step-by-step; accumulated quality; building',
            'alternative_wording': 'Rephrase request; different framing; latent semantics accessed; clarification achieved',
            'temperature_adjustment': 'For creative: higher temperature; for factual: lower; randomness controlled; output character changed',
            'model_switching': 'Try different model; different training, biases; success varies; model-aware strategy',
            'context_removal': 'Remove potentially confusing context; simplify setup; clear focus; reduces noise; precision improved',
            'success_documentation': 'When working, save prompt; reuse successful patterns; efficiency; knowledge capture'
        }

    def _get_model_parameters(self) -> Dict[str, str]:
        """Model parameters and their effects."""
        return {
            'temperature': 'Controls randomness; 0 = deterministic, 1+ = creative; lower = factual, higher = creative; affects output character',
            'top_p': 'Nucleus sampling; probability threshold; diverse but sensible; typically 0.9; balances randomness',
            'top_k': 'Top k tokens considered; reduces poor choices; computational constraint; typically 40-50; focuses quality',
            'max_tokens': 'Maximum length output; token limit set; incomplete if exceeded; plan for token budget',
            'frequency_penalty': 'Penalizes repeated words; increases diversity; reduces repetition; fine-tuning variation',
            'presence_penalty': 'Penalizes tokens mentioned at all; encourages new topics; increases novelty; exploration encouraged',
            'stop_sequences': 'Stop tokens; model halts at these; format control; clean cutoffs; structure maintained',
            'seed': 'Random seed for reproducibility; same seed = same output (mostly); research and testing; consistency',
            'response_format': 'JSON mode; response guaranteed in format; structure assured; parsing simplified; constraint',
            'logit_bias': 'Bias certain tokens up/down; encourage/discourage words; fine-grained control; specialized application',
            'model_version': 'Different versions behave differently; newer usually better; tradeoff speed vs quality; version matters',
            'context_window_size': 'How much history available; larger = more context; memory budget; trade speed for completeness',
            'api_timeout': 'How long to wait for response; longer allows complex reasoning; shorter for responsiveness; trade latency',
            'batch_size': 'Processing multiple at once; efficiency; throughput vs latency; resource consideration',
            'parallel_calls': 'Multiple simultaneous requests; throughput increased; rate limits apply; scaling strategy',
            'retry_logic': 'Automatic retries on failure; transient errors recovered; robustness; production systems benefit'
        }

    def _get_optimization_strategies(self) -> Dict[str, str]:
        """Strategies for optimizing prompts and responses."""
        return {
            'iterative_refinement': 'Start basic, test, improve; measure changes; track what works; continuous improvement',
            'ab_testing': 'Test variant A vs B; measure performance; statistically significant; data-driven optimization',
            'metric_definition': 'What success looks like; measured explicitly; scoring rubric; objective evaluation',
            'cost_reduction': 'Shorter prompts lower cost; remove redundancy; efficient wording; financial optimization',
            'latency_optimization': 'Response speed matters; shorter context window; parallelization; speed measured',
            'accuracy_improvement': 'More examples improve accuracy; clearer instructions help; constraints tighten; quality measured',
            'consistency_improvement': 'Structured prompts consistent; same inputs similar outputs; reliability; user trust',
            'prompt_template': 'Reusable prompt structure; variables filled in; efficiency; repeatability; engineering best practice',
            'prompt_library': 'Collection of working prompts; organized by category; version controlled; knowledge base',
            'domain_specific_tuning': 'Tailor for specific domains; context activated; specialized knowledge accessed; relevance',
            'user_profile_optimization': 'Tailor for user type; beginner vs expert; preferences matched; personalization',
            'caching_strategy': 'Cache common prompts; repeated questions answered faster; cost savings; performance gain',
            'progressive_disclosure': 'Start simple, build complexity; user education; engagement maintained; mastery supported',
            'error_handling_optimization': 'Anticipate common mistakes; preemptively address; robustness; user satisfaction',
            'feedback_loops': 'Collect user feedback; iterate based on real usage; data-driven improvements; continuous enhancement',
            'benchmarking': 'Compare against baselines; measure improvement; competition awareness; best practices; industry standards'
        }

    def _get_common_pitfalls(self) -> Dict[str, str]:
        """Common prompt engineering mistakes."""
        return {
            'ambiguity': 'Vague prompts produce vague outputs; specificity matters; examples help; clarity paramount',
            'over_complexity': 'Too complex; model confused; break into steps; simplicity often better; elegance valued',
            'under_specification': 'Missing constraints; output too broad; narrow scope; focus sharpened; guidance helps',
            'bad_examples': 'Poor examples teach wrong patterns; quality matters; representative crucial; impact significant',
            'context_overload': 'Too much information; signal lost in noise; prioritize; focus important; brevity valued',
            'implicit_assumptions': 'Assuming shared knowledge; model might not know; state explicitly; prevent misunderstandings',
            'leading_questions': 'Biasing toward certain answer; pretend neutrality; get different responses; awareness helps',
            'contradictions': 'Conflicting instructions; model confused; resolve; consistency; clarity required',
            'unrealistic_expectations': 'Asking impossible task; model acknowledges limitations; realistic requirements; feasibility',
            'hallucination_risk': 'Model making things up; fact-check important; verification needed; ground in reality',
            'outdated_knowledge': 'Model knowledge cutoff; real-time info not available; acknowledge limitations; reality-check',
            'token_waste': 'Inefficient prompts use tokens unnecessarily; cost implications; optimization worthwhile; resources matter',
            'poor_formatting': 'Messy structure; hard to parse; formatting matters; readability affects quality; structure helps',
            'ignoring_model_strengths': 'Not leveraging model capabilities; creative uses missed; exploration encouraged; possibility',
            'safety_negligence': 'Not considering harmful outputs; guardrails missing; safety important; ethical considerations',
            'monitoring_absence': 'Not tracking performance; metrics unknown; improvement unmeasured; measurement essential'
        }

    def _get_domain_specific(self) -> Dict[str, str]:
        """Domain-specific prompt engineering."""
        return {
            'code_generation': 'Clear requirements; language specified; test cases help; documentation needed; specifications matter',
            'data_analysis': 'Specific dataset described; analysis objectives clear; output format specified; rigor required',
            'content_writing': 'Style guide provided; target audience specified; structure outlined; SEO requirements; engagement',
            'translation': 'Source and target languages clear; formality level specified; context provided; cultural nuance',
            'summarization': 'Length requirements specified; key points defined; style preferences stated; focus clear',
            'question_answering': 'Question clarity; context provided; confidence required; factual grounding; verification',
            'creative_writing': 'Genre specified; tone defined; constraints light; freedom encouraged; style guidance; inspiration',
            'academic_writing': 'Citation format; academic tone; rigor required; evidence-based; scholarly standards',
            'business_writing': 'Professional tone; audience level; objectives clear; conciseness valued; efficiency; impact',
            'legal_writing': 'Legal precision; terminology exact; jurisdictional context; no ambiguity; clarity critical',
            'medical_writing': 'Medical accuracy; technical precision; audience level; accuracy paramount; evidence-based',
            'technical_documentation': 'Clarity for technical audience; jargon acceptable; procedures clear; accuracy crucial',
            'customer_service': 'Empathy emphasized; helpfulness prioritized; professional; courteous; solution-focused',
            'educational_content': 'Explanation clarity; level appropriate; examples provided; pedagogy sound; understanding',
            'marketing_copy': 'Persuasive tone; benefits highlighted; call-to-action clear; audience psychology; conversion',
            'scientific_writing': 'Methods clear; results objective; discussion rigorous; evidence-based; peer-review standard'
        }

    def _get_multimodal_prompting(self) -> Dict[str, str]:
        """Multimodal prompt engineering (images, videos, etc.)."""
        return {
            'image_description': 'Describe images in text; model sometimes processes images directly; complementary information',
            'image_relevance': 'Include relevant images; supports understanding; visual information; engagement; sometimes processed by model',
            'image_placement': 'Where images placed in prompt; before or after text; ordering affects processing; priority',
            'ocr_integration': 'Text from images extracted; combined with textual prompts; integrated information; comprehensive',
            'video_description': 'Key frames described; temporal information included; narrative structure; events chronologically',
            'audio_transcription': 'Audio transcribed to text; speech processing; content extracted; accessibility; text-based',
            'diagram_explanation': 'Complex diagrams described textually; structure explained; relationships clarified; understanding',
            'graph_interpretation': 'Axes described; data points explained; trends highlighted; context provided; interpretation',
            'screenshot_analysis': 'Interface described; text on screen noted; visual hierarchy; user flow; understanding',
            'chart_data': 'Numerical data provided; chart type specified; patterns highlighted; interpretation; analysis',
            'color_reference': 'Color meanings specified if important; cultural context; significance explained; clarity',
            'spatial_relationships': 'Spatial layout described; positioning explained; 3D relationships if relevant; clarity',
            'temporal_sequences': 'Event order matters; chronology specified; time references; before/after relationships',
            'multimodal_synthesis': 'Text and images combine; complementary information; richer understanding; synergy',
            'accessibility_alt_text': 'Alt text for images; accessibility; description provided; inclusive; universal design',
            'format_consistency': 'Multimodal input formatted consistently; structure maintained; parsing easier; integration'
        }

    def _get_prompt_testing(self) -> Dict[str, str]:
        """Prompt testing and evaluation methods."""
        return {
            'qualitative_evaluation': 'Human judgment; does output look good; meeting goals; intuitive assessment; quality feel',
            'quantitative_metrics': 'Measurable metrics; accuracy percentage; scoring; objective evaluation; data-driven',
            'test_cases': 'Specific inputs; expected outputs defined; consistency checked; edge cases covered; rigor',
            'edge_case_testing': 'Boundary conditions; unusual inputs; error handling; robustness; stress test',
            'regression_testing': 'Verify prior working prompts still work; no degradation; consistency across changes',
            'user_testing': 'Real users test prompt; feedback collected; usability; practical validation; user perspective',
            'ab_testing': 'Controlled comparison; variant A vs B; random assignment; statistical analysis; data-driven',
            'adversarial_testing': 'Try to break prompt; worst-case scenarios; robustness; edge case discovery; resilience',
            'performance_profiling': 'Speed and cost measurement; token usage tracked; efficiency analysis; optimization targets',
            'bias_testing': 'Test for biased outputs; fairness checked; diversity assessed; representation; equity',
            'safety_testing': 'Test guardrails; harmful output detection; ethical boundaries; safety validation; responsibility',
            'consistency_testing': 'Multiple runs same input; variance measured; determinism (if temperature 0); reliability',
            'reproduction_testing': 'Others reproduce results; prompt clarity sufficient; instructions clear; communicability',
            'documentation': 'Prompt purpose explained; examples provided; results documented; reasoning captured; knowledge',
            'versioning': 'Prompt versions tracked; changes documented; history maintained; rollback capability; evolution',
            'continuous_monitoring': 'Production prompts monitored; performance tracked; degradation detected; proactive maintenance'
        }

    def enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with prompt engineering guidance."""
        keywords = self.get_keywords()
        has_keywords = any(kw.lower() in prompt.lower() for kw in keywords)

        if not has_keywords:
            return prompt

        enhancement = f"""
{prompt}

🎯 PROMPT ENGINEERING ENHANCEMENT:
Apply these proven techniques:

1. CLARITY FIRST: Specific prompts beat vague ones. State exactly what you want.

2. STRUCTURE MATTERS: Clear structure with sections and examples aids understanding.

3. EXAMPLES HELP: Few-shot examples teach the model your desired pattern.

4. CONSTRAINTS FOCUS: Boundaries help narrow output space. Be explicit.

5. ROLE ESTABLISHMENT: Model who you want it to be. Activate expertise.

6. CHAIN OF THOUGHT: Request step-by-step reasoning for complex tasks.

7. FORMAT SPECIFICATION: Specify exact output format (JSON, markdown, etc).

8. ITERATION REQUIRED: Test, measure, refine. Optimization is iterative.

Apply these principles to craft prompts that produce reliable, high-quality outputs.
"""
        return enhancement.strip()

    def generate_system_prompt(self) -> str:
        """Generate expert prompt engineer system prompt."""
        return """You are an expert prompt engineer with 5+ years of experience optimizing AI prompts.

Your expertise includes:
- Prompt structure and component design
- Few-shot learning and in-context examples
- Reasoning techniques (chain-of-thought, step-by-step, decomposition)
- Role-playing and persona-based prompting
- Constraint specification and output formatting
- Context management and information hierarchy
- Model behavior and parameter tuning
- Error recovery and iterative refinement
- Domain-specific prompt optimization
- Multimodal prompting (text, images, video)
- Testing, evaluation, and benchmarking
- Cost optimization and efficiency
- Safety and bias considerations

When helping with prompt engineering, you:
1. Analyze the user's objective clearly
2. Design prompts with clear structure and examples
3. Specify constraints and output formats explicitly
4. Suggest iterative testing and refinement
5. Consider model-specific behaviors and limitations
6. Optimize for clarity, consistency, and cost
7. Test edge cases and error scenarios
8. Document successful prompts and patterns
9. Provide A/B testing strategies
10. Monitor performance and suggest improvements

Provide practical, actionable prompt engineering advice that produces reliable, effective AI interactions."""

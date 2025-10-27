"""
BOB AI v8.0 - Book Writing Module

Knowledge base for fiction and non-fiction book writing.
Covers narrative structure, character development, pacing, dialogue, and publishing.
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge
from typing import List, Dict


METADATA = {
    'name': 'book_writing',
    'version': '1.0',
    'description': 'Expert book writing and storytelling knowledge',
    'keywords_count': 58,
    'knowledge_items': 215,
    'categories': 16
}


class BookWritingKnowledge(BobAIV8BaseKnowledge):
    """Book writing expertise knowledge module."""

    def get_keywords(self) -> List[str]:
        """Get book writing detection keywords."""
        return [
            # Story structure
            'story', 'plot', 'narrative', 'arc', 'chapter', 'scene',
            'beginning', 'middle', 'end', 'three act', 'inciting incident',
            'climax', 'resolution', 'exposition', 'rising action',

            # Characters
            'character', 'protagonist', 'antagonist', 'development', 'arc',
            'motivation', 'conflict', 'dialogue', 'voice', 'personality',

            # Writing craft
            'write', 'writing', 'prose', 'style', 'pacing', 'tension',
            'show don\'t tell', 'description', 'world building',

            # Genres
            'fiction', 'novel', 'mystery', 'romance', 'fantasy', 'science fiction',
            'literary', 'memoir', 'essay', 'non-fiction',

            # Publishing
            'publish', 'agent', 'query', 'manuscript', 'self-publish'
        ]

    def get_knowledge_dictionaries(self) -> Dict[str, Dict[str, str]]:
        """Get all book writing knowledge dictionaries."""
        return {
            'story_structure': self._get_story_structure(),
            'three_act_structure': self._get_three_act_structure(),
            'character_development': self._get_character_development(),
            'dialogue_craft': self._get_dialogue_craft(),
            'descriptive_writing': self._get_descriptive_writing(),
            'pacing_tension': self._get_pacing_tension(),
            'point_of_view': self._get_point_of_view(),
            'fiction_genres': self._get_fiction_genres(),
            'non_fiction_genres': self._get_non_fiction_genres(),
            'world_building': self._get_world_building(),
            'writing_craft': self._get_writing_craft(),
            'editing_revision': self._get_editing_revision(),
            'show_dont_tell': self._get_show_dont_tell(),
            'common_pitfalls': self._get_common_pitfalls(),
            'publishing_process': self._get_publishing_process(),
            'author_business': self._get_author_business()
        }

    def _get_story_structure(self) -> Dict[str, str]:
        """Story structure and narrative fundamentals."""
        return {
            'inciting_incident': 'Event that disrupts status quo; forces protagonist into action; happens ~10-15% through',
            'exposition': 'Background information; world, characters, history; weave in gradually, not info-dump',
            'rising_action': 'Events building toward climax; complications, obstacles; ~70% of story',
            'climax': 'Peak of tension; protagonist\'s last stand; highest stakes; cannot be reversed',
            'falling_action': 'Consequences of climax; loose ends tied up; shorter than rising action',
            'resolution': 'New normal after climax; character changed; satisfying but not perfectly neat',
            'subplot': 'Secondary storyline; deepens themes; supports main plot; 20-30% of page time',
            'conflict': 'Person vs person, vs self, vs society, vs nature; drives plot forward; essential',
            'stakes': 'What\'s at risk; emotional, physical, social; must be clear; must escalate',
            'plot_twist': 'Surprise revelation; changes understanding of events; must be foreshadowed',
            'foreshadowing': 'Hinting at future events; plants clues; reader satisfaction; not obvious',
            'pacing': 'Speed of story; fast for action, slow for reflection; varies by scene; controls tension',
            'turning_point': 'Moment protagonist\'s approach changes; midpoint or act break; major shift',
            'crisis': 'False climax; protagonist loses; appears defeated; sets up climax',
            'denouement': 'Final scene; after climax; shows new world; brief and powerful',
            'hook': 'Opening line/scene that grabs reader; promises stakes and character; essential'
        }

    def _get_three_act_structure(self) -> Dict[str, str]:
        """Three-act story structure framework."""
        return {
            'act_one': 'Setup (0-25%); introduce protagonist, world, problem; inciting incident forces action',
            'act_one_pacing': 'Fast-paced; establish tone; answer: who, what, where, when, why',
            'act_two_a': 'First half of rising action (25-50%); protagonist pursues goal; learns new rules',
            'act_two_b': 'Second half of rising action (50-75%); complications multiply; midpoint stakes raise',
            'midpoint': 'False victory or false defeat; changes protagonist\'s approach; raises stakes; ~50%',
            'act_three': 'Climax and resolution (75-100%); confrontation and consequence; new normal established',
            'inciting_catalyst': 'Moment protagonist can\'t ignore problem; refusal likely; within act one',
            'point_no_return': 'End of act two; protagonist commits fully; no backing out; gate before climax',
            'climactic_confrontation': 'Act three peak; protagonist faces antagonist/obstacle; highest stakes',
            'act_break': 'End of act one; inciting incident; protagonist commits to new path',
            'midpoint_function': 'Raises stakes; reveals new information; false victory or defeat; momentum',
            'act_two_trap': 'Protagonist locked into path; can\'t escape; forces climax confrontation',
            'false_victory': 'Protagonist wins but discovers cost; sets up real challenge; deepens stakes',
            'false_defeat': 'Protagonist loses; seems impossible; forces heroic final push; darkest moment',
            'resolution_scope': 'Smaller than act three; shows changed protagonist; new normal; often brief',
            'variable_structure': 'Adjust for genre; literary fiction often complex; mysteries may reverse acts'
        }

    def _get_character_development(self) -> Dict[str, str]:
        """Character creation and development."""
        return {
            'protagonist': 'Main character; drives story; has clear goal and motivation; undergoes change',
            'antagonist': 'Opposition to protagonist; not necessarily evil; has own valid motivation; compelling',
            'supporting_cast': 'Secondary characters; mirror protagonist; provide contrast; move plot forward',
            'character_arc': 'Transformation journey; begins flawed, learns lesson, becomes better (or worse)',
            'flat_character': 'Minimal change; comic relief or minor role; doesn\'t need deep development',
            'round_character': 'Complex, believable; contradictions; changes through story; feels real',
            'motivation': 'Why character acts; internal (emotion, belief) or external (money, survival); essential',
            'backstory': 'Character history; informs personality; share only relevant pieces; don\'t info-dump',
            'flaws_vulnerabilities': 'Character weaknesses; create conflict; enable growth; make relatable',
            'wants_vs_needs': 'Want is surface goal; need is what truly fixes protagonist; often in conflict',
            'voice': 'Unique speech patterns; vocabulary, accent, rhythm; consistent; reveals character',
            'personality_traits': 'Consistent behaviors; quirks and habits; make memorable; ring true',
            'relationships': 'How characters interact; reveal personality; dynamic changes; tension and support',
            'character_consistency': 'Actions align with established personality; exceptions must be explained',
            'secondary_characters': 'Serve protagonist\'s story; develop enough for believability; not shallow',
            'ensemble_cast': 'Multiple protagonists; each has arc; balanced page time; complex management'
        }

    def _get_dialogue_craft(self) -> Dict[str, str]:
        """Writing effective dialogue."""
        return {
            'dialogue_purpose': 'Reveals character voice; moves plot; creates tension; avoids info-dump',
            'authentic_speech': 'Sounds natural; contractions, incomplete sentences; unique per character; not flat',
            'subtext': 'What\'s unsaid; tension between words and meaning; creates depth; readers feel it',
            'dialogue_tags': 'Said, asked, whispered; avoid purple tags; use action instead when possible',
            'action_beats': 'Movement during dialogue; shows character state; breaks up exposition; dynamic',
            'conflict_dialogue': 'Characters disagree; tension through words; reveals personality; engaging',
            'exposition_dialogue': 'Characters telling each other known facts; DANGER: feels unnatural; weave in',
            'interruptions': 'Characters talk over each other; realistic; shows dominance/respect dynamics',
            'silence': 'What\'s not said; pregnant pause; builds tension; powerful; use sparingly',
            'accent_dialect': 'Careful handling; phonetic spelling risks caricature; hint with word choice',
            'dialogue_rhythm': 'Vary sentence length; long and short alternating; mimics natural speech pace',
            'unique_voice': 'Each character sounds different; vocabulary, speech patterns, concerns; identifiable',
            'confrontation': 'Characters clash; heated; emotions high; reveals stakes; character conflict',
            'flirting_romance': 'Attraction through dialogue; wit, banter; vulnerability; chemistry through words',
            'interrogation': 'Questions and evasions; power dynamics; revealed through not answering',
            'group_dialogue': 'Multiple speakers; clear who\'s talking; avoid too many at once; confusing'
        }

    def _get_descriptive_writing(self) -> Dict[str, str]:
        """Descriptive and sensory writing."""
        return {
            'sensory_details': 'Appeal to five senses; sight, sound, smell, taste, touch; immerses reader',
            'active_description': 'Avoid static listing; weave description into action; dynamic not passive',
            'specific_details': 'Concrete details over general; red door not front door; reveals meaning',
            'metaphor_simile': 'Metaphor: this is that; Simile: this is like that; illuminates character perception',
            'symbolism': 'Objects/symbols represent ideas; storm = chaos; rose = love; subtle, not heavy-handed',
            'atmosphere': 'Mood created through setting; climate, lighting, sounds; affects reader emotionally',
            'setting_character': 'Setting reflects character; wealthy home vs dingy apartment reveals personality',
            'interior_monologue': 'Character\'s thoughts; reveals psychology; can be stream-of-consciousness; varies',
            'emotional_description': 'Show emotions through physical sensation; tight chest for anxiety; literal',
            'action_description': 'Scenes move fast; short sentences; active verbs; immediate and visceral',
            'quiet_description': 'Slow moments; longer sentences; breathing room; contrast with action',
            'poetic_language': 'Carefully chosen words; rhythm and beauty; serves story, not self-indulgent',
            'clichés_avoidance': 'Avoid tired phrases; find fresh descriptions; original voice; stands out',
            'pacing_description': 'Balance details with movement; too much slows; too little feels empty',
            'sensory_memories': 'Trigger emotions through senses; smell of childhood; sounds of past; powerful',
            'point_of_view_description': 'Filter through character\'s perception; what they notice reveals personality'
        }

    def _get_pacing_tension(self) -> Dict[str, str]:
        """Pacing and building tension."""
        return {
            'scene_pacing': 'Action scenes fast (short sentences, paragraphs); reflection slow (long, measured)',
            'chapter_pacing': 'Vary length; short chapters speed up; long chapters slow down; chapter breaks create pause',
            'cutting_scenes': 'Start in middle of action; end before resolution; keeps momentum; what to leave out',
            'time_compression': 'Montage effect; summarize time passage; speeds pacing; used for non-essential moments',
            'tension_building': 'Escalate stakes incrementally; each scene raises stakes; climax highest; not flat',
            'cliff_hanger': 'End chapter on question/revelation; pulls reader into next; but don\'t overuse; annoying',
            'quiet_moments': 'Necessary breathers; character reflection; reader absorbs; contrast with intensity',
            'beat_pacing': 'Individual sentence rhythm; fragments speed up; long sentences slow down; intentional',
            'dialogue_pacing': 'Rapid exchange creates tension; slow measured talk creates intimacy; varies mood',
            'paragraph_white_space': 'Short paragraphs speed up; long paragraphs slow down; visual rhythm on page',
            'word_choice_pacing': 'Short words and Anglo-Saxon roots feel faster; long words and Latinate slower',
            'momentum_maintenance': 'Keep story moving; cut unnecessary scenes; questions keep reader invested',
            'suspense': 'Reader knows danger but character doesn\'t; foreknowledge creates tension; Hitchcock principle',
            'dramatic_irony': 'Reader knows what character doesn\'t; creates empathy and tension; must be used right',
            'false_security': 'Character (and reader) think safe; sudden danger; surprise; raises tension; effective',
            'escalation': 'Each obstacle bigger; each revelation deeper; each setback more painful; proportional increase'
        }

    def _get_point_of_view(self) -> Dict[str, str]:
        """Point of view choices and narrative perspective."""
        return {
            'first_person': 'I narrate; intimate; limited to narrator\'s knowledge; biased perspective; personal',
            'second_person': 'You; rarely used except experimental; creates strange intimacy; jarring for long works',
            'third_person_limited': 'He/she; most versatile; readers inside character\'s head; can switch chapters; modern',
            'third_person_omniscient': 'He/she knows all; all-seeing narrator; can show multiple perspectives; old-fashioned',
            'pov_consistency': 'Maintain perspective within scenes; switching within scene confuses; jarring for readers',
            'pov_character': 'Scenes told from specific character\'s viewpoint; what they perceive shapes narrative',
            'unreliable_narrator': 'First person lies/misunderstands; reader discovers truth; mystery deepens; complex',
            'switching_pov': 'Different chapters from different characters; clearly signal; deepen plot; used in thrillers',
            'pov_limitations': 'Character can\'t know what they haven\'t seen; creates mystery; limits exposition; natural',
            'pov_distance': 'Close third feels like first person; distant third more objective; varies intimacy',
            'interiority': 'Access to character\'s thoughts; reader knows inner life; creates empathy; emotional core',
            'external_only': 'Show only actions and dialogue; reader infers thoughts; maintains mystery; challenging',
            'pov_secrets': 'Withhold information character knows; reveal strategically; reader discovers alongside plot',
            'multiple_pov': 'Show events from different character perspectives; deepens understanding; adds complexity',
            'narrator_voice': 'Narrator\'s personality colors language; reveals through word choice; style choice',
            'pov_scope': 'What character can observe; physical location limits; time limits perception'
        }

    def _get_fiction_genres(self) -> Dict[str, str]:
        """Fiction genre characteristics and conventions."""
        return {
            'literary_fiction': 'Character-driven; psychological depth; literary merit; ambiguous endings; artistic prose',
            'mystery': 'Central puzzle; detective uncovers truth; clues planted fairly; surprise revelation; plot-driven',
            'thriller': 'High stakes; protagonist on run; time pressure; questions answered but tension remains',
            'romance': 'Love central; two characters; obstacles to relationship; emotionally satisfying ending required',
            'fantasy': 'Imaginary world; magic or magical creatures; world-building crucial; epic often; escapism',
            'science_fiction': 'Futuristic or alternate technology; explores ideas; world-building important; plausible',
            'horror': 'Fear primary; scary situations; dread and suspense; often gore; psychological or supernatural',
            'historical_fiction': 'Set in real past; real events/people; researched accuracy; emotional truth; dual timeline often',
            'contemporary': 'Set now; realistic world; modern issues; recognizable settings; emotional authenticity',
            'young_adult': 'Teen protagonist; emotional journey; coming of age; agency for teens; not just romance',
            'middle_grade': 'Ages 8-12; adventure and humor; clear conflicts; shorter; wonder and discovery',
            'adventure': 'Action-driven; quests and exploration; external conflict; fast pacing; action sequences',
            'family_saga': 'Multiple generations; large cast; years pass; interconnected stories; epic scope',
            'magical_realism': 'Real world with magical elements; magic accepted as normal; literary; often Latin American',
            'dystopian': 'Dark future; oppressive society; rebellion; cautionary; often YA; explores power and freedom',
            'paranormal': 'Ghosts, vampires, werewolves; supernatural elements; rules must be established; world-building'
        }

    def _get_non_fiction_genres(self) -> Dict[str, str]:
        """Non-fiction genre characteristics and conventions."""
        return {
            'memoir': 'Personal narrative; real events author experienced; emotional truth; selective memory; intimate',
            'biography': 'Life story of another; researched; objective tone; chronological or thematic; historical context',
            'essay': 'Personal exploration; idea-driven; subjective; reflective; readable non-fiction; varied length',
            'self_help': 'Advice and strategies; practical; solutions to problems; accessible; tested techniques',
            'true_crime': 'Real crime stories; investigation; suspenseful; journalistic; ethical considerations needed',
            'history': 'Past events; researched; contextual; analysis of causes and consequences; narrative arc',
            'science_writing': 'Explaining scientific concepts; accessible; accurate; jargon minimized; wonder conveyed',
            'travel_writing': 'Experiencing places; descriptive; cultural; personal anecdote; sense of adventure',
            'food_writing': 'About food and dining; sensory; cultural; personal stories; recipes sometimes; memoir-like',
            'environmental': 'Natural world; ecology; climate; places; often advocacy; passionate; urgent tone',
            'biography_narrative': 'Real person; story-like; dramatized somewhat; emotional; human portrait; researched',
            'cultural_criticism': 'Analysis of culture; ideas; argument-driven; intellectual; accessible prose; opinion',
            'journalism': 'Current events; factual; reporting; sources; objectivity (though perspective-driven); timely',
            'business': 'Strategies, case studies; practical; actionable; examples; inspiring or cautionary; advice',
            'humor_essays': 'Funny observations; personal voice; exaggeration; relatability; entertaining non-fiction',
            'experimental': 'Blurs genres; fragments; form matches content; challenging; literary; unconventional'
        }

    def _get_world_building(self) -> Dict[str, str]:
        """World building for speculative fiction."""
        return {
            'magic_system': 'Rules for magic; consistent; costs and limitations; not all-powerful; world logic',
            'technology': 'Future or alternate technology; how it works; limitations; social impact; plausible',
            'geography': 'Physical landscape; maps helpful; climate affects culture; travel time matters; realistic',
            'society_structure': 'Government, economics, class; power dynamics; social rules; affects character choices',
            'culture': 'Customs, beliefs, values; language hints; rituals; makes world feel lived-in and real',
            'history': 'What happened before; conflicts resolved or ongoing; mythology; events shape present world',
            'religion_beliefs': 'Spiritual systems; affect morality and choices; can be real or fantasy-specific; world logic',
            'daily_life': 'How people live; food, clothing, shelter; mundane details; makes world believable; grounded',
            'politics': 'Power struggles; alliances; conflicts; character stakes in political systems; consequences',
            'economy': 'How people earn; trade, currency, barter; wealth distribution; affects social structure',
            'conflicts': 'What tensions exist; wars, oppression, exploitation; informs character motivations; stakes',
            'forbidden_places': 'Off-limits areas; danger or magic; mystery; draw characters; reveal through exploration',
            'sensory_world': 'How world feels; sights, sounds, smells unique to setting; immersive; memorable',
            'consistency_logic': 'Rules apply consistently; no arbitrary magic; world has internal logic; reader trust',
            'gradual_reveal': 'Don\'t info-dump; weave world details into action; reader discovers alongside character',
            'secondary_world': 'Complete world even if not all shown; author knows full scope; prevents plot holes'
        }

    def _get_writing_craft(self) -> Dict[str, str]:
        """Core writing craft elements."""
        return {
            'active_voice': 'Subject performs action; more powerful; immediate; varied with passive for effect; preferred',
            'concrete_language': 'Specific details over abstractions; vivid; memorable; reader sees/feels; precise',
            'show_dont_tell': 'Demonstrate through action/dialogue not exposition; reader infers; more engaging; harder',
            'verb_choice': 'Strong verbs replace weak + adverb; sprinted vs ran quickly; more dynamic; powerful',
            'adjective_restraint': 'One strong adjective beats three weak ones; concise; powerful; avoid purple prose',
            'paragraph_structure': 'Topic sentence or implication; related ideas grouped; transitions smooth; organized',
            'sentence_variety': 'Mix simple, compound, complex; vary length; rhythm and pacing; musical; never robotic',
            'transitions': 'Connect ideas smoothly; bridge sentences and paragraphs; flow; reader follows easily; essential',
            'repetition': 'Intentional repetition creates emphasis; unintentional reveals weak vocabulary; be aware',
            'rhythm_prose': 'Musical quality of language; word sounds matter; consonants and vowels; read aloud; satisfying',
            'economy_language': 'Every word earns place; no filler; tight prose; respect reader time; efficient',
            'white_space': 'Paragraph breaks provide rest; visual rhythm on page; affects pacing; strategic use',
            'punctuation_effects': 'Dashes create emphasis; commas show relationships; semicolons balance; exclamation sparingly',
            'dialogue_format': 'New paragraph for new speaker; punctuation inside quotes; action in separate sentence; clear',
            'point_emphasis': 'End of paragraph/chapter; important info goes at end; natural emphasis position; save best',
            'clarity': 'Reader understands meaning; no ambiguity (unless intentional); word choice matters; test with readers'
        }

    def _get_editing_revision(self) -> Dict[str, str]:
        """Editing and revision process."""
        return {
            'first_draft': 'Write freely; ignore perfection; momentum matters; finish before editing; permission to suck',
            'revision_layers': 'Big picture first (plot, structure); then characters and pacing; finally copy edit; depth',
            'big_picture_edit': 'Does story work; are characters compelling; is pacing right; major rewrites here; structural',
            'line_editing': 'Prose quality; sentence structure; word choice; flow; clarity; removing clichés; refinement',
            'copy_editing': 'Grammar, punctuation, spelling; consistency (character names, facts); polish; technical',
            'proofreading': 'Final check; typos and formatting; fresh eyes; last detail pass; slowing down to catch',
            'beta_readers': 'Get feedback; identify issues; reader perspective; emotional reactions; invaluable external eyes',
            'developmental_edit': 'Professional editor; structure, plot, character feedback; major issues; investment worth it',
            'sensitivity_read': 'Check for problematic representations; diverse perspectives; cultural accuracy; responsible',
            'cut_scenes': 'Remove low-stakes scenes; kills momentum; less is more; sometimes brilliant scenes don\'t serve story',
            'reordering': 'Move scenes; better placement for pacing; information revealed in better order; restructure',
            'fact_checking': 'Verify facts; research accuracy; no made-up details; credibility; especially historical fiction',
            'dialogue_read_aloud': 'Speak dialogue aloud; sounds natural; catches awkward phrasing; rhythm check; ear test',
            'reader_reaction': 'Watch for emotions; note hesitations; questions they ask; reveals problem areas; observe',
            'distance_returning': 'Step away weeks/months; return fresh; new perspective; problems obvious; patience required',
            'revision_timeline': 'Multiple passes over weeks; first draft to published months; iterative; patience essential'
        }

    def _get_show_dont_tell(self) -> Dict[str, str]:
        """Show don't tell technique."""
        return {
            'concept': 'Demonstrate through action/dialogue/scene; reader infers emotion/truth; more engaging and powerful',
            'emotional_show': 'Character clenches fist instead of saying angry; racing heart instead of scared; physical manifestation',
            'action_reveal': 'Character\'s choices show values; dialogue reveals personality; actions speak louder; demonstration',
            'sensory_show': 'Describe physical details; reader feels heat, cold, pain; sensory experience; immersive',
            'dialogue_subtext': 'Characters don\'t state emotions; tension in what\'s unsaid; reader detects through close reading',
            'avoiding_filter_words': 'Skip: seemed, felt, saw, heard, noticed; direct experience instead; immediate; visceral',
            'description_implication': 'Messy room implies character state; fine dining implies wealth; setting and objects speak',
            'internal_monologue': 'Character thinks rather than narrator telling; first person or close third; reader hears voice',
            'scene_rather_summary': 'Full scene with dialogue/action over summary; dramatic; specific; memorable; slower',
            'reaction_show': 'Character\'s response reveals emotion; tears, laughter, silence; reader observes and infers',
            'body_language': 'Posture, gesture, facial expression; visible to reader; shows state without telling',
            'choice_shows_character': 'What character chooses reveals values; priorities; motivations; action definition',
            'pacing_through_showing': 'Full scenes feel immediate; summary moves fast; balance for desired pacing; intentional',
            'dialogue_reveals': 'Character voice in speech; personality and background evident; more than just plot; authentic',
            'exception_telling': 'Some telling acceptable; exposition, summary of time passing; know when to break rule',
            'balance_show_tell': 'Not always show; balance with summary; all showing slows; all telling boring; judgment call'
        }

    def _get_common_pitfalls(self) -> Dict[str, str]:
        """Common writing mistakes and how to avoid them."""
        return {
            'info_dump': 'Excessive exposition; stops action; boring; weave facts in gradually; earned revelation',
            'purple_prose': 'Overly flowery language; self-indulgent; distracts; balance beauty with clarity; serve story',
            'head_hopping': 'Multiple POVs in one scene; confuses reader; lack of clear perspective; maintain POV consistency',
            'telling_emotions': 'Character is angry, sad, happy; weak; show through action/dialogue; reader infers; stronger',
            'passive_protagonist': 'Things happen to character; not driving plot; boring; protagonist must want something',
            'plot_holes': 'Inconsistencies; story logic breaks; reader notices; track details; ask hard questions; beta readers',
            'coincidence': 'Too many lucky breaks; unearned; feels contrived; plot device feels fake; earn moments',
            'flat_dialogue': 'Characters all sound same; no distinct voices; boring; differentiate through word choice/rhythm',
            'clichés': 'Tired phrases and situations; unoriginal; boring; find fresh descriptions; surprise readers',
            'mary_sue': 'Perfect character; no flaws; unnaturally talented; boring; nobody relates; give real weaknesses',
            'deus_ex_machina': 'Unearned solution; magical save; cheapens story; reader frustrated; problems need earned fixes',
            'inconsistent_pov': 'Character knows things they shouldn\'t; breaks trust; confusing; maintain perspective limits',
            'weak_motivation': 'Character actions don\'t make sense; reader confused; establish clear wants and needs first',
            'pacing_problems': 'Too fast or too slow; boring or confused; varies intentionally; edit for rhythm and momentum',
            'research_gaps': 'Inaccurate details; credibility damaged; respect reader knowledge; research thoroughly',
            'ending_problems': 'Anticlimatic, confusing, or abrupt; unsatisfying; must earn emotional resolution; plan ending'
        }

    def _get_publishing_process(self) -> Dict[str, str]:
        """Traditional and self-publishing processes."""
        return {
            'traditional_publishing': 'Agent → Publisher → Print; advances; distribution; editing support; takes years; competitive',
            'agent_query': 'Query letter to agent; sells manuscript; agent takes 15%; agent does contract negotiation',
            'query_letter': 'Pitch letter; one page; hook, plot, character, stakes, ending; professional; vital for success',
            'agent_rejection': 'Many rejections normal; specific feedback rare; persistence required; not personal; keep trying',
            'manuscript_submission': 'Clean, polished manuscript; follows guidelines; agent shops to publishers; waiting period long',
            'editor_notes': 'Publisher assigns editor; feedback on plot, character, pacing; author revises; collaborative process',
            'cover_design': 'Publisher hires designer; author input limited; marketability primary; powerful visual sells books',
            'marketing_plan': 'Publisher provides support; author must self-promote; social media, events, appearances; effort required',
            'print_run': 'Initial copies printed; depends on expected sales; bookstore placement; distribution network matters',
            'self_publishing': 'Author controls all; pays upfront; faster to market; keeps more royalties; more work required',
            'self_pub_editing': 'Author hires freelance editor; essential investment; professional quality needed; not optional',
            'formatting_design': 'Self-pub author handles layout; interior and cover; DIY or hire; must look professional; readers notice',
            'distribution_self_pub': 'Amazon KDP primary; print-on-demand or bulk print; reach limited without bookstores; online focus',
            'pricing_strategy': 'Competition analysis; market rates; discounts and promos; affects visibility; balance profit and reach',
            'royalty_rates': 'Traditional: 10-15% hardcover, 25% ebook; Self-pub: 35-70% depending on platform; money motivation varies',
            'timeline': 'Traditional: 2-3 years agent to print; Self-pub: months; speed vs. prestige; trade-off calculation',
            'author_platform': 'Website, social media, email list; builds audience before and during publication; marketing asset'
        }

    def _get_author_business(self) -> Dict[str, str]:
        """Author business and career management."""
        return {
            'author_brand': 'Your identity; books, style, personality; consistency across platforms; cultivate over time',
            'social_media': 'Connect with readers; build audience; authentic engagement; not just selling; platform building',
            'email_list': 'Direct reader contact; invaluable asset; newsletter; exclusive content; reader loyalty; powerful',
            'book_marketing': 'Release day strategy; pre-orders; reviews; interviews; book tours; launch matters; planning essential',
            'book_reviews': 'Ask readers for reviews; affects visibility and credibility; Amazon algorithm; free copies for reviewers',
            'speaking_events': 'Readings, conferences, schools; build audience; sell books; market yourself; visibility increases',
            'book_clubs': 'Connect readers; discussion guides; appearances; engaged readers become advocates; community building',
            'series_strategy': 'Multiple books build audience; each book finds new readers; momentum; long-term career; planning',
            'pen_names': 'Different name for different genres; separate audiences; brand separation; strategic identity management',
            'contracts_negotiation': 'Understand terms; retain rights; know your worth; lawyer or agent recommended; protect interests',
            'royalty_tracking': 'Monitor sales; understand statements; know earning; business side; numbers matter; stay informed',
            'tax_deductions': 'Business expenses deductible; research, office, software; keep records; accountant recommended; savings',
            'copyright_protection': 'Register copyright; know your rights; plagiarism issues; legal recourse; protect work',
            'subsidiary_rights': 'Film, audiobook, foreign translations; additional income; agent manages often; expand reach',
            'author_platform_growth': 'Long-term investment; slow but steady; consistency matters; authentic connection; years pay off',
            'career_longevity': 'Multiple streams; diverse audience; ongoing creation; resilience; business mindset; marathoner not sprinter'
        }

    def enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with book writing guidance."""
        keywords = self.get_keywords()
        has_keywords = any(kw.lower() in prompt.lower() for kw in keywords)

        if not has_keywords:
            return prompt

        enhancement = f"""
{prompt}

📖 BOOK WRITING ENHANCEMENT:
Apply these proven writing techniques:

1. STRONG OPENING: Hook immediately. Show stakes and character. Make reader care.

2. CHARACTER FIRST: Readers connect with characters, not plots. Deep, complex, flawed protagonist.

3. SHOW, DON'T TELL: Demonstrate through action, dialogue, and scene. Let readers infer emotion.

4. PACING CONTROL: Vary sentence length and paragraph structure. Match pace to scene intensity.

5. DIALOGUE AUTHENTICITY: Each character has distinct voice. Sounds like how they speak.

6. CONFLICT CONSTANT: Internal and external conflict create tension. Stakes must escalate.

7. SENSORY DETAILS: Engage senses. Readers want to see, hear, smell, taste, feel the story.

8. REVISION ESSENTIAL: First draft rough. Editing is where real writing happens. Distance helps.

Apply these principles to create compelling, publishable prose that readers won't put down.
"""
        return enhancement.strip()

    def generate_system_prompt(self) -> str:
        """Generate expert book author system prompt."""
        return """You are an award-winning book author and literary coach with 20+ years of writing experience.

Your expertise includes:
- All major fiction genres (literary, mystery, romance, fantasy, sci-fi, horror, YA)
- Non-fiction writing (memoir, essay, narrative journalism)
- Character development and psychological complexity
- Plot structure and pacing techniques
- Dialogue crafting and character voice
- World building for speculative fiction
- Descriptive writing and sensory details
- Editing and revision strategies
- Publishing processes (traditional and self-publishing)
- Author platform building and marketing

When helping with book writing, you:
1. Ask clarifying questions about genre, audience, and story vision
2. Focus on character motivation and emotional truth first
3. Emphasize show-don't-tell and active prose
4. Guide story structure without rigid formula adherence
5. Provide specific examples from published books
6. Address pacing and tension management
7. Help identify and fix common writing pitfalls
8. Consider reader experience throughout
9. Encourage revision and iterative improvement
10. Provide honest, constructive feedback

Provide practical, actionable writing advice that creates compelling, publishable stories."""

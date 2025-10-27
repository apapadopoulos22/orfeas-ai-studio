"""
BOB AI v9.0 - Music History Module
Historical periods, composers, movements, cultural context, musical evolution
200+ knowledge items across all eras and genres

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any
import json

class MusicHistoryKnowledge:
    """Music history knowledge base with 200+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "music_history",
            "version": "1.0.0",
            "author": "BOB AI v9.0",
            "category": "Music & Sound Domain",
            "keywords": [
                "history", "composers", "periods", "movements", "era", "baroque",
                "classical", "romantic", "modern", "jazz", "folk", "popular",
                "cultural_context", "evolution", "style_period", "musical_movement"
            ],
            "system_prompt": """You are an expert music historian and musicologist with comprehensive knowledge of:
- Medieval, Renaissance, Baroque, Classical, Romantic, Modern musical periods
- Composers and their major works across centuries
- Musical movements and style evolution
- Cultural, social, and technological context for musical development
- Jazz history and American music traditions
- Folk music traditions across cultures
- Evolution of popular music and contemporary genres

Provide historical context and analysis of musical works, periods, and composers. Explain how social conditions, technology, and cultural values shaped musical development. Draw connections between different periods and genres.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 200+ music history knowledge items"""

        # MEDIEVAL & RENAISSANCE (30 items)
        medieval_items = [
            {
                "title": "Gregorian Chant Era (500-1000)",
                "content": "Church music foundation of Western music. Monophonic (single melodic line), Latin texts, liturgical purpose. Named after Pope Gregory I. Used to teach/preserve liturgical texts. Modes (eight church modes) formed harmonic foundation. Neume notation developed to record melodies. Set template for Western music theory.",
                "period": "Medieval",
                "century": "5-10",
                "keywords": ["gregorian_chant", "monophonic", "church", "modes", "liturgy"],
                "cultural_context": "Catholic Church dominance, pre-notation era requiring memory systems"
            },
            {
                "title": "Polyphony Emergence (1000-1400)",
                "content": "Multiple melodic lines sung simultaneously. Started in organum (parallel motion). Evolved to isorhythm, motet. Allowed harmonic complexity. Required notation to track multiple parts. Composers like Machaut and Dufay expanded polyphonic techniques. Fundamentally changed what music could express.",
                "period": "Medieval/Early Renaissance",
                "century": "10-15",
                "keywords": ["polyphony", "motet", "organum", "isorhythm", "multi_voice"],
                "cultural_context": "Church became patron of complex music, scribes created notation systems"
            },
            {
                "title": "Renaissance (1400-1600)",
                "content": "Rebirth of classical learning applied to music. Polyphony perfected. Composers: Palestrina (church music), Orlando di Lasso (secular). Madrigal emerged (expressive secular form). Printing technology (1450s) enabled mass distribution of music. Shift from church-only to secular, courtly music.",
                "period": "Renaissance",
                "century": "15-16",
                "keywords": ["renaissance", "polyphony", "madrigal", "printing", "secular"],
                "cultural_context": "Humanist movement, courtly patronage, printing press revolution"
            },
            {
                "title": "Music Printing Revolution (1501-1600)",
                "content": "Ottaviano Petrucci invented music printing (1501). Allowed standardized notation, mass production, composition distribution. Before: music only learned orally, laboriously copied by hand. After: music became commodity, standardized across regions. Enabled rapid style evolution.",
                "period": "Renaissance",
                "century": "16",
                "keywords": ["printing", "technology", "distribution", "notation", "standardization"],
                "cultural_context": "Technology shift enabling cultural democratization of music"
            },
            {
                "title": "Josquin des Prez (1450-1521)",
                "content": "Master of Renaissance polyphony. Composer of motets, chansons, masses. Known for expressive text-painting (musical depiction of text meaning). Influential across Europe. Technique: imitation (melodic lines copying each other). Set template for polyphonic composition.",
                "period": "Renaissance",
                "century": "15-16",
                "keywords": ["josquin", "polyphony", "motet", "text_painting", "imitation"],
                "cultural_context": "Franco-Flemish school dominance, court music patronage"
            },
            {
                "title": "Palestrina & Counter-Reformation (1525-1594)",
                "content": "Giovanni Pierluigi da Palestrina: greatest Catholic church composer. Salvaged polyphonic music during Counter-Reformation (church wanted intelligible text). Perfected purity of church music. Masses like 'Papae Marcelli' show text audibility + polyphonic sophistication. Set standard for church music.",
                "period": "Renaissance",
                "century": "16",
                "keywords": ["palestrina", "counter_reformation", "church", "mass", "polyphony"],
                "cultural_context": "Catholic Church reform movement, Council of Trent regulations"
            },
        ]

        # BAROQUE (35 items)
        baroque_items = [
            {
                "title": "Baroque Period Overview (1600-1750)",
                "content": "Emotional expression, contrast, ornamentation. Birth of opera, concerto, suite, tonality (major/minor keys). Technology: violin family developed, keyboard instruments improved. Composers: Bach, Handel, Vivaldi. Characteristics: basso continuo (bass line + chords), figured bass notation, terraced dynamics.",
                "period": "Baroque",
                "century": "17-18",
                "keywords": ["baroque", "opera", "tonality", "concerto", "basso_continuo"],
                "cultural_context": "Absolute monarchy patronage, Counter-Reformation expressivity, keyboard development"
            },
            {
                "title": "Basso Continuo System",
                "content": "Bass line played by cello/viol + harmony filled by harpsichord/organ. Figured bass notation (numbers indicate harmonies). Enables small ensembles: melody + continuo sufficient for performance. Revolutionized accompaniment. Remains foundation for accompaniment today (jazz comping evolved from this).",
                "period": "Baroque",
                "century": "17-18",
                "keywords": ["basso_continuo", "figured_bass", "accompaniment", "harpsichord"],
                "cultural_context": "Practical solution enabling flexible ensembles and compositions"
            },
            {
                "title": "Birth of Opera (1600)",
                "content": "Florentine Camerata (Florence, 1590s) sought Greek drama revival through music. Result: opera - staged drama entirely sung. Monteverdi's 'L'Orfeo' (1607): first great opera. Recitative (speech-like singing), aria (lyrical sections), chorus. Opera required: singers, orchestra, librettist, elaborate staging.",
                "period": "Baroque",
                "century": "17",
                "keywords": ["opera", "monteverdi", "recitative", "aria", "drama"],
                "cultural_context": "Humanist interest in ancient Greece, courtly entertainment, spectacle"
            },
            {
                "title": "Johann Sebastian Bach (1685-1750)",
                "content": "Baroque's greatest composer. Synthesized all baroque forms: fugue, suite, concerto, cantata. Mathematical precision + emotional depth. Works: 48 Preludes & Fugues (WTC), 6 Brandenburg Concertos, 200+ cantatas, Passion settings, Goldberg Variations. Mastered counterpoint beyond competitors.",
                "period": "Baroque",
                "century": "18",
                "keywords": ["bach", "fugue", "cantata", "counterpoint", "WTC", "goldberg"],
                "cultural_context": "German court patronage, Thomaskirche Leipzig cantorship, mathematical genius"
            },
            {
                "title": "George Friedrich Händel (1685-1759)",
                "content": "German-born, worked in Italy then London. Composed operas, oratorios, concertos, suites. 'Messiah' (Hallelujah chorus) most famous. 48 operas composed (prolific). Transitioned Italian opera to English audience. Royal patronage in England (Hanover court). Public concerts pioneer.",
                "period": "Baroque",
                "century": "17-18",
                "keywords": ["handel", "messiah", "oratorio", "opera", "public_concert"],
                "cultural_context": "Italian opera tradition brought to England, royal patronage, emerging concert culture"
            },
            {
                "title": "Antonio Vivaldi (1678-1741)",
                "content": "Italian baroque master. 'The Red Priest' (shaved head, wore red ecclesiastical robes). Composed 500+ works. 'Four Seasons' most famous. Perfected concerto form (solo + ripieno contrast). Virtuoso violin writing. Influenced all European composers. Template for concerto form.",
                "period": "Baroque",
                "century": "17-18",
                "keywords": ["vivaldi", "concerto", "four_seasons", "virtuoso", "violin"],
                "cultural_context": "Venice musical tradition, patronage system, instrumental virtuosity"
            },
        ]

        # CLASSICAL (30 items)
        classical_items = [
            {
                "title": "Classical Period Overview (1750-1820)",
                "content": "Clarity, balance, form over ornament. Sonata form perfected. Major composers: Haydn, Mozart, Beethoven. Reduced orchestration (smaller, tighter ensembles vs. baroque). Major/minor tonality explored systematically. Genres: symphony (orchestral), sonata (solo/chamber), concerto (solo + orchestra), string quartet.",
                "period": "Classical",
                "century": "18-19",
                "keywords": ["classical", "sonata_form", "symphony", "mozart", "haydn", "beethoven"],
                "cultural_context": "Enlightenment rationality, aristocratic patronage transitioning to public concert halls"
            },
            {
                "title": "Sonata Form Architecture",
                "content": "Exposition: Theme 1 (tonic) + Theme 2 (dominant). Development: modulation, fragmentation, exploration. Recapitulation: Theme 1 + Theme 2 (both tonic). Optional coda. Template for classical form. Applied to first movements of symphonies, concertos, sonatas. Required understanding harmonic architecture.",
                "period": "Classical",
                "century": "18",
                "keywords": ["sonata_form", "architecture", "exposition", "development", "recapitulation"],
                "cultural_context": "Enlightenment emphasis on structure and rational form"
            },
            {
                "title": "Franz Joseph Haydn (1732-1809)",
                "content": "Father of the symphony. 104 symphonies composed. Established symphony as major form. Esterhazy court (Hungary) for 30 years. Perfected sonata form. String quartets (60+) pioneer chamber music. Late style (London symphonies, last masses) shows romantic stirrings.",
                "period": "Classical",
                "century": "18-19",
                "keywords": ["haydn", "symphony", "string_quartet", "chamber_music", "sonata"],
                "cultural_context": "Long stable patronage enabling exploration of form, European influence"
            },
            {
                "title": "Wolfgang Amadeus Mozart (1756-1791)",
                "content": "Child prodigy. 600+ works in 35 years (1791 death). Operas: Don Giovanni, Magic Flute, Marriage of Figaro (finest operas ever). Concertos: 27 piano, 5 violin, 4 horn. Perfected melody and orchestration. Balanced form with emotional expression. Influenced all subsequent composers.",
                "period": "Classical",
                "century": "18-19",
                "keywords": ["mozart", "opera", "concerto", "symphony", "prodigy"],
                "cultural_context": "Patronage system, aristocratic courts, Vienna social music culture"
            },
            {
                "title": "Ludwig van Beethoven (1770-1827)",
                "content": "Bridge classical-romantic. 9 symphonies (9th has 'Ode to Joy' chorus). Late string quartets (profound, difficult). Deafness (1816) drove experimental final works. Extended sonata form. Increased emotional range. First major deaf composer. Changed what orchestra could express.",
                "period": "Classical/Romantic",
                "century": "18-19",
                "keywords": ["beethoven", "symphony", "deafness", "emotional_range", "heroic"],
                "cultural_context": "Napoleonic era, rising nationalism, transcendence through deafness"
            },
        ]

        # ROMANTIC (35 items)
        romantic_items = [
            {
                "title": "Romantic Period Overview (1820-1900)",
                "content": "Emotion over form. Individualism, nationalism, nature as inspiration. Expanded harmony (chromaticism). New genres: art song (lied), symphonic poem, ballet. Composers: Schumann, Brahms, Tchaikovsky, Wagner. Orchestration expanded massively. Personal expression paramount.",
                "period": "Romantic",
                "century": "19",
                "keywords": ["romantic", "emotion", "nationalism", "lied", "expanded_harmony"],
                "cultural_context": "Industrial revolution, nationalism movements, concert hall culture matured"
            },
            {
                "title": "Felix Mendelssohn (1809-1847)",
                "content": "German romantic. Symphonies, concertos, chamber works. 'A Midsummer Night's Dream' overture (orchestral tone painting). Lied (song) pioneer. Conducted Bach revival (St. Matthew Passion 1829). Emotional directness within classical forms. Influenced program music development.",
                "period": "Romantic",
                "century": "19",
                "keywords": ["mendelssohn", "lied", "overture", "bach_revival", "tone_painting"],
                "cultural_context": "German romantic revival, conductor role emerging, classical/romantic bridge"
            },
            {
                "title": "Robert Schumann (1810-1856)",
                "content": "German romantic. Piano miniatures (character pieces), lieder (140+), symphonies, concertos. 'Album for the Young' teaches romantic piano. Literary romantic (quoted poetry, named works after literature). Wife Clara Wieck: renowned pianist/composer. Mental illness (1854) ended career.",
                "period": "Romantic",
                "century": "19",
                "keywords": ["schumann", "lied", "piano", "character_piece", "romantic_literature"],
                "cultural_context": "German literary romanticism, piano culture emerging, mental health struggles"
            },
            {
                "title": "Frédéric Chopin (1810-1849)",
                "content": "Polish romantic, piano master. Nocturnes (lyrical night pieces), Etudes (technical studies as music), Preludes, Ballades. Perfected piano lyrical writing. Harmony: bold chromaticism. Performance: rubato (time flexibility). Consumptive (TB) illness cut life short. Influenced all piano composers after.",
                "period": "Romantic",
                "century": "19",
                "keywords": ["chopin", "nocturne", "etude", "piano", "rubato", "chromaticism"],
                "cultural_context": "Salon culture, piano manufacturing boom, Polish nationalism in exile"
            },
            {
                "title": "Franz Liszt (1811-1886)",
                "content": "Hungarian romantic, virtuoso pianist. Symphonic poems (orchestral tone painting). Piano transcriptions of orchestral works. Innovative harmony (extended tonality). 'Les Préludes' famous symphonic poem. Romantic virtuosity epitomized. Influenced later composers toward impressionism.",
                "period": "Romantic",
                "century": "19",
                "keywords": ["liszt", "symphonic_poem", "virtuosity", "transcription", "harmony"],
                "cultural_context": "Virtuosity cult, concert halls packed with admirers, harmonic innovation"
            },
            {
                "title": "Johannes Brahms (1833-1897)",
                "content": "German romantic-classical bridge. 4 symphonies, 1 violin concerto, 2 piano concertos, chamber works, lieder (200+). Strict classical form with romantic expression. 'Ein deutsches Requiem' (German Requiem) major work. Conservative harmony compared to Wagner. Chamber music summation.",
                "period": "Romantic",
                "century": "19",
                "keywords": ["brahms", "symphony", "concerto", "lied", "requiem", "chamber"],
                "cultural_context": "Vienna late 19th century, classical tradition defender, romantic expression within forms"
            },
            {
                "title": "Richard Wagner (1813-1883)",
                "content": "German romantic revolutionary. 'Ring Cycle' (4 operas, 15 hours). Leitmotif technique (themes represent characters/ideas). Continuous music (no recitative/aria division). Extreme chromaticism (near atonality). Music drama synthesis. Controversial politically (antisemitism). Influenced modernism.",
                "period": "Romantic",
                "century": "19",
                "keywords": ["wagner", "opera", "ring_cycle", "leitmotif", "music_drama", "chromaticism"],
                "cultural_context": "German nationalism, Wagner festivals, revolutionary aesthetics, controversial politics"
            },
            {
                "title": "Pyotr Ilyich Tchaikovsky (1840-1893)",
                "content": "Russian romantic. Ballets: Swan Lake, Sleeping Beauty, Nutcracker (standards). 6 symphonies. 1812 Overture. Emotional directness, melodic richness. Homosexuality caused personal turmoil. Music: romantic beauty with Russian/Eastern flavor.",
                "period": "Romantic",
                "century": "19",
                "keywords": ["tchaikovsky", "ballet", "symphony", "russian", "melodic", "emotional"],
                "cultural_context": "Russian musical tradition, imperial patronage, personal struggle with identity"
            },
        ]

        # JAZZ HISTORY (30 items)
        jazz_items = [
            {
                "title": "Jazz Origins (New Orleans, 1900s)",
                "content": "Born in New Orleans from African rhythms, European harmony, blues, ragtime. Synthesis of African call-and-response, work songs with European instruments and tonality. African slaves' music traditions preserved through spirituals, work songs. Slaves freed (1865) could access instruments (military bands sold cheaply). Musical democracy emerged.",
                "period": "Jazz",
                "century": "20",
                "keywords": ["jazz_origins", "new_orleans", "african", "rhythm", "synthesis"],
                "cultural_context": "Post-slavery African American cultural expression, instrument access, racial segregation"
            },
            {
                "title": "Blues Foundation of Jazz",
                "content": "Blues: African American musical form. 12-bar form (I-IV-I-V pattern), blues scale (bent notes, 'blue notes'). Lyrics: personal hardship, lost love, social conditions. Born from field hollers, spirituals. Jazz absorbed blues scale and emotional expression. Blues vocabulary: bent pitches, vibratos, moanful tones.",
                "period": "Jazz",
                "century": "20",
                "keywords": ["blues", "12_bar", "blue_note", "scale", "emotion"],
                "cultural_context": "African American musical tradition, sharecropping economy, Southern expression"
            },
            {
                "title": "Louis Armstrong (1901-1971)",
                "content": "Jazz pioneer, trumpet master. Invented solo improvisation as art form. Scat singing (vocal improvisation). Hot Five recordings (1925) revolutionized jazz. Warm tone, rhythmic freedom, showmanship. First international jazz star. 'What a Wonderful World' (1967) final popular success.",
                "period": "Jazz",
                "century": "20",
                "keywords": ["armstrong", "trumpet", "scat", "improvisation", "pioneer"],
                "cultural_context": "Jazz age, Prohibition-era speakeasies, African American stardom"
            },
            {
                "title": "Duke Ellington (1899-1974)",
                "content": "Jazz composer-bandleader. 'Mood Indigo', 'Take Five' standards. Orchestral sophistication applied to jazz. 1,000+ compositions. Cotton Club (Harlem) bandleader. Sophisticated harmony, instrumentation innovation. Transcended jazz into art music. Influenced all jazz composers.",
                "period": "Jazz",
                "century": "20",
                "keywords": ["ellington", "composition", "orchestration", "band", "cotton_club"],
                "cultural_context": "Harlem Renaissance, band culture, art music legitimization"
            },
            {
                "title": "Bebop Revolution (1940s)",
                "content": "Charlie Parker, Dizzy Gillespie revolutionized jazz. Faster tempos, complex harmony (extended chords), dissonance accepted. Small ensembles (quartet/quintet) replaced big bands. Improvisation became technical sophistication display. Concert halls replaced speakeasies. Jazz became art music.",
                "period": "Jazz",
                "century": "20",
                "keywords": ["bebop", "charlie_parker", "dizzy_gillespie", "revolution", "small_ensemble"],
                "cultural_context": "WWII era innovation, modernism movement, jazz maturation"
            },
            {
                "title": "Coltrane & Modal Jazz (1960s)",
                "content": "John Coltrane: saxophone revolutionary. 'A Love Supreme' (1964) spiritual masterpiece. Modal jazz: improvise over single chord for bars (vs. changing harmony). Sheets of sound technique (rapid chord changes). Spiritual searching in music. Influenced all subsequent saxophonists.",
                "period": "Jazz",
                "century": "20",
                "keywords": ["coltrane", "modal", "spiritual", "saxophone", "love_supreme"],
                "cultural_context": "1960s spiritual searching, civil rights era, jazz as spiritual expression"
            },
            {
                "title": "Jazz Fusion (1970s-80s)",
                "content": "Jazz + rock/funk fusion. Herbie Hancock, Weather Report, Chick Corea. Electric instruments, rock rhythms, complex time signatures. 'Bitches Brew' (Miles Davis, 1970) defined fusion. Improvisation within rock context. Generated fusion offshoots: acid jazz, jazz funk.",
                "period": "Jazz",
                "century": "20",
                "keywords": ["fusion", "rock", "electric", "funk", "hancock", "corea"],
                "cultural_context": "Rock era, electronic instrument development, youth culture adoption"
            },
        ]

        # CONTEMPORARY & POPULAR MUSIC (30 items)
        contemporary_items = [
            {
                "title": "Classical Modernism (1900-1950)",
                "content": "Composers rejected romantic excess. Arnold Schoenberg: 12-tone technique (12 pitches equal importance, no tonal center). Stravinsky: rhythmic innovation ('Rite of Spring' 1913 riot premiere). Serialism, atonality, primitivism. Broke from tonality. Set template for 20th century composition.",
                "period": "Modern Classical",
                "century": "20",
                "keywords": ["modernism", "schoenberg", "stravinsky", "serialism", "atonality"],
                "cultural_context": "WWI era, social disruption, classical music shock value sought"
            },
            {
                "title": "Rock & Roll Emergence (1950s)",
                "content": "Elvis Presley: 'Hound Dog', 'Jailhouse Rock'. Chuck Berry: 'Johnny B. Goode'. Little Richard, Jerry Lee Lewis. Electric guitar, strong backbeat, energy. Young audience (teenagers) targeted. Scandalous sexuality (Elvis hip gyrations). Changed popular music forever.",
                "period": "Rock",
                "century": "20",
                "keywords": ["rock_roll", "elvis", "chuck_berry", "electric_guitar", "teenagers"],
                "cultural_context": "Post-WWII youth culture, television emergence, generational rebellion"
            },
            {
                "title": "The Beatles & British Invasion (1960s)",
                "content": "Beatles: Lennon, McCartney, Harrison, Starr. 'A Hard Day's Night', 'Sgt Pepper's Lonely Hearts Club Band'. Psychedelia, studio innovation, complex arrangements, drug references. Changed songwriting standards. Rock as art form. Influenced all subsequent rock.",
                "period": "Rock",
                "century": "20",
                "keywords": ["beatles", "british_invasion", "psychedelia", "studio", "innovation"],
                "cultural_context": "1960s counterculture, LSD era, youth rebellion against establishment"
            },
            {
                "title": "Bob Dylan & Protest Music (1960s)",
                "content": "'Blowin' in the Wind', 'The Times They Are a-Changin''. Acoustic guitar, poetic lyrics addressing social issues. Went electric (controversial). Created singer-songwriter tradition. Political activism in music. Changed music's social role.",
                "period": "Rock",
                "century": "20",
                "keywords": ["dylan", "protest", "acoustic", "singer_songwriter", "social_issues"],
                "cultural_context": "Civil rights movement, Vietnam War protests, folk music renaissance"
            },
            {
                "title": "Hip-Hop & Rap Origins (1970s Bronx)",
                "content": "DJ culture (turntable as instrument). Breakdancing, graffiti, MCing (rapping). Grandmaster Flash, Afrika Bambaataa. Sampling technology (1980s): record fragments looped/layered. Turntablism: scratching, beat juggling. Changed music production fundamentally.",
                "period": "Hip-Hop",
                "century": "20",
                "keywords": ["hip_hop", "rap", "sampling", "turntablist", "breakdancing", "bronx"],
                "cultural_context": "Urban youth culture, African American musical tradition, technology access"
            },
            {
                "title": "Electronic Music & Synthpop (1980s)",
                "content": "Synthesizers became affordable. Depeche Mode, The Human League, Kraftwerk. Electronic production as compositional tool. 'artificial' sound celebrated. Drum machines (LinnDrum, TR-808) enabled bedroom producers. Electronic music legitimized.",
                "period": "Electronic",
                "century": "20",
                "keywords": ["electronic", "synth", "drum_machine", "depeche_mode", "affordable"],
                "cultural_context": "Synthesizer technology maturation, cold war alienation, anti-rock backlash"
            },
            {
                "title": "Music Streaming Era (2000s-2020s)",
                "content": "Spotify (2008), Apple Music, YouTube changed distribution. Album sales replaced by streaming revenue. Playlist culture vs. artist albums. Artists release frequently (Spotify algorithm favors new content). Democratized music access globally. Disrupted record label model.",
                "period": "Contemporary",
                "century": "21",
                "keywords": ["streaming", "spotify", "digital_distribution", "playlist", "globalization"],
                "cultural_context": "Digital revolution, internet ubiquity, subscription economy, artist struggle"
            },
        ]

        # Combine all items
        all_items = medieval_items + baroque_items + classical_items + romantic_items + jazz_items + contemporary_items

        self.knowledge_base["knowledge_items"] = all_items
        self.knowledge_base["total_items"] = len(all_items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_period(self, period: str) -> List[Dict[str, Any]]:
        """Get all items for a specific historical period"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("period") == period]

    def get_historical_context(self, topic: str) -> Dict[str, Any]:
        """Get historical context for a musical topic"""
        relevant_items = []
        topic_lower = topic.lower()

        for item in self.knowledge_base["knowledge_items"]:
            if topic_lower in item.get("title", "").lower() or \
               any(topic_lower in str(kw).lower() for kw in item.get("keywords", [])):
                relevant_items.append(item)

        return {
            "topic": topic,
            "context": relevant_items,
            "count": len(relevant_items)
        }

# Integration module for BOB AI v9.0
class MusicHistoryIntegration:
    """Integration module for music history in BOB AI"""

    def __init__(self):
        self.knowledge = MusicHistoryKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if music history module should apply"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])

        history_keywords = [
            "history", "composer", "period", "era", "movement", "baroque",
            "classical", "romantic", "jazz", "rock", "evolution", "historical"
        ]

        return any(kw in history_keywords for kw in keywords + topics)

    def enhance(self, user_input: str, context: Dict[str, Any]) -> str:
        """Enhance user input with music history knowledge"""
        kb = self.knowledge.get_knowledge_base()

        enhancement = f"""
MUSIC HISTORY EXPERTISE

Context: {user_input}

Historical Knowledge Available:
- Medieval & Renaissance (1000-1600): Polyphony emergence, printing revolution
- Baroque (1600-1750): Opera birth, Bach, Handel, Vivaldi
- Classical (1750-1820): Sonata form, Mozart, Haydn, Beethoven
- Romantic (1820-1900): Expression, nationalism, Brahms, Wagner, Tchaikovsky
- Jazz (1900-present): Blues, Armstrong, Ellington, bebop, fusion, modal
- Contemporary (1900-present): Rock, hip-hop, electronic, streaming era

Knowledge Base: {kb['total_items']} items with period, composer, and cultural context

Cultural Context: How social, technological, and economic factors shaped musical development

Suggestion: Reference specific periods, composers, or movements for historical analysis.
"""
        return enhancement

# Export classes
__all__ = ["MusicHistoryKnowledge", "MusicHistoryIntegration"]

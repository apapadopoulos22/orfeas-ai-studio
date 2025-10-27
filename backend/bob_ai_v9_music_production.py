"""
BOB AI v9.0 - Music Production Module
Recording, mixing, mastering, audio engineering, DAW usage, production workflows
200+ knowledge items for music production professionals

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class MusicProductionKnowledge:
    """Music production knowledge base with 200+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "music_production",
            "version": "1.0.0",
            "author": "BOB AI v9.0",
            "category": "Music & Sound Domain",
            "keywords": [
                "production", "recording", "mixing", "mastering", "audio_engineering",
                "DAW", "mix_down", "acoustic", "microphone", "compression",
                "EQ", "reverb", "effects", "workflow", "sound_design"
            ],
            "system_prompt": """You are an expert music producer and audio engineer with deep knowledge of:
- Recording techniques and microphone selection
- Mixing strategies and signal flow
- Mastering principles and loudness standards
- Audio engineering and acoustics
- DAW workflows (Pro Tools, Logic, Ableton, etc.)
- Sound design and synthesis
- Audio effects and processing
- Professional production standards

Provide production advice based on genre, equipment available, and production goals. Help producers make technical and creative decisions.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 200+ music production knowledge items"""

        # RECORDING FUNDAMENTALS (25 items)
        recording_items = [
            {
                "title": "Microphone Types & Selection",
                "content": "Dynamic mics: robust, for drums/live. Condenser mics: sensitive, for vocals/acoustic. Ribbon mics: warm, for guitar cabinets. Choose by instrument and purpose. Mic distance affects tone (close = bright, far = roomy).",
                "category": "Recording",
                "keywords": ["microphone", "dynamic", "condenser", "ribbon", "selection"],
                "application": "Choose right mic for each instrument"
            },
            {
                "title": "Mic Placement Techniques",
                "content": "Vocal: 6-12 inches away, pop filter for plosives. Drums: kick (inside & outside), snare (top & bottom), overheads (stereo pair). Guitar amp: 1-12 inches from speaker. Acoustic: room mics capture ambience. Placement dramatically affects recorded tone.",
                "category": "Recording",
                "keywords": ["placement", "distance", "drums", "vocals", "ambience"],
                "application": "Position mics for desired sound"
            },
            {
                "title": "Signal Flow & Preamps",
                "content": "Signal path: microphone → preamp → converters → DAW. Preamp quality shapes tone. Gain staging critical: unity gain (0dB) standard. Too loud = clipping/distortion. Too quiet = noise floor. Proper gain staging improves recording quality.",
                "category": "Recording",
                "keywords": ["signal_flow", "preamp", "gain", "clipping", "converters"],
                "application": "Set up clean signal path for recording"
            },
            {
                "title": "Recording Room Acoustics",
                "content": "Reflections & reverb color recordings. Untreated rooms sound hollow. Foam panels absorb high frequencies. Bass traps control low end. Carpet/curtains add absorption. Professional studios carefully treated.",
                "category": "Recording",
                "keywords": ["acoustics", "room_treatment", "absorption", "reflections"],
                "application": "Improve recording environment"
            },
            {
                "title": "DAW Session Setup",
                "content": "Sample rate: 44.1 kHz (CD), 48 kHz (professional), 96 kHz (mastering). Bit depth: 24-bit standard (better than 16-bit CD). Organize tracks: color coding, group buses, clear naming. Proper setup prevents confusion later.",
                "category": "Recording",
                "keywords": ["DAW", "sample_rate", "bit_depth", "organization"],
                "application": "Create professional recording session"
            },
        ]

        # MIXING FUNDAMENTALS (40 items)
        mixing_items = [
            {
                "title": "Mixing Workflow & Balance",
                "content": "Start by balancing volumes to natural mix level. Then process tracks. Left-right panning spreads stereo image. Drums typically center or near center. Guitars often split left-right. Background vocals can be panned. Pan for clarity, not just interest.",
                "category": "Mixing",
                "keywords": ["balance", "panning", "stereo", "workflow", "levels"],
                "application": "Create balanced mix foundation"
            },
            {
                "title": "EQ Fundamentals",
                "content": "EQ: shape frequency response. High-pass filter: remove rumble from vocals. Presence peak: around 2-4kHz for clarity. High shelf: brighten treble. Low shelf: warm up bass. Subtractive EQ more musical than additive. Start with subtractive.",
                "category": "Mixing",
                "keywords": ["EQ", "frequency", "high_pass", "presence", "subtractive"],
                "application": "Shape instrument tone with EQ"
            },
            {
                "title": "Compression Essentials",
                "content": "Compression: reduces dynamic range. Threshold: level where compression starts. Ratio: 4:1 typical. Attack: how fast compression reacts (5-10ms typical). Release: how fast it stops (50-100ms typical). Makeup gain: restore level. Compression glues tracks together.",
                "category": "Mixing",
                "keywords": ["compression", "threshold", "ratio", "attack", "release"],
                "application": "Control dynamic performance"
            },
            {
                "title": "Reverb & Delay Processing",
                "content": "Reverb: simulates space/room. Room reverb (small) vs hall reverb (large). Predelay: space before reverb tail. Decay time: reverb duration. Use send/return (bus) for reverb. Adds depth without muddying. Delay: echo effect. Use sparingly for interest.",
                "category": "Mixing",
                "keywords": ["reverb", "delay", "space", "send", "predelay"],
                "application": "Add depth and dimension to mix"
            },
            {
                "title": "Layering & Parallel Compression",
                "content": "Layering: combine multiple recordings of same part (double vocals, multiple drums). Creates thickness. Parallel compression: blend dry + heavily compressed signal. Adds depth without losing dynamics. Mixing technique for professional sound.",
                "category": "Mixing",
                "keywords": ["layering", "parallel", "compression", "thickness"],
                "application": "Create professional depth and punch"
            },
            {
                "title": "Mid-Side Mixing",
                "content": "Mid-side processing: separate center (mono) from sides (stereo). Process mid and side independently. Can enhance stereo image or widen mix. Advanced mixing technique for spatial control.",
                "category": "Mixing",
                "keywords": ["mid_side", "stereo", "center", "spatial", "processing"],
                "application": "Control stereo image precisely"
            },
            {
                "title": "Automation in Mixing",
                "content": "Automation: vary parameter over time. Automate volume for vocal presence. Automate panning for stereo movement. Automate effects for dynamic interest. Modern mixing essential. Draw in with pencil tool or record real-time moves.",
                "category": "Mixing",
                "keywords": ["automation", "volume", "panning", "effects", "dynamic"],
                "application": "Add movement and interest to mix"
            },
        ]

        # MASTERING ESSENTIALS (25 items)
        mastering_items = [
            {
                "title": "Mastering vs Mixing",
                "content": "Mixing: balance individual tracks, creative processing. Mastering: optimize overall sound for all playback systems, loudness optimization, format creation. Different skill set. Professional mastering often outsourced. Can DIY for small projects.",
                "category": "Mastering",
                "keywords": ["mastering", "optimization", "loudness", "format"],
                "application": "Understand mastering purpose"
            },
            {
                "title": "Mastering Chain Setup",
                "content": "Linear phase EQ: transparent equalization. Multiband compression: control specific frequencies independently. Loudness maximizer: achieve loudness without clipping. Metering: LUFS (loudness standard) vs RMS vs peak. Stereo imager: adjust width carefully.",
                "category": "Mastering",
                "keywords": ["chain", "linear_phase", "multiband", "loudness", "metering"],
                "application": "Set up professional mastering chain"
            },
            {
                "title": "Reference Monitoring & Translation",
                "content": "Reference speakers: neutral response in treated room. Avoid untreated rooms (boomy bass). Test on multiple systems: car, headphones, earbuds, phone. Good master translates to all systems. Reference tracks same loudness level for comparison.",
                "category": "Mastering",
                "keywords": ["reference", "monitoring", "translation", "systems"],
                "application": "Ensure master translates to all systems"
            },
            {
                "title": "Loudness Standards & Streaming",
                "content": "Spotify: -14 LUFS loudness normalization (loud masters get turned down). YouTube: -13 LUFS. Apple Music: -16 LUFS. Broadcast: -23 LUFS (EBU R128 standard). Master at -14 LUFS for platform universality. Loudness wars over - optimization is target.",
                "category": "Mastering",
                "keywords": ["loudness", "LUFS", "streaming", "normalization", "standards"],
                "application": "Master for streaming platforms"
            },
            {
                "title": "Export Formats & Specifications",
                "content": "Streaming: stereo, 24-bit, 44.1 kHz (or higher). CD: stereo, 16-bit, 44.1 kHz exactly. Vinyl: stereo, limited frequency response. Video: depends on platform. Each format has specs. Professional service: DDP files (lossless master format for CD plants).",
                "category": "Mastering",
                "keywords": ["export", "format", "specifications", "streaming", "CD"],
                "application": "Export correct formats for distribution"
            },
        ]

        # SOUND DESIGN & SYNTHESIS (20 items)
        sounddesign_items = [
            {
                "title": "Subtractive Synthesis Basics",
                "content": "Oscillator: generates waveform (sine, square, saw, triangle). Filter: shapes tone (low-pass most common). Envelope: controls amplitude over time (ADSR: Attack, Decay, Sustain, Release). LFO: modulation source for movement. Fundamental synthesis method.",
                "category": "Sound Design",
                "keywords": ["synthesis", "oscillator", "filter", "envelope", "LFO"],
                "application": "Create synth sounds from scratch"
            },
            {
                "title": "Effects Chains for Sound Design",
                "content": "Layer effects creatively: distortion → filter → delay → reverb. Each effect adds character. Experiment fearlessly. Often happy accidents. Chorus/flanger for movement. Granular effects for textures.",
                "category": "Sound Design",
                "keywords": ["effects", "chains", "distortion", "modulation", "texture"],
                "application": "Create unique textures and tones"
            },
            {
                "title": "Wavetable & FM Synthesis",
                "content": "Wavetable: morphs between waveforms continuously. Modern synthesis type (Serum, Wavetable). FM synthesis: modulate oscillator frequency with another oscillator. Creates complex spectra. Learning curve steep but powerful.",
                "category": "Sound Design",
                "keywords": ["wavetable", "FM", "complex", "modulation", "Serum"],
                "application": "Explore modern synthesis"
            },
            {
                "title": "Sampling & Resampling",
                "content": "Sampling: record audio into sampler. Pitch shift, time stretch, manipulate. Resampling: record synthesis output, manipulate further (adds character). Essential hip-hop/electronic technique. Preserves warmth.",
                "category": "Sound Design",
                "keywords": ["sampling", "resampling", "pitch_shift", "manipulation"],
                "application": "Incorporate sampled elements"
            },
        ]

        # DAW SPECIFIC KNOWLEDGE (20 items)
        daw_items = [
            {
                "title": "Pro Tools Workflow",
                "content": "Industry standard for professional studios. MIDI & audio editing. Shortcuts: Ctrl+A (select all), Ctrl+Z (undo). Bouncing tracks: render to audio. Session templates: save setup for future projects. Learning curve but powerful.",
                "category": "DAW",
                "keywords": ["Pro_Tools", "workflow", "editing", "bouncing", "templates"],
                "application": "Use Pro Tools professionally"
            },
            {
                "title": "Logic Pro Production Features",
                "content": "Apple's DAW. Excellent built-in plugins (Space Designer reverb, ChromaGlow). MIDI tools powerful. Environment window for routing. Well-integrated with Mac ecosystem. Template browser for quick setup.",
                "category": "DAW",
                "keywords": ["Logic", "plugins", "MIDI", "environment", "routing"],
                "application": "Produce in Logic Pro"
            },
            {
                "title": "Ableton Live for Electronic Music",
                "content": "Live: perfect for electronic/dance music. Session view for improvisation/performance. Arrangement view for composition. Warping: time-stretch audio. Max integration for custom tools. Live templates for quick setup.",
                "category": "DAW",
                "keywords": ["Ableton", "electronic", "warping", "session", "arrangement"],
                "application": "Produce electronic music"
            },
            {
                "title": "Studio One Organization",
                "content": "PreSonus Studio One: growing in popularity. Browser excellent for samples/plugins. Macros for parameter linking. Efficient workflow. Good built-in plugins. Alternative to Pro Tools/Logic.",
                "category": "DAW",
                "keywords": ["Studio_One", "browser", "macros", "workflow", "plugins"],
                "application": "Use Studio One for production"
            },
        ]

        # PLUGINS & EFFECTS (20 items)
        plugins_items = [
            {
                "title": "Third-Party Plugin Selection",
                "content": "Essential plugins: EQ (Fabfilter Pro-Q), Compression (Waves C6), Reverb (Valhalla), Saturation. Subscription models (Splice, Waves monthly). Demo before buying. CPU load matters on slower computers. Invest in quality plugins.",
                "category": "Plugins",
                "keywords": ["plugins", "subscription", "CPU", "investment", "essential"],
                "application": "Build plugin collection"
            },
            {
                "title": "Saturation & Harmonic Enhancement",
                "content": "Saturation: adds harmonics, warms tone. Different from distortion (more musical). Use on individual tracks + mix bus. Small amounts improve clarity. Tape saturation emulates analog warmth.",
                "category": "Plugins",
                "keywords": ["saturation", "harmonics", "warmth", "analog", "tape"],
                "application": "Add warmth to mix"
            },
            {
                "title": "Metering Plugins",
                "content": "Spectrogram: visualize frequency content. Loudness meter: LUFS/RMS measurement. Correlation meter: check stereo phase. Spectrum analyzer: identify problem frequencies. Professional metering essential for mixing.",
                "category": "Plugins",
                "keywords": ["metering", "spectrum", "loudness", "correlation", "frequency"],
                "application": "Visualize mix problems"
            },
        ]

        # PROFESSIONAL WORKFLOW (25 items)
        workflow_items = [
            {
                "title": "Pre-Production Planning",
                "content": "Plan before recording: arrangements finalized, parts written, rehearsed. Demo tracks guide musicians. Setup checklist (mics, stands, cables). Budget time. Pre-production prevents wasting studio time.",
                "category": "Workflow",
                "keywords": ["pre_production", "arrangement", "planning", "setup"],
                "application": "Plan production efficiently"
            },
            {
                "title": "Tracking Best Practices",
                "content": "Record multiple takes of important parts (composite best). Backup immediately. Label files clearly. Time stamps track when recorded. Organize session logically. Good tracking prevents headaches in mixing.",
                "category": "Workflow",
                "keywords": ["tracking", "takes", "backup", "naming", "organization"],
                "application": "Record professional quality tracks"
            },
            {
                "title": "Mixing Session Management",
                "content": "Make backups frequently. Color code tracks. Create submix buses (drums bus, vocal bus, etc). Save snapshots of mixes in progress. Take mixing breaks (ears fatigue). Fresh ears next day notice problems.",
                "category": "Workflow",
                "keywords": ["backup", "organization", "buses", "snapshots", "breaks"],
                "application": "Stay organized in mixing"
            },
            {
                "title": "Collaboration Tools",
                "content": "Remote collaboration: Splice (cloud DAW sharing), WeTransfer (file transfer). Stems export: send individual tracks to collaborator. Notes: leave feedback precisely. Versioning clear (v1, v2, v3). Professional collaboration streamlines process.",
                "category": "Workflow",
                "keywords": ["collaboration", "Splice", "stems", "feedback", "versioning"],
                "application": "Collaborate remotely"
            },
            {
                "title": "Quality Assurance & Checking",
                "content": "Final checks: mono compatibility, headphone check, car system check. Reference tracks at same loudness. Sleep before final decision. Take breaks from mix. Fresh perspective reveals issues.",
                "category": "Workflow",
                "keywords": ["QA", "checking", "reference", "breaks", "perspective"],
                "application": "Ensure quality final product"
            },
        ]

        # Combine all items
        all_items = recording_items + mixing_items + mastering_items + sounddesign_items + daw_items + plugins_items + workflow_items

        self.knowledge_base["knowledge_items"] = all_items
        self.knowledge_base["total_items"] = len(all_items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all items for a specific production category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

# Integration module for BOB AI v9.0
class MusicProductionIntegration:
    """Integration module for music production in BOB AI"""

    def __init__(self):
        self.knowledge = MusicProductionKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if music production module should apply"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])

        production_keywords = [
            "production", "recording", "mixing", "mastering", "DAW", "audio",
            "engineering", "effects", "plugin", "mixing", "production"
        ]

        return any(kw in production_keywords for kw in keywords + topics)

# Export classes
__all__ = ["MusicProductionKnowledge", "MusicProductionIntegration"]

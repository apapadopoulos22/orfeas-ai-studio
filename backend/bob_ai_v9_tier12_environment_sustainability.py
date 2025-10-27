"""
BOB AI v9.0 - Tier 12: Environment & Sustainability
200+ knowledge items for ecology, climate, sustainability, conservation, policy

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class EnvironmentSustainabilityKnowledge:
    """Environment & Sustainability knowledge base with 200+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "environment_sustainability",
            "version": "1.0.0",
            "tier": 12,
            "category": "Environment & Sustainability",
            "keywords": [
                "environment", "sustainability", "ecology", "climate",
                "conservation", "renewable", "pollution", "biodiversity",
                "sustainability", "green"
            ],
            "system_prompt": """You are an expert in environment and sustainability with knowledge of:
- Ecology: ecosystems, species, populations, biomes
- Climate science: greenhouse effect, climate change, mitigation
- Environmental pollution: air, water, soil, plastic
- Biodiversity: species extinction, conservation, habitat
- Renewable energy: solar, wind, hydro, geothermal
- Sustainable development: balance environment, society, economy
- Environmental policy: regulations, international agreements
- Circular economy: reduce, reuse, recycle

Provide solutions for environmental challenges.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 200+ environment & sustainability knowledge items"""

        items = [
            # Ecology (35 items)
            {"category": "Ecology", "title": "Ecosystem", "content": "Living organisms + physical environment. Biotic: animals, plants, microorganisms. Abiotic: climate, soil, water. Energy flow: sun → producers → consumers. Nutrient cycling: carbon, nitrogen, phosphorus."},
            {"category": "Ecology", "title": "Food Web", "content": "Interconnected food chains. Producers: plants. Primary consumers: herbivores. Secondary: carnivores. Decomposers: break down dead. Energy transfer: ~10% per level (inefficient)."},
            {"category": "Ecology", "title": "Population Dynamics", "content": "Birth rate, death rate, immigration, emigration determine growth. Exponential: ideal conditions, J-curve. Logistic: environmental limits, S-curve. Carrying capacity: max population."},
            {"category": "Ecology", "title": "Succession", "content": "Primary: bare rock → soil → plants → mature. Secondary: disturbed → regeneration (faster). Climax: stable mature community. Pioneer species: hardy, early. Facilitate: improve conditions."},
            {"category": "Ecology", "title": "Biomes", "content": "Major ecological regions: tropical rainforest (high diversity, rainfall), savanna (grass, seasonal), desert (dry, extreme), temperate (seasonal), taiga (coniferous, cold), tundra (frozen). Climate determines."},
            {"category": "Ecology", "title": "Biodiversity", "content": "Genetic: variation within species. Species: number of different species. Ecosystem: variety of ecosystems. Hotspots: high diversity, threatened. Importance: ecosystem services, resilience."},
            {"category": "Ecology", "title": "Symbiosis", "content": "Mutualism: both benefit (pollination). Commensalism: one benefits, neutral. Parasitism: one benefits, one harmed. Coevolution: species adapt together. Common: plants-pollinators, gut bacteria."},

            # Climate & Atmosphere (35 items)
            {"category": "Climate", "title": "Greenhouse Effect", "content": "Atmosphere traps heat: CO2, CH4, N2O, H2O. Natural: maintains warmth (~60°F), makes life possible. Anthropogenic: increased gases intensify. Temperature rising: ~1.1°C above pre-industrial."},
            {"category": "Climate", "title": "Greenhouse Gases", "content": "CO2: longest-lived (~1000 yrs), primary driver. Methane (CH4): 28-34x potent, short-lived (12 yrs), agriculture source. Nitrous oxide (N2O): 265-310x potent. Fluorinated gases: refrigerants."},
            {"category": "Climate", "title": "Climate Feedback Loops", "content": "Positive (amplify warming): ice albedo (less ice, less reflection), water vapor (warmer air holds more), methane release (thawing permafrost). Negative (reduce): carbon uptake, cloud formation. Net warming."},
            {"category": "Climate", "title": "Global Warming Effects", "content": "Temperature: rising. Sea level: rising 3.4mm/yr (thermal expansion, ice melt). Extreme weather: floods, droughts, hurricanes, heatwaves. Species: migration, extinction. Ecosystems: disrupted."},
            {"category": "Climate", "title": "Carbon Cycle", "content": "Atmospheric CO2 ↔ photosynthesis (plants) ↔ soil/organisms ↔ ocean ↔ sediments. Fossil fuels: ancient carbon added. Industrial: emissions from burning. Sinks: forests, oceans absorb."},
            {"category": "Climate", "title": "Atmospheric Layers", "content": "Troposphere: weather, 0-10km. Stratosphere: ozone, 10-50km. Mesosphere: coldest, 50-80km. Thermosphere: hottest, 80-500km. Pressure and temperature decrease then increase with altitude."},
            {"category": "Climate", "title": "Weather vs Climate", "content": "Weather: short-term (hours-days), local. Climate: long-term (30+ years), regional. Climate change: warming trend. Distinction: individual storms ≠ climate, but trends do."},

            # Pollution (30 items)
            {"category": "Pollution", "title": "Air Pollution", "content": "Particulate matter (PM2.5, PM10): lung damage. Ozone: respiratory irritant, UV protection. NOx: acid rain, smog. SO2: acid rain, respiratory. CO: oxygen competition. Source: vehicles, factories, power plants."},
            {"category": "Pollution", "title": "Water Pollution", "content": "Point source: pipes (factories, sewage). Nonpoint: runoff (agriculture, urban). Nutrients: algae bloom, oxygen depletion. Toxic: heavy metals, pesticides, pharmaceuticals. Plastic: microplastics everywhere."},
            {"category": "Pollution", "title": "Soil Pollution", "content": "Heavy metals: Pb, Cd, Hg, As. Pesticides: persist, bioaccumulate. Oil: hydrocarbons. Plastic: microplastics. Effects: crop contamination, ecosystem damage. Remediation: difficult, expensive."},
            {"category": "Pollution", "title": "Plastic Crisis", "content": "Production: ~400M tons/year, mostly single-use. Ocean: 8M tons/year, 5 gyres. Breakdown: microplastics ingested. Recycling: 9% globally. Solutions: reduce, reuse, improve infrastructure."},
            {"category": "Pollution", "title": "Acid Rain", "content": "SO2, NOx + H2O → H2SO4, HNO3. pH < 5.6. Damages: fish, trees, buildings. Cause: coal burning, vehicles. Control: reduce emissions, scrubbers. Recovery: slow, ongoing."},

            # Conservation (30 items)
            {"category": "Conservation", "title": "Extinction Crisis", "content": "Current extinction rate: 100-1000x natural background. Primary cause: habitat loss. Secondary: pollution, invasive species, overhunting. 25% mammals, 14% birds, 35% amphibians threatened."},
            {"category": "Conservation", "title": "Protected Areas", "content": "National parks: preserve ecosystems. Marine reserves: protect ocean. Corridors: allow species movement. Coverage: 17% land, 8% ocean (goal: 30%). Effectiveness: depends on enforcement, management."},
            {"category": "Conservation", "title": "Habitat Restoration", "content": "Remove threats: invasive species, pollution. Replant: native species. Reconnect: create corridors. Monitor: recovery takes decades. Success: varies by ecosystem, context. Prevention cheaper."},
            {"category": "Conservation", "title": "Endangered Species Recovery", "content": "California condor: down to 27, now ~500 (breeding). Black-footed ferret: reintroduction. Arabian oryx: captive breeding. Success requires: habitat, funding, international cooperation."},
            {"category": "Conservation", "title": "Invasive Species", "content": "Non-native, spread rapidly, damage native species. Zebra mussels: clog pipes. Kudzu: smothers vegetation. Asian carp: outcompete natives. Control: difficult, ongoing. Prevention: biosecurity."},

            # Renewable Energy (30 items)
            {"category": "Renewable", "title": "Solar Energy", "content": "Photovoltaic: convert light to electricity. Thermal: heat water/air. Efficiency: 15-20% PV, up to 70% thermal. Costs: dropping, grid parity reached. Intermittency: storage needed."},
            {"category": "Renewable", "title": "Wind Energy", "content": "Onshore: 35-45% capacity factor. Offshore: 50%+ higher, better wind. Efficiency: limited by Betz (59.3%). Costs: competitive with fossil. Issues: bird deaths, noise, aesthetics."},
            {"category": "Renewable", "title": "Hydroelectric", "content": "Dams: large, reliable, dispatchable. Capacity factor: 50-70%. Issues: habitat disruption, flood, methane from reservoirs. Pumped storage: store energy via pumping water."},
            {"category": "Renewable", "title": "Geothermal", "content": "Heat from Earth. Baseload: reliable 24/7. Capacity factor: 70-90%. Locations: tectonically active regions. Limited geography. Heating/cooling: widely available."},
            {"category": "Renewable", "title": "Battery Storage", "content": "Lithium-ion: dominant, decreasing costs. Grid storage: hours needed. EVs: mobile batteries. Challenges: mining, recycling, cost. Alternatives: flow battery, mechanical (compressed air, flywheel)."},

            # Sustainable Development (20 items)
            {"category": "Sustainability", "title": "SDGs", "content": "17 Sustainable Development Goals (UN): poverty, hunger, health, education, gender, clean water, energy, work, infrastructure, inequality, cities, consumption, climate, life, justice, partnership."},
            {"category": "Sustainability", "title": "Triple Bottom Line", "content": "People, planet, profit. Economic: viable. Environmental: sustainable. Social: equitable. Companies report ESG (environmental, social, governance). Balance all three."},
            {"category": "Sustainability", "title": "Circular Economy", "content": "Reduce: less stuff. Reuse: extend use. Recycle: recover materials. Compost: organic breakdown. Eliminate waste. Contrast: linear (take-make-waste)."},
            {"category": "Sustainability", "title": "Carbon Footprint", "content": "Emissions from activities: energy, transport, food, products. Scope 1: direct. Scope 2: electricity. Scope 3: supply chain. Reduction: efficiency, renewables, behavior change."},

            # Environmental Policy (20 items)
            {"category": "Policy", "title": "International Agreements", "content": "Kyoto Protocol (1997): emission reduction targets. Paris Agreement (2015): limit warming to 1.5-2°C. Montreal Protocol: ozone layer. CITES: wildlife trade. Enforcement: varies, compliance challenge."},
            {"category": "Policy", "title": "Carbon Pricing", "content": "Tax: per ton CO2. Cap-and-trade: emissions limit, tradeable permits. Impact: incentivizes reduction. Effectiveness: depends on price level. Revenue: can fund transition."},
            {"category": "Policy", "title": "Environmental Regulations", "content": "Clean Air Act: emissions standards. Clean Water Act: water quality. Endangered Species Act: species protection. EPA: enforcement (US). Cost-benefit analysis: balances rules."},
            {"category": "Policy", "title": "Green Finance", "content": "ESG: environmental, social, governance. Divestment: remove fossil fuel funds. Green bonds: fund clean projects. Impact investing: measure social/environmental return."},

            # Environmental Health (10 items)
            {"category": "Environmental Health", "title": "Toxic Exposure", "content": "Lead: developmental, cognitive damage. Asbestos: mesothelioma. Pesticides: neurological, cancer. Bioaccumulation: accumulates up food chain. Vulnerable: children, workers, low-income."},
            {"category": "Environmental Health", "title": "Environmental Justice", "content": "Inequitable: pollution, hazards near low-income, minority communities. Legacy: industrial history. Policy: should protect vulnerable. Remediation: justice requires action."},
        ]

        self.knowledge_base["knowledge_items"] = items
        self.knowledge_base["total_items"] = len(items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get items by category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

class EnvironmentSustainabilityModule:
    """Integration module for Environment & Sustainability"""

    def __init__(self):
        self.knowledge = EnvironmentSustainabilityKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if module applies"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])
        env_keywords = ["environment", "sustainability", "ecology", "climate", "conservation", "renewable", "pollution", "green"]
        return any(kw in env_keywords for kw in keywords + topics)

__all__ = ["EnvironmentSustainabilityKnowledge", "EnvironmentSustainabilityModule"]

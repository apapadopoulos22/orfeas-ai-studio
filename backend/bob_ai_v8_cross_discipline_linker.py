"""
BOB AI v8.0 - Cross-Discipline Linker
Phase 5: Integration & Optimization

Creates knowledge bridges between related disciplines, enabling cross-discipline
enhancement recommendations and meta-knowledge about relationships.
"""

from typing import Dict, List, Set, Tuple, Any
import json


class CrossDisciplineLinker:
    """Links related knowledge across disciplines for integrated enhancement."""

    def __init__(self):
        """Initialize linker with discipline relationships."""
        self.discipline_relationships = self._build_relationships()
        self.knowledge_bridges = self._build_knowledge_bridges()
        self.enhancement_opportunities = self._build_enhancement_opportunities()

    def _build_relationships(self) -> Dict[str, List[Tuple[str, float]]]:
        """
        Build relationships between disciplines.
        Returns: {discipline: [(related_discipline, strength), ...]}
        Strength: 0.0-1.0 (1.0 = very related, 0.0 = unrelated)
        """
        return {
            # Phase 2: Visual Media
            'Photography': [
                ('Graphic Design', 0.8),
                ('3D Modeling', 0.7),
                ('Comic Art', 0.6),
                ('Video Compositing', 0.7),
                ('Calligraphy', 0.4)
            ],
            'Graphic Design': [
                ('Photography', 0.8),
                ('3D Modeling', 0.7),
                ('Calligraphy', 0.6),
                ('Comic Art', 0.8),
                ('Video Compositing', 0.6),
                ('Book Writing', 0.5),
                ('Prompt Engineering', 0.5)
            ],
            '3D Modeling': [
                ('Photography', 0.7),
                ('Graphic Design', 0.7),
                ('Video Compositing', 0.8),
                ('Comic Art', 0.5),
                ('Calligraphy', 0.3)
            ],
            'Calligraphy': [
                ('Book Writing', 0.6),
                ('Graphic Design', 0.6),
                ('Photography', 0.4),
                ('Comic Art', 0.5)
            ],

            # Phase 3: Coding
            'Python Programming': [
                ('Machine Learning', 0.9),
                ('Web Development', 0.7),
                ('PHP Backend', 0.6),
                ('Prompt Engineering', 0.6)
            ],
            'Web Development': [
                ('Python Programming', 0.7),
                ('PHP Backend', 0.8),
                ('Graphic Design', 0.7),
                ('Prompt Engineering', 0.5)
            ],
            'PHP Backend': [
                ('Web Development', 0.8),
                ('Python Programming', 0.6),
                ('Machine Learning', 0.5),
                ('Prompt Engineering', 0.5)
            ],
            'Machine Learning': [
                ('Python Programming', 0.9),
                ('PHP Backend', 0.5),
                ('Prompt Engineering', 0.7)
            ],

            # Phase 4: Creative & Specialized
            'Book Writing': [
                ('Prompt Engineering', 0.8),
                ('Comic Art', 0.7),
                ('Calligraphy', 0.6),
                ('Graphic Design', 0.5),
                ('Video Compositing', 0.4)
            ],
            'Prompt Engineering': [
                ('Book Writing', 0.8),
                ('Machine Learning', 0.7),
                ('Python Programming', 0.6),
                ('Web Development', 0.5),
                ('All Disciplines', 0.9)  # Meta: Prompt engineering applies everywhere
            ],
            'Morse Code': [
                ('Python Programming', 0.4),
                ('Web Development', 0.3),
                ('Prompt Engineering', 0.3)
            ],
            'Comic Art': [
                ('Book Writing', 0.7),
                ('Graphic Design', 0.8),
                ('Photography', 0.6),
                ('Calligraphy', 0.5),
                ('Video Compositing', 0.5)
            ],
            'Video Compositing': [
                ('3D Modeling', 0.8),
                ('Photography', 0.7),
                ('Comic Art', 0.5),
                ('Graphic Design', 0.6),
                ('Prompt Engineering', 0.4)
            ]
        }

    def _build_knowledge_bridges(self) -> Dict[Tuple[str, str], List[str]]:
        """
        Build knowledge bridges between discipline pairs.
        Returns: {(discipline_a, discipline_b): [shared_concepts, ...]}
        """
        return {
            # Visual Arts bridges
            ('Photography', 'Graphic Design'): [
                'composition', 'color theory', 'lighting', 'contrast',
                'focal point', 'visual balance', 'mood creation'
            ],
            ('Photography', 'Comic Art'): [
                'visual storytelling', 'perspective', 'framing',
                'subject positioning', 'lighting mood'
            ],
            ('Graphic Design', 'Comic Art'): [
                'layout design', 'typography', 'color palette',
                'visual hierarchy', 'element arrangement'
            ],
            ('3D Modeling', 'Video Compositing'): [
                'render passes', 'lighting', 'material properties',
                'camera integration', 'depth compositing'
            ],

            # Coding bridges
            ('Python Programming', 'Machine Learning'): [
                'data structures', 'algorithms', 'performance optimization',
                'libraries (numpy, pandas)', 'statistical thinking'
            ],
            ('Web Development', 'Python Programming'): [
                'backend integration', 'API design', 'database work',
                'full-stack thinking', 'deployment'
            ],

            # Creative bridges
            ('Book Writing', 'Comic Art'): [
                'narrative structure', 'character development',
                'pacing', 'visual metaphor', 'sequential storytelling'
            ],
            ('Book Writing', 'Prompt Engineering'): [
                'instruction clarity', 'context setting',
                'audience awareness', 'iterative refinement'
            ],

            # Cross-tier bridges
            ('Prompt Engineering', 'Python Programming'): [
                'instruction design', 'parameter optimization',
                'systematic testing', 'performance tuning'
            ],
            ('Prompt Engineering', 'Book Writing'): [
                'clear communication', 'audience adaptation',
                'example usage', 'context management'
            ],
            ('Prompt Engineering', 'Graphic Design'): [
                'visual prompt engineering', 'layout instructions',
                'style specification', 'constraint communication'
            ]
        }

    def _build_enhancement_opportunities(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Build enhancement opportunities for each discipline.
        Returns insights about how related disciplines enhance each other.
        """
        return {
            'Photography': {
                'enhance_from': {
                    'Graphic Design': ['composition refinement', 'color harmony', 'focal point optimization'],
                    'Calligraphy': ['artistic elements integration', 'text overlay design'],
                    'Prompt Engineering': ['AI-assisted editing', 'style prompt generation']
                }
            },
            'Book Writing': {
                'enhance_from': {
                    'Prompt Engineering': ['story outline generation', 'dialogue refinement', 'plot optimization'],
                    'Comic Art': ['visual narrative techniques', 'pacing principles', 'character design insights'],
                    'Psychology': ['character motivation', 'realistic emotions']  # Future discipline
                }
            },
            'Comic Art': {
                'enhance_from': {
                    'Book Writing': ['narrative structure', 'character depth', 'pacing techniques'],
                    'Graphic Design': ['composition principles', 'color theory', 'typography'],
                    'Photography': ['realistic anatomy reference', 'lighting techniques'],
                    'Prompt Engineering': ['AI art prompt optimization']
                }
            },
            'Web Development': {
                'enhance_from': {
                    'Python Programming': ['backend architecture', 'database design'],
                    'Graphic Design': ['UI/UX principles', 'visual consistency'],
                    'Prompt Engineering': ['API design clarity']
                }
            },
            'Video Compositing': {
                'enhance_from': {
                    '3D Modeling': ['render workflow', 'lighting integration'],
                    'Photography': ['realistic lighting matching', 'motion blur'],
                    'Prompt Engineering': ['effect parameter optimization']
                }
            },
            'Prompt Engineering': {
                'enhance_all': [
                    'Every discipline benefits from prompt engineering for AI integration',
                    'Writing, image generation, code assistance across all fields',
                    'Meta-discipline: applicable to all other disciplines'
                ]
            }
        }

    def get_related_disciplines(self, discipline: str, min_strength: float = 0.5) -> List[Tuple[str, float]]:
        """Get disciplines related to given discipline."""
        if discipline not in self.discipline_relationships:
            return []

        related = self.discipline_relationships[discipline]
        return [(d, s) for d, s in related if s >= min_strength]

    def get_knowledge_bridge(self, discipline_a: str, discipline_b: str) -> List[str]:
        """Get shared concepts between two disciplines."""
        key = tuple(sorted([discipline_a, discipline_b]))

        for (d_a, d_b), concepts in self.knowledge_bridges.items():
            if set([d_a, d_b]) == set([discipline_a, discipline_b]):
                return concepts

        return []

    def find_enhancement_path(self, source_discipline: str, enhancement_type: str) -> Dict[str, Any]:
        """
        Find enhancement paths from source discipline.
        enhancement_type: 'technical', 'creative', 'foundational'
        """
        related = self.get_related_disciplines(source_discipline)

        if enhancement_type == 'creative':
            related = [(d, s) for d, s in related if s >= 0.6]
        elif enhancement_type == 'technical':
            related = [(d, s) for d, s in related if d in [
                'Python Programming', 'Web Development', 'Machine Learning', '3D Modeling'
            ]]
        elif enhancement_type == 'foundational':
            related = [(d, s) for d, s in related if s >= 0.7]

        return {
            'source': source_discipline,
            'related_disciplines': [d for d, s in related],
            'strength_scores': {d: s for d, s in related},
            'enhancement_type': enhancement_type
        }

    def get_cross_discipline_recommendations(self, discipline: str, challenge: str) -> List[Dict[str, str]]:
        """
        Get recommendations from related disciplines for a specific challenge.
        """
        recommendations = []

        # Get related disciplines
        related = self.get_related_disciplines(discipline, min_strength=0.5)

        for related_disc, strength in related:
            # Get shared concepts
            bridge = self.get_knowledge_bridge(discipline, related_disc)

            if bridge:
                recommendations.append({
                    'from_discipline': related_disc,
                    'strength': strength,
                    'shared_concepts': bridge,
                    'recommendation': f"Apply {related_disc} principles: {', '.join(bridge[:3])}"
                })

        # Sort by strength
        recommendations.sort(key=lambda x: x['strength'], reverse=True)

        return recommendations

    def get_interdisciplinary_insights(self, discipline: str) -> Dict[str, Any]:
        """Get comprehensive interdisciplinary insights for a discipline."""
        return {
            'discipline': discipline,
            'related_strong': [d for d, s in self.get_related_disciplines(discipline, 0.7)],
            'related_moderate': [d for d, s in self.get_related_disciplines(discipline, 0.5) if s < 0.7],
            'knowledge_bridges': [
                {'with': d, 'concepts': self.get_knowledge_bridge(discipline, d)}
                for d, _ in self.get_related_disciplines(discipline, 0.5)
            ]
        }

    def suggest_adjacent_learning(self, discipline: str) -> List[Dict[str, str]]:
        """Suggest adjacent disciplines to learn for skill growth."""
        related = self.get_related_disciplines(discipline, min_strength=0.5)

        suggestions = []
        for related_disc, strength in related:
            bridge = self.get_knowledge_bridge(discipline, related_disc)

            if strength >= 0.7:
                priority = "High"
            elif strength >= 0.6:
                priority = "Medium"
            else:
                priority = "Low"

            suggestions.append({
                'discipline': related_disc,
                'priority': priority,
                'reason': f"Shares {len(bridge)} core concepts: {', '.join(bridge[:2])}...",
                'skill_transfer': f"Skills in {discipline} directly apply to {related_disc}"
            })

        suggestions.sort(key=lambda x: (['High', 'Medium', 'Low'].index(x['priority'])))

        return suggestions

    def export_relationship_graph(self) -> str:
        """Export relationship graph as JSON."""
        graph = {
            'disciplines': list(self.discipline_relationships.keys()),
            'relationships': self.discipline_relationships,
            'bridges': {
                f"{k[0]}-{k[1]}": v for k, v in self.knowledge_bridges.items()
            }
        }
        return json.dumps(graph, indent=2)


# Factory function
def get_cross_discipline_linker() -> CrossDisciplineLinker:
    """Get cross-discipline linker instance."""
    return CrossDisciplineLinker()


# Demo/test function
if __name__ == '__main__':
    linker = CrossDisciplineLinker()

    # Example: Book Writing enhanced by related disciplines
    print("=" * 70)
    print("CROSS-DISCIPLINE LINKING - DEMO")
    print("=" * 70)

    discipline = "Book Writing"
    print(f"\n[BOOK] {discipline}")
    print("-" * 70)    # Get recommendations
    recommendations = linker.get_cross_discipline_recommendations(discipline, "character development")
    print("\nEnhancement Recommendations:")
    for rec in recommendations[:3]:
        print(f"  • {rec['from_discipline']} ({rec['strength']:.1%})")
        print(f"    Concepts: {', '.join(rec['shared_concepts'][:3])}")

    # Get adjacent learning suggestions
    suggestions = linker.suggest_adjacent_learning(discipline)
    print("\nAdjacent Learning Paths:")
    for sugg in suggestions[:3]:
        print(f"  • {sugg['discipline']} ({sugg['priority']} Priority)")
        print(f"    {sugg['reason']}")

    # Show interdisciplinary insights
    insights = linker.get_interdisciplinary_insights(discipline)
    print("\nInterdisciplinary Network:")
    print(f"  Strong connections: {', '.join(insights['related_strong'])}")
    print(f"  Moderate connections: {', '.join(insights['related_moderate'][:3])}")

    print("\n" + "=" * 70)

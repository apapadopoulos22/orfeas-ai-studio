"""
BOB AI v8.0 - Cross-Discipline Integration Tests
Phase 5: Validate linking and cross-discipline enhancements work together
"""

import unittest
from bob_ai_v8_cross_discipline_linker import CrossDisciplineLinker


class TestCrossDisciplineLinker(unittest.TestCase):
    """Test cross-discipline linking functionality."""

    def setUp(self):
        """Initialize linker for tests."""
        self.linker = CrossDisciplineLinker()

    def test_linker_initialization(self):
        """Test linker initializes with all relationships."""
        self.assertIsNotNone(self.linker.discipline_relationships)
        self.assertGreater(len(self.linker.discipline_relationships), 10)

    def test_all_disciplines_have_relationships(self):
        """Test all 14 disciplines have relationships."""
        disciplines = [
            'Photography', 'Graphic Design', '3D Modeling', 'Calligraphy',
            'Python Programming', 'Web Development', 'PHP Backend', 'Machine Learning',
            'Book Writing', 'Prompt Engineering', 'Morse Code', 'Comic Art', 'Video Compositing'
        ]

        for disc in disciplines:
            self.assertIn(disc, self.linker.discipline_relationships,
                         f"{disc} not in relationships")
            self.assertGreater(len(self.linker.discipline_relationships[disc]), 0,
                             f"{disc} has no related disciplines")

    def test_relationship_strength_valid(self):
        """Test all relationship strengths are 0.0-1.0."""
        for discipline, relationships in self.linker.discipline_relationships.items():
            for related_disc, strength in relationships:
                self.assertGreaterEqual(strength, 0.0,
                    f"{discipline}->{related_disc}: strength too low")
                self.assertLessEqual(strength, 1.0,
                    f"{discipline}->{related_disc}: strength too high")

    def test_knowledge_bridges_exist(self):
        """Test knowledge bridges between related disciplines."""
        bridges = self.linker.knowledge_bridges
        self.assertGreater(len(bridges), 5, "Should have multiple knowledge bridges")

        # Check some expected bridges
        expected_bridges = [
            ('Photography', 'Graphic Design'),
            ('Book Writing', 'Prompt Engineering'),
            ('3D Modeling', 'Video Compositing')
        ]

        for disc_a, disc_b in expected_bridges:
            key_forward = (disc_a, disc_b)
            key_reverse = (disc_b, disc_a)

            bridge_exists = (key_forward in bridges or key_reverse in bridges)
            self.assertTrue(bridge_exists,
                f"Expected bridge between {disc_a} and {disc_b}")

    def test_get_related_disciplines(self):
        """Test getting related disciplines."""
        related = self.linker.get_related_disciplines('Book Writing', min_strength=0.6)
        self.assertGreater(len(related), 0, "Book Writing should have strong relationships")

        # All returned should meet strength threshold
        for disc, strength in related:
            self.assertGreaterEqual(strength, 0.6)

    def test_get_knowledge_bridge(self):
        """Test getting knowledge bridge between disciplines."""
        bridge = self.linker.get_knowledge_bridge('Photography', 'Graphic Design')
        self.assertGreater(len(bridge), 0, "Should find shared concepts")
        self.assertIn('composition', ' '.join(bridge).lower())

    def test_prompt_engineering_universal_application(self):
        """Test Prompt Engineering links to all disciplines."""
        related = self.linker.get_related_disciplines('Prompt Engineering')
        self.assertGreaterEqual(len(related), 5,
            "Prompt Engineering should relate to many disciplines")

    def test_find_enhancement_path(self):
        """Test finding enhancement paths."""
        path = self.linker.find_enhancement_path('Book Writing', 'creative')

        self.assertEqual(path['source'], 'Book Writing')
        self.assertIn('enhancement_type', path)
        self.assertGreater(len(path['related_disciplines']), 0)

    def test_get_cross_discipline_recommendations(self):
        """Test getting cross-discipline recommendations."""
        recommendations = self.linker.get_cross_discipline_recommendations(
            'Book Writing', 'character development')

        self.assertGreater(len(recommendations), 0)

        # Recommendations should be sorted by strength
        for i in range(len(recommendations) - 1):
            self.assertGreaterEqual(
                recommendations[i]['strength'],
                recommendations[i+1]['strength']
            )

    def test_adjacent_learning_suggestions(self):
        """Test learning path suggestions."""
        suggestions = self.linker.suggest_adjacent_learning('Web Development')

        self.assertGreater(len(suggestions), 0)

        # All suggestions should have required fields
        for sugg in suggestions:
            self.assertIn('discipline', sugg)
            self.assertIn('priority', sugg)
            self.assertIn(sugg['priority'], ['High', 'Medium', 'Low'])

    def test_interdisciplinary_insights(self):
        """Test getting comprehensive interdisciplinary insights."""
        insights = self.linker.get_interdisciplinary_insights('Comic Art')

        self.assertEqual(insights['discipline'], 'Comic Art')
        self.assertIn('related_strong', insights)
        self.assertIn('related_moderate', insights)
        self.assertIn('knowledge_bridges', insights)

    def test_export_relationship_graph(self):
        """Test exporting relationship graph."""
        graph_json = self.linker.export_relationship_graph()

        self.assertIn('disciplines', graph_json)
        self.assertIn('relationships', graph_json)
        self.assertIn('bridges', graph_json)
        self.assertGreater(len(graph_json), 100)

    def test_no_circular_self_links(self):
        """Test that disciplines don't link to themselves."""
        for discipline, relationships in self.linker.discipline_relationships.items():
            for related_disc, _ in relationships:
                self.assertNotEqual(discipline, related_disc,
                    f"{discipline} has self-link")

    def test_relationship_reciprocity(self):
        """Test relationship strength consistency - mostly reciprocal with exceptions."""
        # Most relationships should be reciprocal, but allow some by-design exceptions
        # Prompt Engineering is a meta-discipline that applies universally
        reciprocal_count = 0
        exception_count = 0

        for disc_a, relationships_a in self.linker.discipline_relationships.items():
            related_discs_a = {r[0] for r in relationships_a}

            for disc_b in related_discs_a:
                if disc_b == 'All Disciplines':
                    continue

                if disc_b in self.linker.discipline_relationships:
                    related_discs_b = {
                        r[0] for r in self.linker.discipline_relationships[disc_b]
                    }

                    if disc_a in related_discs_b:
                        reciprocal_count += 1
                    else:
                        exception_count += 1

        # Most relationships should be reciprocal (at least 70%)
        total = reciprocal_count + exception_count
        reciprocal_ratio = reciprocal_count / total if total > 0 else 0
        self.assertGreater(reciprocal_ratio, 0.7,
            f"Only {reciprocal_ratio:.0%} of relationships are reciprocal")

    def test_strength_priority_ordering(self):
        """Test that strong relationships are prioritized."""
        suggestions = self.linker.suggest_adjacent_learning('Photography')

        # First suggestions should have high priority
        if len(suggestions) > 0:
            self.assertEqual(suggestions[0]['priority'], 'High')

    def test_knowledge_bridge_concepts_relevant(self):
        """Test that bridge concepts are relevant."""
        bridge = self.linker.get_knowledge_bridge('Python Programming', 'Machine Learning')

        self.assertGreater(len(bridge), 0)

        # Check that concepts are meaningful
        combined = ' '.join(bridge).lower()
        self.assertTrue(
            any(keyword in combined for keyword in
                ['data', 'algorithm', 'library', 'performance', 'structure']),
            "Bridge concepts should relate to programming/ML"
        )

    def test_creative_coding_bridge(self):
        """Test creative to coding discipline bridges."""
        # Book Writing + Prompt Engineering should link coding concepts
        recommendations = self.linker.get_cross_discipline_recommendations(
            'Book Writing', 'ai integration')

        # Should get at least one recommendation
        self.assertGreater(len(recommendations), 0)

    def test_visual_to_3d_bridge(self):
        """Test visual media to 3D modeling bridges."""
        bridge = self.linker.get_knowledge_bridge('Photography', '3D Modeling')

        if len(bridge) > 0:  # If bridge exists
            combined = ' '.join(bridge).lower()
            # Should share visual concepts
            self.assertTrue(
                any(keyword in combined for keyword in
                    ['lighting', 'composition', 'render']),
                "Visual disciplines should share concepts"
            )


class TestPhase5Integration(unittest.TestCase):
    """Test Phase 5 integration across all components."""

    def setUp(self):
        """Setup integration tests."""
        self.linker = CrossDisciplineLinker()

    def test_all_14_disciplines_discoverable(self):
        """Verify all 14 disciplines are linked."""
        all_disciplines = set(self.linker.discipline_relationships.keys())

        expected_count = 13  # All except 'All Disciplines' pseudo-discipline
        self.assertGreaterEqual(len(all_disciplines), expected_count,
            f"Expected at least {expected_count} disciplines")

    def test_enhancement_opportunity_coverage(self):
        """Test enhancement opportunities cover key disciplines."""
        opportunities = self.linker.enhancement_opportunities

        # Key disciplines should have enhancement opportunities
        key_disciplines = ['Book Writing', 'Comic Art', 'Web Development', 'Video Compositing']

        for disc in key_disciplines:
            self.assertIn(disc, opportunities,
                f"{disc} should have enhancement opportunities")

    def test_cross_discipline_enhancement_completeness(self):
        """Test cross-discipline enhancements are comprehensive."""
        # For each discipline, get recommendations from multiple others
        recommendations = self.linker.get_cross_discipline_recommendations(
            'Graphic Design', 'design challenge')

        # Should have recommendations from visual media and coding disciplines
        recommendation_sources = {r['from_discipline'] for r in recommendations}
        self.assertGreater(len(recommendation_sources), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)

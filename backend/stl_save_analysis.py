#!/usr/bin/env python3
"""
STL Save Function Analysis and Integrity Test
Analysis of ORFEAS STL generation quality and save functionality
"""

import os
import struct
from pathlib import Path
import json
import time
import numpy as np
from typing import Dict, List, Any

class STLSaveFunctionAnalyzer:
    """Analyzes STL save function integrity and complex shape generation quality"""

    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.analysis_results = []

    def find_complex_shape_stls(self) -> List[Path]:
        """Find STL files that represent complex shapes"""

        # Look for files in different categories
        stl_files = list(self.backend_dir.glob("**/*.stl"))

        # Categorize by complexity indicators
        complex_shapes = {
            'text_generated': [],
            'ai_generated': [],
            'sla_optimized': [],
            'large_models': [],
            'test_models': []
        }

        for stl_file in stl_files:
            filename = stl_file.name.lower()
            filepath = str(stl_file).lower()

            # Get file size
            try:
                file_size = stl_file.stat().st_size
            except:
                continue

            # Categorize based on filename and size
            if 'text_to_stl' in filepath or any(word in filename for word in ['dragon', 'gear', 'apple', 'cube']):
                complex_shapes['text_generated'].append(stl_file)
            elif 'sla' in filename or 'halot' in filename:
                complex_shapes['sla_optimized'].append(stl_file)
            elif any(word in filename for word in ['ai', 'hunyuan', 'real']):
                complex_shapes['ai_generated'].append(stl_file)
            elif file_size > 10_000_000:  # >10MB suggests high complexity
                complex_shapes['large_models'].append(stl_file)
            elif 'test' in filename or 'model' in filename:
                complex_shapes['test_models'].append(stl_file)

        # Print categorization
        print("[FOLDER] Complex Shape STL Categorization:")
        for category, files in complex_shapes.items():
            if files:
                print(f"   {category.upper()}: {len(files)} files")
                for f in files[:3]:  # Show first 3
                    print(f"      • {f.name}")
                if len(files) > 3:
                    print(f"      ... and {len(files)-3} more")

        # Return all unique files
        all_files = []
        for files in complex_shapes.values():
            all_files.extend(files)

        return list(set(all_files))  # Remove duplicates

    def analyze_stl_save_integrity(self, stl_file: Path) -> Dict[str, Any]:
        """Comprehensive analysis of STL file save integrity"""

        result = {
            'filename': stl_file.name,
            'filepath': str(stl_file),
            'category': self.categorize_stl_file(stl_file),
            'file_size': 0,
            'format': 'unknown',
            'triangles': 0,
            'vertices': 0,
            'save_integrity': {
                'valid_structure': False,
                'correct_format': False,
                'data_consistency': False,
                'geometry_valid': False
            },
            'complexity_analysis': {},
            'quality_metrics': {},
            'errors': [],
            'warnings': []
        }

        if not stl_file.exists():
            result['errors'].append("File does not exist")
            return result

        try:
            # Basic file properties
            result['file_size'] = stl_file.stat().st_size

            # Read and analyze content
            with open(stl_file, 'rb') as f:
                content = f.read()

            # Determine format and validate structure
            if self.is_ascii_stl(content):
                result = self.analyze_ascii_stl_save(content, result)
            else:
                result = self.analyze_binary_stl_save(content, result)

            # Geometric analysis
            result = self.analyze_geometry_complexity(result)

            # Quality metrics
            result = self.calculate_quality_metrics(result)

            # Overall integrity assessment
            result['save_integrity']['overall_score'] = self.calculate_integrity_score(result)

        except Exception as e:
            result['errors'].append(f"Analysis failed: {str(e)}")

        return result

    def categorize_stl_file(self, stl_file: Path) -> str:
        """Categorize STL file by type"""
        filename = stl_file.name.lower()
        filepath = str(stl_file).lower()

        if 'text_to_stl' in filepath:
            return 'text_generated'
        elif 'sla' in filename:
            return 'sla_optimized'
        elif any(word in filename for word in ['ai', 'hunyuan', 'real']):
            return 'ai_generated'
        elif stl_file.stat().st_size > 50_000_000:  # >50MB
            return 'large_complex'
        else:
            return 'standard'

    def is_ascii_stl(self, content: bytes) -> bool:
        """Check if STL is ASCII format"""
        try:
            # ASCII STL starts with 'solid' and has text content
            if content.startswith(b'solid '):
                sample = content[:2000].decode('utf-8', errors='ignore')
                return 'facet normal' in sample
        except:
            pass
        return False

    def analyze_ascii_stl_save(self, content: bytes, result: Dict) -> Dict:
        """Analyze ASCII STL save integrity"""
        result['format'] = 'ASCII STL'

        try:
            content_str = content.decode('utf-8', errors='ignore')

            # Structure validation
            has_solid = content_str.strip().startswith('solid ')
            has_endsolid = 'endsolid' in content_str
            facet_count = content_str.count('facet normal')
            vertex_count = content_str.count('vertex')

            result['triangles'] = facet_count
            result['vertices'] = vertex_count

            # Save integrity checks
            result['save_integrity']['valid_structure'] = has_solid and has_endsolid
            result['save_integrity']['correct_format'] = facet_count > 0 and vertex_count == facet_count * 3
            result['save_integrity']['data_consistency'] = self.check_ascii_consistency(content_str)

            # Warnings
            if not content_str.strip().endswith('endsolid'):
                result['warnings'].append("File doesn't end with 'endsolid'")

        except Exception as e:
            result['errors'].append(f"ASCII analysis failed: {str(e)}")

        return result

    def analyze_binary_stl_save(self, content: bytes, result: Dict) -> Dict:
        """Analyze binary STL save integrity"""
        result['format'] = 'Binary STL'

        try:
            if len(content) < 84:
                result['errors'].append("File too small for binary STL")
                return result

            # Read header and triangle count
            header = content[:80]
            triangle_count = struct.unpack('<I', content[80:84])[0]

            result['triangles'] = triangle_count
            result['vertices'] = triangle_count * 3

            # Calculate expected vs actual size
            expected_size = 84 + (triangle_count * 50)  # 50 bytes per triangle
            actual_size = len(content)

            # Save integrity checks
            result['save_integrity']['valid_structure'] = triangle_count > 0
            result['save_integrity']['correct_format'] = abs(expected_size - actual_size) <= 2
            result['save_integrity']['data_consistency'] = self.check_binary_consistency(content, triangle_count)

            # Store detailed info
            result['complexity_analysis'] = {
                'header_info': header.decode('utf-8', errors='ignore').strip('\x00'),
                'expected_size': expected_size,
                'actual_size': actual_size,
                'size_difference': actual_size - expected_size
            }

            if abs(expected_size - actual_size) > 2:
                result['errors'].append(f"Size mismatch: expected {expected_size}, got {actual_size}")

        except Exception as e:
            result['errors'].append(f"Binary analysis failed: {str(e)}")

        return result

    def check_ascii_consistency(self, content_str: str) -> bool:
        """Check ASCII STL data consistency"""
        try:
            # Check that each facet has proper structure
            lines = content_str.split('\n')
            in_facet = False
            vertex_count = 0

            for line in lines:
                line = line.strip()
                if line.startswith('facet normal'):
                    if in_facet:
                        return False  # Nested facets
                    in_facet = True
                    vertex_count = 0
                elif line.startswith('vertex') and in_facet:
                    vertex_count += 1
                elif line == 'endfacet':
                    if not in_facet or vertex_count != 3:
                        return False  # Wrong vertex count
                    in_facet = False

            return True

        except:
            return False

    def check_binary_consistency(self, content: bytes, triangle_count: int) -> bool:
        """Check binary STL data consistency (sample first few triangles)"""
        try:
            # Sample first 100 triangles for consistency check
            sample_size = min(triangle_count, 100)

            for i in range(sample_size):
                offset = 84 + (i * 50)
                if offset + 50 > len(content):
                    return False

                # Read triangle data
                triangle_data = struct.unpack('<12fH', content[offset:offset+50])

                # Check for valid float values (not NaN or infinite)
                for j in range(12):  # 12 floats per triangle
                    if not np.isfinite(triangle_data[j]):
                        return False

            return True

        except:
            return False

    def analyze_geometry_complexity(self, result: Dict) -> Dict:
        """Analyze geometric complexity of the 3D model"""

        triangles = result.get('triangles', 0)
        file_size = result.get('file_size', 0)

        # Complexity classification
        if triangles == 0:
            complexity = 'invalid'
        elif triangles < 100:
            complexity = 'very_simple'
        elif triangles < 1000:
            complexity = 'simple'
        elif triangles < 10000:
            complexity = 'moderate'
        elif triangles < 100000:
            complexity = 'complex'
        else:
            complexity = 'very_complex'

        # Density analysis
        if triangles > 0 and file_size > 0:
            if result['format'] == 'Binary STL':
                bytes_per_triangle = (file_size - 84) / triangles
                expected_bpt = 50  # Expected bytes per triangle
                density_efficiency = expected_bpt / bytes_per_triangle if bytes_per_triangle > 0 else 0
            else:
                bytes_per_triangle = file_size / triangles
                density_efficiency = 1.0  # ASCII efficiency harder to calculate
        else:
            bytes_per_triangle = 0
            density_efficiency = 0

        result['complexity_analysis'].update({
            'complexity_level': complexity,
            'triangle_count': triangles,
            'bytes_per_triangle': bytes_per_triangle,
            'density_efficiency': density_efficiency,
            'estimated_vertices': triangles * 3,
            'estimated_edges': triangles * 3  # Approximate for closed mesh
        })

        # Geometric validity
        result['save_integrity']['geometry_valid'] = (
            triangles > 0 and
            complexity != 'invalid' and
            density_efficiency > 0.8
        )

        return result

    def calculate_quality_metrics(self, result: Dict) -> Dict:
        """Calculate quality metrics for STL save function"""

        triangles = result.get('triangles', 0)
        file_size = result.get('file_size', 0)
        save_integrity = result.get('save_integrity', {})

        # Quality scores (0-100)
        scores = {
            'structural_integrity': 100 if save_integrity.get('valid_structure', False) else 0,
            'format_compliance': 100 if save_integrity.get('correct_format', False) else 0,
            'data_consistency': 100 if save_integrity.get('data_consistency', False) else 0,
            'geometry_validity': 100 if save_integrity.get('geometry_valid', False) else 0,
            'file_efficiency': 0
        }

        # File efficiency based on compression ratio
        if triangles > 0:
            if result['format'] == 'Binary STL':
                optimal_size = 84 + (triangles * 50)
                efficiency = min(100, (optimal_size / file_size) * 100) if file_size > 0 else 0
            else:
                # ASCII is inherently less efficient
                efficiency = 70  # Base score for ASCII
            scores['file_efficiency'] = efficiency

        # Overall quality (weighted average)
        weights = {
            'structural_integrity': 0.25,
            'format_compliance': 0.25,
            'data_consistency': 0.20,
            'geometry_validity': 0.20,
            'file_efficiency': 0.10
        }

        overall_score = sum(scores[metric] * weight for metric, weight in weights.items())

        result['quality_metrics'] = {
            'individual_scores': scores,
            'overall_quality': overall_score,
            'grade': self.get_quality_grade(overall_score)
        }

        return result

    def get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def calculate_integrity_score(self, result: Dict) -> float:
        """Calculate overall save integrity score"""

        save_integrity = result.get('save_integrity', {})

        # Base score from boolean checks
        checks = ['valid_structure', 'correct_format', 'data_consistency', 'geometry_valid']
        passed_checks = sum(1 for check in checks if save_integrity.get(check, False))
        base_score = (passed_checks / len(checks)) * 100

        # Penalty for errors
        error_count = len(result.get('errors', []))
        error_penalty = min(error_count * 10, 50)  # Max 50 point penalty

        # Warning penalty
        warning_count = len(result.get('warnings', []))
        warning_penalty = min(warning_count * 5, 20)  # Max 20 point penalty

        final_score = max(0, base_score - error_penalty - warning_penalty)
        return final_score

    def run_comprehensive_analysis(self):
        """Run comprehensive analysis on all complex shape STLs"""

        print("[TARGET] STL SAVE FUNCTION INTEGRITY ANALYSIS")
        print("="*60)

        # Find complex STL files
        complex_stls = self.find_complex_shape_stls()

        if not complex_stls:
            print("[FAIL] No complex shape STL files found")
            return

        print(f"\n[SEARCH] Analyzing {len(complex_stls)} complex shape STL files...")
        print("="*60)

        results = []

        for stl_file in complex_stls:
            print(f"\n Analyzing: {stl_file.name}")
            result = self.analyze_stl_save_integrity(stl_file)
            results.append(result)

            # Print immediate results
            save_score = result['save_integrity'].get('overall_score', 0)
            quality_grade = result.get('quality_metrics', {}).get('grade', 'F')

            status = "[OK]" if save_score >= 80 else "[WARN]" if save_score >= 60 else "[FAIL]"
            print(f"   {status} Category: {result['category']}")
            print(f"   [STATS] Integrity Score: {save_score:.1f}/100 (Grade: {quality_grade})")
            print(f"   üìê Format: {result['format']} | Triangles: {result['triangles']:,}")
            print(f"   üíæ File Size: {result['file_size']/1024:.1f} KB")

            # Show critical issues
            if result['errors']:
                for error in result['errors'][:2]:
                    print(f"   üö´ Error: {error}")

            if result['warnings']:
                for warning in result['warnings'][:1]:
                    print(f"   [WARN] Warning: {warning}")

        # Generate comprehensive report
        self.generate_integrity_report(results)

    def generate_integrity_report(self, results: List[Dict]):
        """Generate comprehensive STL save function integrity report"""

        print("\n" + "="*80)
        print("[STATS] COMPREHENSIVE STL SAVE FUNCTION ANALYSIS REPORT")
        print("="*80)

        total_files = len(results)

        # Category analysis
        categories = {}
        for result in results:
            cat = result['category']
            categories[cat] = categories.get(cat, 0) + 1

        print(f"\n[FOLDER] File Categories:")
        for category, count in categories.items():
            percentage = (count / total_files) * 100
            print(f"   {category.upper()}: {count} files ({percentage:.1f}%)")

        # Quality distribution
        quality_grades = {}
        integrity_scores = []

        for result in results:
            grade = result.get('quality_metrics', {}).get('grade', 'F')
            score = result.get('save_integrity', {}).get('overall_score', 0)

            quality_grades[grade] = quality_grades.get(grade, 0) + 1
            integrity_scores.append(score)

        print(f"\n[METRICS] Quality Distribution:")
        for grade in ['A', 'B', 'C', 'D', 'F']:
            if grade in quality_grades:
                count = quality_grades[grade]
                percentage = (count / total_files) * 100
                print(f"   Grade {grade}: {count} files ({percentage:.1f}%)")

        # Statistics
        avg_score = sum(integrity_scores) / len(integrity_scores) if integrity_scores else 0
        max_score = max(integrity_scores) if integrity_scores else 0
        min_score = min(integrity_scores) if integrity_scores else 0

        print(f"\n[STATS] Integrity Statistics:")
        print(f"   Average Score: {avg_score:.1f}/100")
        print(f"   Score Range: {min_score:.1f} - {max_score:.1f}")
        print(f"   Files ≥80 (Excellent): {sum(1 for s in integrity_scores if s >= 80)}")
        print(f"   Files ≥60 (Good): {sum(1 for s in integrity_scores if s >= 60)}")
        print(f"   Files <60 (Poor): {sum(1 for s in integrity_scores if s < 60)}")

        # Format analysis
        formats = {}
        total_triangles = 0
        total_size = 0

        for result in results:
            fmt = result['format']
            formats[fmt] = formats.get(fmt, 0) + 1
            total_triangles += result['triangles']
            total_size += result['file_size']

        print(f"\n Format Analysis:")
        for fmt, count in formats.items():
            percentage = (count / total_files) * 100
            print(f"   {fmt}: {count} files ({percentage:.1f}%)")

        print(f"\n[TARGET] Geometry Summary:")
        print(f"   Total Triangles: {total_triangles:,}")
        print(f"   Average Triangles: {total_triangles/total_files:,.0f}")
        print(f"   Total File Size: {total_size/1024/1024:.2f} MB")
        print(f"   Average File Size: {total_size/total_files/1024:.1f} KB")

        # Best and worst performers
        best_result = max(results, key=lambda r: r.get('save_integrity', {}).get('overall_score', 0))
        worst_result = min(results, key=lambda r: r.get('save_integrity', {}).get('overall_score', 0))

        print(f"\n[TROPHY] Best Performing STL:")
        print(f"    {best_result['filename']}")
        print(f"   [STATS] Score: {best_result['save_integrity'].get('overall_score', 0):.1f}/100")
        print(f"   üìê {best_result['triangles']:,} triangles, {best_result['file_size']/1024:.1f} KB")

        print(f"\n[WARN] Lowest Performing STL:")
        print(f"    {worst_result['filename']}")
        print(f"   [STATS] Score: {worst_result['save_integrity'].get('overall_score', 0):.1f}/100")
        if worst_result['errors']:
            print(f"   üö´ Issues: {', '.join(worst_result['errors'][:2])}")

        # Save detailed report
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_type': 'STL Save Function Integrity',
            'summary': {
                'total_files': total_files,
                'average_integrity_score': avg_score,
                'quality_distribution': quality_grades,
                'category_distribution': categories
            },
            'detailed_results': results
        }

        report_file = Path(f"stl_save_integrity_report_{int(time.time())}.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        print(f"\nüíæ Detailed report saved to: {report_file}")

        # Overall assessment
        excellent_count = sum(1 for s in integrity_scores if s >= 80)
        good_count = sum(1 for s in integrity_scores if s >= 60)

        print(f"\nüéâ OVERALL ASSESSMENT:")
        if excellent_count / total_files >= 0.8:
            print("   [OK] EXCELLENT: STL save function performing very well!")
        elif good_count / total_files >= 0.7:
            print("   üëç GOOD: STL save function mostly reliable with minor issues")
        else:
            print("   [WARN] NEEDS IMPROVEMENT: STL save function has significant issues")

        print("="*80)

def main():
    """Main analysis function"""
    analyzer = STLSaveFunctionAnalyzer()
    analyzer.run_comprehensive_analysis()

if __name__ == "__main__":
    main()

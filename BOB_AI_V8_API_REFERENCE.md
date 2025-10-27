# BOB AI v8.0 - Complete API Reference

**Version:** 8.0.0 | **Status:** Production | **Last Updated:** October 27, 2025

## Table of Contents

1. [Core Module Loader](#core-module-loader)
2. [Knowledge Base API](#knowledge-base-api)
3. [Discipline Integration Modules](#discipline-integration-modules)
4. [Cross-Discipline Linker](#cross-discipline-linker)
5. [Performance Profiling](#performance-profiling)
6. [Complete Examples](#complete-examples)

---

## Core Module Loader

### `BobAIV8ModuleLoader`

The central module loader that discovers, loads, and initializes all BOB AI knowledge modules.

**Location:** `backend/bob_ai_v8_loader.py`

#### Constructor

```python
loader = BobAIV8ModuleLoader(backend_path: Optional[str] = None)
```

- `backend_path` (str, optional): Path to backend directory. If None, auto-detects.

#### Key Methods

**`load_all_modules() -> Tuple[int, int, Dict[str, str]]`**

Loads all discovered BOB AI modules.

**Returns:**

- `(loaded_count, failed_count, errors_dict)`

**Example:**

```python
loader = BobAIV8ModuleLoader()
loaded, failed, errors = loader.load_all_modules()
print(f"Loaded {loaded} modules, {failed} failed")
```

---

**`get_instantiated_knowledge(module_name: str) -> Optional[Any]`**

Get instantiated knowledge object for a discipline.

**Parameters:**

- `module_name` (str): e.g., 'bob_ai_v8_book_writing' or 'Book Writing'

**Returns:** Instantiated knowledge object or None

**Example:**

```python
book_writing_knowledge = loader.get_instantiated_knowledge('Book Writing')
if book_writing_knowledge:
    print(book_writing_knowledge.knowledge_items[:5])
```

---

**`get_instantiated_integration(module_name: str) -> Optional[Any]`**

Get instantiated integration module for a discipline.

**Parameters:**

- `module_name` (str): Discipline name

**Returns:** Integration object with `should_apply()`, `enhance()` methods

**Example:**

```python
book_integration = loader.get_instantiated_integration('Book Writing')
if book_integration.should_apply("character development"):
    enhanced = book_integration.enhance("Initial prompt")
```

---

**`validate_module(module_name: str) -> Tuple[bool, List[str]]`**

Validate a module structure and content.

**Returns:**

- `(is_valid, error_list)`

**Example:**

```python
is_valid, errors = loader.validate_module('Comic Art')
if not is_valid:
    print(f"Validation errors: {errors}")
```

---

**`get_status_report() -> Dict[str, Any]`**

Get comprehensive system status report.

**Returns:** Dictionary with module counts, failed modules, system metrics

**Example:**

```python
status = loader.get_status_report()
print(f"Total modules: {status['total_modules']}")
print(f"Loaded: {status['loaded_modules']}")
print(f"Failed: {status['failed_modules']}")
```

---

## Knowledge Base API

### Knowledge Object Structure

Each discipline knowledge base is a Python object with:

```python
class KnowledgeBase:
    discipline: str              # "Book Writing", "Python Programming", etc.
    version: str                 # "1.0.0"
    author: str                  # Module author
    category: str                # Category name
    knowledge_items: List[Dict]  # All knowledge items
    keywords: List[str]          # Searchable keywords
    system_prompt: str           # System prompt for AI enhancement
```

### Accessing Knowledge Items

**Example:**

```python
loader = BobAIV8ModuleLoader()
book_knowledge = loader.get_instantiated_knowledge('Book Writing')

# Access raw knowledge
print(f"Total items: {len(book_knowledge.knowledge_items)}")
print(f"Keywords: {len(book_knowledge.keywords)}")

# Iterate through items
for item in book_knowledge.knowledge_items[:5]:
    print(f"{item['title']}: {item['content'][:50]}...")
```

### Metadata Structure

Each knowledge item contains:

```python
{
    'title': str,           # Item title
    'content': str,         # Item content (guidelines, techniques, etc.)
    'category': str,        # Category (e.g., "Plot Structure", "Character Development")
    'keywords': List[str],  # Associated keywords
    'application': str,     # How to apply this knowledge
    'examples': str,        # Usage examples (optional)
}
```

---

## Discipline Integration Modules

### Integration Module API

Each discipline has an integration module with:

**Location Pattern:** `backend/bob_ai_v8_<discipline>_integration.py`

### Methods

**`should_apply(user_input: str) -> bool`**

Determine if this discipline is relevant to the user input.

**Parameters:**

- `user_input` (str): User prompt or context

**Returns:** True if discipline applies

**Example:**

```python
integration = loader.get_instantiated_integration('Book Writing')
if integration.should_apply("I'm writing a chapter about time travel"):
    print("Book Writing module applies!")
```

---

**`enhance(prompt: str, context: Dict[str, Any] = None) -> str`**

Enhance user prompt with discipline-specific guidance.

**Parameters:**

- `prompt` (str): Original user prompt
- `context` (dict, optional): Additional context (user_level, focus_area, etc.)

**Returns:** Enhanced prompt with discipline recommendations

**Example:**

```python
integration = loader.get_instantiated_integration('Comic Art')
enhanced = integration.enhance(
    "Draw an action scene",
    context={'focus_area': 'perspective', 'user_level': 'intermediate'}
)
print(enhanced)
```

---

**`detect_context(user_input: str) -> Dict[str, Any]`**

Extract discipline-specific context from user input.

**Returns:** Dictionary with extracted parameters

**Example:**

```python
context = integration.detect_context("I'm a beginner designing a sci-fi magazine cover")
# Returns: {'user_level': 'beginner', 'genre': 'sci-fi', 'format': 'magazine_cover', ...}
```

---

## Cross-Discipline Linker

### `CrossDisciplineLinker`

**Location:** `backend/bob_ai_v8_cross_discipline_linker.py`

#### Constructor

```python
linker = CrossDisciplineLinker()
```

Auto-initializes with all 14 discipline relationships and knowledge bridges.

#### Key Methods

**`get_related_disciplines(discipline: str, min_strength: float = 0.5) -> List[Tuple[str, float]]`**

Get disciplines related to the given discipline.

**Returns:** List of (discipline, relationship_strength) tuples, sorted by strength

**Example:**

```python
related = linker.get_related_disciplines('Book Writing', min_strength=0.7)
for disc, strength in related:
    print(f"{disc}: {strength:.0%}")
# Output:
# Prompt Engineering: 80%
# Comic Art: 70%
```

---

**`get_cross_discipline_recommendations(discipline: str, challenge: str) -> List[Dict[str, Any]]`**

Get recommendations from related disciplines for a specific challenge.

**Returns:** List of recommendation dictionaries

**Example:**

```python
recommendations = linker.get_cross_discipline_recommendations(
    'Book Writing', 'character development'
)
for rec in recommendations:
    print(f"From {rec['from_discipline']}: {rec['recommendation']}")
```

---

**`get_knowledge_bridge(discipline_a: str, discipline_b: str) -> List[str]`**

Get shared concepts between two disciplines.

**Returns:** List of shared concepts

**Example:**

```python
bridge = linker.get_knowledge_bridge('Photography', 'Graphic Design')
print(f"Shared concepts: {', '.join(bridge[:5])}")
# Output: "Shared concepts: composition, color theory, lighting, contrast, focal point"
```

---

**`suggest_adjacent_learning(discipline: str) -> List[Dict[str, str]]`**

Suggest adjacent disciplines to learn for skill progression.

**Returns:** List of learning suggestions with priority

**Example:**

```python
suggestions = linker.suggest_adjacent_learning('Web Development')
for sugg in suggestions:
    print(f"{sugg['discipline']} ({sugg['priority']}): {sugg['reason']}")
```

---

**`get_interdisciplinary_insights(discipline: str) -> Dict[str, Any]`**

Get comprehensive interdisciplinary network for a discipline.

**Example:**

```python
insights = linker.get_interdisciplinary_insights('Comic Art')
print(f"Strong connections: {', '.join(insights['related_strong'])}")
print(f"Moderate connections: {', '.join(insights['related_moderate'][:3])}")
```

---

## Performance Profiling

### `PerformanceProfiler`

**Location:** `backend/bob_ai_v8_performance_optimizer.py`

#### Methods

**`profile_bootstrap() -> Dict[str, float]`**

Profile system bootstrap time.

**Returns:** Timing metrics (loader_time_ms, module_load_time_ms, linker_time_ms, total_bootstrap_ms)

**Example:**

```python
profiler = PerformanceProfiler()
bootstrap = profiler.profile_bootstrap()
print(f"Total bootstrap: {bootstrap['total_bootstrap_ms']:.0f}ms")
```

---

**`profile_cross_discipline_linking() -> Dict[str, Any]`**

Profile cross-discipline linking performance.

**Returns:** Per-discipline and average timing

---

**`profile_batch_operations(batch_size: int = 10) -> Dict[str, Any]`**

Profile batch operations performance.

**Returns:** Total time, per-item average, throughput

---

## Complete Examples

### Example 1: Basic Enhancement Flow

```python
from bob_ai_v8_loader import BobAIV8ModuleLoader

# Initialize
loader = BobAIV8ModuleLoader()
loader.load_all_modules()

# Get integration module
book_integration = loader.get_instantiated_integration('Book Writing')

# Check if applicable
user_prompt = "I'm starting a fantasy novel with complex world-building"
if book_integration.should_apply(user_prompt):
    # Enhance the prompt
    enhanced = book_integration.enhance(user_prompt)
    print("Enhanced prompt:", enhanced)
else:
    print("Not applicable")
```

### Example 2: Cross-Discipline Integration

```python
from bob_ai_v8_loader import BobAIV8ModuleLoader
from bob_ai_v8_cross_discipline_linker import CrossDisciplineLinker

loader = BobAIV8ModuleLoader()
loader.load_all_modules()

linker = CrossDisciplineLinker()

# Get main discipline
user_prompt = "Design a book cover"
graphic_design = loader.get_instantiated_integration('Graphic Design')

if graphic_design.should_apply(user_prompt):
    # Get related disciplines
    related = linker.get_related_disciplines('Graphic Design', min_strength=0.7)

    print("Graphic Design can be enhanced by:")
    for discipline, strength in related:
        integration = loader.get_instantiated_integration(discipline)
        enhanced = integration.enhance(user_prompt, context={'focus': 'visual_design'})
        print(f"  - {discipline}: {enhanced[:100]}...")
```

### Example 3: Learning Path Suggestion

```python
from bob_ai_v8_cross_discipline_linker import CrossDisciplineLinker

linker = CrossDisciplineLinker()

current_skill = 'Web Development'
suggestions = linker.suggest_adjacent_learning(current_skill)

print(f"Learning path recommendations for {current_skill}:")
for sugg in suggestions:
    print(f"  {sugg['priority']:6} | {sugg['discipline']:25} | {sugg['reason']}")
```

### Example 4: Knowledge Base Exploration

```python
from bob_ai_v8_loader import BobAIV8ModuleLoader

loader = BobAIV8ModuleLoader()
loader.load_all_modules()

# Get all Book Writing knowledge
book_knowledge = loader.get_instantiated_knowledge('Book Writing')

print(f"Discipline: {book_knowledge.discipline}")
print(f"Version: {book_knowledge.version}")
print(f"Total items: {len(book_knowledge.knowledge_items)}")
print(f"Keywords: {len(book_knowledge.keywords)}")
print(f"\nSystem Prompt:\n{book_knowledge.system_prompt}\n")

# Explore categories
categories = set()
for item in book_knowledge.knowledge_items:
    categories.add(item['category'])

print(f"Categories ({len(categories)}):")
for category in sorted(categories):
    count = sum(1 for item in book_knowledge.knowledge_items if item['category'] == category)
    print(f"  - {category}: {count} items")
```

---

## Error Handling

### Common Exceptions

**`ModuleNotFoundError`**: Discipline module not found

```python
try:
    integration = loader.get_instantiated_integration('NonExistent')
except ModuleNotFoundError:
    print("Discipline not found")
```

**`AttributeError`**: Module missing required methods

```python
try:
    result = integration.should_apply(None)
except AttributeError:
    print("Module missing required method")
```

### Validation Pattern

```python
loader = BobAIV8ModuleLoader()
loaded, failed, errors = loader.load_all_modules()

if failed > 0:
    print(f"Warning: {failed} modules failed to load")
    for module, error in errors.items():
        print(f"  {module}: {error}")

# Validate specific module
is_valid, validation_errors = loader.validate_module('Book Writing')
if not is_valid:
    print(f"Validation issues: {validation_errors}")
```

---

## Performance Targets

- **Bootstrap:** <500ms (loader init + module discovery)
- **Single Enhancement:** <100ms per discipline
- **Cross-Discipline Recommendations:** <50ms
- **Batch Operations:** <1000ms for 10 operations

For profiling:

```python
from bob_ai_v8_performance_optimizer import PerformanceProfiler

profiler = PerformanceProfiler()
report = profiler.generate_report()
print(report)
```

---

## Configuration

### Environment Variables

```bash
# Loader configuration
BOB_AI_BACKEND_PATH=./backend
BOB_AI_LOG_LEVEL=INFO

# Performance tuning
BOB_AI_CACHE_ENABLED=true
BOB_AI_LAZY_LOAD=false
```

### Loader Configuration

```python
loader = BobAIV8ModuleLoader(backend_path='/custom/path')
```

---

## Migration Guide

### From v7.x to v8.0

**Old (v7.x):**

```python
from bob_ai import load_discipline
knowledge = load_discipline('Book Writing')
```

**New (v8.0):**

```python
from bob_ai_v8_loader import BobAIV8ModuleLoader
loader = BobAIV8ModuleLoader()
loader.load_all_modules()
knowledge = loader.get_instantiated_knowledge('Book Writing')
```

### Breaking Changes

1. Loader is now singleton pattern (call `BobAIV8ModuleLoader()` once, reuse instance)
2. Module names must use underscore_case internally: `bob_ai_v8_book_writing.py`
3. Knowledge classes now require `instantiate()` method
4. Cross-discipline linker is separate module

---

## Support & Troubleshooting

- **Module fails to load:** Check logs with `get_status_report()`
- **Enhancement not applying:** Use `should_apply()` to debug detection
- **Performance issues:** Run `PerformanceProfiler().generate_report()`

For detailed troubleshooting, see `BOB_AI_V8_TROUBLESHOOTING.md`

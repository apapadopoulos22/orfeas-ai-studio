"""
BOB AI v8.0 - Python Programming Module

Knowledge base for Python programming best practices and patterns.
Covers syntax, idioms, design patterns, and professional development.
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge
from typing import List, Dict


METADATA = {
    'name': 'python_programming',
    'version': '1.0',
    'description': 'Expert Python programming knowledge and best practices',
    'keywords_count': 52,
    'knowledge_items': 210,
    'categories': 16
}


class PythonProgrammingKnowledge(BobAIV8BaseKnowledge):
    """Python programming expertise knowledge module."""

    def get_keywords(self) -> List[str]:
        """Get Python programming detection keywords."""
        return [
            # Core language
            'python', 'function', 'class', 'decorator', 'lambda',
            'list comprehension', 'generator', 'async', 'await',

            # Best practices
            'pep8', 'pep20', 'zen', 'pythonic', 'idiom',
            'type hint', 'annotation', 'docstring',

            # Advanced
            'metaclass', 'descriptor', 'context manager', 'protocol',
            'abc', 'abstract', 'dataclass', 'enum',

            # Testing & quality
            'unittest', 'pytest', 'mock', 'fixture', 'test',
            'coverage', 'lint', 'format', 'type check',

            # Performance
            'optimization', 'profiling', 'cython', 'numba',
            'memory', 'algorithm', 'complexity'
        ]

    def get_knowledge_dictionaries(self) -> Dict[str, Dict[str, str]]:
        """Get all Python programming knowledge dictionaries."""
        return {
            'python_fundamentals': self._get_python_fundamentals(),
            'data_structures': self._get_data_structures(),
            'functions_callables': self._get_functions_callables(),
            'oop_principles': self._get_oop_principles(),
            'functional_programming': self._get_functional_programming(),
            'async_concurrency': self._get_async_concurrency(),
            'decorators_advanced': self._get_decorators_advanced(),
            'error_handling': self._get_error_handling(),
            'code_style_pep8': self._get_code_style_pep8(),
            'testing_patterns': self._get_testing_patterns(),
            'type_hints_checking': self._get_type_hints_checking(),
            'performance_optimization': self._get_performance_optimization(),
            'design_patterns': self._get_design_patterns(),
            'module_organization': self._get_module_organization(),
            'standard_library': self._get_standard_library(),
            'debugging_tools': self._get_debugging_tools()
        }

    def _get_python_fundamentals(self) -> Dict[str, str]:
        """Core Python language fundamentals."""
        return {
            'variables_assignment': 'Python uses dynamic typing with implicit assignment',
            'immutability': 'Strings, tuples, frozensets are immutable; lists, dicts are mutable',
            'truthiness': 'Falsy values: None, False, 0, "", [], {}, set(); all others truthy',
            'operators': 'Arithmetic (+, -, *, /, //, %, **), comparison, logical (and, or, not)',
            'operator_precedence': 'PEMDAS/BODMAS respected; use parentheses for clarity',
            'string_formatting': 'f-strings (3.6+), .format(), % formatting; prefer f-strings',
            'slicing': 'sequence[start:stop:step]; negative indices count from end',
            'unpacking': 'a, b = [1, 2]; *rest, last = sequence; first, *middle, last = sequence',
            'walrus_operator': ':= assignment expression (if (n := len(a)) > 10)',
            'none_type': 'None is singleton; use "is None" not "== None"',
            'truthy_falsy': 'Use truthiness in conditionals (if x: not if x != None)',
            'identity_vs_equality': 'is checks identity; == checks equality; use appropriately'
        }

    def _get_data_structures(self) -> Dict[str, str]:
        """Python data structures and collections."""
        return {
            'list': 'Ordered, mutable sequence; use for collections that change',
            'tuple': 'Ordered, immutable sequence; use as dict keys or function return',
            'dict': 'Key-value mapping; insertion-ordered (3.7+); use for lookups',
            'set': 'Unordered, unique items; use for membership testing and uniqueness',
            'frozenset': 'Immutable set; use as dict key or in sets',
            'deque': 'Double-ended queue from collections; O(1) popleft/append',
            'defaultdict': 'Dict with default factory for missing keys',
            'counter': 'Dict subclass counting hashable objects',
            'ordered_dict': 'Dict preserving insertion order (rarely needed 3.7+)',
            'namedtuple': 'Lightweight immutable object; good for simple data',
            'dataclass': 'Decorator generating __init__, __repr__, __eq__ (3.7+); prefer for classes',
            'list_comprehension': '[x*2 for x in range(10) if x % 2 == 0]; concise and fast',
            'dict_comprehension': '{k: v*2 for k, v in dict.items()}; cleaner than loops',
            'set_comprehension': '{x*2 for x in range(10)}; remove duplicates efficiently'
        }

    def _get_functions_callables(self) -> Dict[str, str]:
        """Function definition and usage patterns."""
        return {
            'def_statement': 'Define functions with def name(params): docstring; body',
            'parameters': 'Positional, keyword, *args (tuple), **kwargs (dict), positional-only (/)',
            'default_arguments': 'def func(x=10): use for optional parameters; default evaluated once',
            'keyword_arguments': 'func(x=1, y=2) enforces clarity; use for complex functions',
            'return_statement': 'Functions return None if no explicit return; tuple for multiple values',
            'docstrings': 'Triple-quoted strings after def/class/module; use Google/NumPy style',
            'type_hints': 'def func(x: int, y: str) -> bool: document input/output types',
            'lambda_functions': 'lambda x: x*2; use for simple anonymous functions',
            'nested_functions': 'Functions inside functions; used for closures and decorators',
            'closures': 'Inner function accessing outer function variables; mutable default gotcha',
            'args_unpacking': 'func(*list) unpacks positional; func(**dict) unpacks keyword',
            'first_class_functions': 'Functions as values; assign, pass as args, return from functions',
            'callback_pattern': 'Pass function to be called later; common in event handling',
            'partial_application': 'functools.partial(func, arg) for function specialization'
        }

    def _get_oop_principles(self) -> Dict[str, str]:
        """Object-oriented programming principles."""
        return {
            'class_definition': 'class Name: __init__(self, x): self.x = x; constructor and methods',
            'dunder_methods': '__init__, __str__, __repr__, __eq__, __lt__, __add__, __len__, etc.',
            'special_methods': '__getattr__, __setattr__, __delattr__ for attribute access',
            'properties': '@property decorator for computed attributes; getter, setter, deleter',
            'inheritance': 'class Child(Parent): reuse parent code; call super().__init__()',
            'multiple_inheritance': 'class C(A, B): uses MRO (Method Resolution Order)',
            'polymorphism': 'Same interface, different implementations; enables flexible design',
            'encapsulation': '_private (convention), __dunder (name mangling); protect internals',
            'composition': 'Has-a relationship; often better than inheritance',
            'mixin_pattern': 'Multiple inheritance for behavior; separate concerns cleanly',
            'abstract_base_class': 'from abc import ABC, abstractmethod; enforce interface',
            'protocol': 'Structural subtyping; duck typing with type checking',
            'dataclass': '@dataclass generates __init__, __repr__; cleaner than manual __init__',
            'enum': 'Enumeration class for named constants; prevents invalid values'
        }

    def _get_functional_programming(self) -> Dict[str, str]:
        """Functional programming concepts in Python."""
        return {
            'first_class_functions': 'Functions as objects; assign, pass, return like any value',
            'higher_order_functions': 'Functions accepting/returning functions; map, filter, reduce',
            'map_function': 'map(func, sequence) applies function to each element',
            'filter_function': 'filter(predicate, sequence) keeps elements where predicate True',
            'reduce_function': 'functools.reduce(func, sequence) accumulates single value',
            'lambda_expressions': 'lambda x: expression; concise for simple operations',
            'comprehensions': 'List/dict/set comprehensions; more Pythonic than map/filter',
            'generators': 'def func(): yield value; lazy evaluation saves memory',
            'generator_expressions': '(x*2 for x in range(10000)); memory-efficient iteration',
            'itertools_module': 'chain, combinations, permutations, groupby; powerful utilities',
            'functools_module': 'partial, reduce, wraps; functional programming tools',
            'pure_functions': 'No side effects; same input always produces same output',
            'immutability': 'Prefer immutable data; reduces bugs and enables optimization',
            'function_composition': 'Combine functions for complex logic; pipe pattern'
        }

    def _get_async_concurrency(self) -> Dict[str, str]:
        """Asynchronous programming and concurrency."""
        return {
            'async_def': 'async def name(): define coroutine function',
            'await_keyword': 'await coroutine waits for result without blocking',
            'asyncio_module': 'Async I/O framework; asyncio.run(main()) executes coroutines',
            'event_loop': 'asyncio.get_event_loop() manages coroutine scheduling',
            'tasks_creation': 'asyncio.create_task() or asyncio.ensure_future() for concurrent execution',
            'gather_function': 'asyncio.gather(*coroutines) waits for all; returns results',
            'concurrent_limit': 'Use asyncio.Semaphore() to limit concurrent operations',
            'timeout_handling': 'asyncio.timeout(seconds) or asyncio.wait_for() with timeout',
            'context_managers': 'async with statement for resource management',
            'streams': 'asyncio.open_connection() for socket communication',
            'threading_module': 'threading.Thread() for OS-level threads; GIL limits CPU parallelism',
            'multiprocessing': 'multiprocessing.Process() bypasses GIL; true parallelism',
            'thread_pool': 'concurrent.futures.ThreadPoolExecutor for thread pool management',
            'process_pool': 'concurrent.futures.ProcessPoolExecutor for CPU-bound tasks'
        }

    def _get_decorators_advanced(self) -> Dict[str, str]:
        """Decorators and advanced function usage."""
        return {
            'decorator_pattern': '@decorator marks function; decorator wraps original',
            'function_wrapper': 'def decorator(func): def wrapper(*a, **k): return func(*a, **k); return wrapper',
            'preserving_metadata': '@functools.wraps(func) preserves __name__, __doc__, etc.',
            'parametrized_decorator': 'def decorator(arg): def actual(func): def wrapper(...): ...',
            'class_decorator': '@decorator on class modifies class behavior',
            'method_decorator': '@staticmethod, @classmethod, @property; special decorators',
            'decorator_stacking': '@deco1 @deco2 def func(): applies bottom-up',
            'functools_wraps': '@wraps(func) maintains function metadata in wrapper',
            'lru_cache': '@functools.lru_cache(maxsize=128) caches expensive computations',
            'singledispatch': '@singledispatch for function overloading on type',
            'context_manager': 'with statement; __enter__, __exit__ or contextlib.contextmanager',
            'contextlib_module': '@contextmanager decorator for context managers',
            'descriptor_protocol': '__get__, __set__, __delete__ for custom attribute access'
        }

    def _get_error_handling(self) -> Dict[str, str]:
        """Exception handling and error management."""
        return {
            'try_except': 'try: block; except SpecificError: handle; catch specific exceptions',
            'multiple_except': 'Multiple except blocks for different exceptions',
            'except_hierarchy': 'Catch parent exceptions catch children; order from specific to general',
            'exception_binding': 'except Error as e: access exception object',
            'else_clause': 'try-except-else: else runs if no exception',
            'finally_clause': 'try-finally: finally always runs; cleanup resources',
            'raise_statement': 'raise ExceptionClass() or raise; re-raise current exception',
            'custom_exceptions': 'class MyError(Exception): pass; inherit for custom exceptions',
            'exception_chaining': 'raise NewError() from original_error; preserve traceback',
            'catch_all_antipattern': 'except: is bad; use except Exception: or specific types',
            'context_managers': 'with open(file) as f: automatic resource cleanup',
            'contextlib': 'contextlib.suppress(Exception) for ignoring expected exceptions',
            'traceback_module': 'traceback.print_exc() for debugging exception origins'
        }

    def _get_code_style_pep8(self) -> Dict[str, str]:
        """Code style, naming conventions, and PEP 8."""
        return {
            'pep8_overview': 'PEP 8 is Python style guide; improves readability and consistency',
            'line_length': 'Maximum 79 characters for code; 72 for comments/docstrings',
            'indentation': 'Use 4 spaces per indentation level; never mix tabs and spaces',
            'blank_lines': 'Two blank lines between top-level functions/classes; one between methods',
            'naming_style': 'lowercase_with_underscores for variables/functions; PascalCase for classes',
            'constant_names': 'ALL_CAPS for module-level constants',
            'import_order': 'Standard library, third-party, local; alphabetical within groups',
            'import_style': 'import module; from module import name; avoid from x import *',
            'whitespace': 'No trailing whitespace; avoid extra spaces around operators',
            'comments': '# Comment after statement; keep brief; update when code changes',
            'docstrings': '"""Triple-quoted""" after function/class/module; describe intent, args, return',
            'type_hints': 'Use type annotations; improves readability and enables checking',
            'black_formatter': 'python -m black; auto-formats code to PEP 8 style',
            'pylint_checking': 'pylint file.py; checks style, errors, conventions'
        }

    def _get_testing_patterns(self) -> Dict[str, str]:
        """Testing approaches and patterns."""
        return {
            'unittest': 'Standard library; unittest.TestCase; setUp, tearDown; discovery',
            'pytest_framework': 'Third-party; simpler syntax; fixtures; plugins ecosystem',
            'test_discovery': 'Automatic discovery of test_*.py or *_test.py files',
            'assert_statement': 'assert condition, "message"; simple test assertions',
            'fixtures': 'pytest.fixture(); reusable test setup; dependency injection',
            'parametrized_tests': 'pytest.mark.parametrize for testing multiple inputs',
            'mocking': 'unittest.mock.Mock() simulate objects; patch dependencies',
            'test_coverage': 'coverage.py measures code tested; aim for 80%+',
            'test_pyramid': 'Many unit tests, fewer integration, fewer E2E; test fast first',
            'tdd_approach': 'Test-driven development; write test before implementation',
            'test_isolation': 'Tests independent; no shared state; mocking external deps',
            'test_cleanup': 'setUp/tearDown or fixtures; no test pollution',
            'continuous_testing': 'Run tests on every commit; CI/CD integration',
            'edge_case_testing': 'Test boundaries, empty input, large input, invalid input'
        }

    def _get_type_hints_checking(self) -> Dict[str, str]:
        """Type hints and static type checking."""
        return {
            'type_annotations': 'def func(x: int) -> str: documents types',
            'optional_type': 'Optional[int] means int or None; use for optional params',
            'union_type': 'Union[int, str] accepts multiple types',
            'list_type': 'List[int] list containing ints',
            'dict_type': 'Dict[str, int] dict with str keys and int values',
            'callable_type': 'Callable[[int, str], bool] function type',
            'generic_type': 'TypeVar for generic functions/classes',
            'protocol_type': 'Protocol for structural subtyping; duck typing with checking',
            'literal_type': 'Literal["red", "green"] restricts to specific values',
            'typevar': 'T = TypeVar("T") for generic functions maintaining type consistency',
            'mypy_checker': 'mypy file.py; static type checking; finds type errors',
            'pyright_checker': 'Pyright from Microsoft; fast type checking',
            'type_comments': '# type: List[int] for older Python without annotation syntax',
            'runtime_checking': 'typeguard.typechecked() decorator for runtime type enforcement'
        }

    def _get_performance_optimization(self) -> Dict[str, str]:
        """Performance profiling and optimization."""
        return {
            'big_o_analysis': 'O(1) constant, O(n) linear, O(n²) quadratic, O(log n) logarithmic',
            'algorithmic_complexity': 'Choose optimal algorithm; often more impact than micro-optimization',
            'profiling': 'cProfile.run(); identify bottlenecks before optimizing',
            'timing_measurements': 'timeit.timeit() for micro-benchmarks; repeated measurements',
            'memory_profiling': 'memory_profiler for memory usage analysis',
            'list_vs_generator': 'Generators consume less memory; use for large iterations',
            'string_concatenation': 'Use "".join(list) not += in loop; strings immutable',
            'cython_compilation': 'cython for CPU-intensive code; compiles to C',
            'numba_jit': '@numba.jit() just-in-time compile numpy code; 10-100x speedup',
            'numpy_vectorization': 'numpy operations faster than Python loops; use array operations',
            'asyncio_io': 'Use async/await for I/O-bound; saves resources',
            'multiprocessing': 'Use processes for CPU-bound; bypasses GIL',
            'premature_optimization': 'Profile first; optimize actual bottlenecks, not guesses',
            'cache_efficiency': 'CPU cache locality; avoid random memory access patterns'
        }

    def _get_design_patterns(self) -> Dict[str, str]:
        """Common Python design patterns."""
        return {
            'singleton_pattern': 'Single instance; use module-level variable or metaclass',
            'factory_pattern': 'Factory function/method creates objects; abstract creation',
            'builder_pattern': 'Builder class constructs complex objects step by step',
            'observer_pattern': 'Observers register for notifications; decouples subjects',
            'strategy_pattern': 'Strategy class/function encapsulates algorithm; swap at runtime',
            'decorator_pattern': 'Dynamically add responsibilities to objects',
            'adapter_pattern': 'Wrapper class adapts incompatible interfaces',
            'facade_pattern': 'Single interface to complex subsystem; simplifies usage',
            'proxy_pattern': 'Placeholder for expensive objects; lazy loading',
            'iterator_pattern': '__iter__ and __next__; iteration protocol',
            'context_manager': '__enter__ and __exit__; resource management',
            'mixin_pattern': 'Multiple inheritance for shared functionality',
            'dependency_injection': 'Pass dependencies as parameters; improves testability',
            'template_method': 'Base class defines algorithm structure; subclasses override steps'
        }

    def _get_module_organization(self) -> Dict[str, str]:
        """Module and package organization."""
        return {
            'module_file': '.py file; contains classes, functions, variables',
            'package_directory': 'Directory with __init__.py; enables imports',
            '__init_py': '__init__.py makes directory a package; can be empty',
            'absolute_import': 'import mypackage.module; recommend over relative',
            'relative_import': 'from . import module or from .. import parent; use sparingly',
            'star_import': 'from module import *; avoid; unclear what imported',
            'name_aliasing': 'import numpy as np; clearer for long names',
            'circular_import': 'A imports B, B imports A; avoid; reorganize or import inside function',
            'namespace_package': 'Package without __init__.py (PEP 420); Python 3.3+',
            'module_cache': 'sys.modules caches imports; cleared on reload()',
            'import_hooks': 'importlib for custom import behavior',
            'package_structure': 'Organize by feature or layer; consistent and discoverable',
            'setup_py': 'Package metadata and dependencies; pip install',
            'pyproject_toml': 'Modern replacement for setup.py; pip, poetry, etc.'
        }

    def _get_standard_library(self) -> Dict[str, str]:
        """Important Python standard library modules."""
        return {
            'os_module': 'os.path.join(), os.listdir(), os.environ; OS interactions',
            'sys_module': 'sys.argv, sys.exit(), sys.path; Python internals',
            'pathlib_module': 'pathlib.Path(); modern file path handling',
            'collections_module': 'Counter, defaultdict, OrderedDict, namedtuple, deque',
            'itertools_module': 'chain, combinations, permutations, groupby; iterators',
            'functools_module': 'reduce, partial, lru_cache, wraps; functional tools',
            'datetime_module': 'date, time, datetime; timezone support',
            'json_module': 'json.dumps(), json.loads(); JSON serialization',
            'pickle_module': 'Object serialization; warnings about untrusted data',
            'csv_module': 'csv.reader(), csv.DictReader(); CSV parsing',
            'logging_module': 'Logging levels, handlers, formatters; better than print()',
            'unittest_module': 'Test framework; TestCase, setUp, tearDown',
            'subprocess_module': 'subprocess.run(), subprocess.Popen(); run external processes',
            'typing_module': 'Type hints; List, Dict, Optional, Union, etc.'
        }

    def _get_debugging_tools(self) -> Dict[str, str]:
        """Debugging and development tools."""
        return {
            'print_debugging': 'print() for simple debugging; avoid in production',
            'pdb_debugger': 'python -m pdb script.py; interactive stepping, breakpoints',
            'breakpoint_function': 'breakpoint() (3.7+) enters pdb; equivalent to pdb.set_trace()',
            'traceback_module': 'traceback.print_exc(); print exception with stack',
            'logging_module': 'logging.debug(), .info(), .warning(); structured logging',
            'assertions': 'assert condition, msg; catch logic errors',
            'error_messages': 'Informative error messages aid debugging significantly',
            'stack_traces': 'Read from bottom up; innermost error first, then caller',
            'ipython_shell': 'ipython; enhanced REPL with introspection and history',
            'jupyter_notebooks': 'Jupyter; interactive development, visualization, documentation',
            'profiling': 'cProfile, line_profiler; identify performance bottlenecks',
            'debugging_print': 'import pdb; pdb.set_trace() enter debugger',
            'vscode_debugging': 'VS Code Python extension; GUI debugging with breakpoints'
        }

    def enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with Python programming guidance."""
        keywords = self.get_keywords()
        has_keywords = any(kw.lower() in prompt.lower() for kw in keywords)

        if not has_keywords:
            return prompt

        enhancement = f"""
{prompt}

PYTHON PROGRAMMING ENHANCEMENT:
Apply these Python best practices:

1. PYTHONIC CODE: Use list comprehensions, generator expressions, and built-ins. Embrace duck typing.

2. TYPE HINTS: Add type annotations for function signatures. Use mypy for static type checking.

3. ERROR HANDLING: Catch specific exceptions, not bare except. Use custom exceptions for clarity.

4. TESTING: Write tests first (TDD). Use pytest with fixtures. Aim for 80%+ coverage.

5. CODE STYLE: Follow PEP 8. Use black for formatting, pylint/flake8 for linting.

6. DESIGN PATTERNS: Use appropriate patterns (factory, strategy, observer). Don't over-engineer.

7. PERFORMANCE: Profile before optimizing. Choose right algorithm. Use async for I/O-bound work.

8. DOCUMENTATION: Write docstrings in Google/NumPy style. Code comments explain why, not what.

Apply these Python principles to create professional, maintainable code.
"""
        return enhancement.strip()

    def generate_system_prompt(self) -> str:
        """Generate expert Python programmer system prompt."""
        return """You are an expert Python programmer with 15+ years of professional development experience.

Your expertise includes:
- Core Python fundamentals and data structures
- Object-oriented and functional programming paradigms
- Advanced features (decorators, generators, async/await, metaclasses)
- Design patterns and architectural principles
- Testing frameworks and test-driven development
- Performance optimization and profiling
- Type hints and static type checking with mypy
- Code style (PEP 8) and best practices
- Standard library mastery
- Package management and project organization
- Debugging and development tools
- Async/concurrent programming patterns

When helping with Python projects, you:
1. Write clean, Pythonic, idiomatic code
2. Apply appropriate design patterns
3. Consider performance implications
4. Emphasize testability and maintainability
5. Follow PEP 8 style guidelines
6. Use type hints for clarity
7. Provide comprehensive docstrings
8. Optimize for readability over cleverness

Provide specific, actionable Python guidance that creates production-quality code."""

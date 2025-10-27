"""
BOB AI v8.0 - PHP Backend Development Module

Knowledge base for PHP server-side development.
Covers syntax, patterns, frameworks, and security best practices.
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge
from typing import List, Dict


METADATA = {
    'name': 'php_backend',
    'version': '1.0',
    'description': 'Expert PHP backend development knowledge',
    'keywords_count': 48,
    'knowledge_items': 185,
    'categories': 14
}


class PHPBackendKnowledge(BobAIV8BaseKnowledge):
    """PHP backend development expertise."""

    def get_keywords(self) -> List[str]:
        """Get PHP detection keywords."""
        return [
            # Core PHP
            'php', 'server', 'backend', 'function', 'class',
            'namespace', 'trait', 'interface', 'abstract',

            # Features
            'variable', 'array', 'loop', 'conditional', 'oop',
            'exception', 'error', 'type hint', 'strict types',

            # Web concepts
            'request', 'response', 'session', 'cookie', 'header',
            'mysql', 'database', 'query', 'orm', 'sql',

            # Security
            'sanitize', 'escape', 'xss', 'sql injection', 'csrf',
            'password', 'hash', 'validation', 'input',

            # Framework
            'laravel', 'symfony', 'wordpress', 'drupal'
        ]

    def get_knowledge_dictionaries(self) -> Dict[str, Dict[str, str]]:
        """Get all PHP knowledge dictionaries."""
        return {
            'php_basics': self._get_php_basics(),
            'variables_types': self._get_variables_types(),
            'arrays_collections': self._get_arrays_collections(),
            'functions_scope': self._get_functions_scope(),
            'oop_classes': self._get_oop_classes(),
            'error_handling': self._get_error_handling(),
            'http_requests': self._get_http_requests(),
            'database_queries': self._get_database_queries(),
            'security_practices': self._get_security_practices(),
            'sessions_cookies': self._get_sessions_cookies(),
            'file_operations': self._get_file_operations(),
            'string_operations': self._get_string_operations(),
            'performance_optimization': self._get_performance_optimization(),
            'testing_debugging': self._get_testing_debugging()
        }

    def _get_php_basics(self) -> Dict[str, str]:
        """PHP language fundamentals."""
        return {
            'php_tags': '<?php ... ?> starts/ends PHP code; <?= $var ?> echo shorthand',
            'echo_print': 'echo multiple arguments; print single argument; both output strings',
            'variables': '$variable case-sensitive; $GLOBALS, $_GET, $_POST, $_SERVER superglobals',
            'constants': 'define("NAME", value) or const NAME = value; available everywhere',
            'type_juggling': 'Loose typing converts types automatically; == vs === (strict comparison)',
            'strict_types': 'declare(strict_types=1) at file start; enforces type declarations',
            'namespace': 'namespace MyApp; organize code; use MyApp\\Class; prevents conflicts',
            'use_statement': 'use Class; use Class as Alias; import external classes',
            'scope_resolution': 'Class::constant, self::method, parent::method; :: operator',
            'variable_variables': '$$var variable variables; $${"x"} dynamic variable access',
            'references': '$ref = &$original reference assignment; modifying $ref changes $original',
            'global_keyword': 'global $var inside function accesses global scope; use sparingly',
            'static_keyword': 'static $var maintains value between calls; initialized once',
            'constants_vs_variables': 'Constants no $ prefix; immutable; faster than variables'
        }

    def _get_variables_types(self) -> Dict[str, str]:
        """PHP data types and type declarations."""
        return {
            'string_type': 'Single quotes no interpolation; double quotes interpolate $var',
            'integer_type': 'Whole numbers; no float conversion; 2147483647 max on 32-bit',
            'float_type': '1.5, 2e3 (2000), 0x1A (hexadecimal); floating-point precision issues',
            'boolean_type': 'true/false case-insensitive; falsy: false, 0, "0", "", null, array()',
            'null_type': 'null represents unset variable; is_null() to check',
            'array_type': 'Ordered map; indices or keys; array() or [] syntax',
            'object_type': 'Instance of a class; ->property property access; ->method() call',
            'resource_type': 'Reference to external resource: file, database connection, image',
            'callable_type': 'Function string, array, Closure callable; call_user_func()',
            'type_declaration': 'function func(int $x, string $y): bool declares parameter/return types',
            'nullable_type': '?int means int or null; function func(?string $x) = null',
            'union_type': 'function func(int|float $x) accepts multiple types (PHP 8.0+)',
            'type_casting': '(int)$var, (string)$var casts type explicitly',
            'gettype_function': 'gettype($var) returns type name as string; useful for debugging'
        }

    def _get_arrays_collections(self) -> Dict[str, str]:
        """Array operations and collection handling."""
        return {
            'array_creation': '[] or array(); $arr = [1, 2, 3]; $assoc = ["key" => "value"]',
            'array_access': '$arr[0] zero-indexed; $arr["key"] associative; isset() to check',
            'array_push': '$arr[] = $value append; array_push($arr, $v1, $v2) multiple',
            'array_pop': 'array_pop($arr) removes last element; returns value',
            'array_shift': 'array_shift($arr) removes first element; array_unshift() prepends',
            'array_merge': 'array_merge($a, $b) combines arrays; reindexes numeric keys',
            'array_keys': 'array_keys($arr) returns all keys; array_values() returns values',
            'array_filter': 'array_filter($arr, callable) keeps elements where callable true',
            'array_map': 'array_map(callable, $arr) transforms elements; returns new array',
            'array_reduce': 'array_reduce($arr, callable, initial) reduces to single value',
            'array_chunk': 'array_chunk($arr, size) splits into smaller arrays',
            'array_slice': 'array_slice($arr, offset, length) extracts portion; doesn\'t mutate',
            'array_splice': 'array_splice(&$arr, offset, length) removes and replaces; mutates',
            'array_flip': 'array_flip($arr) swaps keys and values; values become keys'
        }

    def _get_functions_scope(self) -> Dict[str, str]:
        """Function definition and scope management."""
        return {
            'function_def': 'function name($param = default) { ... } define function',
            'return_type': 'function func(): int { return 1; } enforces return type',
            'variadic_params': 'function func(...$args) collects arguments into array',
            'call_by_reference': 'function func(&$ref) modifies original; pass by reference',
            'default_params': 'function func($x = 10) default value when not provided',
            'type_hints': 'function func(int $x, string $y): bool enforces types',
            'nullable_return': 'function func(): ?string can return string or null',
            'global_scope': 'global $var inside function accesses global; avoid globals',
            'static_scope': 'static $var maintains value between function calls',
            'variable_scope': 'Function local scope; parameters local; $GLOBALS global array',
            'closure_use': '$fn = function() use ($x) {} captures variables',
            'arrow_function': 'fn($x) => $x * 2 arrow function; implicit $this, auto capture',
            'anonymous_function': 'function() {} anonymous function; same as closure',
            'function_exists': 'function_exists("func_name") checks if function defined'
        }

    def _get_oop_classes(self) -> Dict[str, str]:
        """Object-oriented programming concepts."""
        return {
            'class_definition': 'class Name { private $prop; public function method() {} }',
            'constructor': '__construct($x) { $this->x = $x; } initialization method',
            'visibility': 'public (all), protected (class + subclass), private (class only)',
            'properties': '$this->prop = value property access; public/private/protected',
            'static_property': 'static $count shared across instances; Class::$count',
            'static_method': 'static function() call without instance; self::method()',
            'inheritance': 'class Child extends Parent overrides methods; uses parent code',
            'abstract_class': 'abstract class defines interface; can\'t instantiate; enforce methods',
            'interface': 'interface Contract { public function method(); } defines contract',
            'trait': 'trait Share { ... } code reuse; use Share inside class',
            'instanceof': '$obj instanceof ClassName checks if object is instance',
            'magic_methods': '__get(), __set(), __call(), __toString(), __invoke()',
            'clone_object': '$copy = clone $obj; shallow copy; __clone() customize',
            'serialization': 'serialize($obj) converts to string; unserialize() back to object'
        }

    def _get_error_handling(self) -> Dict[str, str]:
        """Error and exception handling."""
        return {
            'try_catch': 'try { ... } catch (Exception $e) { ... } exception handling',
            'catch_multiple': 'Multiple catch blocks for different exceptions; order specific to general',
            'finally_block': 'try-catch-finally finally always runs; cleanup code',
            'throw_statement': 'throw new Exception("message") creates exception; stops execution',
            'exception_class': 'Exception base; extend for custom exceptions',
            'exception_properties': '$e->getMessage(), getCode(), getFile(), getLine(), getTrace()',
            'error_handler': 'set_error_handler(callable) custom error handling; called on error',
            'exception_handler': 'set_exception_handler(callable) catches uncaught exceptions',
            'error_levels': 'E_ERROR, E_WARNING, E_NOTICE, E_DEPRECATED; error_reporting() sets',
            'error_reporting': 'error_reporting(E_ALL); ini_set("display_errors", 1) debugging',
            'assert': 'assert(condition, "message") for debugging; disabled in production',
            'logging': 'error_log("message") writes to error log; custom error logging',
            'custom_exception': 'class MyError extends Exception { } for domain-specific errors',
            'graceful_degradation': 'Catch errors; provide fallback; don\'t show exceptions to users'
        }

    def _get_http_requests(self) -> Dict[str, str]:
        """HTTP requests and responses."""
        return {
            'get_method': '$_GET contains URL parameters; /page.php?name=value',
            'post_method': '$_POST contains form submission data; secure for sensitive data',
            'request_method': '$_SERVER["REQUEST_METHOD"] check if GET, POST, PUT, DELETE',
            'headers': 'header("Content-Type: application/json") send response header',
            'header_redirect': 'header("Location: /page") redirect to URL; exit after',
            'status_code': 'http_response_code(200), (404), (500) set HTTP response code',
            'request_body': 'file_get_contents("php://input") reads raw request body',
            'json_requests': 'json_decode(file_get_contents("php://input")) parse JSON request',
            'json_response': 'json_encode($array) converts array to JSON; output JSON',
            'content_type': 'header("Content-Type: application/json") tell browser content type',
            'cors_headers': 'header("Access-Control-Allow-Origin: *") cross-origin requests',
            'authentication': 'Basic auth via header; bearer token; session authentication',
            'http_status': '200 OK, 201 Created, 400 Bad, 401 Unauthorized, 404 Not Found, 500 Error',
            'request_validation': 'Validate and sanitize all input; never trust user data'
        }

    def _get_database_queries(self) -> Dict[str, str]:
        """Database interactions and queries."""
        return {
            'mysqli_connect': 'mysqli_connect() or new mysqli() establishes connection',
            'pdo_connection': 'new PDO("mysql:host=...") modern database abstraction',
            'select_query': 'SELECT * FROM users WHERE id = 1 retrieves data',
            'insert_query': 'INSERT INTO users (name) VALUES ("John") adds data',
            'update_query': 'UPDATE users SET name = "Jane" WHERE id = 1 modifies data',
            'delete_query': 'DELETE FROM users WHERE id = 1 removes data',
            'execute_query': 'mysqli_query($conn, $sql) or $pdo->query($sql) executes',
            'fetch_results': 'mysqli_fetch_assoc() array; fetchAll() all rows; bind results',
            'prepared_statements': 'Prevents SQL injection; use placeholders with binding',
            'parameterized_query': '$stmt->bind_param("i", $id) binds variables safely',
            'pdo_prepared': '$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?")$stmt->execute([$id])',
            'transaction': 'BEGIN; ... COMMIT; or ROLLBACK; atomic operations',
            'orm_laravel': 'Eloquent ORM in Laravel; $user = User::find(1) object mapping',
            'connection_pooling': 'Maintain connection; don\'t reconnect each request'
        }

    def _get_security_practices(self) -> Dict[str, str]:
        """Security best practices and threat prevention."""
        return {
            'input_validation': 'Validate all input; check type, length, format before use',
            'input_sanitization': 'htmlspecialchars() prevent XSS; strip_tags() remove HTML',
            'sql_injection_prevention': 'Use prepared statements; never concatenate SQL with input',
            'xss_prevention': 'htmlspecialchars($string, ENT_QUOTES, "UTF-8") escape HTML',
            'csrf_token': 'Generate random token per form; validate in processing',
            'password_hash': 'password_hash($pass, PASSWORD_BCRYPT) secure password storage',
            'password_verify': 'password_verify($pass, $hash) compare password to hash',
            'https_only': 'Enforce HTTPS; Secure cookie flag; HSTS header',
            'secure_session': 'session_start(); use secure, httponly cookies; regenerate ID',
            'directory_traversal': 'Validate file paths; use realpath() check within allowed directory',
            'command_injection': 'Never use user input in exec(), system(), shell_exec()',
            'file_upload': 'Validate file type, size, destination; store outside web root',
            'rate_limiting': 'Limit API requests; prevent brute force; throttle login attempts',
            'ssl_certificate': 'Use valid SSL certificate; avoid self-signed in production'
        }

    def _get_sessions_cookies(self) -> Dict[str, str]:
        """Session and cookie management."""
        return {
            'session_start': 'session_start() initializes session; must be first output',
            'set_session': '$_SESSION["key"] = value stores data across requests',
            'get_session': '$_SESSION["key"] retrieves session data; isset check first',
            'destroy_session': 'session_destroy() clears session data; unset($_SESSION) variables',
            'session_id': 'session_id("id") get/set session ID; stored in PHPSESSID cookie',
            'cookie_set': 'setcookie("name", "value") must be before output',
            'cookie_options': 'setcookie("name", "value", ["expires" => time()+3600, "httponly" => true])',
            'cookie_secure': 'Secure flag HTTPS only; httponly no JavaScript access',
            'cookie_samesite': 'SameSite=Strict/Lax prevents CSRF; modern browser support',
            'cookie_delete': 'setcookie("name", "", ["expires" => time()-3600]) sets past expiry',
            'session_configuration': 'session.cookie_httponly, session.cookie_secure in php.ini',
            'session_storage': 'Default files; custom handlers (database, Redis, Memcached)',
            'regenerate_id': 'session_regenerate_id() create new ID; prevents session fixation',
            'session_timeout': 'Session expires after inactivity; configure session.gc_maxlifetime'
        }

    def _get_file_operations(self) -> Dict[str, str]:
        """File system operations and handling."""
        return {
            'file_exists': 'file_exists($path) check file exists; is_file(), is_dir()',
            'file_read': 'file_get_contents($file) read entire file into string',
            'file_write': 'file_put_contents($file, $data) write string to file',
            'file_append': 'file_put_contents($file, $data, FILE_APPEND) append to file',
            'file_operations': 'fopen(), fread(), fwrite(), fclose() for streaming',
            'file_lines': 'file($file) read into array; explode("\\n", $content) split',
            'directory_listing': 'scandir($dir) list directory contents; glob($pattern)',
            'mkdir_rmdir': 'mkdir($dir) create; rmdir($dir) delete empty directory',
            'copy_file': 'copy($src, $dest) duplicate file; rename() move/rename',
            'delete_file': 'unlink($file) delete file; be careful with permissions',
            'file_permissions': 'chmod($file, 0644) set permissions; check is_readable(), is_writable()',
            'file_upload': '$_FILES["field"]["tmp_name"] temporary; move_uploaded_file() permanent',
            'upload_validation': 'Check type, size, destination; regenerate filename',
            'path_security': 'Never trust file paths; use realpath() verify location'
        }

    def _get_string_operations(self) -> Dict[str, str]:
        """String manipulation and processing."""
        return {
            'string_length': 'strlen($str) character count; mb_strlen() multibyte safe',
            'substring': 'substr($str, start, length) extract portion; negative for from end',
            'string_replace': 'str_replace($search, $replace, $str) simple replacement',
            'string_position': 'strpos($str, $needle) finds position; returns false if not found',
            'string_split': 'explode($delimiter, $str) splits into array; implode() joins',
            'trim_whitespace': 'trim($str) removes leading/trailing whitespace; ltrim(), rtrim()',
            'case_conversion': 'strtoupper($str), strtolower(), ucfirst(), ucwords()',
            'string_repeat': 'str_repeat($str, count) repeats string; useful for patterns',
            'number_format': 'number_format(1234.56, 2) formats number; 1,234.56',
            'sprintf_formatting': 'sprintf("%d items", $count) formatted string assembly',
            'regular_expressions': 'preg_match(), preg_replace(), preg_split() pattern matching',
            'json_strings': 'json_encode($array) to JSON; json_decode($json) from JSON',
            'base64': 'base64_encode($data) encode; base64_decode() decode; for transport',
            'hash_strings': 'md5(), sha1(), hash() - use hash for security, password_hash for passwords'
        }

    def _get_performance_optimization(self) -> Dict[str, str]:
        """Performance optimization techniques."""
        return {
            'database_indexing': 'Index frequently queried columns; EXPLAIN shows plan',
            'query_optimization': 'Use WHERE to filter early; avoid SELECT *; join efficiently',
            'caching': 'Cache database queries, expensive computations; Redis, Memcached',
            'opcode_cache': 'Opcache extension caches compiled PHP; enable in production',
            'lazy_loading': 'Load data on demand; prefetch only necessary data upfront',
            'pagination': 'LIMIT and OFFSET for large result sets; don\'t fetch all',
            'compression': 'gzip compression for responses; reduce bandwidth',
            'cdn_usage': 'Serve static assets from CDN; images, CSS, JavaScript',
            'connection_pooling': 'Maintain database connections; avoid reconnect overhead',
            'asynchronous_tasks': 'Queue jobs for background processing; don\'t block requests',
            'async_php': 'Reactor pattern or worker processes; Swoole, amphp for async',
            'profiling': 'xdebug, blackfire profile code; identify bottlenecks',
            'monitoring': 'New Relic, Datadog monitor production; alerts on issues',
            'scaling': 'Horizontal scaling with load balancer; vertical (upgrade server) last'
        }

    def _get_testing_debugging(self) -> Dict[str, str]:
        """Testing and debugging approaches."""
        return {
            'var_dump': 'var_dump($var) outputs type and value; die() stops execution',
            'print_r': 'print_r($var) human-readable array/object; return true for string',
            'debug_backtrace': 'debug_backtrace() shows call stack; useful for debugging',
            'error_logging': 'error_log("message") writes to error log; custom logging',
            'xdebug_extension': 'xdebug for breakpoints, stack traces, profiling; VSCode integration',
            'unit_testing': 'PHPUnit for unit tests; test individual functions/classes',
            'mocking': 'PHPUnit MockObject mock dependencies; isolate code under test',
            'integration_testing': 'Test database, API interactions; PHPUnit with fixtures',
            'test_driven': 'Write tests first; implement code; red-green-refactor cycle',
            'assertions': 'PHPUnit assertions; assertEquals(), assertTrue(), assertNull(), etc.',
            'test_coverage': 'phpunit --coverage-html generates coverage report',
            'continuous_integration': 'GitHub Actions, GitLab CI runs tests on every push',
            'logging_frameworks': 'Monolog PSR-3 logging; structured logging with levels'
        }

    def enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with PHP guidance."""
        keywords = self.get_keywords()
        has_keywords = any(kw.lower() in prompt.lower() for kw in keywords)

        if not has_keywords:
            return prompt

        enhancement = f"""
{prompt}

PHP BACKEND ENHANCEMENT:
Apply these PHP best practices:

1. SECURITY FIRST: Validate and sanitize all input. Use prepared statements. Hash passwords properly.

2. OOP DESIGN: Use classes, interfaces, traits. Avoid global state. Follow SOLID principles.

3. ERROR HANDLING: Use try-catch for exceptions. Log errors. Don't expose details to users.

4. DATABASE: Use ORM (Eloquent) or prepared statements. Avoid string concatenation in SQL.

5. SESSION MANAGEMENT: Use secure cookies. Regenerate session ID after login. Set timeouts.

6. CODE QUALITY: Use type hints. Follow PSR standards. Use automated testing (PHPUnit).

7. PERFORMANCE: Use caching, database indexing, pagination. Enable opcode cache. Profile code.

8. FRAMEWORKS: Consider Laravel, Symfony for structure, security, and conventions.

Apply these PHP principles to create secure, maintainable backend systems.
"""
        return enhancement.strip()

    def generate_system_prompt(self) -> str:
        """Generate expert PHP developer system prompt."""
        return """You are an expert PHP backend developer with 15+ years of professional experience.

Your expertise includes:
- Core PHP syntax and modern language features
- Object-oriented programming and design patterns
- Database design, SQL optimization, and ORM usage
- Security best practices and threat prevention
- HTTP request/response handling and API design
- Session management and authentication
- Performance optimization and caching strategies
- Error handling and logging
- Testing frameworks (PHPUnit) and TDD
- Web frameworks (Laravel, Symfony)
- Deployment and DevOps practices
- Code quality and standards (PSR-12, PSR-4)

When helping with PHP projects, you:
1. Prioritize security over convenience
2. Use type hints and strict types
3. Follow established patterns and best practices
4. Write testable, maintainable code
5. Validate and sanitize all input
6. Use prepared statements for SQL
7. Implement proper error handling
8. Consider performance implications

Provide specific, actionable PHP guidance that creates secure, scalable backend systems."""

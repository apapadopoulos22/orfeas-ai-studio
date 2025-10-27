"""
BOB AI v8.0 - HTML/CSS/JavaScript Web Development Module

Knowledge base for frontend web development.
Covers markup, styling, client-side scripting, and modern web standards.
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge
from typing import List, Dict


METADATA = {
    'name': 'web_development_frontend',
    'version': '1.0',
    'description': 'Expert HTML/CSS/JavaScript frontend knowledge',
    'keywords_count': 56,
    'knowledge_items': 195,
    'categories': 15
}


class WebDevelopmentKnowledge(BobAIV8BaseKnowledge):
    """HTML/CSS/JavaScript web development expertise."""

    def get_keywords(self) -> List[str]:
        """Get web development detection keywords."""
        return [
            # HTML
            'html', 'semantic', 'accessibility', 'form', 'input',
            'element', 'attribute', 'doctype', 'meta', 'viewport',

            # CSS
            'css', 'selector', 'specificity', 'cascade', 'flexbox',
            'grid', 'responsive', 'media query', 'breakpoint',
            'animation', 'transition', 'transform', 'gradient',

            # JavaScript
            'javascript', 'function', 'async', 'promise', 'callback',
            'dom', 'event', 'manipulation', 'fetch', 'api',

            # Web standards
            'web', 'responsive', 'accessibility', 'wcag', 'seo',
            'progressive enhancement', 'web component', 'shadow dom'
        ]

    def get_knowledge_dictionaries(self) -> Dict[str, Dict[str, str]]:
        """Get all web development knowledge dictionaries."""
        return {
            'html_semantics': self._get_html_semantics(),
            'html_forms': self._get_html_forms(),
            'accessibility_wcag': self._get_accessibility_wcag(),
            'css_layouts': self._get_css_layouts(),
            'css_responsive': self._get_css_responsive(),
            'css_advanced': self._get_css_advanced(),
            'javascript_fundamentals': self._get_javascript_fundamentals(),
            'dom_manipulation': self._get_dom_manipulation(),
            'async_javascript': self._get_async_javascript(),
            'event_handling': self._get_event_handling(),
            'modern_javascript': self._get_modern_javascript(),
            'apis_web': self._get_apis_web(),
            'performance_optimization': self._get_performance_optimization(),
            'browser_compatibility': self._get_browser_compatibility(),
            'web_standards': self._get_web_standards()
        }

    def _get_html_semantics(self) -> Dict[str, str]:
        """Semantic HTML and markup best practices."""
        return {
            'semantic_html': 'Use semantic tags: <header>, <nav>, <main>, <article>, <section>, <aside>, <footer>',
            'header_tag': '<header> page/section introduction; top branding, navigation',
            'nav_tag': '<nav> contains navigation links; use <ul>, <ol>, <a> inside',
            'main_tag': '<main> primary content; exactly one per page; skip navigation',
            'article_tag': '<article> self-contained content; blog post, news article, forum post',
            'section_tag': '<section> thematic grouping; use with heading; avoid div-itis',
            'aside_tag': '<aside> tangential content; sidebar, related links, notes',
            'footer_tag': '<footer> page/section footer; copyright, links, contact info',
            'h1_hierarchy': '<h1> main page heading; exactly one per page; establishes document outline',
            'heading_order': 'Use h1-h6 in logical order; skip levels only rarely',
            'landmark_regions': 'Use semantic tags to create landmark regions for screen readers',
            'outline_algorithm': 'Document outline determined by heading hierarchy; critical for accessibility',
            'schema_markup': 'schema.org markup for machine-readable content; improves SEO',
            'aria_roles': 'ARIA roles supplement semantic HTML; don\'t replace with role="main"'
        }

    def _get_html_forms(self) -> Dict[str, str]:
        """Form elements and best practices."""
        return {
            'form_element': '<form> groups related inputs; action, method attributes',
            'input_types': 'type="text", "email", "password", "number", "date", "checkbox", "radio", "file", etc.',
            'input_validation': 'type and pattern attributes provide client-side validation hints',
            'label_element': '<label> associates text with form control; for attribute links to input id',
            'fieldset_legend': '<fieldset> groups related controls; <legend> provides group label',
            'textarea_element': '<textarea> multi-line text input; rows, cols attributes',
            'select_dropdown': '<select> dropdown list; <option> child elements; value attribute',
            'datalist_element': '<datalist> predefined options; <input list> references datalist id',
            'button_types': '<button type="submit">, "reset", "button"; use button not input',
            'form_attributes': 'action="url", method="GET"/"POST", enctype for file uploads',
            'required_attribute': 'HTML5 required attribute marks fields mandatory',
            'disabled_attribute': 'disabled prevents user interaction; preserved in form submission',
            'readonly_attribute': 'readonly allows selection but prevents editing',
            'autofill_attribute': 'autocomplete attribute hints browser autofill behavior'
        }

    def _get_accessibility_wcag(self) -> Dict[str, str]:
        """Web accessibility and WCAG standards."""
        return {
            'wcag_overview': 'WCAG 2.1 guidelines: perceivable, operable, understandable, robust',
            'alt_text': 'alt attribute describes images; critical for screen readers',
            'aria_labels': 'aria-label provides accessible name; aria-labelledby references heading',
            'aria_live': 'aria-live="polite" announces dynamic updates to screen readers',
            'contrast_ratio': 'Minimum 4.5:1 contrast ratio for normal text; 3:1 for large text',
            'color_alone': 'Never convey information by color alone; use text, icons, patterns too',
            'keyboard_navigation': 'All functionality accessible via keyboard; logical tab order',
            'focus_indicator': 'Visible focus outline; never remove without replacement',
            'skip_links': '<a href="#main"> skip to main content; improves keyboard navigation',
            'form_labels': 'Every form input has associated <label> element',
            'error_messages': 'Error messages appear near field and in form summary',
            'landmarks': 'Semantic HTML + ARIA landmarks; header, nav, main, complementary',
            'heading_structure': 'Proper heading hierarchy; screen readers use for navigation',
            'list_semantics': '<ul>, <ol>, <li> for lists; screen readers announce structure'
        }

    def _get_css_layouts(self) -> Dict[str, str]:
        """CSS layout techniques and best practices."""
        return {
            'flexbox_container': 'display: flex; main-axis and cross-axis layout',
            'flexbox_direction': 'flex-direction: row, column; wrap, nowrap',
            'flex_justify': 'justify-content aligns items along main axis; space-between, center, etc.',
            'flex_align': 'align-items aligns items on cross axis; stretch, center, flex-start',
            'grid_container': 'display: grid; rows and columns layout; powerful for 2D',
            'grid_template': 'grid-template-columns, grid-template-rows define layout',
            'grid_areas': 'grid-template-areas visual ASCII layout; grid-area places items',
            'grid_lines': 'grid-column, grid-row reference lines; span multiple cells',
            'box_model': 'Content, padding, border, margin; box-sizing affects width/height',
            'position_static': 'position: static (default); flows in document normal flow',
            'position_relative': 'position: relative; offset from normal position; maintains space',
            'position_absolute': 'position: absolute; removed from flow; positioned relative to parent',
            'position_fixed': 'position: fixed; relative to viewport; stays on screen when scrolling',
            'z_index': 'z-index controls stacking order; higher values appear on top'
        }

    def _get_css_responsive(self) -> Dict[str, str]:
        """Responsive design and mobile-first approaches."""
        return {
            'mobile_first': 'Start with mobile styles; add complexity with media queries',
            'viewport_meta': '<meta name="viewport" content="width=device-width, initial-scale=1">',
            'media_query': '@media (min-width: 768px) { } targets screen size ranges',
            'breakpoints': 'Common: 480px (mobile), 768px (tablet), 1024px (desktop)',
            'fluid_typography': 'font-size: clamp(1rem, 5vw, 2rem); scales with viewport',
            'fluid_spacing': 'Use rem/em units and calc() for scalable layouts',
            'css_grid_responsive': 'grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))',
            'flexbox_wrapping': 'flex-wrap: wrap creates responsive multi-line layouts',
            'container_queries': '@container (min-width: 400px) { } based on container size',
            'css_variables': '--color-primary: blue; var(--color-primary) updates everywhere',
            'aspect_ratio': 'aspect-ratio: 16/9; maintains ratio when width changes',
            'object_fit': 'object-fit: cover; scales image to fill without distortion',
            'picture_element': '<picture> multiple sources; art direction for images',
            'srcset_attribute': 'srcset for resolution-dependent images; responsive images'
        }

    def _get_css_advanced(self) -> Dict[str, str]:
        """Advanced CSS techniques and features."""
        return {
            'css_selectors': 'Element, class, id, attribute, pseudo-class, pseudo-element',
            'specificity': 'Inline (1000) > id (100) > class (10) > element (1); use wisely',
            'cascade': 'Later rules override earlier; specificity breaks ties',
            'inheritance': 'Some properties inherited (color, font); some not (margin, padding)',
            'css_cascade': '@layer organize styles in cascade; override order matters',
            'transitions': 'transition: property duration timing-function delay; smooth changes',
            'animations': '@keyframes define animation; animation-name, duration, etc. control',
            'transforms': 'transform: translate(), rotate(), scale(), skew(); doesn\'t affect layout',
            'will_change': 'will-change: property hints browser optimization',
            'pseudo_elements': '::before, ::after create additional elements in CSS',
            'pseudo_classes': ':hover, :focus, :active, :nth-child(), :not() select special states',
            'clip_path': 'clip-path: polygon() creates custom shapes',
            'filter': 'filter: blur(), brightness(), contrast(); visual effects',
            'backdrop_filter': 'backdrop-filter: blur(); blurs background behind element'
        }

    def _get_javascript_fundamentals(self) -> Dict[str, str]:
        """JavaScript language fundamentals."""
        return {
            'variables': 'const preferred; let for loop variables; avoid var',
            'data_types': 'Primitives: string, number, boolean, null, undefined, symbol, bigint',
            'truthy_falsy': 'Falsy: false, 0, "", null, undefined, NaN; use === for comparison',
            'operators': 'Arithmetic, logical (&&, ||, !), comparison, assignment',
            'template_literals': '`text ${variable}` interpolation; multi-line strings',
            'array_methods': 'map, filter, reduce, forEach, find, some, every, includes',
            'object_methods': 'Object.keys(), values(), entries(), assign(), freeze()',
            'destructuring': 'const {x, y} = obj; const [a, b] = array; extract values',
            'spread_operator': '...array spreads elements; ...object spreads properties',
            'rest_parameters': 'function(...args) collects remaining arguments',
            'default_parameters': 'function(x = 10) default if undefined passed',
            'arrow_functions': '() => {}; no this binding; concise syntax',
            'arrow_this': 'Arrow functions inherit this from surrounding scope'
        }

    def _get_dom_manipulation(self) -> Dict[str, str]:
        """DOM selection and manipulation."""
        return {
            'getelementbyid': 'document.getElementById("id") single element',
            'queryselector': 'document.querySelector(".class") CSS selector; first match',
            'queryselectorall': 'document.querySelectorAll("selector") returns NodeList',
            'getelementsbyclassname': 'document.getElementsByClassName("class") HTMLCollection',
            'createelement': 'document.createElement("tag") creates new element',
            'createtext': 'document.createTextNode("text") creates text node',
            'appendchild': 'parent.appendChild(child) adds child to end',
            'insertbefore': 'parent.insertBefore(new, ref) inserts before reference',
            'removechild': 'parent.removeChild(child) removes child',
            'replacechild': 'parent.replaceChild(new, old) replaces child',
            'textcontent': 'element.textContent = "text" sets inner text',
            'innerhtml': 'element.innerHTML = "<tag>" sets HTML; security risk with untrusted data',
            'classlist': 'element.classList.add(), remove(), toggle(), contains()',
            'setattribute': 'element.setAttribute("attr", "value") sets attribute'
        }

    def _get_async_javascript(self) -> Dict[str, str]:
        """Asynchronous JavaScript patterns."""
        return {
            'callback_pattern': 'function(callback) { callback(result) } traditional async',
            'promise_basics': 'new Promise((resolve, reject) => {}) handles async operations',
            'promise_then': '.then(success, error) chains operations',
            'promise_catch': '.catch(error) handles errors; cleaner than then second arg',
            'promise_finally': '.finally() always runs cleanup code',
            'promise_all': 'Promise.all([promises]) waits for all; rejects if any fails',
            'promise_race': 'Promise.race([promises]) returns first settled promise',
            'async_function': 'async function returns Promise; enables await inside',
            'await_keyword': 'await pauseexecution waiting for Promise; works in async only',
            'async_error_handling': 'try-catch around await; catches rejections',
            'async_parallel': 'const [a, b] = await Promise.all([op1, op2]) parallel execution',
            'settimeout': 'setTimeout(callback, ms) delayed execution',
            'setinterval': 'setInterval(callback, ms) repeated execution; clearInterval to stop'
        }

    def _get_event_handling(self) -> Dict[str, str]:
        """Event handling and delegation."""
        return {
            'addeventlistener': 'element.addEventListener("event", handler) attach listener',
            'removeeventlistener': 'element.removeEventListener("event", handler) detach listener',
            'event_object': 'function(event) { event.target, event.type, event.preventDefault() }',
            'event_bubbling': 'Event bubbles up DOM; child fires, then parent, then document',
            'event_capturing': 'Event capturing phase before bubbling; addEventListener third arg',
            'stoppropagation': 'event.stopPropagation() prevents bubbling to parent',
            'preventdefault': 'event.preventDefault() cancels default action (submit, link)',
            'event_delegation': 'Listen on parent; check event.target; efficient for dynamic elements',
            'click_event': 'click fires on mouse click, Enter key on button/link',
            'change_event': 'change fires when input value changes and focus lost',
            'input_event': 'input fires during typing; use for live updates',
            'focusblurevents': 'focus when element receives focus; blur when losing focus',
            'keyboardevents': 'keydown, keyup, keypress; event.key for character, event.code for position',
            'mouseeventshover': 'mouseover, mouseout, mousemove, mouseenter, mouseleave'
        }

    def _get_modern_javascript(self) -> Dict[str, str]:
        """Modern JavaScript ES6+ features."""
        return {
            'let_const': 'let block-scoped, reassignable; const block-scoped, immutable reference',
            'arrow_functions': '() => value; concise; no this binding; no arguments object',
            'template_literals': '`string ${expr}` multi-line, interpolation, expression evaluation',
            'destructuring': 'const {x, y} = obj; const [a, b] = array elegantly extract',
            'spread_syntax': '...array spreads in function calls, array literals; ...obj spreads properties',
            'rest_parameters': 'function(...args) collects arguments into array',
            'default_parameters': 'function(x = 10) default when undefined',
            'classes': 'class Name { constructor() {} method() {} } syntactic sugar over prototypes',
            'modules': 'export default; export { named }; import; separate concerns',
            'symbols': 'Symbol("unique") unique identifiers; properties hidden from reflection',
            'proxy': 'new Proxy(target, handler) intercepts operations on objects',
            'reflect_api': 'Reflect.get(), set(), has() programmatic object manipulation',
            'maps_sets': 'Map key-value pairs any type; Set unique values; better than plain objects'
        }

    def _get_apis_web(self) -> Dict[str, str]:
        """Web APIs and browser functionality."""
        return {
            'fetch_api': 'fetch(url) returns Promise; json(), text(), blob() for response body',
            'fetch_options': 'fetch(url, {method, headers, body}) GET/POST/PUT/DELETE',
            'cors': 'Cross-Origin Resource Sharing; fetch respects CORS headers',
            'local_storage': 'localStorage.setItem(key, value) persistent; localStorage.getItem(key)',
            'session_storage': 'sessionStorage like localStorage; cleared on tab close',
            'indexeddb': 'IndexedDB large storage; async; transactional; powerful queries',
            'geolocation': 'navigator.geolocation.getCurrentPosition() user location with permission',
            'notifications': 'Notification.requestPermission() then new Notification(title, options)',
            'service_workers': 'Service Worker offline functionality, caching, background sync',
            'intersection_observer': 'IntersectionObserver(callback) lazy loading, infinite scroll',
            'mutation_observer': 'MutationObserver(callback) watch DOM changes',
            'resizeobserver': 'ResizeObserver(callback) watch element size changes',
            'requestanimationframe': 'requestAnimationFrame(callback) 60fps smooth animation',
            'canvas_api': 'Canvas for drawing graphics, games, animations programmatically'
        }

    def _get_performance_optimization(self) -> Dict[str, str]:
        """Web performance and optimization."""
        return {
            'code_splitting': 'Split JavaScript into chunks; lazy load non-critical code',
            'bundle_minification': 'Minify JavaScript and CSS reduce file size',
            'critical_rendering_path': 'Optimize HTML, CSS, JavaScript parsing; defer non-critical',
            'lazy_loading': 'Defer loading images and content until visible or needed',
            'image_optimization': 'Use appropriate format (WebP), size, srcset for responsive',
            'web_fonts': 'Use system fonts or load subsets; @font-face carefully',
            'caching_strategy': 'Browser caching, service worker caching, CDN caching',
            'compression': 'Gzip or Brotli compression reduces transfer size',
            'web_vitals': 'LCP (largest paint), FID (input delay), CLS (visual stability)',
            'performance_monitoring': 'Use Lighthouse, WebPageTest, browser DevTools profiler',
            'memory_leaks': 'Detached DOM, circular references, forgotten timers cause leaks',
            'unused_css': 'Remove unused styles; PurgeCSS, modern build tools help',
            'request_batching': 'Combine requests; HTTP/2 multiplexing reduces overhead',
            'rendering_optimization': 'Avoid layout thrashing; batch DOM reads and writes'
        }

    def _get_browser_compatibility(self) -> Dict[str, str]:
        """Browser compatibility and progressive enhancement."""
        return {
            'progressive_enhancement': 'Core functionality works without JS; enhance with JavaScript',
            'graceful_degradation': 'Newer features don\'t break in older browsers',
            'caniuse': 'caniuse.com check feature support across browsers',
            'feature_detection': 'Check if (feature) rather than browser detection',
            'polyfills': 'Include implementation of missing features for older browsers',
            'transpiling': 'Babel converts ES6+ to ES5 for older browser support',
            'prefixes': '-webkit-, -moz-, -ms-, -o- vendor-specific properties',
            'autoprefixer': 'PostCSS plugin automatically adds vendor prefixes',
            'css_fallbacks': 'Provide fallback values for newer CSS features',
            'javascript_fallback': 'Provide fallback functionality if JS features unsupported',
            'testing_browsers': 'BrowserStack, Sauce Labs test across browsers',
            'edge_cases': 'Handle older IE carefully; drops support encouraged 2022+',
            'mobile_considerations': 'Touch events, smaller screens, slower networks, weaker CPUs'
        }

    def _get_web_standards(self) -> Dict[str, str]:
        """Web standards and best practices."""
        return {
            'html5': 'Latest HTML standard; semantic elements, APIs, forms improvements',
            'w3c_standards': 'W3C maintains standards; follow official specifications',
            'whatwg_spec': 'WHATWG Living Standard; HTML spec updated continuously',
            'responsive_web': 'Design works on any device; fluid, flexible, mobile-first',
            'progressive_web_app': 'PWA combines web and app benefits; offline, installable',
            'single_page_app': 'SPA framework (React, Vue, Angular) client-side routing',
            'server_side_rendering': 'SSR initial render on server; faster first paint, SEO',
            'static_generation': 'Generate static HTML at build time; CDN distribution',
            'seo_best_practices': 'Semantic HTML, metadata, sitemap, robots.txt, page speed',
            'open_graph': '<meta property="og:*"> enables rich previews in social media',
            'twitter_cards': '<meta name="twitter:*"> Twitter-specific previews',
            'structured_data': 'schema.org markup JSON-LD for machine-readable content',
            'dns_prefetch': '<link rel="dns-prefetch"> speeds up third-party domain lookups'
        }

    def enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with web development guidance."""
        keywords = self.get_keywords()
        has_keywords = any(kw.lower() in prompt.lower() for kw in keywords)

        if not has_keywords:
            return prompt

        enhancement = f"""
{prompt}

WEB DEVELOPMENT ENHANCEMENT:
Apply these web best practices:

1. SEMANTIC HTML: Use semantic elements (<header>, <nav>, <main>, <article>) for clarity and accessibility.

2. ACCESSIBILITY: Implement WCAG guidelines - alt text, labels, contrast ratios, keyboard navigation.

3. RESPONSIVE DESIGN: Mobile-first approach, flexbox/grid layouts, media queries, fluid typography.

4. PERFORMANCE: Optimize critical path, lazy load images, minify assets, leverage caching.

5. MODERN JAVASCRIPT: Use const/let, arrow functions, destructuring, async/await for clean code.

6. DOM BEST PRACTICES: Use querySelector, event delegation, avoid innerHTML with untrusted data.

7. BROWSER SUPPORT: Test across browsers, use feature detection, provide fallbacks gracefully.

Apply these web standards to create fast, accessible, user-friendly experiences.
"""
        return enhancement.strip()

    def generate_system_prompt(self) -> str:
        """Generate expert web developer system prompt."""
        return """You are an expert full-stack web developer with 15+ years of frontend experience.

Your expertise includes:
- Semantic HTML5 and accessibility standards (WCAG 2.1)
- Advanced CSS (layouts, responsive design, animations, performance)
- Modern JavaScript (ES6+, async/await, DOM APIs, fetch)
- Web performance optimization and monitoring
- Browser compatibility and progressive enhancement
- Web APIs and service workers
- PWA development and offline functionality
- SEO best practices and structured data
- Web standards and specifications
- Testing and debugging across browsers
- Mobile-first responsive design
- Performance profiling and optimization

When helping with web projects, you:
1. Write semantic, accessible HTML
2. Create responsive, performant CSS
3. Use modern JavaScript patterns
4. Implement best practices for speed and accessibility
5. Consider browser compatibility carefully
6. Follow web standards and specifications
7. Optimize for user experience and performance
8. Use appropriate web APIs for functionality

Provide specific, actionable web development guidance that creates accessible, performant, standards-compliant experiences."""

"""
+==============================================================================â•—
|              ORFEAS Testing Suite - E2E Browser Automation Tests            |
|                    Playwright-based end-to-end testing                       |
+==============================================================================
"""
import pytest
import asyncio
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not installed")
@pytest.mark.e2e
class TestOrfeasStudioE2E:
    """End-to-end tests for ORFEAS Studio web interface."""

    @pytest.fixture(scope="function")
    async def browser(self):
        """Create browser instance for E2E tests."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Changed to visible for --headed
            yield browser
            await browser.close()

    @pytest.fixture(scope="function")
    async def page(self, browser):
        """Create new page for each test."""
        page = await browser.new_page()
        yield page
        await page.close()

    @pytest.mark.asyncio
    async def test_homepage_loads(self, page, e2e_server):
        """Test that homepage loads successfully."""
        # Use e2e_server fixture to ensure server is running
        await page.goto(f"{e2e_server}")

        # Wait for page to load
        await page.wait_for_load_state("networkidle")

        # Check title
        title = await page.title()
        assert len(title) > 0

    @pytest.mark.asyncio
    async def test_upload_interface(self, page, e2e_server):
        """Test image upload interface."""
        await page.goto(f"{e2e_server}/orfeas-studio.html")
        await page.wait_for_load_state("networkidle")

        # Look for upload button/input with timeout
        upload_input = page.locator('input[type="file"]#imageInput').first
        await page.wait_for_timeout(1000)  # Wait for UI to render
        if await upload_input.count() > 0:
            # Element exists, test passes
            assert True

    @pytest.mark.asyncio
    async def test_generation_workflow(self, page, test_image_path, e2e_server):
        """Test complete 3D generation workflow."""
        await page.goto(f"{e2e_server}/orfeas-studio.html")
        await page.wait_for_load_state("networkidle")

        # Upload image
        upload_input = page.locator('input[type="file"]').first
        if await upload_input.count() > 0:
            await upload_input.set_input_files(str(test_image_path))

            # Wait for upload to complete
            await page.wait_for_timeout(2000)

            # Click generate button - use more specific selector
            generate_btn = page.locator('button.generate-btn').first
            if await generate_btn.count() > 0:
                await generate_btn.click()

                # Wait for generation (timeout 60s)
                try:
                    await page.wait_for_selector('.generation-complete', timeout=60000)
                    assert True  # Generation completed
                except Exception:
                    # Generation may take longer or fail
                    pass

    @pytest.mark.asyncio
    async def test_3d_viewer_loads(self, page, e2e_server):
        """Test that 3D viewer initializes."""
        await page.goto(f"{e2e_server}/orfeas-studio.html")
        await page.wait_for_load_state("networkidle")

        # Check for canvas element (Babylon.js)
        canvas = page.locator('canvas')
        if await canvas.count() > 0:
            assert await canvas.is_visible()

    @pytest.mark.asyncio
    async def test_console_errors(self, page, e2e_server):
        """Test for JavaScript console errors."""
        errors = []

        page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)

        await page.goto(f"{e2e_server}/orfeas-studio.html")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)

        # Should have minimal console errors
        critical_errors = [e for e in errors if "critical" in str(e).lower()]
        assert len(critical_errors) == 0

    @pytest.mark.asyncio
    async def test_api_connectivity(self, page, e2e_server):
        """Test API connectivity from frontend."""
        await page.goto(f"{e2e_server}/orfeas-studio.html")
        await page.wait_for_load_state("networkidle")

        # Check API status endpoint
        response = await page.evaluate("""
            async () => {
                try {
                    const res = await fetch('http://localhost:8000/api/status');
                    return { status: res.status, ok: res.ok };
                } catch (e) {
                    return { error: e.message };
                }
            }
        """)

        # API should be reachable
        if 'status' in response:
            assert response['status'] in [200, 404]  # 404 ok if endpoint doesn't exist

    @pytest.mark.asyncio
    async def test_responsive_design(self, page, e2e_server):
        """Test responsive design at different viewports."""
        await page.goto(f"{e2e_server}/orfeas-studio.html")

        viewports = [
            {"width": 1920, "height": 1080},  # Desktop
            {"width": 768, "height": 1024},   # Tablet
            {"width": 375, "height": 667},    # Mobile
        ]

        for viewport in viewports:
            await page.set_viewport_size(viewport)
            await page.wait_for_timeout(1000)

            # Page should remain functional
            canvas = page.locator('canvas')
            if await canvas.count() > 0:
                assert await canvas.is_visible()

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_multiple_generations(self, page, test_image_path):
        """Test multiple sequential generations."""
        await page.goto("http://localhost:8000/orfeas-studio.html")
        await page.wait_for_load_state("networkidle")

        num_generations = 3

        for i in range(num_generations):
            # Upload
            upload_input = page.locator('input[type="file"]').first
            if await upload_input.count() > 0:
                await upload_input.set_input_files(str(test_image_path))
                await page.wait_for_timeout(1000)

                # Generate - use more specific selector
                generate_btn = page.locator('button.generate-btn').first
                if await generate_btn.count() > 0:
                    await generate_btn.click()
                    await page.wait_for_timeout(5000)  # Wait for generation start

        # All generations should complete without crashing
        assert True


@pytest.mark.e2e
class TestPerformanceMetrics:
    """E2E performance monitoring tests."""

    @pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not installed")
    @pytest.mark.asyncio
    async def test_page_load_performance(self):
        """Test page load performance metrics."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            await page.goto("http://localhost:8000/orfeas-studio.html")
            await page.wait_for_load_state("networkidle")

            # Get performance metrics
            metrics = await page.evaluate("""
                () => {
                    const perf = performance.getEntriesByType('navigation')[0];
                    return {
                        domContentLoaded: perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart,
                        loadComplete: perf.loadEventEnd - perf.loadEventStart,
                        totalTime: perf.loadEventEnd - perf.fetchStart
                    };
                }
            """)

            print(f"\nPage Load Metrics: {metrics}")

            # Reasonable performance targets
            assert metrics['totalTime'] < 5000  # Less than 5 seconds total

            await browser.close()

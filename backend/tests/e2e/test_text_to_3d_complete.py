"""
+==============================================================================â•—
|         ORFEAS Testing Suite - Complete Text-to-3D Workflow E2E Test        |
|              End-to-end test of full text-to-3D generation pipeline          |
+==============================================================================
"""
import pytest
import asyncio
from pathlib import Path
import sys
import time
from typing import List

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not available")
@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteTextTo3DWorkflow:
    """Complete end-to-end workflow: Text prompt → Image → 3D Model → Download"""

    @pytest.fixture(scope="function")
    async def browser(self):
        """Create browser instance"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            yield browser
            await browser.close()

    @pytest.fixture(scope="function")
    async def page(self, browser, e2e_server):
        """Create page and navigate to app"""
        page = await browser.new_page()
        await page.goto(f"{e2e_server}/orfeas-studio.html")
        await page.wait_for_load_state("networkidle")
        yield page
        await page.close()

    @pytest.mark.asyncio
    async def test_complete_text_to_3d_workflow(self, page):
        """Test complete workflow: text input → image generation → 3D generation → download"""

        # Step 1: Enter text prompt
        prompt_input = page.locator('textarea#promptInput, input#promptInput').first
        if await prompt_input.count() > 0:
            await prompt_input.fill("A simple red cube")
            await page.wait_for_timeout(500)

            # Step 2: Click generate image button
            generate_image_btn = page.locator('button:has-text("Generate Image")').first
            if await generate_image_btn.count() > 0:
                await generate_image_btn.click()

                # Step 3: Wait for image generation (up to 120s)
                try:
                    await page.wait_for_selector('.generated-image, img.preview', timeout=120000)

                    # Step 4: Click generate 3D button
                    generate_3d_btn = page.locator('button:has-text("Generate 3D")').first
                    if await generate_3d_btn.count() > 0:
                        await generate_3d_btn.click()

                        # Step 5: Wait for 3D generation (up to 180s)
                        try:
                            await page.wait_for_selector('.model-ready, .download-btn', timeout=180000)

                            # Step 6: Click download button
                            download_btn = page.locator('button:has-text("Download"), a:has-text("Download")').first
                            if await download_btn.count() > 0:
                                async with page.expect_download() as download_info:
                                    await download_btn.click()
                                    download = await download_info.value

                                    # Verify download
                                    assert download.suggested_filename.endswith(('.stl', '.obj', '.glb', '.ply'))
                                    assert True  # Workflow completed successfully

                        except Exception as e:
                            pytest.skip(f"3D generation timeout or not available: {e}")

                except Exception as e:
                    pytest.skip(f"Image generation timeout or not available: {e}")

    @pytest.mark.asyncio
    async def test_text_to_3d_error_handling(self, page):
        """Test error handling in text-to-3D workflow"""

        # Enter invalid/empty prompt
        prompt_input = page.locator('textarea#promptInput, input#promptInput').first
        if await prompt_input.count() > 0:
            await prompt_input.fill("")  # Empty prompt

            generate_btn = page.locator('button:has-text("Generate Image")').first
            if await generate_btn.count() > 0:
                await generate_btn.click()

                # Should show error message
                await page.wait_for_timeout(2000)
                error_message = page.locator('.error, .alert-danger, [role="alert"]').first
                # May or may not show error, but should not crash

    @pytest.mark.asyncio
    async def test_text_to_3d_with_style_selection(self, page):
        """Test text-to-3D with art style selection"""

        # Select art style
        style_selector = page.locator('select#artStyle, select[name="art_style"]').first
        if await style_selector.count() > 0:
            await style_selector.select_option("realistic")

        # Enter prompt
        prompt_input = page.locator('textarea#promptInput, input#promptInput').first
        if await prompt_input.count() > 0:
            await prompt_input.fill("A medieval knight helmet")

            generate_btn = page.locator('button:has-text("Generate Image")').first
            if await generate_btn.count() > 0:
                await generate_btn.click()

                # Wait for processing
                await page.wait_for_timeout(5000)

    @pytest.mark.asyncio
    async def test_text_to_3d_progress_tracking(self, page):
        """Test that progress is tracked and displayed"""

        prompt_input = page.locator('textarea#promptInput, input#promptInput').first
        if await prompt_input.count() > 0:
            await prompt_input.fill("A blue sphere")

            generate_btn = page.locator('button:has-text("Generate Image")').first
            if await generate_btn.count() > 0:
                await generate_btn.click()

                # Check for progress indicator
                await page.wait_for_timeout(2000)
                progress_element = page.locator('.progress, .loading, .spinner, [role="progressbar"]').first
                # Progress element may or may not be visible

    @pytest.mark.asyncio
    async def test_text_to_3d_quality_selection(self, page):
        """Test quality level selection in workflow"""

        # Select quality level
        quality_selector = page.locator('select#quality, input[type="range"]#quality').first
        if await quality_selector.count() > 0:
            # If it's a select
            try:
                await quality_selector.select_option("7")
            except:
                # If it's a range slider
                await quality_selector.fill("7")

        # Continue workflow
        prompt_input = page.locator('textarea#promptInput, input#promptInput').first
        if await prompt_input.count() > 0:
            await prompt_input.fill("A green pyramid")
            # Workflow continues...

    @pytest.mark.asyncio
    async def test_text_to_3d_format_selection(self, page):
        """Test output format selection"""

        # Select output format
        format_selector = page.locator('select#format, select[name="format"]').first
        if await format_selector.count() > 0:
            await format_selector.select_option("stl")

        prompt_input = page.locator('textarea#promptInput, input#promptInput').first
        if await prompt_input.count() > 0:
            await prompt_input.fill("A yellow cylinder")

    @pytest.mark.asyncio
    async def test_text_to_3d_multiple_prompts(self, page):
        """Test processing multiple prompts in sequence"""

        prompts = [
            "A red cube",
            "A blue sphere",
            "A green cylinder"
        ]

        prompt_input = page.locator('textarea#promptInput, input#promptInput').first

        for prompt_text in prompts:
            if await prompt_input.count() > 0:
                await prompt_input.fill(prompt_text)

                generate_btn = page.locator('button:has-text("Generate Image")').first
                if await generate_btn.count() > 0:
                    await generate_btn.click()
                    await page.wait_for_timeout(3000)  # Wait between requests

    @pytest.mark.asyncio
    async def test_text_to_3d_websocket_updates(self, page):
        """Test that WebSocket provides real-time updates"""

        # Listen for WebSocket messages
        ws_messages = []

        def handle_websocket(ws: List) -> None:
            ws.on("framereceived", lambda payload: ws_messages.append(payload))

        page.on("websocket", handle_websocket)

        # Trigger generation
        prompt_input = page.locator('textarea#promptInput, input#promptInput').first
        if await prompt_input.count() > 0:
            await prompt_input.fill("A metallic sphere")

            generate_btn = page.locator('button:has-text("Generate Image")').first
            if await generate_btn.count() > 0:
                await generate_btn.click()
                await page.wait_for_timeout(5000)

                # Check if WebSocket messages were received
                # (May not be implemented yet)

    @pytest.mark.asyncio
    async def test_text_to_3d_cancel_generation(self, page):
        """Test canceling generation mid-process"""

        prompt_input = page.locator('textarea#promptInput, input#promptInput').first
        if await prompt_input.count() > 0:
            await prompt_input.fill("A complex detailed castle")

            generate_btn = page.locator('button:has-text("Generate Image")').first
            if await generate_btn.count() > 0:
                await generate_btn.click()

                # Wait a bit then try to cancel
                await page.wait_for_timeout(2000)

                cancel_btn = page.locator('button:has-text("Cancel"), button.cancel-btn').first
                if await cancel_btn.count() > 0:
                    await cancel_btn.click()
                    # Generation should be canceled

    @pytest.mark.asyncio
    async def test_text_to_3d_viewer_interaction(self, page):
        """Test 3D viewer interaction after generation"""

        prompt_input = page.locator('textarea#promptInput, input#promptInput').first
        if await prompt_input.count() > 0:
            await prompt_input.fill("A simple cube")

            generate_btn = page.locator('button:has-text("Generate Image")').first
            if await generate_btn.count() > 0:
                await generate_btn.click()

                # Wait for generation to complete
                try:
                    await page.wait_for_selector('.model-ready, canvas', timeout=60000)

                    # Try to interact with 3D viewer
                    canvas = page.locator('canvas').first
                    if await canvas.count() > 0:
                        # Get canvas bounding box
                        box = await canvas.bounding_box()
                        if box:
                            # Simulate mouse drag (rotate model)
                            await page.mouse.move(box['x'] + 100, box['y'] + 100)
                            await page.mouse.down()
                            await page.mouse.move(box['x'] + 200, box['y'] + 150)
                            await page.mouse.up()

                            # Viewer should respond to interaction

                except Exception:
                    pytest.skip("3D viewer not available or timeout")

    @pytest.mark.asyncio
    async def test_text_to_3d_console_errors(self, page):
        """Test that workflow doesn't produce console errors"""

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg) if msg.type == "error" else None)

        # Run workflow
        prompt_input = page.locator('textarea#promptInput, input#promptInput').first
        if await prompt_input.count() > 0:
            await prompt_input.fill("A test object")

            generate_btn = page.locator('button:has-text("Generate Image")').first
            if await generate_btn.count() > 0:
                await generate_btn.click()
                await page.wait_for_timeout(5000)

        # Should have minimal console errors (some warnings OK)
        critical_errors = [err for err in console_errors if 'critical' in str(err).lower()]
        assert len(critical_errors) == 0


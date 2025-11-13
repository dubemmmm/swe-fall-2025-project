"""
Test improved adoption form styling
"""
import asyncio
from playwright.async_api import async_playwright

async def test_adoption_form():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        try:
            # Login
            await page.goto("http://localhost:8000/users/login/")
            await page.fill('input[name="username"]', 'frontendtest')
            await page.fill('input[name="password"]', 'TestPass123!')
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(2000)

            # Go to adoption form
            await page.goto("http://localhost:8000/adoption/create/")
            await page.wait_for_timeout(1000)

            # Full page screenshot
            await page.screenshot(path='.local_notes/screenshots/ticket2_improved_full.png', full_page=True)
            print("✅ Captured: Full adoption form (improved)")

            # Top section
            await page.screenshot(path='.local_notes/screenshots/ticket2_improved_top.png', full_page=False)
            print("✅ Captured: Top section (improved)")

            # Scroll to bottom to see cancel button
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(500)
            await page.screenshot(path='.local_notes/screenshots/ticket2_improved_bottom.png', full_page=False)
            print("✅ Captured: Bottom with cancel button (improved)")

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_adoption_form())

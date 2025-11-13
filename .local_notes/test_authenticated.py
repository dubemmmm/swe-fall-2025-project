"""
Test authenticated pages for Jira tickets
"""
import asyncio
from playwright.async_api import async_playwright

async def test_authenticated():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        base_url = "http://localhost:8000"

        try:
            # Login first
            print("Logging in...")
            await page.goto(f"{base_url}/users/login/")
            await page.fill('input[name="username"]', 'frontendtest')
            await page.fill('input[name="password"]', 'TestPass123!')
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(2000)

            # Ticket 2: Adoption Form with Cancel Button
            print("\nTesting Ticket 2: Adoption Form Cancel Button...")
            await page.goto(f"{base_url}/adoption/create/")
            await page.wait_for_timeout(1000)
            await page.screenshot(path='.local_notes/screenshots/ticket2_1_adoption_form_top.png', full_page=False)

            # Scroll to see cancel button
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(500)
            await page.screenshot(path='.local_notes/screenshots/ticket2_2_adoption_form_bottom_cancel.png', full_page=False)

            # Full page
            await page.screenshot(path='.local_notes/screenshots/ticket2_3_adoption_form_full.png', full_page=True)
            print("✅ Captured: Adoption form with cancel button")

            # Ticket 6: Playdate Form with Cancel Button
            print("\nTesting Ticket 6: Playdate Form Cancel Button...")
            await page.goto(f"{base_url}/playdates/create/")
            await page.wait_for_timeout(1000)
            await page.screenshot(path='.local_notes/screenshots/ticket6_1_playdate_form_top.png', full_page=False)

            # Scroll to bottom to see cancel button
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(500)
            await page.screenshot(path='.local_notes/screenshots/ticket6_2_playdate_form_bottom_cancel.png', full_page=False)

            # Full page
            await page.screenshot(path='.local_notes/screenshots/ticket6_3_playdate_form_full.png', full_page=True)
            print("✅ Captured: Playdate form with cancel button")

            # Ticket 5: Notifications Page
            print("\nTesting Ticket 5: Notifications Page...")
            await page.goto(f"{base_url}/notifications/")
            await page.wait_for_timeout(1000)
            await page.screenshot(path='.local_notes/screenshots/ticket5_1_notifications_page.png', full_page=True)
            print("✅ Captured: Notifications page")

            # Ticket 3: Pet Photo Upload (part of pet creation form)
            print("\nTesting Ticket 3: Pet Form with Photo Validation...")
            await page.goto(f"{base_url}/pets/create/")
            await page.wait_for_timeout(1000)
            await page.screenshot(path='.local_notes/screenshots/ticket3_1_pet_form.png', full_page=True)
            print("✅ Captured: Pet creation form (photo upload)")

            print("\n" + "="*60)
            print("✅ All authenticated screenshots saved!")
            print("="*60)
            print("\nCaptured:")
            print("  • Ticket 2: Adoption form with cancel button (3 screenshots)")
            print("  • Ticket 3: Pet form with photo validation (1 screenshot)")
            print("  • Ticket 5: Notifications page (1 screenshot)")
            print("  • Ticket 6: Playdate form with cancel button (3 screenshots)")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path='.local_notes/screenshots/error_auth.png', full_page=True)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_authenticated())

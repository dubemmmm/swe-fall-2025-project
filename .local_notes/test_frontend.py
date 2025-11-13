"""
Playwright script to test frontend changes for Jira tickets
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def test_frontend():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        base_url = "http://localhost:8000"

        try:
            # First, create a test user and login
            print("Setting up test user...")
            await page.goto(f"{base_url}/users/register/")
            await page.fill('input[name="username"]', 'testuser_frontend')
            await page.fill('input[name="email"]', 'testfrontend@example.com')
            await page.fill('input[name="password1"]', 'TestPass123!')
            await page.fill('input[name="password2"]', 'TestPass123!')
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(1000)

            # Ticket 7: Password Reset Flow
            print("Testing Ticket 7: Password Reset...")
            await page.goto(f"{base_url}/users/login/")
            await page.screenshot(path='.local_notes/screenshots/ticket7_1_login_page.png', full_page=True)

            # Click "Forgot Password?" link
            await page.click('a[href*="password-reset"]')
            await page.wait_for_timeout(500)
            await page.screenshot(path='.local_notes/screenshots/ticket7_2_password_reset_form.png', full_page=True)

            # Fill in email
            await page.fill('input[name="email"]', 'testfrontend@example.com')
            await page.screenshot(path='.local_notes/screenshots/ticket7_3_password_reset_filled.png', full_page=True)

            # Submit form
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(1000)
            await page.screenshot(path='.local_notes/screenshots/ticket7_4_password_reset_done.png', full_page=True)

            # Login for other tests
            print("Logging in...")
            await page.goto(f"{base_url}/users/login/")
            await page.fill('input[name="username"]', 'testuser_frontend')
            await page.fill('input[name="password"]', 'TestPass123!')
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(1500)

            # Create a pet first (needed for adoption)
            print("Creating test pet...")
            await page.goto(f"{base_url}/pets/create/")
            await page.fill('input[name="name"]', 'Test Pet')
            await page.select_option('select[name="species"]', 'DOG')
            await page.fill('input[name="breed"]', 'Test Breed')
            await page.fill('input[name="age"]', '2')
            await page.select_option('select[name="general_size"]', 'MEDIUM')
            await page.select_option('select[name="energy_level"]', 'MEDIUM')
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(1500)

            # Ticket 2: Adoption Form with Cancel Button
            print("Testing Ticket 2: Adoption Form Cancel Button...")
            await page.goto(f"{base_url}/adoption/create/")
            await page.wait_for_timeout(500)
            await page.screenshot(path='.local_notes/screenshots/ticket2_1_adoption_form.png', full_page=True)

            # Scroll to bottom to see cancel button
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(300)
            await page.screenshot(path='.local_notes/screenshots/ticket2_2_adoption_form_cancel_button.png', full_page=True)

            # Ticket 6: Playdate Form with Cancel Button
            print("Testing Ticket 6: Playdate Form Cancel Button...")
            await page.goto(f"{base_url}/playdates/create/")
            await page.wait_for_timeout(500)
            await page.screenshot(path='.local_notes/screenshots/ticket6_1_playdate_form.png', full_page=True)

            # Scroll to bottom to see cancel button
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(300)
            await page.screenshot(path='.local_notes/screenshots/ticket6_2_playdate_form_cancel_button.png', full_page=True)

            # Ticket 5: Notifications page
            print("Testing Ticket 5: Notifications...")
            await page.goto(f"{base_url}/notifications/")
            await page.wait_for_timeout(500)
            await page.screenshot(path='.local_notes/screenshots/ticket5_notifications_page.png', full_page=True)

            print("\n✅ All screenshots saved to .local_notes/screenshots/")
            print("\nScreenshots captured:")
            print("- Ticket 2: Adoption form with cancel button (2 screenshots)")
            print("- Ticket 5: Notifications page (1 screenshot)")
            print("- Ticket 6: Playdate form with cancel button (2 screenshots)")
            print("- Ticket 7: Password reset flow (4 screenshots)")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            await page.screenshot(path='.local_notes/screenshots/error.png', full_page=True)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_frontend())

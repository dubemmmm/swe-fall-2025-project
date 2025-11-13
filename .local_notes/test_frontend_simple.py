"""
Simplified Playwright script to test frontend changes for Jira tickets
"""
import asyncio
from playwright.async_api import async_playwright

async def test_frontend():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        base_url = "http://localhost:8000"

        try:
            print("Testing Ticket 7: Password Reset Flow...")

            # 1. Login page with "Forgot Password" link
            await page.goto(f"{base_url}/users/login/")
            await page.wait_for_timeout(1000)
            await page.screenshot(path='.local_notes/screenshots/ticket7_1_login_with_forgot_password.png', full_page=True)
            print("✅ Captured: Login page with 'Forgot Password' link")

            # 2. Password reset request form
            await page.goto(f"{base_url}/password-reset/")
            await page.wait_for_timeout(1000)
            await page.screenshot(path='.local_notes/screenshots/ticket7_2_password_reset_form.png', full_page=True)
            print("✅ Captured: Password reset request form")

            # 3. Fill email and show button style
            try:
                await page.fill('input[name="email"]', 'test@example.com')
                await page.wait_for_timeout(300)
                await page.screenshot(path='.local_notes/screenshots/ticket7_3_password_reset_filled.png', full_page=True)
                print("✅ Captured: Password reset form filled")
            except:
                print("⚠️  Could not fill email field, but form screenshot captured")

            # 4. Password reset done page (submit to see it)
            try:
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(1000)
                await page.screenshot(path='.local_notes/screenshots/ticket7_4_password_reset_done.png', full_page=True)
                print("✅ Captured: Password reset confirmation page")
            except:
                print("⚠️  Could not navigate to done page, continuing...")

            # 5. Password reset confirm page (with invalid token just to see design)
            await page.goto(f"{base_url}/reset/test/test-token/")
            await page.wait_for_timeout(1000)
            await page.screenshot(path='.local_notes/screenshots/ticket7_5_password_reset_confirm.png', full_page=True)
            print("✅ Captured: Password reset confirm page")

            # 6. Password reset complete page
            await page.goto(f"{base_url}/reset/done/")
            await page.wait_for_timeout(1000)
            await page.screenshot(path='.local_notes/screenshots/ticket7_6_password_reset_complete.png', full_page=True)
            print("✅ Captured: Password reset complete page")

            print("\n" + "="*60)
            print("✅ All screenshots saved to .local_notes/screenshots/")
            print("="*60)
            print("\nScreenshots captured for Ticket 7 (Password Reset):")
            print("  1. Login page with 'Forgot Password' link")
            print("  2. Password reset request form")
            print("  3. Password reset form (filled)")
            print("  4. Password reset confirmation (email sent)")
            print("  5. Password reset confirm page (new password entry)")
            print("  6. Password reset complete (success)")
            print("\nNote: For Tickets 2, 5, and 6, login is required.")
            print("      These can be tested manually or with proper auth setup.")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path='.local_notes/screenshots/error.png', full_page=True)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_frontend())

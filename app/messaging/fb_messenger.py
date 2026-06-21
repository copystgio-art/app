"""
Sends Facebook messages via Playwright using a saved session.
Manages login and session persistence.
"""
import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright, Page, BrowserContext

from app.core.config import settings


async def login_and_save_session() -> bool:
    """
    Opens a visible browser for the user to log in to Facebook.
    Saves the session for future automated use.
    Returns True on success.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.facebook.com/login", timeout=30000)
        print(">>> Effettua il login su Facebook nel browser aperto.")
        print(">>> Quando hai finito, premi INVIO qui per salvare la sessione.")
        input()

        storage = await context.storage_state()
        Path(settings.fb_session_path).parent.mkdir(parents=True, exist_ok=True)
        with open(settings.fb_session_path, "w") as f:
            json.dump(storage, f)

        await browser.close()
        print(f"Sessione salvata in {settings.fb_session_path}")
        return True


def _session_exists() -> bool:
    return os.path.exists(settings.fb_session_path)


async def send_facebook_message(page_url: str, message: str) -> bool:
    """
    Navigates to a Facebook page and sends a message via Messenger.
    Requires a saved session.
    Returns True if message sent successfully.
    """
    if not _session_exists():
        raise RuntimeError(
            f"Sessione Facebook non trovata in {settings.fb_session_path}. "
            "Esegui prima il login con /api/auth/fb-login"
        )

    with open(settings.fb_session_path) as f:
        storage_state = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=storage_state,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        try:
            # Go to the page
            await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)

            # Click "Send Message" button
            sent = await _click_send_message_and_type(page, message)
            return sent

        finally:
            await browser.close()


async def _click_send_message_and_type(page: Page, message: str) -> bool:
    """Finds and clicks the Send Message button, then types and sends the message."""
    # Try multiple selectors for "Send Message" / "Invia messaggio"
    send_btn_selectors = [
        'a[href*="messenger.com/t/"]',
        'div[aria-label="Invia messaggio"]',
        'div[aria-label="Send Message"]',
        'a[data-testid="message-button"]',
        '//span[contains(text(), "Invia messaggio")]',
        '//span[contains(text(), "Send Message")]',
    ]

    clicked = False
    for sel in send_btn_selectors:
        try:
            if sel.startswith("//"):
                el = page.locator(f"xpath={sel}").first
            else:
                el = page.locator(sel).first
            await el.click(timeout=5000)
            clicked = True
            break
        except Exception:
            continue

    if not clicked:
        # Try finding via text content
        try:
            await page.get_by_text("Invia messaggio", exact=False).first.click(timeout=5000)
            clicked = True
        except Exception:
            pass

    if not clicked:
        return False

    await asyncio.sleep(2)

    # The Messenger popup or new window
    # Type message in the input
    msg_input_selectors = [
        'div[aria-label="Messaggio"]',
        'div[aria-label="Message"]',
        'div[role="textbox"]',
        'textarea[placeholder*="messag"]',
    ]

    typed = False
    for sel in msg_input_selectors:
        try:
            el = page.locator(sel).last
            await el.click(timeout=5000)
            await el.type(message, delay=30)
            typed = True
            break
        except Exception:
            continue

    if not typed:
        return False

    await asyncio.sleep(1)

    # Press Enter or click Send
    try:
        await page.keyboard.press("Enter")
        await asyncio.sleep(2)
        return True
    except Exception:
        return False

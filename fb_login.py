"""Run this script directly to log in to Facebook and save the session."""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

SESSION_PATH = "./fb_session.json"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.facebook.com/login")
        print("\n>>> Si è aperto il browser Facebook.")
        print(">>> Effettua il login manualmente, poi torna qui e premi INVIO.")
        input()
        storage = await context.storage_state()
        with open(SESSION_PATH, "w") as f:
            json.dump(storage, f)
        await browser.close()
        print(f"Sessione salvata in {SESSION_PATH}")


asyncio.run(main())

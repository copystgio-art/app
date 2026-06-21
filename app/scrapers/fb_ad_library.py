"""
Scraper for Facebook Ad Library using Playwright.
No login required — Ad Library is public.
"""
import asyncio
import re
from dataclasses import dataclass, field
from playwright.async_api import async_playwright, Page, BrowserContext


@dataclass
class AdData:
    ad_id: str
    page_name: str
    page_id: str
    page_url: str
    website_url: str | None
    ad_text: str | None
    ad_image_url: str | None
    ad_started: str | None
    search_keyword: str
    category: str | None = None
    raw_data: dict = field(default_factory=dict)


AD_LIBRARY_URL = "https://www.facebook.com/ads/library/"


async def scrape_ad_library(
    keyword: str,
    country: str = "IT",
    ad_type: str = "ALL",
    max_results: int = 50,
    headless: bool = True,
) -> list[AdData]:
    ads: list[AdData] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="it-IT",
        )
        page = await context.new_page()

        try:
            url = (
                f"{AD_LIBRARY_URL}"
                f"?active_status=active"
                f"&ad_type={ad_type}"
                f"&country={country}"
                f"&q={keyword}"
                f"&search_type=keyword_unordered"
                f"&media_type=all"
            )
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)

            # Accept cookie banner if present
            try:
                await page.click('[data-testid="cookie-policy-manage-dialog-accept-button"]', timeout=5000)
                await asyncio.sleep(1)
            except Exception:
                pass

            await _scroll_and_collect(page, ads, keyword, max_results)

        finally:
            await browser.close()

    return ads


async def _scroll_and_collect(page: Page, ads: list[AdData], keyword: str, max_results: int):
    seen_ids: set[str] = set()
    no_new_count = 0

    for _ in range(30):
        if len(ads) >= max_results:
            break

        cards = await page.query_selector_all('[class*="x8gbvx8"]')
        if not cards:
            # fallback selector
            cards = await page.query_selector_all('[data-testid*="ad-library"]')

        # Try generic card detection by structure
        cards = await page.query_selector_all("div[class*='_7jyr']") or \
                await page.query_selector_all("div[class*='xh8yej3']")

        extracted = await _extract_from_page(page, keyword, seen_ids)
        new_count = 0
        for ad in extracted:
            if len(ads) >= max_results:
                break
            ads.append(ad)
            new_count += 1

        if new_count == 0:
            no_new_count += 1
            if no_new_count >= 3:
                break
        else:
            no_new_count = 0

        await page.evaluate("window.scrollBy(0, 1200)")
        await asyncio.sleep(2)


async def _extract_from_page(page: Page, keyword: str, seen_ids: set[str]) -> list[AdData]:
    """Extract ad data using JS evaluation on the page."""
    results = []

    raw_ads = await page.evaluate("""
        () => {
            const ads = [];
            // Ad Library cards usually have a link to the page and the ad content
            const cards = document.querySelectorAll('[class*="xh8yej3"], [class*="_7jyr"], [class*="x1n2onr6"]');
            cards.forEach(card => {
                const pageLink = card.querySelector('a[href*="/ads/library"], a[href*="facebook.com"]');
                const textEl = card.querySelector('[class*="x1lliihq"], span, p');
                const img = card.querySelector('img[src*="fbcdn"]');
                const dateEl = card.querySelector('[class*="x1rg5ohu"]');

                const ad = {
                    page_name: pageLink ? pageLink.innerText.trim() : null,
                    page_url: pageLink ? pageLink.href : null,
                    ad_text: textEl ? textEl.innerText.trim().substring(0, 2000) : null,
                    ad_image_url: img ? img.src : null,
                    ad_started: dateEl ? dateEl.innerText.trim() : null,
                    html_snippet: card.innerHTML.substring(0, 500),
                };
                if (ad.page_name && ad.page_name.length > 0) {
                    ads.push(ad);
                }
            });
            return ads;
        }
    """)

    for i, raw in enumerate(raw_ads):
        page_url = raw.get("page_url") or ""
        page_id = _extract_page_id(page_url) or f"unknown_{i}"
        ad_id = f"{page_id}_{keyword}_{i}"

        if ad_id in seen_ids:
            continue
        seen_ids.add(ad_id)

        # Try to find website URL from the card snippet
        website_url = _extract_website_from_snippet(raw.get("html_snippet", ""))

        results.append(AdData(
            ad_id=ad_id,
            page_name=raw.get("page_name") or "Unknown",
            page_id=page_id,
            page_url=page_url,
            website_url=website_url,
            ad_text=raw.get("ad_text"),
            ad_image_url=raw.get("ad_image_url"),
            ad_started=raw.get("ad_started"),
            search_keyword=keyword,
        ))

    return results


def _extract_page_id(url: str) -> str | None:
    match = re.search(r"facebook\.com/([^/?#]+)", url)
    if match:
        return match.group(1)
    return None


def _extract_website_from_snippet(snippet: str) -> str | None:
    match = re.search(r'href="(https?://(?!(?:www\.)?facebook\.com)[^"]+)"', snippet)
    if match:
        return match.group(1)
    return None

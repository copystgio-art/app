"""
Scrapes website content for AI analysis.
"""
import httpx
from bs4 import BeautifulSoup


async def scrape_website(url: str, timeout: int = 15) -> dict:
    """Returns a dict with title, description, headings, and body text."""
    if not url:
        return {}

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; bot/1.0)"},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        return {"error": str(e)}

    soup = BeautifulSoup(html, "lxml")

    # Remove scripts and styles
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else ""
    description = ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag:
        description = desc_tag.get("content", "")

    h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]

    body_text = soup.get_text(separator=" ", strip=True)
    body_text = " ".join(body_text.split())[:3000]

    return {
        "url": url,
        "title": title,
        "description": description,
        "h1": h1s,
        "h2": h2s[:10],
        "body_excerpt": body_text,
    }

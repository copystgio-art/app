"""
Uses Claude to analyze an ad + website and select the best preset message.
"""
import json
import anthropic
from app.core.config import settings
from app.core.messages import PRESET_MESSAGES, PresetMessage, get_message_by_id
from app.scrapers.fb_ad_library import AdData
from app.scrapers.website_scraper import scrape_website


client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

MESSAGES_SUMMARY = "\n".join(
    f"  ID {m.id} - {m.name}: tags={m.tags}, min_score={m.min_score}"
    for m in PRESET_MESSAGES
)

SYSTEM_PROMPT = f"""Sei un esperto di marketing digitale e lead qualification.
Analizzerai inserzioni Facebook e siti web di aziende per valutare quanto sono adatte a ricevere
una proposta di servizi di marketing/advertising.

Hai a disposizione 20 messaggi preimpostati con questi profili:
{MESSAGES_SUMMARY}

Devi rispondere SOLO con un JSON valido nel formato:
{{
  "score": <intero 0-100, quanto è adatto questo lead>,
  "category": "<categoria principale del business>",
  "summary": "<analisi sintetica in 2-3 frasi>",
  "selected_message_id": <id del messaggio più adatto, o null se score < 40>,
  "reasoning": "<perché hai scelto quel messaggio>"
}}
"""


async def analyze_lead(ad: AdData) -> dict:
    """
    Analyzes an ad lead using Claude.
    Returns analysis dict with score, category, selected_message_id, etc.
    """
    # Scrape website if available
    website_data = {}
    if ad.website_url:
        website_data = await scrape_website(ad.website_url)

    user_content = _build_analysis_prompt(ad, website_data)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    text = response.content[0].text.strip()

    # Parse JSON
    try:
        # Handle possible markdown code fences
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)
    except Exception:
        data = {
            "score": 0,
            "category": "unknown",
            "summary": "Errore nel parsing della risposta AI.",
            "selected_message_id": None,
            "reasoning": "",
        }

    return data


def _build_analysis_prompt(ad: AdData, website: dict) -> str:
    parts = [
        f"## Inserzione Facebook",
        f"Pagina: {ad.page_name}",
        f"URL pagina: {ad.page_url}",
    ]
    if ad.ad_text:
        parts.append(f"Testo inserzione:\n{ad.ad_text}")
    if ad.ad_started:
        parts.append(f"Attiva dal: {ad.ad_started}")

    if website and not website.get("error"):
        parts.append("\n## Sito Web")
        if website.get("title"):
            parts.append(f"Titolo: {website['title']}")
        if website.get("description"):
            parts.append(f"Descrizione: {website['description']}")
        if website.get("h1"):
            parts.append(f"H1: {', '.join(website['h1'][:3])}")
        if website.get("h2"):
            parts.append(f"H2: {', '.join(website['h2'][:5])}")
        if website.get("body_excerpt"):
            parts.append(f"Contenuto:\n{website['body_excerpt'][:1500]}")

    return "\n".join(parts)


def format_message(message: PresetMessage, page_name: str) -> str:
    return message.text.format(page_name=page_name)

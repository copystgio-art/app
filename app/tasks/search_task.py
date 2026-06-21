"""
Celery task: scrape Ad Library + analyze leads.
"""
import asyncio
from datetime import datetime, timezone
from celery import shared_task
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.models import AdLead, SearchJob
from app.scrapers.fb_ad_library import scrape_ad_library
from app.analyzers.lead_analyzer import analyze_lead


@celery_app.task(bind=True, name="search_and_analyze")
def search_and_analyze(self, job_id: int):
    """Main task: scrape FB Ad Library and analyze each lead with Claude."""
    return asyncio.get_event_loop().run_until_complete(_run(self, job_id))


async def _run(task, job_id: int):
    async with AsyncSessionLocal() as db:
        job = await db.get(SearchJob, job_id)
        if not job:
            return {"error": "Job not found"}

        job.status = "running"
        await db.commit()

    try:
        ads = await scrape_ad_library(
            keyword=job.keyword,
            country=job.country,
            ad_type=job.ad_type,
            max_results=job.max_results,
        )

        analyzed = 0
        qualified = 0

        for i, ad in enumerate(ads):
            task.update_state(
                state="PROGRESS",
                meta={"current": i, "total": len(ads), "found": analyzed},
            )

            # Check duplicate
            async with AsyncSessionLocal() as db:
                existing = await db.execute(
                    select(AdLead).where(AdLead.ad_id == ad.ad_id)
                )
                if existing.scalar_one_or_none():
                    continue

            analysis = await analyze_lead(ad)
            score = analysis.get("score", 0)
            analyzed += 1

            if score >= job.min_score:
                qualified += 1

            async with AsyncSessionLocal() as db:
                lead = AdLead(
                    page_id=ad.page_id,
                    page_name=ad.page_name,
                    page_url=ad.page_url,
                    website_url=ad.website_url,
                    ad_id=ad.ad_id,
                    ad_text=ad.ad_text,
                    ad_image_url=ad.ad_image_url,
                    ad_started=ad.ad_started,
                    search_keyword=ad.search_keyword,
                    category=analysis.get("category"),
                    analysis_score=score,
                    analysis_summary=analysis.get("summary"),
                    selected_message_id=analysis.get("selected_message_id"),
                    analysis_data=analysis,
                )
                db.add(lead)
                await db.commit()

                # Auto-send if enabled and score is good
                if job.auto_send and score >= job.min_score and analysis.get("selected_message_id"):
                    from app.tasks.message_task import send_message_to_lead
                    send_message_to_lead.delay(lead.id)

        async with AsyncSessionLocal() as db:
            job = await db.get(SearchJob, job_id)
            job.status = "completed"
            job.ads_found = analyzed
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()

        return {"analyzed": analyzed, "qualified": qualified}

    except Exception as e:
        async with AsyncSessionLocal() as db:
            job = await db.get(SearchJob, job_id)
            if job:
                job.status = "failed"
                job.error = str(e)
                await db.commit()
        raise

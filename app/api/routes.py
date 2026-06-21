from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.models import AdLead, SearchJob
from app.core.messages import get_all_messages, get_message_by_id
from app.tasks.search_task import search_and_analyze
from app.tasks.message_task import send_message_to_lead

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    keyword: str
    country: str = "IT"
    ad_type: str = "ALL"
    max_results: int = 50
    min_score: int = 60
    auto_send: bool = False


class SendMessageRequest(BaseModel):
    lead_id: int
    message_id: Optional[int] = None


class UpdateMessageRequest(BaseModel):
    message_id: int


# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post("/auth/fb-login")
async def fb_login():
    """Opens browser for Facebook login and saves session."""
    from app.messaging.fb_messenger import login_and_save_session
    import asyncio
    try:
        success = await login_and_save_session()
        return {"success": success, "message": "Sessione Facebook salvata con successo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/fb-status")
async def fb_session_status():
    from app.messaging.fb_messenger import _session_exists
    return {"session_active": _session_exists()}


# ── Search Jobs ───────────────────────────────────────────────────────────────

@router.post("/search")
async def create_search(req: SearchRequest, db: AsyncSession = Depends(get_db)):
    """Start a new Ad Library search + analysis job."""
    job = SearchJob(
        keyword=req.keyword,
        country=req.country,
        ad_type=req.ad_type,
        max_results=req.max_results,
        min_score=req.min_score,
        auto_send=req.auto_send,
        status="pending",
    )
    db.add(job)
    await db.flush()

    task = search_and_analyze.delay(job.id)
    job.celery_task_id = task.id
    await db.commit()

    return {"job_id": job.id, "task_id": task.id, "status": "pending"}


@router.get("/search/{job_id}")
async def get_search_job(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await db.get(SearchJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "keyword": job.keyword,
        "status": job.status,
        "ads_found": job.ads_found,
        "messages_sent": job.messages_sent,
        "error": job.error,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
    }


@router.get("/search")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SearchJob).order_by(desc(SearchJob.created_at)).limit(50))
    jobs = result.scalars().all()
    return [
        {
            "id": j.id,
            "keyword": j.keyword,
            "status": j.status,
            "ads_found": j.ads_found,
            "messages_sent": j.messages_sent,
            "created_at": j.created_at,
        }
        for j in jobs
    ]


# ── Leads ─────────────────────────────────────────────────────────────────────

@router.get("/leads")
async def list_leads(
    min_score: int = 0,
    message_sent: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    q = select(AdLead).where(AdLead.analysis_score >= min_score)
    if message_sent is not None:
        q = q.where(AdLead.message_sent == message_sent)
    q = q.order_by(desc(AdLead.analysis_score)).limit(limit).offset(offset)

    result = await db.execute(q)
    leads = result.scalars().all()
    return [_lead_dict(l) for l in leads]


@router.get("/leads/{lead_id}")
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    lead = await db.get(AdLead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return _lead_dict(lead)


@router.post("/leads/{lead_id}/send")
async def send_message(lead_id: int, req: SendMessageRequest, db: AsyncSession = Depends(get_db)):
    """Send a message to a specific lead (queues Celery task)."""
    lead = await db.get(AdLead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.message_sent:
        raise HTTPException(status_code=400, detail="Message already sent to this lead")

    task = send_message_to_lead.delay(lead_id, req.message_id)
    return {"task_id": task.id, "lead_id": lead_id}


@router.patch("/leads/{lead_id}/message")
async def update_lead_message(
    lead_id: int, req: UpdateMessageRequest, db: AsyncSession = Depends(get_db)
):
    """Change which preset message is assigned to a lead."""
    lead = await db.get(AdLead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    msg = get_message_by_id(req.message_id)
    if not msg:
        raise HTTPException(status_code=400, detail=f"Message ID {req.message_id} not found")
    lead.selected_message_id = req.message_id
    await db.commit()
    return {"success": True}


# ── Messages ──────────────────────────────────────────────────────────────────

@router.get("/messages")
async def list_messages():
    return [
        {"id": m.id, "name": m.name, "tags": m.tags, "min_score": m.min_score, "text": m.text}
        for m in get_all_messages()
    ]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _lead_dict(l: AdLead) -> dict:
    return {
        "id": l.id,
        "page_name": l.page_name,
        "page_url": l.page_url,
        "website_url": l.website_url,
        "ad_text": l.ad_text,
        "search_keyword": l.search_keyword,
        "category": l.category,
        "analysis_score": l.analysis_score,
        "analysis_summary": l.analysis_summary,
        "selected_message_id": l.selected_message_id,
        "message_sent": l.message_sent,
        "message_sent_at": l.message_sent_at,
        "message_error": l.message_error,
        "created_at": l.created_at,
    }

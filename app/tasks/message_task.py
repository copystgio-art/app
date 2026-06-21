"""
Celery task: send Facebook message to a lead.
"""
import asyncio
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.models import AdLead
from app.core.messages import get_message_by_id
from app.analyzers.lead_analyzer import format_message
from app.messaging.fb_messenger import send_facebook_message


@celery_app.task(bind=True, name="send_message_to_lead")
def send_message_to_lead(self, lead_id: int, message_id: int | None = None):
    return asyncio.get_event_loop().run_until_complete(_send(lead_id, message_id))


async def _send(lead_id: int, override_message_id: int | None = None):
    async with AsyncSessionLocal() as db:
        lead = await db.get(AdLead, lead_id)
        if not lead:
            return {"error": "Lead not found"}

        if lead.message_sent:
            return {"error": "Message already sent"}

        msg_id = override_message_id or lead.selected_message_id
        if not msg_id:
            return {"error": "No message selected for this lead"}

        message_template = get_message_by_id(msg_id)
        if not message_template:
            return {"error": f"Message ID {msg_id} not found"}

        text = format_message(message_template, lead.page_name)

        try:
            success = await send_facebook_message(lead.page_url, text)
            lead.message_sent = success
            lead.message_sent_at = datetime.now(timezone.utc) if success else None
            if not success:
                lead.message_error = "Impossibile trovare il pulsante Invia Messaggio"
        except Exception as e:
            lead.message_error = str(e)
            success = False

        await db.commit()
        return {"success": success, "lead_id": lead_id}

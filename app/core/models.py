from sqlalchemy import String, Text, DateTime, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.core.database import Base


class AdLead(Base):
    __tablename__ = "ad_leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    page_id: Mapped[str] = mapped_column(String(100), index=True)
    page_name: Mapped[str] = mapped_column(String(255))
    page_url: Mapped[str] = mapped_column(String(500))
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    ad_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    ad_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ad_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ad_started: Mapped[str | None] = mapped_column(String(50), nullable=True)

    search_keyword: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Analysis results
    analysis_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    analysis_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    analysis_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Outreach status
    message_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    message_sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    message_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class SearchJob(Base):
    __tablename__ = "search_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255))
    country: Mapped[str] = mapped_column(String(10), default="IT")
    ad_type: Mapped[str] = mapped_column(String(20), default="ALL")
    max_results: Mapped[int] = mapped_column(Integer, default=50)
    min_score: Mapped[int] = mapped_column(Integer, default=60)
    auto_send: Mapped[bool] = mapped_column(Boolean, default=False)

    status: Mapped[str] = mapped_column(String(30), default="pending")
    celery_task_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ads_found: Mapped[int] = mapped_column(Integer, default=0)
    messages_sent: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

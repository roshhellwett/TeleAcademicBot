from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database.db import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    source = Column(String)
    source_url = Column(String)
    pdf_url = Column(String)

    content_hash = Column(String, unique=True)

    published_date = Column(DateTime)
    scraped_at = Column(DateTime)


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    active = Column(Boolean, default=True)
#@roshhellwett makaut tele bot
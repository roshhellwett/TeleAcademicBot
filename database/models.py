from sqlalchemy import Column, Integer, String, DateTime, Text
from database.db import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    source = Column(String(100), nullable=True)
    source_url = Column(Text, nullable=False)
    pdf_url = Column(Text, nullable=True)
    content_hash = Column(String(64), unique=True, index=True, nullable=False)
    published_date = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, nullable=True)

class SystemFlag(Base):
    __tablename__ = "system_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(String(255), nullable=True)

#@academictelebotbyroshhellwett
from sqlalchemy import Column, Integer, DateTime
from database.db import Base  # Importing SHARED Base

class UserStrike(Base):
    """
    Security Table: Tracks user violations.
    Persists across re-deployments thanks to PostgreSQL.
    """
    __tablename__ = "user_strikes"
    
    user_id = Column(Integer, primary_key=True, index=True)
    strike_count = Column(Integer, default=0)
    last_violation = Column(DateTime, nullable=True)
    #@academictelebotbyroshhellwett
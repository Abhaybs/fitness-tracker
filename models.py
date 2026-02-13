from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class PushupRecord(Base):
    __tablename__ = "pushup_sessions"

    id = Column(Integer, primary_key=True, index=True)
    reps = Column(Integer, nullable=False)
    view_type = Column(String, index=True)
    date_logged = Column(DateTime, default=datetime.utcnow)
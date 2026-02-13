from fastapi import FastAPI, Depends
from pydantic import BaseModel
from datetime import datetime

from sqlalchemy.orm import Session

from database import init_db, get_db
from models import PushupRecord

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()

# 1. Define the expected data structure
class PushupSession(BaseModel):
    reps: int
    view_type: str
    # Automatically grab the current time if the client doesn't provide it
    date: str = datetime.now().isoformat() 

# 2. Create the POST endpoint
@app.post("/log_pushups/")
async def log_pushups(session: PushupSession, db: Session = Depends(get_db)):
    try:
        date_logged = datetime.fromisoformat(session.date)
    except ValueError:
        date_logged = datetime.utcnow()

    record = PushupRecord(
        reps=session.reps,
        view_type=session.view_type,
        date_logged=date_logged,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "status": "success",
        "message": "Session logged successfully",
        "data": {
            "id": record.id,
            "reps": record.reps,
            "view_type": record.view_type,
            "date_logged": record.date_logged.isoformat(),
        },
    }
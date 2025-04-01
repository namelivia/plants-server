from app.tasks.tasks import Tasks
from app.database import engine, Base
from app.dependencies import get_db


def main():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    Tasks.send_watering_reminders(db)

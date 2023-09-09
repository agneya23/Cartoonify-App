from app import app, db
from app.models import User
from datetime import date
import schedule

def renew():
    if date.today().day != 1:
        return
    users = User.query.all()
    for u in users:
        u.remaining_credits = 5
    db.session.commit()

schedule.every().day.at("00:00").do(renew)
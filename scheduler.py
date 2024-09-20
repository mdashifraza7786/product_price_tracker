import schedule
import time
from tracker import check_prices
from db_setup import get_db

def job():
    db = get_db()
    print("Running Check Price")
    check_prices(db)

schedule.every().minute.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

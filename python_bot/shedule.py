import time
import schedule
from db import BotDatabase



db = BotDatabase('database.db')
def uvu_count_update():
    db.update_all_user_uvu_count(0)



schedule.every().day.at("13:40").do(uvu_count_update)

while True:
    schedule.run_pending()
    time.sleep(1)
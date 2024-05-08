import time
import schedule
from db import BotDatabase



db = BotDatabase('database.db')
def uvu_count_update():
    try:
        db.update_all_user_uvu_count()
        print('uvu_count updated for all')
    except Exception as e:
        print(e)



schedule.every().day.at("10:45").do(uvu_count_update)

while True:
    schedule.run_pending()
    time.sleep(1)
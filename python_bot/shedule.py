import time
import schedule
from db import BotDatabase



db = BotDatabase('database.db')



schedule.every().day.at("21:00").do(uvu_count_update)

while True:
    schedule.run_pending()
    time.sleep(1)
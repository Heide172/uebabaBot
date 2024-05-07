import asyncio
import logging
import config
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.enums import ParseMode

#from db import BotDatabase

# Включаем логирование, чтобы не пропустить важные сообщения
#logging.basicConfig(filename='logs.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Объект бота
bot = Bot(token=config.BOT_TOKEN)
# Диспетчер
dp = Dispatcher()
#База данных бота
#db = BotDatabase('database.db')

# Хэндлер на команду /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    logging.info('/start called')
    print(message.chat.id)
    await message.answer("fsdff")
    
@dp.message(Command("in"))
async def in_command(message: types.Message):
    logging.info('/in called')
    chat_id = message.from_id
    user = message.from_user
    logging.info('/in called, chat_id=%s user_id=%s', chat_id, user.id)
    user_name = user.username or user.first_name or 'anonymous'
    #db.add_user(user.id, user_name)
    #db.add_user_to_chat(chat_id, user.id)
    message = f'Thanks for opting in {user_name}'
    await message.reply(message)
    
@dp.message(Command("out"))
async def out_command(message: types.Message):
    logging.info('/out called')
    await message.answer("out_command")
    
@dp.message(Command("all"))
async def all_command(message: types.Message):
    chat_id = message.chat.id
    user_list = [['187973974','heide172'],['383745190','Thesauros']]
    logging.info('/all called, chat_id=%s user_count=%s', chat_id, len(user_list))
    if not user_list:
        message = 'There are no users. To opt in type /in command'
        await message.reply(text=message)
    else:
        mentions = [mention_markdown(user_id, user_name)
                    for user_id, user_name in user_list]
        
        await message.answer(text=str(mentions), parse_mode=ParseMode.MARKDOWN_V2)
        
def mention_markdown(user_id, user_name):
    return "["+user_name+"](tg://user?id="+str(user_id)+")"
@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    await message.answer("stats_command")
    
@dp.message(Command("dice"))
async def cmd_dice(message: types.Message, bot: Bot):
    await bot.send_dice(-100123456789, emoji=DiceEmoji.DICE)

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
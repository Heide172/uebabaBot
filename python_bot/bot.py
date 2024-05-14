import asyncio
import logging
from config_reader import config
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram import Router
from aiogram.filters import Filter
from aiogram import F
from aiogram.types import Message
from aiogram.enums.dice_emoji import DiceEmoji
from db import BotDatabase
import random
from user_agent import get_joke
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(filename='logs.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Объект бота
bot = Bot(token=config.BOT_TOKEN.get_secret_value())
# Диспетчер
dp = Dispatcher()
#База данных бота
db = BotDatabase('database.db')


def exception_handler(e):
        ex = e + e.__traceback__ + __file__
        print(e,e.__traceback__, __file__)
        return e
    
@dp.message(Command("all"))
async def all_command(message: types.Message):
    print('all executed')
    try:
        chat_id = message.chat.id
        user_list = db.get_users_from_chat(chat_id)
        logging.info('/all called, chat_id=%s user_count=%s', chat_id, len(user_list))
        if not user_list:
            message = 'There are no users. To opt in type /in command'
            await message.reply(text=message)
        else:
            mentions = [mention_markdown(user_id, user_name)
                        for user_id, user_name in user_list]
            
            await message.answer(text=str(mentions), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        await message.answer(exception_handler(e))

@dp.message(Command("hui"))
async def xui_command(message: types.Message):
    user = message.from_user
    user_name = user.username or user.first_name or 'anonymous'
    size = db.get_user_uvu_count(user.id) + 1 / 1000
    db.update_user_uvu_count(size*1000, user.id)
    await message.answer('Член %s длиной %s см', user_name, size )

# Хэндлер на команду /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer('Start')

# @dp.message(Command("in"))
# async def in_command(message: types.Message):
#     try:
#         chat_id = message.chat.id
#         user = message.from_user
#         logging.info('/in called, chat_id=%s user_id=%s', chat_id, user.id)
#         user_name = user.username or user.first_name or 'anonymous'
#         db.add_user(user.id, user_name, 0)
#         db.add_user_to_chat(chat_id, user.id)
#         await message.reply('Thanks for opting in')
#     except Exception as e:
#         await message.answer(exception_handler(e))

    
# @dp.message(Command("out"))
# async def out_command(message: types.Message):
#     chat_id = message.chat.id
#     user = message.from_user
#     db.delete_user_from_chat(chat_id, user.id)
#     await message.reply('No')
    

def mention_markdown(user_id, user_name):
    return "["+user_name+"](tg://user?id="+str(user_id)+")"
    
@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    user = message.from_user
    reply = f'users: {db.count_users()[0]}\n' \
              f'chats: {db.count_chats()[0]}\n' \
              f'groups: {db.count_groups()[0]}\n' \
              f'увы: {20 - db.get_user_uvu_count(user.id)}'
    await message.answer(text=reply)
    
@dp.message(Command("dice"))
async def cmd_dice(message: types.Message, bot: Bot):
    await bot.send_dice(message.chat.id, emoji=DiceEmoji.DICE)

@dp.message(Command("joke"))
async def joke_command(message: types.Message):
    reply = get_joke()
    await message.answer(text=reply)
    
@dp.message(F.text.lower().contains('увы'))
async def yvy_command(message: types.Message):
#    user = message.from_user
    try:
#        count = db.get_user_uvu_count(user.id)
        if (random.randrange(0,50) != 0):
            return
        else:
#            db.update_user_uvu_count(count + 1, user.id)
            if (random.randrange(0,50) == 0):
                await message.answer_sticker(r'CAACAgIAAxkBAAEFQMRmOjyP3TzJgZwh9fHNMm8gGqaFtwACjS0AAiq1EUjDQfFev1DanzUE') 
            else: 
                await message.answer(text='увы')
    except Exception as e:
        print(e) 
    
    

    
# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
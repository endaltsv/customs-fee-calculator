import asyncio

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bot.bot import dp, bot, send_course


async def main():
    scheduler = AsyncIOScheduler()

    timezone = pytz.timezone('Europe/Moscow')
    scheduler.add_job(send_course, CronTrigger(hour=12, minute=0, timezone=timezone))
    scheduler.add_job(send_course, CronTrigger(hour=16, minute=0, timezone=timezone))

    scheduler.start()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
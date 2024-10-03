import asyncio
import logging
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bot.bot import dp, bot
from bot.handlers import *
from services.course_service import schedule_send_course
from utils.get_course import test_proxy_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    await test_proxy_connection()
    scheduler = AsyncIOScheduler()

    await schedule_send_course()

    timezone = pytz.timezone('Europe/Moscow')
    scheduler.add_job(schedule_send_course, CronTrigger(hour=6, minute=0, timezone=timezone))
    scheduler.add_job(schedule_send_course, CronTrigger(hour=12, minute=0, timezone=timezone))

    scheduler.start()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

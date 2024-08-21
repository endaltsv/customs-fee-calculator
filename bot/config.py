from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')
PUBLIC_CHAT_ID = os.getenv('PUBLIC_CHAT_ID')
THREAD_ID = os.getenv('THREAD_ID')
URL_CALCULATOR = os.getenv('URL_CALCULATOR')
URL_COURSES = os.getenv('URL_COURSES')

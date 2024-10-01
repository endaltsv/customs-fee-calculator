from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')
PUBLIC_CHAT_ID = os.getenv('PUBLIC_CHAT_ID')
THREAD_ID = os.getenv('THREAD_ID')
URL_CALCULATOR = os.getenv('URL_CALCULATOR')
URL_COURSES = os.getenv('URL_COURSES')
PROXY_URL = os.getenv('PROXY_URL')
PROXY_USERNAME = os.getenv('PROXY_USERNAME')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')

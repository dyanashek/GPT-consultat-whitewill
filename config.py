import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

MANAGER_ID = os.getenv('MANAGER_ID')

AI_TOKEN = os.getenv('AI_TOKEN')
AI_ENDPOINT = os.getenv('AI_ENDPOINT')

REPORT_FLAG = False
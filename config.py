import os
from datetime import datetime

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
    
    # Telegram configuration (you'll set these later)
    TELEGRAM_BOT_TOKEN = '8083496802:AAE3h44C7ydCWOjAQyE5kCD3wbBbymnugk8'  # Add your bot token here
    ADMIN_CHAT_IDS = [1230226330]  # Add admin chat IDs here
    
    # Admin credentials
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = '1234'
    
    # Application settings
    RECORDS_PER_PAGE = 20
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
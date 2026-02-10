import requests
import json
from config import Config
import datetime

class TelegramNotifier:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.admin_chat_ids = Config.ADMIN_CHAT_IDS
    
    def send_notification(self, message, record_type, record_id):
        """Send notification to all admin chat IDs"""
        if not self.bot_token or not self.admin_chat_ids:
            print("Telegram bot token or chat IDs not configured")
            return False
        
        full_message = f"🚨 *New {record_type} Submission*\n\n"
        full_message += f"📋 *Record ID:* {record_id}\n"
        full_message += message
        full_message += f"\n\n📅 _Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        
        success = True
        for chat_id in self.admin_chat_ids:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': full_message,
                'parse_mode': 'Markdown'
            }
            
            try:
                response = requests.post(url, data=payload)
                if response.status_code != 200:
                    print(f"Failed to send notification to chat_id {chat_id}")
                    success = False
            except Exception as e:
                print(f"Error sending Telegram notification: {e}")
                success = False
        
        return success
    
    def send_status_update(self, record_type, record_id, old_status, new_status, amount_paid=None):
        """Send status update notification"""
        if not self.bot_token or not self.admin_chat_ids:
            return False
        
        message = f"🔄 *Status Update - {record_type}*\n\n"
        message += f"📋 *Record ID:* {record_id}\n"
        message += f"📊 *Old Status:* {old_status}\n"
        message += f"✅ *New Status:* {new_status}\n"
        if amount_paid:
            message += f"💰 *Amount Paid:* ₹{amount_paid}\n"
        
        success = True
        for chat_id in self.admin_chat_ids:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            try:
                requests.post(url, data=payload)
            except:
                success = False
        
        return success

# Create global instance
telegram_notifier = TelegramNotifier()
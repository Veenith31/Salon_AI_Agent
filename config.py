import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Twilio SMS Configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # WhatsApp Business API
    WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    
    # Facebook/Instagram API
    FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
    FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
    INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
    
    # Twitter API
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # Database Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'salon_booking')
    
    # Web Dashboard
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Salon Information
    SALON_NAME = os.getenv('SALON_NAME', 'Beauty Salon')
    SALON_PHONE = os.getenv('SALON_PHONE')
    SALON_ADDRESS = os.getenv('SALON_ADDRESS')
    SALON_WEBSITE = os.getenv('SALON_WEBSITE')
    
    # Notification Settings
    SMS_REMINDER_HOURS = int(os.getenv('SMS_REMINDER_HOURS', '24'))
    WHATSAPP_REMINDER_HOURS = int(os.getenv('WHATSAPP_REMINDER_HOURS', '24'))
    EMAIL_REMINDER_HOURS = int(os.getenv('EMAIL_REMINDER_HOURS', '24'))
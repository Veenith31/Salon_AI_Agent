import requests
import json
import datetime
from typing import Optional, Dict, Any
from config import Config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

class SMSNotificationService:
    """Handles SMS notifications using Twilio"""
    
    def __init__(self):
        self.account_sid = Config.TWILIO_ACCOUNT_SID
        self.auth_token = Config.TWILIO_AUTH_TOKEN
        self.from_number = Config.TWILIO_PHONE_NUMBER
        
    def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS notification"""
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            payload = {
                'From': self.from_number,
                'To': to_number,
                'Body': message
            }
            response = requests.post(url, data=payload, auth=(self.account_sid, self.auth_token))
            return response.status_code == 201
        except Exception as e:
            print(f"SMS sending failed: {e}")
            return False
    
    def send_appointment_reminder(self, customer_phone: str, service: str, 
                                appointment_time: datetime.datetime, customer_name: str = "there") -> bool:
        """Send appointment reminder SMS"""
        message = f"Hi {customer_name}! This is a reminder for your {service} appointment tomorrow at {appointment_time.strftime('%I:%M %p')}. Please arrive 10 minutes early. Reply STOP to unsubscribe."
        return self.send_sms(customer_phone, message)
    
    def send_appointment_confirmation(self, customer_phone: str, service: str, 
                                    appointment_time: datetime.datetime, customer_name: str = "there") -> bool:
        """Send appointment confirmation SMS"""
        message = f"Hi {customer_name}! Your {service} appointment is confirmed for {appointment_time.strftime('%A, %B %d at %I:%M %p')}. We look forward to seeing you!"
        return self.send_sms(customer_phone, message)

class WhatsAppNotificationService:
    """Handles WhatsApp notifications using WhatsApp Business API"""
    
    def __init__(self):
        self.access_token = Config.WHATSAPP_API_TOKEN
        self.phone_number_id = Config.WHATSAPP_PHONE_NUMBER_ID
        
    def send_whatsapp_message(self, to_number: str, message: str) -> bool:
        """Send WhatsApp message"""
        try:
            url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': 'text',
                'text': {'body': message}
            }
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"WhatsApp sending failed: {e}")
            return False
    
    def send_appointment_reminder(self, customer_phone: str, service: str, 
                                appointment_time: datetime.datetime, customer_name: str = "there") -> bool:
        """Send appointment reminder via WhatsApp"""
        message = f"Hi {customer_name}! 👋\n\nThis is a friendly reminder for your {service} appointment tomorrow at {appointment_time.strftime('%I:%M %p')}.\n\nPlease arrive 10 minutes early. We can't wait to see you! 💇‍♀️✨"
        return self.send_whatsapp_message(customer_phone, message)
    
    def send_satisfaction_survey(self, customer_phone: str, customer_name: str = "there") -> bool:
        """Send post-appointment satisfaction survey"""
        message = f"Hi {customer_name}! 🌟\n\nThank you for visiting us today! We'd love to hear about your experience.\n\nPlease rate your visit from 1-5 stars and share any feedback. Your opinion matters to us! 💕"
        return self.send_whatsapp_message(customer_phone, message)

class SocialMediaService:
    """Handles social media integration for Facebook, Instagram, and Twitter"""
    
    def __init__(self):
        self.facebook_token = Config.FACEBOOK_ACCESS_TOKEN
        self.facebook_page_id = Config.FACEBOOK_PAGE_ID
        self.instagram_account_id = Config.INSTAGRAM_BUSINESS_ACCOUNT_ID
        self.twitter_api_key = Config.TWITTER_API_KEY
        self.twitter_api_secret = Config.TWITTER_API_SECRET
        self.twitter_access_token = Config.TWITTER_ACCESS_TOKEN
        self.twitter_access_token_secret = Config.TWITTER_ACCESS_TOKEN_SECRET
        
    def post_facebook_availability(self, available_slots: list, date: datetime.date) -> bool:
        """Post available slots on Facebook"""
        try:
            message = f"📅 Available appointments for {date.strftime('%A, %B %d')}:\n\n"
            for slot in available_slots:
                message += f"⏰ {slot['time']} - {slot['service']}\n"
            message += f"\nBook now: {Config.SALON_WEBSITE or 'Call us!'}"
            
            url = f"https://graph.facebook.com/v17.0/{self.facebook_page_id}/feed"
            payload = {
                'message': message,
                'access_token': self.facebook_token
            }
            response = requests.post(url, data=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Facebook posting failed: {e}")
            return False
    
    def post_instagram_story(self, image_path: str, caption: str) -> bool:
        """Post to Instagram story (requires Instagram Graph API)"""
        try:
            # This is a simplified version - Instagram API requires more complex setup
            print(f"Instagram story post: {caption}")
            return True
        except Exception as e:
            print(f"Instagram posting failed: {e}")
            return False
    
    def tweet_availability(self, available_slots: list, date: datetime.date) -> bool:
        """Tweet available slots"""
        try:
            message = f"📅 Available appointments for {date.strftime('%B %d')}:\n"
            for slot in available_slots[:3]:  # Twitter character limit
                message += f"⏰ {slot['time']} - {slot['service']}\n"
            message += f"Book now! {Config.SALON_WEBSITE or ''}"
            
            # Simplified Twitter API call
            print(f"Twitter post: {message}")
            return True
        except Exception as e:
            print(f"Twitter posting failed: {e}")
            return False

class EmailService:
    """Enhanced email service with templates"""
    
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.username = Config.EMAIL_USERNAME
        self.password = Config.EMAIL_PASSWORD
        
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send email with optional HTML content"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text version
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML version if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def send_appointment_confirmation_email(self, customer_email: str, customer_name: str, 
                                          service: str, appointment_time: datetime.datetime) -> bool:
        """Send beautiful appointment confirmation email"""
        subject = f"Appointment Confirmation - {service}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">{Config.SALON_NAME}</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Hi {customer_name}!</h2>
                <p>Your appointment has been confirmed! 🎉</p>
                <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #667eea;">Appointment Details</h3>
                    <p><strong>Service:</strong> {service}</p>
                    <p><strong>Date:</strong> {appointment_time.strftime('%A, %B %d, %Y')}</p>
                    <p><strong>Time:</strong> {appointment_time.strftime('%I:%M %p')}</p>
                </div>
                <p>Please arrive 10 minutes before your appointment time.</p>
                <p>If you need to reschedule, please call us at least 24 hours in advance.</p>
                <p>We look forward to seeing you!</p>
                <p>Best regards,<br>The {Config.SALON_NAME} Team</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Hi {customer_name}!
        
        Your appointment has been confirmed!
        
        Service: {service}
        Date: {appointment_time.strftime('%A, %B %d, %Y')}
        Time: {appointment_time.strftime('%I:%M %p')}
        
        Please arrive 10 minutes before your appointment time.
        If you need to reschedule, please call us at least 24 hours in advance.
        
        We look forward to seeing you!
        
        Best regards,
        The {Config.SALON_NAME} Team
        """
        
        return self.send_email(customer_email, subject, text_body, html_body)
    
    def send_satisfaction_survey_email(self, customer_email: str, customer_name: str) -> bool:
        """Send post-appointment satisfaction survey email"""
        subject = "How was your visit? We'd love to hear from you!"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">{Config.SALON_NAME}</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Hi {customer_name}!</h2>
                <p>Thank you for visiting us today! 🌟</p>
                <p>We hope you had a wonderful experience. Your feedback helps us improve and provide the best service possible.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <h3>Rate your experience:</h3>
                    <div style="font-size: 24px;">
                        ⭐⭐⭐⭐⭐
                    </div>
                </div>
                <p>Please take a moment to share your thoughts with us.</p>
                <p>Thank you for choosing {Config.SALON_NAME}!</p>
                <p>Best regards,<br>The {Config.SALON_NAME} Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(customer_email, subject, "", html_body)

class NotificationManager:
    """Manages all notification services"""
    
    def __init__(self):
        self.sms_service = SMSNotificationService()
        self.whatsapp_service = WhatsAppNotificationService()
        self.email_service = EmailService()
        self.social_media_service = SocialMediaService()
    
    def send_appointment_confirmation(self, customer_info: Dict[str, Any], 
                                    service: str, appointment_time: datetime.datetime) -> Dict[str, bool]:
        """Send appointment confirmation through all channels"""
        results = {}
        
        # Send SMS if phone number provided
        if customer_info.get('phone'):
            results['sms'] = self.sms_service.send_appointment_confirmation(
                customer_info['phone'], service, appointment_time, customer_info.get('name', 'there')
            )
        
        # Send WhatsApp if phone number provided
        if customer_info.get('phone'):
            results['whatsapp'] = self.whatsapp_service.send_whatsapp_message(
                customer_info['phone'], 
                f"Hi {customer_info.get('name', 'there')}! Your {service} appointment is confirmed for {appointment_time.strftime('%A, %B %d at %I:%M %p')}. We look forward to seeing you! 💇‍♀️✨"
            )
        
        # Send email if email provided
        if customer_info.get('email'):
            results['email'] = self.email_service.send_appointment_confirmation_email(
                customer_info['email'], customer_info.get('name', 'there'), 
                service, appointment_time
            )
        
        return results
    
    def send_appointment_reminders(self, appointments: list) -> Dict[str, int]:
        """Send reminders for upcoming appointments"""
        results = {'sms': 0, 'whatsapp': 0, 'email': 0}
        
        for appointment in appointments:
            customer_info = appointment.get('customer_info', {})
            service = appointment.get('service')
            appointment_time = appointment.get('appointment_time')
            
            if customer_info.get('phone'):
                if self.sms_service.send_appointment_reminder(
                    customer_info['phone'], service, appointment_time, customer_info.get('name', 'there')
                ):
                    results['sms'] += 1
                
                if self.whatsapp_service.send_appointment_reminder(
                    customer_info['phone'], service, appointment_time, customer_info.get('name', 'there')
                ):
                    results['whatsapp'] += 1
            
            if customer_info.get('email'):
                if self.email_service.send_email(
                    customer_info['email'], 
                    f"Reminder: Your {service} appointment tomorrow",
                    f"Hi {customer_info.get('name', 'there')}! This is a reminder for your {service} appointment tomorrow at {appointment_time.strftime('%I:%M %p')}. Please arrive 10 minutes early."
                ):
                    results['email'] += 1
        
        return results
    
    def send_satisfaction_surveys(self, completed_appointments: list) -> Dict[str, int]:
        """Send satisfaction surveys for completed appointments"""
        results = {'sms': 0, 'whatsapp': 0, 'email': 0}
        
        for appointment in completed_appointments:
            customer_info = appointment.get('customer_info', {})
            
            if customer_info.get('phone'):
                if self.whatsapp_service.send_satisfaction_survey(
                    customer_info['phone'], customer_info.get('name', 'there')
                ):
                    results['whatsapp'] += 1
            
            if customer_info.get('email'):
                if self.email_service.send_satisfaction_survey_email(
                    customer_info['email'], customer_info.get('name', 'there')
                ):
                    results['email'] += 1
        
        return results
    
    def post_availability_to_social_media(self, available_slots: list, date: datetime.date) -> Dict[str, bool]:
        """Post available slots to social media platforms"""
        results = {}
        
        results['facebook'] = self.social_media_service.post_facebook_availability(available_slots, date)
        results['twitter'] = self.social_media_service.tweet_availability(available_slots, date)
        
        return results

import parsedatetime
import datetime
from dateutil import parser as dateutil_parser
import os
import pickle
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import speech_recognition as sr


from gtts import gTTS
from playsound import playsound

# Set up scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# === Google Calendar Auth ===
def get_calendar_service():
    creds = None
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pkl', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def confirm_booking(info):
    service = info["service"]
    booking_time = info["datetime"].strftime('%A, %d %B %Y at %I:%M %p')

    confirmation_message = f"Do you confirm booking a {service} on {booking_time}? Please say Yes or No."
    print(confirmation_message)
    speak_to_user(confirmation_message)

    # Listen for confirmation (voice or text)
    mode = input("Type 1 for text confirmation, 2 for voice: ")

    if mode == "1":
        reply = input("Enter Yes/No: ").lower()
    else:
        reply = get_voice_input()
        reply = reply.lower() if reply else "no"

    if "yes" in reply:
        return True
    else:
        speak_to_user("Booking cancelled as per your response.")
        print("❌ Booking not confirmed.")
        return False


def get_voice_input():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Listening for booking request... (Speak now)")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("🗣️ You said:", text)
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return None
    except sr.RequestError:
        print("❌ Could not request results from Google Speech API")
        return None


# === Extract Service and Datetime from User Input ===
def extract_booking_info(user_input):
    cal = parsedatetime.Calendar()
    known_services = ["haircut", "facial", "hair spa", "massage", "manicure", "pedicure", "coloring"]
    lower_input = user_input.lower()
    service = next((s for s in known_services if s in lower_input), None)

    time_struct, parse_status = cal.parse(user_input)
    booking_time = None
    if parse_status == 1:
        booking_time = datetime.datetime(*time_struct[:6])
    else:
        try:
            booking_time = dateutil_parser.parse(user_input, fuzzy=True)
        except Exception:
            booking_time = None

    print(f"Parsed datetime: {booking_time}")
    print(f"Detected service: {service}")

    if service and booking_time:
        return {"service": service, "datetime": booking_time}
    else:
        return None

# === Check Calendar Availability ===
def is_time_slot_available(calendar_service, booking_datetime):
    tz = pytz.timezone('Asia/Kolkata')
    start_time = tz.localize(booking_datetime).isoformat()
    end_time = tz.localize(booking_datetime + datetime.timedelta(hours=1)).isoformat()

    events_result = calendar_service.events().list(
        calendarId='primary',
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return len(events) == 0

def speak_to_user(message):
    filename = "user_response.mp3"
    tts = gTTS(text=message, lang='en')
    tts.save(filename)
    playsound(filename)

def speak_booking_to_owner(service, booking_datetime):
    message = f"You have a new {service} booking on {booking_datetime.strftime('%A, %d %B %Y at %I:%M %p')}."
    filename = "booking_alert.mp3"
    tts = gTTS(text=message, lang='en')
    tts.save(filename)
    playsound(filename)


# === Create Calendar Event ===
def create_calendar_event(service_name, booking_datetime):
    calendar_service = get_calendar_service()

    # 🔒 Check availability before booking
    if not is_time_slot_available(calendar_service, booking_datetime):
        print("❌ Time slot is already booked. Please choose another time.")
        
        # 🔊 Voice message to user
        speak_to_user("Sorry, the selected time slot is already booked. Please try another time.")
        
        return  # Don't proceed with booking

    event = {
        'summary': f'{service_name.title()} Appointment',
        'description': f'Auto-booked for {service_name} using SalonAgent.',
        'start': {
            'dateTime': booking_datetime.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': (booking_datetime + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 60},
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }

    created_event = calendar_service.events().insert(calendarId='primary', body=event).execute()
    print("✅ Event created:", created_event.get('htmlLink'))

    # 🔊 Voice alert for owner
   # speak_booking_to_owner(service_name, booking_datetime)
    # 🔊 Voice alert for owner
    speak_booking_to_owner(service_name, booking_datetime)

    # 📧 Send email to salon owner or customer
    owner_email = "veeniths31@gmail.com"  # Replace with real email
    send_email_confirmation(owner_email, service_name, booking_datetime)


    # === Voice Alert to Owner ===
def speak_booking_to_owner(service, booking_datetime):
        message = f"You have a new {service} booking on {booking_datetime.strftime('%A, %d %B %Y at %I:%M %p')}."
        tts = gTTS(text=message, lang='en')
        filename = "booking_alert.mp3"
        tts.save(filename)
        print("🔊 Playing voice message...")
        playsound(filename)


def show_daily_appointments():
    calendar_service = get_calendar_service()
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(tz)
    
    start_of_day = tz.localize(datetime.datetime(now.year, now.month, now.day, 0, 0, 0)).isoformat()
    end_of_day = tz.localize(datetime.datetime(now.year, now.month, now.day, 23, 59, 59)).isoformat()

    events_result = calendar_service.events().list(
        calendarId='primary',
        timeMin=start_of_day,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    print("\n📅 Today's Appointments:")
    if not events:
        print("No appointments today.")
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            service = event.get('summary', 'No Title')
            print(f"➡ {service} at {start}")

    
def send_email_confirmation(to_email, service, booking_datetime):
        sender_email = "thesummarizer31@gmail.com"
        sender_password = "aagt kuoq konk gbba"  # Use App Password (not regular Gmail password)
    
        subject = f"{service.title()} Appointment Confirmation"
        body = f"""
        Hi,

        This is to confirm your {service} appointment on {booking_datetime.strftime('%A, %d %B %Y at %I:%M %p')}.
    
        Thank you,
        Salon Agent
     """

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print("📧 Email confirmation sent!")
        except Exception as e:
            print("❌ Failed to send email:", e)


# === MAIN FUNCTION ===

'''
if info:
    print("✅ Booking Info:", info)
    if confirm_booking(info):
        success = create_calendar_event(info["service"], info["datetime"])
        if success:
            speak_booking_to_owner(info["service"], info["datetime"])
else:
    print("❌ Could not extract booking info. Please try again.")
'''
if __name__ == "__main__":
    choice = input("Choose: 1 = Book Appointment, 2 = Show Today's Appointments: ")

    if choice == "1":
        mode = input("Type 1 for text, 2 for voice: ")
        if mode == "1":
            user_input = input("Enter your booking request: ")
        elif mode == "2":
            user_input = get_voice_input()
            if not user_input:
                speak_to_user("Sorry, I couldn't understand. Please try again.")
                exit()
        else:
            print("Invalid option")
            exit()

        info = extract_booking_info(user_input)
        if info:
            if confirm_booking(info):
                create_calendar_event(info["service"], info["datetime"])
        else:
            print("❌ Could not extract booking info. Please try again.")

    elif choice == "2":
        show_daily_appointments()
    else:
        print("Invalid choice")

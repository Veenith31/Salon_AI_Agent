from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
from datetime import datetime, timedelta
import os
from typing import Optional, List, Dict, Any
import json

from database import DatabaseManager
from communication_services import NotificationManager
from config import Config

app = FastAPI(title="Salon Booking Dashboard", version="1.0.0")

# Security
security = HTTPBasic()

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
db = DatabaseManager()
notification_manager = NotificationManager()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Simple authentication - in production, use proper auth"""
    if credentials.username == "admin" and credentials.password == "salon123":
        return credentials.username
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, username: str = Depends(get_current_user)):
    """Main dashboard page"""
    # Get statistics
    stats = db.get_customer_statistics()
    
    # Get today's appointments
    today_appointments = db.get_appointments_by_date(datetime.now())
    
    # Get upcoming appointments
    upcoming_appointments = db.get_upcoming_appointments(24)
    
    # Get recent communications
    recent_communications = db.get_recent_communications(5)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "today_appointments": today_appointments,
        "upcoming_appointments": upcoming_appointments,
        "recent_communications": recent_communications,
        "salon_name": Config.SALON_NAME
    })

@app.get("/appointments", response_class=HTMLResponse)
async def appointments_page(request: Request, username: str = Depends(get_current_user)):
    """Appointments management page"""
    # Get all appointments for the next 7 days
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    appointments = []
    current_date = start_date
    while current_date <= end_date:
        day_appointments = db.get_appointments_by_date(current_date)
        if day_appointments:
            appointments.extend(day_appointments)
        current_date += timedelta(days=1)
    
    return templates.TemplateResponse("appointments.html", {
        "request": request,
        "appointments": appointments,
        "salon_name": Config.SALON_NAME
    })

@app.get("/customers", response_class=HTMLResponse)
async def customers_page(request: Request, username: str = Depends(get_current_user)):
    """Customers management page"""
    # Get all customers (limit to 50 for performance)
    customers = list(db.customers.find().sort('created_at', -1).limit(50))
    
    return templates.TemplateResponse("customers.html", {
        "request": request,
        "customers": customers,
        "salon_name": Config.SALON_NAME
    })

@app.get("/communications", response_class=HTMLResponse)
async def communications_page(request: Request, username: str = Depends(get_current_user)):
    """Communications management page"""
    recent_communications = db.get_recent_communications(20)
    satisfaction_surveys = db.get_satisfaction_surveys(10)
    
    return templates.TemplateResponse("communications.html", {
        "request": request,
        "communications": recent_communications,
        "surveys": satisfaction_surveys,
        "salon_name": Config.SALON_NAME
    })

@app.get("/booking", response_class=HTMLResponse)
async def booking_page(request: Request):
    """Public booking page"""
    # Get available slots for today and tomorrow
    today_slots = db.get_available_slots(datetime.now())
    tomorrow_slots = db.get_available_slots(datetime.now() + timedelta(days=1))
    
    return templates.TemplateResponse("booking.html", {
        "request": request,
        "today_slots": today_slots,
        "tomorrow_slots": tomorrow_slots,
        "salon_name": Config.SALON_NAME,
        "salon_phone": Config.SALON_PHONE,
        "salon_address": Config.SALON_ADDRESS
    })

@app.post("/book-appointment")
async def book_appointment(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    service: str = Form(...),
    appointment_date: str = Form(...),
    appointment_time: str = Form(...)
):
    """Handle appointment booking"""
    try:
        # Parse appointment datetime
        appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
        
        # Check if customer exists, if not create new customer
        customer = db.get_customer_by_phone(phone)
        if not customer:
            customer_data = {
                'name': name,
                'phone': phone,
                'email': email
            }
            customer_id = db.add_customer(customer_data)
            customer = db.get_customer(customer_id)
        
        # Create appointment
        appointment_data = {
            'customer_id': customer['_id'],
            'customer_info': {
                'name': customer['name'],
                'phone': customer['phone'],
                'email': customer['email']
            },
            'service': service,
            'appointment_time': appointment_datetime,
            'duration': 60  # Default duration
        }
        
        appointment_id = db.add_appointment(appointment_data)
        
        # Send confirmation notifications
        notification_results = notification_manager.send_appointment_confirmation(
            customer['communication_preferences'],
            service,
            appointment_datetime
        )
        
        # Log communication
        for channel, success in notification_results.items():
            db.add_communication_log({
                'appointment_id': appointment_id,
                'customer_id': str(customer['_id']),
                'channel': channel,
                'type': 'confirmation',
                'success': success,
                'message': f"Appointment confirmation for {service}"
            })
        
        return {"success": True, "appointment_id": appointment_id}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/send-reminders")
async def send_reminders(username: str = Depends(get_current_user)):
    """Send reminders for upcoming appointments"""
    try:
        upcoming_appointments = db.get_upcoming_appointments(24)
        
        # Filter appointments that haven't had reminders sent
        appointments_to_remind = []
        for appointment in upcoming_appointments:
            if not appointment.get('reminders_sent', {}).get('sms', False):
                appointments_to_remind.append(appointment)
        
        # Send reminders
        results = notification_manager.send_appointment_reminders(appointments_to_remind)
        
        # Mark reminders as sent
        for appointment in appointments_to_remind:
            for channel in ['sms', 'whatsapp', 'email']:
                if results.get(channel, 0) > 0:
                    db.mark_reminder_sent(str(appointment['_id']), channel)
        
        return {"success": True, "results": results}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/send-satisfaction-surveys")
async def send_satisfaction_surveys(username: str = Depends(get_current_user)):
    """Send satisfaction surveys for completed appointments"""
    try:
        completed_appointments = db.get_completed_appointments(24)
        
        # Filter appointments that haven't had surveys sent
        appointments_for_survey = []
        for appointment in completed_appointments:
            if not appointment.get('satisfaction_survey_sent', False):
                appointments_for_survey.append(appointment)
        
        # Send surveys
        results = notification_manager.send_satisfaction_surveys(appointments_for_survey)
        
        # Mark surveys as sent
        for appointment in appointments_for_survey:
            db.mark_satisfaction_survey_sent(str(appointment['_id']))
        
        return {"success": True, "results": results}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/post-social-media")
async def post_social_media(
    date: str = Form(...),
    username: str = Depends(get_current_user)
):
    """Post available slots to social media"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        available_slots = db.get_available_slots(target_date)
        
        # Format slots for social media
        formatted_slots = []
        for slot in available_slots[:5]:  # Limit to 5 slots
            formatted_slots.append({
                'time': slot['time'],
                'service': 'General Appointment'
            })
        
        # Post to social media
        results = notification_manager.post_availability_to_social_media(formatted_slots, target_date)
        
        return {"success": True, "results": results}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/appointments/{date}")
async def get_appointments_by_date(date: str, username: str = Depends(get_current_user)):
    """API endpoint to get appointments for a specific date"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        appointments = db.get_appointments_by_date(target_date)
        
        # Convert ObjectId to string for JSON serialization
        for appointment in appointments:
            appointment['_id'] = str(appointment['_id'])
            if 'customer_id' in appointment:
                appointment['customer_id'] = str(appointment['customer_id'])
        
        return {"appointments": appointments}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/available-slots/{date}")
async def get_available_slots(date: str):
    """API endpoint to get available slots for a specific date"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        slots = db.get_available_slots(target_date)
        
        # Convert datetime to string for JSON serialization
        for slot in slots:
            slot['datetime'] = slot['datetime'].isoformat()
        
        return {"slots": slots}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
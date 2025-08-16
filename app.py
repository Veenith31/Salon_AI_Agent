from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import datetime
from typing import Optional, List, Dict
import uvicorn
import os
from pydantic import BaseModel
from ai_recommendations import AIRecommendationEngine, Customer
import json

# Initialize FastAPI app
app = FastAPI(title="Salon Booking Agent", description="AI-Powered Salon Booking System")

# Create templates and static directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Initialize AI engine
ai_engine = AIRecommendationEngine()

# Pydantic models for API endpoints
class BookingRequest(BaseModel):
    customer_email: str
    service_name: str
    booking_datetime: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None

class CustomerProfile(BaseModel):
    name: str
    email: str
    phone: str
    preferences: Dict

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Main landing page with booking interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/recommendations/{email}")
async def get_recommendations(email: str):
    """Get AI-powered service recommendations for a customer"""
    try:
        recommendations = ai_engine.get_personalized_recommendations(email, limit=6)
        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/book")
async def create_booking(booking: BookingRequest, background_tasks: BackgroundTasks):
    """Create a new booking"""
    try:
        # Parse datetime
        booking_dt = datetime.datetime.fromisoformat(booking.booking_datetime.replace('Z', '+00:00'))
        
        # Create customer if new
        customer = ai_engine.get_customer_by_email(booking.customer_email)
        if not customer and booking.customer_name:
            new_customer = Customer(
                id=f"cust_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=booking.customer_name,
                email=booking.customer_email,
                phone=booking.customer_phone or "",
                preferences={},
                booking_history=[]
            )
            ai_engine.add_customer(new_customer)
        
        # Record the booking
        booking_id = ai_engine.record_booking(
            booking.customer_email, 
            booking.service_name, 
            booking_dt, 
            50.0  # Default price, should be retrieved from service
        )
        
        # Add background task for notifications
        background_tasks.add_task(send_booking_confirmation, booking.customer_email, booking.service_name, booking_dt)
        
        return {
            "success": True, 
            "booking_id": booking_id,
            "message": "Booking confirmed successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/customer/{email}")
async def get_customer_profile(email: str):
    """Get customer profile and booking history"""
    customer = ai_engine.get_customer_by_email(email)
    if not customer:
        return {"success": False, "error": "Customer not found"}
    
    return {
        "success": True,
        "customer": {
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "loyalty_points": customer.loyalty_points,
            "tier": customer.tier,
            "booking_history": customer.booking_history
        }
    }

@app.post("/customer/profile")
async def update_customer_profile(profile: CustomerProfile):
    """Create or update customer profile"""
    try:
        customer = Customer(
            id=f"cust_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=profile.name,
            email=profile.email,
            phone=profile.phone,
            preferences=profile.preferences,
            booking_history=[]
        )
        ai_engine.add_customer(customer)
        return {"success": True, "message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Business dashboard with analytics"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/analytics/overview")
async def get_analytics_overview():
    """Get business analytics overview"""
    # This would typically query your database for real analytics
    return {
        "total_bookings_today": 12,
        "revenue_today": 680.0,
        "popular_services": [
            {"name": "Deep Cleansing Facial", "bookings": 8},
            {"name": "Classic Haircut", "bookings": 6},
            {"name": "Manicure", "bookings": 4}
        ],
        "customer_satisfaction": 4.7,
        "repeat_customers": 78
    }

async def send_booking_confirmation(email: str, service: str, booking_time: datetime.datetime):
    """Background task to send booking confirmation"""
    # This would integrate with your email/SMS service
    print(f"📧 Sending confirmation to {email} for {service} at {booking_time}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
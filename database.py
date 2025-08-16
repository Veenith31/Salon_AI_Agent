from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config import Config
import json

class DatabaseManager:
    """Manages database operations for the salon booking system"""
    
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client[Config.DATABASE_NAME]
        self.customers = self.db.customers
        self.appointments = self.db.appointments
        self.communications = self.db.communications
        self.satisfaction_surveys = self.db.satisfaction_surveys
        
    def add_customer(self, customer_data: Dict[str, Any]) -> str:
        """Add a new customer to the database"""
        customer_data['created_at'] = datetime.now()
        customer_data['updated_at'] = datetime.now()
        
        # Set default communication preferences
        customer_data.setdefault('communication_preferences', {
            'sms': True,
            'whatsapp': True,
            'email': True,
            'social_media': False
        })
        
        result = self.customers.insert_one(customer_data)
        return str(result.inserted_id)
    
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        from bson import ObjectId
        return self.customers.find_one({'_id': ObjectId(customer_id)})
    
    def get_customer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get customer by phone number"""
        return self.customers.find_one({'phone': phone})
    
    def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get customer by email"""
        return self.customers.find_one({'email': email})
    
    def update_customer(self, customer_id: str, update_data: Dict[str, Any]) -> bool:
        """Update customer information"""
        from bson import ObjectId
        update_data['updated_at'] = datetime.now()
        result = self.customers.update_one(
            {'_id': ObjectId(customer_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def add_appointment(self, appointment_data: Dict[str, Any]) -> str:
        """Add a new appointment"""
        appointment_data['created_at'] = datetime.now()
        appointment_data['status'] = 'confirmed'
        appointment_data['reminders_sent'] = {
            'sms': False,
            'whatsapp': False,
            'email': False
        }
        appointment_data['satisfaction_survey_sent'] = False
        
        result = self.appointments.insert_one(appointment_data)
        return str(result.inserted_id)
    
    def get_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get appointment by ID"""
        from bson import ObjectId
        return self.appointments.find_one({'_id': ObjectId(appointment_id)})
    
    def get_appointments_by_date(self, date: datetime) -> List[Dict[str, Any]]:
        """Get all appointments for a specific date"""
        start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        return list(self.appointments.find({
            'appointment_time': {
                '$gte': start_of_day,
                '$lte': end_of_day
            }
        }).sort('appointment_time', 1))
    
    def get_upcoming_appointments(self, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """Get appointments in the next N hours"""
        now = datetime.now()
        future_time = now + timedelta(hours=hours_ahead)
        
        return list(self.appointments.find({
            'appointment_time': {
                '$gte': now,
                '$lte': future_time
            },
            'status': 'confirmed'
        }).sort('appointment_time', 1))
    
    def get_completed_appointments(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Get completed appointments in the last N hours"""
        now = datetime.now()
        past_time = now - timedelta(hours=hours_back)
        
        return list(self.appointments.find({
            'appointment_time': {
                '$gte': past_time,
                '$lte': now
            },
            'status': 'completed'
        }).sort('appointment_time', -1))
    
    def update_appointment_status(self, appointment_id: str, status: str) -> bool:
        """Update appointment status"""
        from bson import ObjectId
        result = self.appointments.update_one(
            {'_id': ObjectId(appointment_id)},
            {'$set': {'status': status, 'updated_at': datetime.now()}}
        )
        return result.modified_count > 0
    
    def mark_reminder_sent(self, appointment_id: str, reminder_type: str) -> bool:
        """Mark a reminder as sent"""
        from bson import ObjectId
        result = self.appointments.update_one(
            {'_id': ObjectId(appointment_id)},
            {'$set': {f'reminders_sent.{reminder_type}': True}}
        )
        return result.modified_count > 0
    
    def mark_satisfaction_survey_sent(self, appointment_id: str) -> bool:
        """Mark satisfaction survey as sent"""
        from bson import ObjectId
        result = self.appointments.update_one(
            {'_id': ObjectId(appointment_id)},
            {'$set': {'satisfaction_survey_sent': True}}
        )
        return result.modified_count > 0
    
    def add_communication_log(self, communication_data: Dict[str, Any]) -> str:
        """Log communication attempts"""
        communication_data['timestamp'] = datetime.now()
        result = self.communications.insert_one(communication_data)
        return str(result.inserted_id)
    
    def add_satisfaction_survey(self, survey_data: Dict[str, Any]) -> str:
        """Add satisfaction survey response"""
        survey_data['submitted_at'] = datetime.now()
        result = self.satisfaction_surveys.insert_one(survey_data)
        return str(result.inserted_id)
    
    def get_available_slots(self, date: datetime, service_duration: int = 60) -> List[Dict[str, Any]]:
        """Get available time slots for a specific date"""
        start_of_day = datetime(date.year, date.month, date.day, 9, 0, 0)  # 9 AM
        end_of_day = datetime(date.year, date.month, date.day, 18, 0, 0)   # 6 PM
        
        # Get booked appointments for the day
        booked_appointments = self.get_appointments_by_date(date)
        
        # Generate all possible slots
        slots = []
        current_time = start_of_day
        
        while current_time + timedelta(minutes=service_duration) <= end_of_day:
            slot_end = current_time + timedelta(minutes=service_duration)
            
            # Check if slot is available
            is_available = True
            for appointment in booked_appointments:
                appt_start = appointment['appointment_time']
                appt_end = appt_start + timedelta(minutes=appointment.get('duration', 60))
                
                # Check for overlap
                if (current_time < appt_end and slot_end > appt_start):
                    is_available = False
                    break
            
            if is_available:
                slots.append({
                    'time': current_time.strftime('%I:%M %p'),
                    'datetime': current_time,
                    'duration': service_duration
                })
            
            current_time += timedelta(minutes=30)  # 30-minute intervals
        
        return slots
    
    def get_customer_statistics(self) -> Dict[str, Any]:
        """Get customer and appointment statistics"""
        total_customers = self.customers.count_documents({})
        total_appointments = self.appointments.count_documents({})
        today_appointments = len(self.get_appointments_by_date(datetime.now()))
        
        # Get appointments by status
        confirmed_appointments = self.appointments.count_documents({'status': 'confirmed'})
        completed_appointments = self.appointments.count_documents({'status': 'completed'})
        cancelled_appointments = self.appointments.count_documents({'status': 'cancelled'})
        
        # Get popular services
        pipeline = [
            {'$group': {'_id': '$service', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        popular_services = list(self.appointments.aggregate(pipeline))
        
        return {
            'total_customers': total_customers,
            'total_appointments': total_appointments,
            'today_appointments': today_appointments,
            'confirmed_appointments': confirmed_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'popular_services': popular_services
        }
    
    def get_recent_communications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent communication logs"""
        return list(self.communications.find().sort('timestamp', -1).limit(limit))
    
    def get_satisfaction_surveys(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent satisfaction survey responses"""
        return list(self.satisfaction_surveys.find().sort('submitted_at', -1).limit(limit))
    
    def search_customers(self, search_term: str) -> List[Dict[str, Any]]:
        """Search customers by name, phone, or email"""
        return list(self.customers.find({
            '$or': [
                {'name': {'$regex': search_term, '$options': 'i'}},
                {'phone': {'$regex': search_term, '$options': 'i'}},
                {'email': {'$regex': search_term, '$options': 'i'}}
            ]
        }).sort('name', 1))
    
    def get_customer_appointments(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all appointments for a specific customer"""
        from bson import ObjectId
        return list(self.appointments.find({
            'customer_id': ObjectId(customer_id)
        }).sort('appointment_time', -1))
    
    def update_customer_communication_preferences(self, customer_id: str, preferences: Dict[str, bool]) -> bool:
        """Update customer communication preferences"""
        from bson import ObjectId
        result = self.customers.update_one(
            {'_id': ObjectId(customer_id)},
            {'$set': {'communication_preferences': preferences}}
        )
        return result.modified_count > 0
import json
import datetime
from typing import Dict, List, Optional
import sqlite3
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np

@dataclass
class Customer:
    id: str
    name: str
    email: str
    phone: str
    preferences: Dict
    booking_history: List[Dict]
    loyalty_points: int = 0
    tier: str = "Bronze"
    created_at: datetime.datetime = None

@dataclass
class Service:
    id: str
    name: str
    category: str
    duration_minutes: int
    base_price: float
    skill_level: str
    popularity_score: float = 0.0
    seasonal_factor: float = 1.0

class AIRecommendationEngine:
    def __init__(self, db_path: str = "salon_data.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for customer data and analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                preferences TEXT,
                loyalty_points INTEGER DEFAULT 0,
                tier TEXT DEFAULT 'Bronze',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                customer_id TEXT,
                service_id TEXT,
                service_name TEXT,
                booking_datetime TIMESTAMP,
                duration_minutes INTEGER,
                price FLOAT,
                status TEXT,
                staff_id TEXT,
                rating INTEGER,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        # Create services table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                duration_minutes INTEGER,
                base_price FLOAT,
                skill_level TEXT,
                popularity_score FLOAT DEFAULT 0.0,
                seasonal_factor FLOAT DEFAULT 1.0,
                description TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize with default services
        self._populate_default_services()
    
    def _populate_default_services(self):
        """Add default salon services to the database"""
        default_services = [
            Service("hair_001", "Classic Haircut", "Hair", 45, 25.0, "Basic", 0.8),
            Service("hair_002", "Hair Coloring", "Hair", 120, 80.0, "Advanced", 0.7),
            Service("hair_003", "Hair Spa Treatment", "Hair", 90, 60.0, "Intermediate", 0.6),
            Service("face_001", "Deep Cleansing Facial", "Facial", 60, 45.0, "Basic", 0.9),
            Service("face_002", "Anti-Aging Facial", "Facial", 75, 70.0, "Advanced", 0.5),
            Service("nail_001", "Manicure", "Nails", 30, 20.0, "Basic", 0.8),
            Service("nail_002", "Pedicure", "Nails", 45, 25.0, "Basic", 0.7),
            Service("body_001", "Full Body Massage", "Massage", 60, 50.0, "Intermediate", 0.6),
            Service("body_002", "Aromatherapy Massage", "Massage", 75, 65.0, "Advanced", 0.4),
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for service in default_services:
            cursor.execute('''
                INSERT OR IGNORE INTO services 
                (id, name, category, duration_minutes, base_price, skill_level, popularity_score, seasonal_factor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (service.id, service.name, service.category, service.duration_minutes, 
                  service.base_price, service.skill_level, service.popularity_score, service.seasonal_factor))
        
        conn.commit()
        conn.close()
    
    def add_customer(self, customer: Customer):
        """Add or update customer in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO customers 
            (id, name, email, phone, preferences, loyalty_points, tier)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer.id, customer.name, customer.email, customer.phone, 
              json.dumps(customer.preferences), customer.loyalty_points, customer.tier))
        
        conn.commit()
        conn.close()
    
    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Retrieve customer by email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM customers WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            customer = Customer(
                id=row[0], name=row[1], email=row[2], phone=row[3],
                preferences=json.loads(row[4]), loyalty_points=row[5], tier=row[6]
            )
            customer.booking_history = self._get_customer_bookings(customer.id)
            return customer
        return None
    
    def _get_customer_bookings(self, customer_id: str) -> List[Dict]:
        """Get booking history for a customer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT service_name, booking_datetime, price, rating, feedback 
            FROM bookings WHERE customer_id = ? 
            ORDER BY booking_datetime DESC
        ''', (customer_id,))
        
        bookings = []
        for row in cursor.fetchall():
            bookings.append({
                'service_name': row[0],
                'booking_datetime': row[1],
                'price': row[2],
                'rating': row[3],
                'feedback': row[4]
            })
        
        conn.close()
        return bookings
    
    def get_personalized_recommendations(self, customer_email: str, limit: int = 5) -> List[Dict]:
        """Generate AI-powered personalized service recommendations"""
        customer = self.get_customer_by_email(customer_email)
        if not customer:
            return self._get_popular_services(limit)
        
        # Analyze customer preferences and history
        recommendations = []
        
        # 1. Recommend based on booking frequency
        service_frequency = defaultdict(int)
        total_spent = 0
        avg_rating = 0
        rating_count = 0
        
        for booking in customer.booking_history:
            service_frequency[booking['service_name']] += 1
            total_spent += booking.get('price', 0)
            if booking.get('rating'):
                avg_rating += booking['rating']
                rating_count += 1
        
        if rating_count > 0:
            avg_rating /= rating_count
        
        # 2. Get all available services
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM services ORDER BY popularity_score DESC')
        all_services = cursor.fetchall()
        conn.close()
        
        # 3. Score services based on multiple factors
        for service_row in all_services:
            service_id, name, category, duration, price, skill_level, popularity, seasonal = service_row[:8]
            
            score = 0.0
            reasons = []
            
            # Popularity boost
            score += popularity * 0.3
            
            # Frequency boost for similar services
            if name in service_frequency:
                score += min(service_frequency[name] * 0.2, 0.8)
                reasons.append("You've enjoyed this service before")
            
            # Category preference boost
            category_count = sum(1 for booking in customer.booking_history 
                               if self._get_service_category(booking['service_name']) == category)
            if category_count > 0:
                score += min(category_count * 0.15, 0.6)
                reasons.append(f"Matches your {category.lower()} preferences")
            
            # Loyalty tier discounts
            if customer.tier == "Gold":
                score += 0.2
                reasons.append("Gold member special")
            elif customer.tier == "Silver":
                score += 0.1
                reasons.append("Silver member benefit")
            
            # Seasonal boost
            current_month = datetime.datetime.now().month
            if current_month in [12, 1, 2] and "facial" in name.lower():  # Winter facial boost
                score += 0.2
                reasons.append("Perfect for winter season")
            elif current_month in [6, 7, 8] and "massage" in name.lower():  # Summer relaxation
                score += 0.15
                reasons.append("Summer relaxation special")
            
            # Price compatibility (prefer services within customer's typical range)
            if total_spent > 0:
                avg_spent = total_spent / len(customer.booking_history)
                price_ratio = min(price / avg_spent, avg_spent / price)
                score += price_ratio * 0.1
            
            recommendations.append({
                'service_id': service_id,
                'service_name': name,
                'category': category,
                'duration_minutes': duration,
                'price': price,
                'score': score,
                'reasons': reasons[:2],  # Top 2 reasons
                'estimated_completion': self._estimate_completion_time(duration),
                'dynamic_price': self._calculate_dynamic_price(price, customer.tier, popularity)
            })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]
    
    def _get_service_category(self, service_name: str) -> str:
        """Get category for a service name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT category FROM services WHERE name = ?', (service_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "General"
    
    def _get_popular_services(self, limit: int) -> List[Dict]:
        """Get popular services for new customers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, category, duration_minutes, base_price, popularity_score 
            FROM services 
            ORDER BY popularity_score DESC 
            LIMIT ?
        ''', (limit,))
        
        services = []
        for row in cursor.fetchall():
            services.append({
                'service_id': row[0],
                'service_name': row[1],
                'category': row[2],
                'duration_minutes': row[3],
                'price': row[4],
                'score': row[5],
                'reasons': ["Popular choice", "Highly rated by customers"],
                'estimated_completion': self._estimate_completion_time(row[3]),
                'dynamic_price': row[4]
            })
        
        conn.close()
        return services
    
    def _estimate_completion_time(self, duration_minutes: int) -> str:
        """Estimate completion time based on current time and duration"""
        now = datetime.datetime.now()
        completion_time = now + datetime.timedelta(minutes=duration_minutes)
        return completion_time.strftime("%I:%M %p")
    
    def _calculate_dynamic_price(self, base_price: float, customer_tier: str, popularity: float) -> float:
        """Calculate dynamic pricing based on demand and customer loyalty"""
        price = base_price
        
        # Loyalty discounts
        if customer_tier == "Gold":
            price *= 0.85  # 15% discount
        elif customer_tier == "Silver":
            price *= 0.92  # 8% discount
        elif customer_tier == "Bronze":
            price *= 0.98  # 2% discount
        
        # Demand-based pricing
        if popularity > 0.8:
            price *= 1.1  # High demand surcharge
        elif popularity < 0.4:
            price *= 0.9   # Low demand discount
        
        return round(price, 2)
    
    def record_booking(self, customer_email: str, service_name: str, booking_datetime: datetime.datetime, price: float):
        """Record a new booking and update customer data"""
        customer = self.get_customer_by_email(customer_email)
        if not customer:
            return
        
        booking_id = f"book_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bookings 
            (id, customer_id, service_name, booking_datetime, price, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (booking_id, customer.id, service_name, booking_datetime.isoformat(), price, "confirmed"))
        
        # Update customer loyalty points
        points_earned = int(price / 5)  # 1 point per $5 spent
        new_points = customer.loyalty_points + points_earned
        
        # Update tier based on points
        new_tier = "Bronze"
        if new_points >= 1000:
            new_tier = "Gold"
        elif new_points >= 500:
            new_tier = "Silver"
        
        cursor.execute('''
            UPDATE customers 
            SET loyalty_points = ?, tier = ? 
            WHERE email = ?
        ''', (new_points, new_tier, customer_email))
        
        conn.commit()
        conn.close()
        
        return booking_id

# Example usage and testing
if __name__ == "__main__":
    # Initialize the AI recommendation engine
    ai_engine = AIRecommendationEngine()
    
    # Add a sample customer
    sample_customer = Customer(
        id="cust_001",
        name="Sarah Johnson",
        email="sarah.johnson@email.com",
        phone="+1234567890",
        preferences={"preferred_time": "afternoon", "style_preference": "modern"},
        booking_history=[],
        loyalty_points=350,
        tier="Silver"
    )
    
    ai_engine.add_customer(sample_customer)
    
    # Record some bookings for better recommendations
    ai_engine.record_booking("sarah.johnson@email.com", "Deep Cleansing Facial", 
                           datetime.datetime.now() - datetime.timedelta(days=30), 45.0)
    ai_engine.record_booking("sarah.johnson@email.com", "Classic Haircut", 
                           datetime.datetime.now() - datetime.timedelta(days=60), 25.0)
    
    # Get personalized recommendations
    recommendations = ai_engine.get_personalized_recommendations("sarah.johnson@email.com")
    
    print("🤖 AI-Powered Recommendations for Sarah:")
    print("=" * 50)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['service_name']} ({rec['category']})")
        print(f"   💰 Price: ${rec['dynamic_price']} | ⏱️ Duration: {rec['duration_minutes']} min")
        print(f"   🎯 Score: {rec['score']:.2f}")
        print(f"   💡 Why: {', '.join(rec['reasons'])}")
        print()
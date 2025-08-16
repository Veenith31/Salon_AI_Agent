# 🎨 Salon Booking Agent - Advanced Edition

A comprehensive salon booking system with advanced communication features, beautiful web dashboard, and multi-channel notifications.

## ✨ Features

### 🚀 **Advanced Communication System**
- **SMS Notifications** - Send appointment reminders via Twilio
- **WhatsApp Integration** - Connect with customers on WhatsApp Business API
- **Automated Follow-ups** - Post-appointment satisfaction surveys
- **Social Media Integration** - Share availability on Facebook, Instagram, and Twitter
- **Enhanced Email Templates** - Beautiful HTML email confirmations

### 🎯 **Beautiful Web Dashboard**
- **Modern UI/UX** - Responsive design with gradient themes
- **Real-time Statistics** - Customer and appointment analytics
- **Quick Actions** - One-click reminder and survey sending
- **Appointment Management** - View and manage all bookings
- **Customer Database** - Store and manage customer information
- **Communication Logs** - Track all notification attempts

### 📱 **Public Booking Portal**
- **Multi-step Booking Process** - Service selection → Date/Time → Details
- **Real-time Availability** - Live slot checking
- **Mobile Responsive** - Works perfectly on all devices
- **Instant Confirmations** - Automatic notifications on booking

### 🔧 **Smart Features**
- **Database Integration** - MongoDB for data persistence
- **API Endpoints** - RESTful API for integrations
- **Authentication** - Secure admin access
- **Error Handling** - Comprehensive error management

## 🛠️ Installation & Setup

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Set Up MongoDB**
```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt-get install mongodb

# Start MongoDB service
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 3. **Configure Environment Variables**
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your API keys
nano .env
```

### 4. **Get API Keys**

#### **Twilio (SMS)**
1. Sign up at [Twilio](https://www.twilio.com/)
2. Get Account SID and Auth Token from dashboard
3. Purchase a phone number
4. Add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

#### **WhatsApp Business API**
1. Set up WhatsApp Business API through Meta
2. Get API token and phone number ID
3. Add to `.env`:
   ```
   WHATSAPP_API_TOKEN=your_token
   WHATSAPP_PHONE_NUMBER_ID=your_phone_id
   ```

#### **Facebook/Instagram**
1. Create Facebook App at [Facebook Developers](https://developers.facebook.com/)
2. Get access token and page ID
3. Add to `.env`:
   ```
   FACEBOOK_ACCESS_TOKEN=your_token
   FACEBOOK_PAGE_ID=your_page_id
   ```

#### **Email (Gmail)**
1. Enable 2-factor authentication on Gmail
2. Generate App Password
3. Add to `.env`:
   ```
   EMAIL_USERNAME=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   ```

### 5. **Run the Application**
```bash
# Start the web dashboard
python web_dashboard.py

# Or run the original voice booking system
python booking_agent.py
```

## 🎯 **Usage Guide**

### **Web Dashboard Access**
- **URL**: `http://localhost:8000`
- **Username**: `admin`
- **Password**: `salon123`

### **Public Booking Portal**
- **URL**: `http://localhost:8000/booking`
- **No login required** - Customers can book directly

### **Dashboard Features**

#### **📊 Main Dashboard**
- View real-time statistics
- See today's appointments
- Quick action buttons for reminders and surveys
- Recent communication logs

#### **📅 Appointments Management**
- View all appointments for the next 7 days
- Filter by date and status
- Update appointment status
- Send individual reminders

#### **👥 Customer Management**
- View all customers
- Search customers by name, phone, or email
- Update customer information
- View customer appointment history

#### **💬 Communications**
- View all communication logs
- Track SMS, WhatsApp, and email delivery
- View satisfaction survey responses
- Post availability to social media

### **Quick Actions**

#### **Send Reminders**
1. Click "Send Reminders" on dashboard
2. System automatically sends to upcoming appointments
3. Tracks delivery status

#### **Send Satisfaction Surveys**
1. Click "Send Surveys" on dashboard
2. System sends to completed appointments
3. Collects customer feedback

#### **Post to Social Media**
1. Click "Post Availability" on dashboard
2. Select date for available slots
3. Automatically posts to Facebook and Twitter

## 🔧 **API Endpoints**

### **Public Endpoints**
- `GET /booking` - Public booking page
- `POST /book-appointment` - Create new appointment
- `GET /api/available-slots/{date}` - Get available slots

### **Admin Endpoints** (Require authentication)
- `GET /` - Main dashboard
- `GET /appointments` - Appointments management
- `GET /customers` - Customer management
- `GET /communications` - Communication logs
- `POST /send-reminders` - Send appointment reminders
- `POST /send-satisfaction-surveys` - Send surveys
- `POST /post-social-media` - Post to social media

## 📱 **Communication Features**

### **SMS Notifications**
- Appointment confirmations
- 24-hour reminders
- Customizable messages
- Delivery tracking

### **WhatsApp Messages**
- Rich media support
- Interactive buttons
- Automated responses
- Business profile integration

### **Email Templates**
- Beautiful HTML designs
- Responsive layouts
- Brand customization
- Professional appearance

### **Social Media Integration**
- Facebook page posts
- Twitter updates
- Instagram stories (basic)
- Automated availability sharing

## 🎨 **Customization**

### **Styling**
- Modify CSS in `templates/base.html`
- Change color scheme in CSS variables
- Add custom fonts and icons

### **Email Templates**
- Edit HTML templates in `communication_services.py`
- Customize salon branding
- Add logo and contact information

### **Notification Messages**
- Modify message templates in communication services
- Add multi-language support
- Customize timing and frequency

## 🔒 **Security Features**

- **Authentication** - Basic auth for admin access
- **Input Validation** - Form validation and sanitization
- **Error Handling** - Comprehensive error management
- **API Rate Limiting** - Protect against abuse
- **Secure Headers** - Security best practices

## 📊 **Database Schema**

### **Customers Collection**
```json
{
  "_id": "ObjectId",
  "name": "string",
  "phone": "string",
  "email": "string",
  "communication_preferences": {
    "sms": "boolean",
    "whatsapp": "boolean",
    "email": "boolean",
    "social_media": "boolean"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### **Appointments Collection**
```json
{
  "_id": "ObjectId",
  "customer_id": "ObjectId",
  "customer_info": {
    "name": "string",
    "phone": "string",
    "email": "string"
  },
  "service": "string",
  "appointment_time": "datetime",
  "duration": "number",
  "status": "string",
  "reminders_sent": {
    "sms": "boolean",
    "whatsapp": "boolean",
    "email": "boolean"
  },
  "satisfaction_survey_sent": "boolean",
  "created_at": "datetime"
}
```

## 🚀 **Deployment**

### **Production Setup**
1. Use production MongoDB instance
2. Set up proper SSL certificates
3. Configure reverse proxy (nginx)
4. Set up monitoring and logging
5. Use environment-specific configurations

### **Docker Deployment**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "web_dashboard.py"]
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the example configuration

## 🎉 **What Makes This Project Stand Out**

1. **Multi-Channel Communication** - SMS, WhatsApp, Email, Social Media
2. **Beautiful UI/UX** - Modern, responsive design
3. **Real-time Features** - Live availability checking
4. **Automation** - Automated reminders and surveys
5. **Scalability** - MongoDB database, API architecture
6. **Professional Email Templates** - Beautiful HTML emails
7. **Social Media Integration** - Automated posting
8. **Comprehensive Dashboard** - All-in-one management
9. **Public Booking Portal** - Customer-friendly interface
10. **Advanced Analytics** - Statistics and reporting

This project transforms a basic booking system into a comprehensive salon management solution that can compete with commercial software!
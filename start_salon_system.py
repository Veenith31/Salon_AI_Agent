#!/usr/bin/env python3
"""
Salon Booking Agent - Startup Script
Choose between Web Dashboard or Voice Booking System
"""

import os
import sys
import subprocess
from datetime import datetime

def print_banner():
    """Print the salon system banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🎨 SALON BOOKING AGENT 🎨                 ║
    ║                     Advanced Edition                         ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'pymongo', 'requests', 
        'python-dotenv', 'jinja2', 'aiofiles'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check if environment file exists"""
    if not os.path.exists('.env'):
        print("⚠️  No .env file found!")
        print("📝 Creating .env file from template...")
        
        if os.path.exists('.env.example'):
            subprocess.run(['cp', '.env.example', '.env'])
            print("✅ Created .env file from template")
            print("🔧 Please edit .env file with your API keys")
        else:
            print("❌ .env.example not found")
            return False
    
    return True

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB connection successful")
        return True
    except Exception as e:
        print("❌ MongoDB connection failed")
        print("   Make sure MongoDB is running:")
        print("   sudo systemctl start mongodb")
        return False

def start_web_dashboard():
    """Start the web dashboard"""
    print("\n🚀 Starting Web Dashboard...")
    print("📱 Dashboard URL: http://localhost:8000")
    print("👤 Username: admin")
    print("🔑 Password: salon123")
    print("📖 Public Booking: http://localhost:8000/booking")
    print("\n⏹️  Press Ctrl+C to stop")
    
    try:
        subprocess.run([sys.executable, 'web_dashboard.py'])
    except KeyboardInterrupt:
        print("\n🛑 Web Dashboard stopped")

def start_voice_system():
    """Start the original voice booking system"""
    print("\n🎤 Starting Voice Booking System...")
    print("💬 You can now use voice commands to book appointments")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        subprocess.run([sys.executable, 'booking_agent.py'])
    except KeyboardInterrupt:
        print("\n🛑 Voice System stopped")

def show_menu():
    """Show the main menu"""
    print("\n" + "="*60)
    print("🎯 CHOOSE YOUR SALON SYSTEM")
    print("="*60)
    print("1. 🌐 Web Dashboard (Recommended)")
    print("   - Beautiful admin interface")
    print("   - SMS/WhatsApp/Email notifications")
    print("   - Social media integration")
    print("   - Customer management")
    print("   - Public booking portal")
    print()
    print("2. 🎤 Voice Booking System (Original)")
    print("   - Voice recognition booking")
    print("   - Google Calendar integration")
    print("   - Basic email notifications")
    print()
    print("3. 🔧 System Check")
    print("   - Check dependencies")
    print("   - Verify configuration")
    print()
    print("4. 📖 View Documentation")
    print("   - Open README.md")
    print()
    print("5. 🚪 Exit")
    print("="*60)

def system_check():
    """Perform comprehensive system check"""
    print("\n🔍 PERFORMING SYSTEM CHECK")
    print("="*40)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if check_dependencies():
        print("✅ All dependencies installed")
    else:
        print("❌ Dependencies check failed")
        return
    
    # Check environment
    print("\n⚙️  Checking environment...")
    if check_environment():
        print("✅ Environment configured")
    else:
        print("❌ Environment check failed")
        return
    
    # Check MongoDB
    print("\n🗄️  Checking MongoDB...")
    if check_mongodb():
        print("✅ MongoDB is running")
    else:
        print("❌ MongoDB check failed")
        return
    
    print("\n🎉 System check completed successfully!")
    print("✅ Your salon booking system is ready to use!")

def view_documentation():
    """Open the README file"""
    if os.path.exists('README.md'):
        print("\n📖 Opening documentation...")
        try:
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', 'README.md'])
            elif sys.platform.startswith('win32'):  # Windows
                subprocess.run(['start', 'README.md'], shell=True)
            else:  # Linux
                subprocess.run(['xdg-open', 'README.md'])
            print("✅ Documentation opened")
        except Exception as e:
            print(f"❌ Could not open documentation: {e}")
            print("📄 You can manually open README.md")
    else:
        print("❌ README.md not found")

def main():
    """Main function"""
    print_banner()
    
    while True:
        show_menu()
        
        try:
            choice = input("\n🎯 Enter your choice (1-5): ").strip()
            
            if choice == '1':
                if check_dependencies() and check_environment() and check_mongodb():
                    start_web_dashboard()
                else:
                    print("\n❌ System check failed. Please fix the issues above.")
                    input("Press Enter to continue...")
            
            elif choice == '2':
                if check_dependencies() and check_environment():
                    start_voice_system()
                else:
                    print("\n❌ System check failed. Please fix the issues above.")
                    input("Press Enter to continue...")
            
            elif choice == '3':
                system_check()
                input("\nPress Enter to continue...")
            
            elif choice == '4':
                view_documentation()
                input("\nPress Enter to continue...")
            
            elif choice == '5':
                print("\n👋 Thank you for using Salon Booking Agent!")
                print("🌟 Have a great day!")
                break
            
            else:
                print("\n❌ Invalid choice. Please enter 1-5.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
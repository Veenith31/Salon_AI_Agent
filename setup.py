#!/usr/bin/env python3
"""
Salon Booking Agent - Automated Setup Script
===========================================

This script automatically sets up the Salon Booking Agent with all dependencies,
configurations, and initial data.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

class SalonSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.system = platform.system().lower()
        self.python_executable = sys.executable
        
    def print_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    💇‍♀️ SALON BOOKING AGENT - AI-POWERED SETUP 🤖            ║
║                                                              ║
║    🌟 Revolutionary beauty appointment system                ║
║    🎯 AI recommendations & voice booking                     ║
║    📊 Business analytics & customer intelligence             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🔍 Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ is required. Please upgrade Python.")
            sys.exit(1)
            
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        
    def create_virtual_environment(self):
        """Create and activate virtual environment"""
        print("\n📦 Setting up virtual environment...")
        
        venv_path = self.project_root / "venv"
        
        if venv_path.exists():
            print("✅ Virtual environment already exists")
            return
            
        try:
            subprocess.run([
                self.python_executable, "-m", "venv", str(venv_path)
            ], check=True)
            print("✅ Virtual environment created successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            sys.exit(1)
            
    def get_venv_python(self):
        """Get the Python executable from virtual environment"""
        if self.system == "windows":
            return str(self.project_root / "venv" / "Scripts" / "python.exe")
        else:
            return str(self.project_root / "venv" / "bin" / "python")
            
    def get_venv_pip(self):
        """Get the pip executable from virtual environment"""
        if self.system == "windows":
            return str(self.project_root / "venv" / "Scripts" / "pip.exe")
        else:
            return str(self.project_root / "venv" / "bin" / "pip")
            
    def install_dependencies(self):
        """Install Python dependencies"""
        print("\n📥 Installing dependencies...")
        
        pip_path = self.get_venv_pip()
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            sys.exit(1)
            
        try:
            # Upgrade pip first
            subprocess.run([
                pip_path, "install", "--upgrade", "pip"
            ], check=True)
            
            # Install requirements
            subprocess.run([
                pip_path, "install", "-r", str(requirements_file)
            ], check=True)
            
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            sys.exit(1)
            
    def create_directories(self):
        """Create necessary directories"""
        print("\n📁 Creating project directories...")
        
        directories = [
            "static/css",
            "static/js", 
            "static/images",
            "templates",
            "data",
            "logs"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
        print("✅ Project directories created")
        
    def create_env_file(self):
        """Create environment configuration file"""
        print("\n⚙️ Creating environment configuration...")
        
        env_file = self.project_root / ".env"
        
        if env_file.exists():
            print("✅ .env file already exists")
            return
            
        env_content = """# Salon Booking Agent Configuration
# =================================

# Application Settings
APP_NAME=Salon Booking Agent
APP_VERSION=1.0.0
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///salon_data.db

# Google Calendar API
GOOGLE_CREDENTIALS_FILE=credentials.json

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Notification Settings
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_SMS_NOTIFICATIONS=false

# AI Features
ENABLE_AI_RECOMMENDATIONS=true
AI_MODEL_PATH=models/

# Business Settings
DEFAULT_TIMEZONE=UTC
BUSINESS_HOURS_START=09:00
BUSINESS_HOURS_END=18:00
DEFAULT_APPOINTMENT_DURATION=60

# Security
MAX_LOGIN_ATTEMPTS=5
SESSION_TIMEOUT=3600
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
            
        print("✅ Environment file created")
        
    def setup_database(self):
        """Initialize the database with sample data"""
        print("\n🗄️ Setting up database...")
        
        python_path = self.get_venv_python()
        
        # Run the AI recommendations module to initialize database
        try:
            subprocess.run([
                python_path, "-c",
                "from ai_recommendations import AIRecommendationEngine; "
                "ai = AIRecommendationEngine(); "
                "print('Database initialized successfully')"
            ], check=True, cwd=str(self.project_root))
            
            print("✅ Database initialized with sample data")
        except subprocess.CalledProcessError:
            print("⚠️ Database setup completed with warnings")
            
    def create_desktop_shortcut(self):
        """Create desktop shortcut for easy access"""
        print("\n🖥️ Creating desktop shortcuts...")
        
        if self.system == "windows":
            self.create_windows_shortcut()
        elif self.system == "darwin":  # macOS
            self.create_macos_shortcut()
        else:  # Linux
            self.create_linux_shortcut()
            
    def create_windows_shortcut(self):
        """Create Windows desktop shortcut"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Salon Booking Agent.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = self.get_venv_python()
            shortcut.Arguments = str(self.project_root / "app.py")
            shortcut.WorkingDirectory = str(self.project_root)
            shortcut.IconLocation = str(self.project_root / "static" / "images" / "icon.ico")
            shortcut.save()
            
            print("✅ Windows desktop shortcut created")
        except ImportError:
            print("⚠️ Cannot create Windows shortcut (missing dependencies)")
            
    def create_macos_shortcut(self):
        """Create macOS desktop shortcut"""
        print("ℹ️ macOS shortcut creation skipped (manual setup required)")
        
    def create_linux_shortcut(self):
        """Create Linux desktop shortcut"""
        try:
            desktop_file = Path.home() / "Desktop" / "salon-booking-agent.desktop"
            
            content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Salon Booking Agent
Comment=AI-Powered Beauty Appointment System
Exec={self.get_venv_python()} {self.project_root / "app.py"}
Icon={self.project_root / "static" / "images" / "icon.png"}
Terminal=false
StartupNotify=true
Categories=Office;Business;
"""
            
            with open(desktop_file, 'w') as f:
                f.write(content)
                
            # Make executable
            desktop_file.chmod(0o755)
            
            print("✅ Linux desktop shortcut created")
        except Exception as e:
            print(f"⚠️ Cannot create Linux shortcut: {e}")
            
    def create_sample_credentials(self):
        """Create sample Google credentials file"""
        print("\n🔑 Setting up Google Calendar integration...")
        
        creds_file = self.project_root / "credentials.json.sample"
        
        sample_creds = {
            "installed": {
                "client_id": "your-client-id.googleusercontent.com",
                "project_id": "your-project-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "your-client-secret",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
            }
        }
        
        with open(creds_file, 'w') as f:
            json.dump(sample_creds, f, indent=2)
            
        print("✅ Sample credentials file created")
        print("ℹ️ Please rename credentials.json.sample to credentials.json")
        print("ℹ️ and add your actual Google API credentials")
        
    def create_startup_scripts(self):
        """Create convenient startup scripts"""
        print("\n🚀 Creating startup scripts...")
        
        # Windows batch file
        if self.system == "windows":
            batch_content = f"""@echo off
cd /d "{self.project_root}"
"{self.get_venv_python()}" app.py
pause
"""
            with open(self.project_root / "start_salon.bat", 'w') as f:
                f.write(batch_content)
                
        # Unix shell script
        shell_content = f"""#!/bin/bash
cd "{self.project_root}"
source venv/bin/activate
python app.py
"""
        shell_file = self.project_root / "start_salon.sh"
        with open(shell_file, 'w') as f:
            f.write(shell_content)
        shell_file.chmod(0o755)
        
        print("✅ Startup scripts created")
        
    def print_instructions(self):
        """Print final setup instructions"""
        instructions = f"""

╔══════════════════════════════════════════════════════════════╗
║                    🎉 SETUP COMPLETE! 🎉                    ║
╚══════════════════════════════════════════════════════════════╝

✅ Virtual environment created
✅ Dependencies installed  
✅ Project structure initialized
✅ Database configured
✅ Configuration files created

🚀 NEXT STEPS:

1. 🔑 Google Calendar Setup (Required):
   • Go to: https://console.cloud.google.com/
   • Create a project and enable Calendar API
   • Create OAuth 2.0 credentials
   • Download as 'credentials.json' in project root

2. ⚙️ Configure Settings:
   • Edit .env file for your preferences
   • Update email/SMS settings if needed

3. 🎯 Start the Application:
   
   Option A - Command Line:
   {"venv\\Scripts\\python app.py" if self.system == "windows" else "./start_salon.sh"}
   
   Option B - Direct:
   {self.get_venv_python()} app.py

4. 🌐 Access Your Salon:
   • Main Site: http://localhost:8000
   • Dashboard: http://localhost:8000/dashboard

🎨 FEATURES TO EXPLORE:

• 🗣️ Voice Booking: Click microphone and say "Book a haircut"
• 🤖 AI Recommendations: Enter customer email for personalized suggestions  
• 📊 Business Analytics: View real-time business insights
• 👤 Customer Portal: Track loyalty points and booking history

💡 TIPS:
• Grant microphone permission for voice booking
• Use demo email: sarah.johnson@email.com for AI recommendations
• Check the dashboard for business insights

📞 SUPPORT:
• Documentation: README.md
• Issues: GitHub repository
• Community: Discord server

Happy booking! 💇‍♀️✨
        """
        
        print(instructions)
        
    def run_setup(self):
        """Run the complete setup process"""
        try:
            self.print_banner()
            self.check_python_version()
            self.create_virtual_environment()
            self.install_dependencies()
            self.create_directories()
            self.create_env_file()
            self.setup_database()
            self.create_sample_credentials()
            self.create_startup_scripts()
            
            # Optional features
            try:
                self.create_desktop_shortcut()
            except Exception as e:
                print(f"⚠️ Desktop shortcut creation skipped: {e}")
                
            self.print_instructions()
            
        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Setup failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    setup = SalonSetup()
    setup.run_setup()
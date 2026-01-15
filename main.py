#!/usr/bin/env python3
"""
AI Rescheduling Agent - Standalone Executable
Runs fully local on localhost - HIPAA compliant
"""

import os
import sys
import time
import threading
import webbrowser
import socket
from pathlib import Path

# Handle PyInstaller bundled resources
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(os.path.dirname(sys.executable))
else:
    # Running as script
    BASE_DIR = Path(__file__).parent
    APP_DIR = BASE_DIR

# Set up paths for templates and static files
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

def setup_environment():
    """Set up environment variables from config file if it exists - MUST RUN BEFORE IMPORTING APP"""
    env_file = APP_DIR / 'config.env'
    
    if env_file.exists():
        print(f"📝 Loading configuration from: {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    os.environ[key] = value
                    # Debug: print loaded values (without showing full credentials)
                    if 'KEY' in key or 'ID' in key:
                        print(f"   Loaded {key}: {value[:10]}...")
                    else:
                        print(f"   Loaded {key}: {value}")
        print("✅ Configuration loaded")
        
        # Validate configuration
        validate_config()
    else:
        print(f"❌ No config file found at: {env_file}")
        print()
        print("   Create config.env with your API credentials:")
        print("   RETELL_API_KEY=your_key")
        print("   RETELL_AGENT_ID=your_agent_id")
        print("   FROM_NUMBER=+15551234567  (must start with +)")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

def validate_config():
    """Validate required environment variables"""
    errors = []
    
    # Check required variables exist
    if not os.environ.get('RETELL_API_KEY'):
        errors.append("❌ RETELL_API_KEY not set in config.env")
    elif os.environ.get('RETELL_API_KEY') == 'your_retell_api_key_here':
        errors.append("❌ RETELL_API_KEY still has placeholder value")
    
    if not os.environ.get('RETELL_AGENT_ID'):
        errors.append("❌ RETELL_AGENT_ID not set in config.env")
    elif os.environ.get('RETELL_AGENT_ID') == 'your_agent_id_here':
        errors.append("❌ RETELL_AGENT_ID still has placeholder value")
    
    from_number = os.environ.get('FROM_NUMBER', '')
    if not from_number:
        errors.append("❌ FROM_NUMBER not set in config.env")
    elif not from_number.startswith('+'):
        errors.append(f"❌ FROM_NUMBER must start with + (E.164 format)")
        errors.append(f"   Current value: {from_number}")
        errors.append(f"   Should be like: +15551234567")
    elif ' ' in from_number or '-' in from_number or '(' in from_number:
        errors.append(f"❌ FROM_NUMBER cannot contain spaces, dashes, or parentheses")
        errors.append(f"   Current value: {from_number}")
        errors.append(f"   Should be like: +15551234567")
    elif from_number == '+1234567890' or from_number == '+15551234567':
        errors.append("⚠️  FROM_NUMBER appears to be a placeholder/example number")
        errors.append(f"   Current value: {from_number}")
        errors.append(f"   Replace with your actual Retell phone number")
    
    if errors:
        print()
        print("="*60)
        print("  CONFIGURATION ERRORS")
        print("="*60)
        for error in errors:
            print(error)
        print()
        print("Please fix these errors in config.env and restart.")
        print("="*60)
        print()
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("✅ Configuration validated")
    print(f"   Using FROM_NUMBER: {os.environ.get('FROM_NUMBER')}")
    print(f"   Using AGENT_ID: {os.environ.get('RETELL_AGENT_ID')}")


def find_free_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    return None

def open_browser(port, delay=1.5):
    """Open browser after a short delay"""
    time.sleep(delay)
    url = f'http://127.0.0.1:{port}'
    print(f"\n🌐 Opening browser to: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠️  Could not auto-open browser: {e}")
        print(f"Please manually open: {url}")


def main():
    """Main entry point for the standalone application"""
    print("="*60)
    print("  AI Rescheduling Agent - Standalone Edition")
    print("  HIPAA Compliant - Runs Fully Local")
    print("="*60)
    print()
    
    # CRITICAL: Setup environment BEFORE importing app
    # This ensures app.py can read the environment variables
    setup_environment()
    print()
    
    # NOW import the Flask app (after environment is set)
    sys.path.insert(0, str(BASE_DIR))
    from app import app
    
    # Find available port
    port = find_free_port()
    if not port:
        print("❌ ERROR: Could not find an available port!")
        print("   Ports 5000-5010 are all in use.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print(f"🔒 Starting local server on port {port}")
    print(f"   Binding to: 127.0.0.1 (localhost only)")
    print(f"   Security: No external access - HIPAA compliant")
    print()
    
    # Set Flask template and static folders
    app.template_folder = str(TEMPLATE_DIR)
    app.static_folder = str(STATIC_DIR)
    
    # Start browser in separate thread
    browser_thread = threading.Thread(target=open_browser, args=(port,), daemon=True)
    browser_thread.start()
    
    # Start Flask server
    print(f"✅ Server starting...")
    print(f"   URL: http://127.0.0.1:{port}")
    print()
    print("="*60)
    print("  SERVER RUNNING")
    print("="*60)
    print()
    print("📱 The application will open in your default browser")
    print("🔒 All data stays on your local machine")
    print("⚠️  Close this window to stop the server")
    print()
    print("="*60)
    print()
    
    try:
        # Run Flask - bind to localhost only for HIPAA compliance
        app.run(
            host='127.0.0.1',  # CRITICAL: localhost only
            port=port,
            debug=False,  # No debug in production
            use_reloader=False,  # Don't reload (breaks PyInstaller)
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == '__main__':
    main()
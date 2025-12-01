#!/usr/bin/env python3
"""
Test script to debug PRONOTE authentication issues
"""

import sys
import os
sys.path.append('backend')

from backend.pronote_client import PronoteClient

def test_pronote_connection(url, username, password, ent=None):
    """Test PRONOTE connection with detailed debugging"""
    print(f"\n🔍 Testing connection to: {url}")
    print(f"👤 Username: {username}")
    print(f"🔑 Password: {'*' * len(password)}")
    if ent:
        print(f"🏫 ENT: {ent}")
    
    try:
        client = PronoteClient(url, username, password, ent)
        
        print("\n📡 Attempting login...")
        success = client.login()
        
        if success:
            print("✅ Login successful!")
            
            # Try to get student info
            try:
                info = client.get_student_info()
                print(f"👨‍🎓 Student: {info.get('name', 'Unknown')}")
                print(f"🏫 School: {info.get('establishment', 'Unknown')}")
                print(f"📚 Class: {info.get('class', 'Unknown')}")
            except Exception as e:
                print(f"⚠️ Could not get student info: {e}")
            
            # Try to get periods
            try:
                periods = client.get_periods()
                print(f"📅 Periods: {len(periods)} found")
                for period in periods[:3]:  # Show first 3
                    print(f"   - {period.get('name', 'Unknown')}")
            except Exception as e:
                print(f"⚠️ Could not get periods: {e}")
            
            # Try to get grades
            try:
                grades = client.get_grades()
                print(f"📊 Grades: {len(grades)} found")
            except Exception as e:
                print(f"⚠️ Could not get grades: {e}")
            
            return True
        else:
            print("❌ Login failed")
            return False
            
    except Exception as e:
        print(f"💥 Connection error: {e}")
        return False

def main():
    """Interactive test function"""
    print("🧪 PRONOTE Authentication Test")
    print("=" * 40)
    
    # Test with demo credentials first
    print("\n1. Testing with demo credentials...")
    demo_success = test_pronote_connection(
        "https://demo.index-education.net/pronote/eleve.html",
        "demonstration",
        "pronotevs"
    )
    
    if not demo_success:
        print("\n⚠️ Demo connection failed. This might indicate a network issue.")
    
    # Interactive test
    print("\n2. Test with your own credentials...")
    print("Enter your PRONOTE details (or press Enter to skip):")
    
    url = input("PRONOTE URL: ").strip()
    if not url:
        print("Skipping custom test.")
        return
    
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    ent = input("ENT (optional): ").strip() or None
    
    if username and password:
        test_pronote_connection(url, username, password, ent)
    else:
        print("Missing credentials, skipping test.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple test script to verify the PRONOTE Grade Analyzer API
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_schools_endpoints():
    """Test the schools database endpoints"""
    try:
        # Test regions
        response = requests.get('http://127.0.0.1:5000/api/schools/regions', timeout=5)
        print(f"Regions: {response.status_code} - {len(response.json())} regions")
        
        # Test demo school
        response = requests.get('http://127.0.0.1:5000/api/schools/search?q=demo', timeout=5)
        print(f"Demo search: {response.status_code} - {len(response.json())} results")
        
        return True
    except Exception as e:
        print(f"Schools endpoints failed: {e}")
        return False

def test_demo_login():
    """Test login with demo credentials"""
    try:
        login_data = {
            "url": "https://demo.index-education.net/pronote/eleve.html",
            "username": "demonstration",
            "password": "pronotevs"
        }
        
        response = requests.post('http://127.0.0.1:5000/api/auth/login', 
                               json=login_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Demo login successful: {data['student']['name']}")
            return data['token']
        else:
            print(f"Demo login failed: {response.status_code} - {response.json()}")
            return None
            
    except Exception as e:
        print(f"Demo login error: {e}")
        return None

def test_data_endpoints(token):
    """Test data retrieval endpoints"""
    if not token:
        print("No token available for data testing")
        return False
        
    headers = {'Authorization': token}
    
    try:
        # Test student info
        response = requests.get('http://127.0.0.1:5000/api/student/info', 
                              headers=headers, timeout=10)
        print(f"Student info: {response.status_code}")
        
        # Test periods
        response = requests.get('http://127.0.0.1:5000/api/periods', 
                              headers=headers, timeout=10)
        print(f"Periods: {response.status_code} - {len(response.json())} periods")
        
        # Test grades
        response = requests.get('http://127.0.0.1:5000/api/grades', 
                              headers=headers, timeout=10)
        print(f"Grades: {response.status_code} - {len(response.json())} grades")
        
        # Test averages
        response = requests.get('http://127.0.0.1:5000/api/averages', 
                              headers=headers, timeout=10)
        print(f"Averages: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"Data endpoints failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== PRONOTE Grade Analyzer API Test ===")
    
    # Wait a moment for the server to be ready
    time.sleep(2)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print("❌ Server is not responding. Make sure the backend is running.")
        return
    
    # Test 2: Schools endpoints
    print("\n2. Testing schools endpoints...")
    schools_ok = test_schools_endpoints()
    
    # Test 3: Demo login
    print("\n3. Testing demo login...")
    token = test_demo_login()
    
    # Test 4: Data endpoints
    if token:
        print("\n4. Testing data endpoints...")
        data_ok = test_data_endpoints(token)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()

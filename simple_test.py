#!/usr/bin/env python3
"""
Simple test to verify PRONOTE connection
"""

import sys
sys.path.append('backend')

def test_basic_connection():
    """Test basic connection without authentication"""
    try:
        import pronotepy
        print(f"✅ pronotepy version: {pronotepy.__version__}")
        
        # Test import of our client
        from backend.pronote_client import PronoteClient
        print("✅ PronoteClient imported successfully")
        
        # Test client creation (without login)
        client = PronoteClient()
        print("✅ PronoteClient created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple PRONOTE Test")
    print("=" * 30)
    test_basic_connection()

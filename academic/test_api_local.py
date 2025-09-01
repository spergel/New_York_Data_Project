#!/usr/bin/env python3
"""
Test the Cloudflare Worker API locally
"""

import json
import requests
from datetime import datetime

def test_api_endpoints():
    """Test various API endpoints"""
    
    # Test health check
    print("🔍 Testing health check...")
    try:
        response = requests.get('http://localhost:8787/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Events count: {data['events_count']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test events endpoint
    print("\n🔍 Testing events endpoint...")
    try:
        response = requests.get('http://localhost:8787/api/events?limit=5')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Events endpoint working: {len(data['data']['events'])} events returned")
            print(f"   Total events: {data['data']['pagination']['total']}")
            if data['data']['events']:
                first_event = data['data']['events'][0]
                print(f"   Sample event: {first_event['name'][:50]}...")
        else:
            print(f"❌ Events endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Events endpoint error: {e}")
    
    # Test sources endpoint
    print("\n🔍 Testing sources endpoint...")
    try:
        response = requests.get('http://localhost:8787/api/sources')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sources endpoint working: {len(data['data'])} sources found")
            print(f"   Sample sources: {', '.join(data['data'][:5])}")
        else:
            print(f"❌ Sources endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Sources endpoint error: {e}")
    
    # Test stats endpoint
    print("\n🔍 Testing stats endpoint...")
    try:
        response = requests.get('http://localhost:8787/api/stats')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint working")
            print(f"   Total events: {data['data']['total_events']}")
            print(f"   Sources: {data['data']['sources']}")
            print(f"   Generated: {data['data']['generated_at']}")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
    
    # Test filtering
    print("\n🔍 Testing filtering...")
    try:
        response = requests.get('http://localhost:8787/api/events?source=columbia&limit=3')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Filtering working: {len(data['data']['events'])} Columbia events")
            if data['data']['events']:
                print(f"   Sample: {data['data']['events'][0]['name'][:50]}...")
        else:
            print(f"❌ Filtering failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Filtering error: {e}")

if __name__ == "__main__":
    print("🧪 Testing NYC Academic Events API")
    print("=" * 50)
    print("Note: Make sure to run 'wrangler dev' in another terminal first")
    print("=" * 50)
    
    test_api_endpoints()

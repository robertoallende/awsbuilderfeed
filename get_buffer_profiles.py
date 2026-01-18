#!/usr/bin/env python3
"""Helper script to get Buffer profile IDs."""

import sys
from config import BUFFER_ACCESS_TOKEN
from src.twitter import get_buffer_profiles

if not BUFFER_ACCESS_TOKEN:
    print("❌ BUFFER_ACCESS_TOKEN not set in .env")
    print("\n1. Go to https://buffer.com/developers/apps")
    print("2. Create a new app")
    print("3. Copy the Access Token")
    print("4. Add to .env: BUFFER_ACCESS_TOKEN=your_token")
    sys.exit(1)

print("📋 Fetching Buffer profiles...")
try:
    profiles = get_buffer_profiles()
    
    print(f"\n✅ Found {len(profiles)} connected account(s):\n")
    
    for profile in profiles:
        service = profile.get('service', 'unknown')
        name = profile.get('formatted_username', 'N/A')
        profile_id = profile['id']
        
        print(f"  {service.upper()}: @{name}")
        print(f"  Profile ID: {profile_id}")
        print(f"  Add to .env: BUFFER_PROFILE_ID={profile_id}")
        print()
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

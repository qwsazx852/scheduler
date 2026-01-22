import requests
import json

# Configuration
API_URL = "http://localhost:8000/generate"

# Sample Data (Mocking what n8n would send from Google Sheets/Form)
payload = {
    "year": 2026,
    "month": 2,
    "employees": [
        {"name": "Alice", "roles": ["Manager"], "allowed_shifts": ["Morning", "Evening"], "available_weekdays": [0,1,2,3,4]},
        {"name": "Bob", "roles": ["Staff"], "allowed_shifts": ["Morning"], "available_weekdays": [0,1,2,3,4,5,6]},
        {"name": "Charlie", "roles": ["Staff"], "allowed_shifts": ["Evening"], "available_weekdays": [5,6]}
    ],
    "shifts": {
        "Morning": {"time": "08:00-16:00", "required_people": 1, "enforce_headcount": True},
        "Evening": {"time": "16:00-00:00", "required_people": 1, "enforce_headcount": True}
    },
    "coverage_rules": [
        {"time_range": "10:00-14:00", "min_people": 2, "required_role": "Manager"} # Test rule
    ],
    "daily_limits": {
        "max_staff_per_day": 5,
        "enforce_limit": True
    }
}

print(f"📡 Sending request to {API_URL}...")
try:
    response = requests.post(API_URL, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Success! Received Schedule:")
        
        # Show first few entries of flat schedule
        flat = data.get("schedule_flat", [])
        print(f"Total assignments: {len(flat)}")
        for item in flat[:5]:
            print(f" - {item['date']} [{item['shift']}]: {item['person']}")
        if len(flat) > 5: print(" ... (more)")
        
        # Show logs
        logs = data.get("logs", [])
        if logs:
            print("\n⚠️ Scheduler Implementation Logs:")
            for log in logs[:3]:
                print(f" - {log}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ Could not connect to API.")
    print("Make sure you are running 'python api_scheduler.py' in another terminal!")

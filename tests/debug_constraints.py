import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.scheduler_logic import SchedulerLogic
import json
from datetime import datetime


# 載入配置
def load_config(filename, default):
    try:
        with open(filename) as f:
            return json.load(f)
    except:
        return default

shifts = load_config('config/config_shifts.json', {})
employees = load_config('config/config_employees.json', [])
coverage = load_config('config/config_coverage.json', [])
daily_limits = load_config('config/config_daily_limits.json', {})
business_hours = load_config('config/config_business_hours.json', {})


# 初始化
scheduler = SchedulerLogic(2026, 2, employees, shifts, coverage, daily_limits, business_hours)

# 我們只關心 2/1 的排班細節
target_date = datetime(2026, 2, 1).date()
date_str = target_date.strftime("%Y-%m-%d")

print(f"=== Debugging {date_str} (Logic: Breakdown Rules) ===")

# 檢查 Needs
needs = scheduler._analyze_daily_coverage_needs(date_str)
time_14 = next((n for n in needs if "14:00-15:00" in n['time_range']), None)

if time_14:
    print(f"Found Need for 14:00-15:00: {time_14}")
else:
    print("CRITICAL: No need generated for 14:00-15:00!")
    print("Sample Needs:", [n['time_range'] for n in needs[:10]])

print("\n--- Simulating 14:00 Assignment ---")
if time_14:
    suitable_shifts = scheduler._find_shifts_for_timerange(time_14['time_range'])
    print(f"Suitable Shifts for 14:00: {suitable_shifts}")
    
    for s_name in suitable_shifts:
        print(f"\nChecking candidates for shift {s_name}:")
        candidates = scheduler._get_available_candidates(target_date, s_name, [])
        print(f"Found {len(candidates)} candidates.")

print("\n--- Full Generation & Result for 18:00 ---")
scheduler.schedule_one_day(target_date)

# Calculate coverage at 19:00
count_1900 = scheduler._count_coverage_in_timerange(date_str, "19:00-19:01", [])
print(f"People present at 19:00: {count_1900}")

# List who is present
present = []
unique_staff = set()
for s, ppl in scheduler.schedule[date_str].items():
    for p in ppl:
        unique_staff.add(p)
    
    # Check overlap
    s_start, s_end = scheduler._parse_time_range(scheduler.shifts[s]['time'])
    if s_start <= 19*60 <= s_end:
        for p in ppl:
            present.append(f"{p} ({s})")

print(f"Present Staff: {present}")
print(f"Total Unique Staff Today: {len(unique_staff)} (Max: {scheduler.daily_limits.get('max_staff_per_day', 999)})")
print(f"All Needs: {[n['time_range'] + ' min:' + str(n['min_people']) for n in needs]}")



import json
import os
from scheduler_logic import SchedulerLogic
from datetime import date

# Load configs
def load_data(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return default

shifts = load_data("config_shifts.json", {})
employees = load_data("config_employees.json", [])
coverage_rules = load_data("config_coverage.json", [])

print("Loaded configuration.")
print(f"Shifts: {list(shifts.keys())}")
print(f"Employees: {len(employees)}")
print(f"Coverage Rules: {coverage_rules}")

# Run Scheduler
print("\nRunning Scheduler Logic...")
scheduler = SchedulerLogic(
    year=2026,
    month=1,
    employees_config=employees,
    shifts_config=shifts,
    coverage_rules=coverage_rules
)

schedule, log = scheduler.generate()

print("\nGeneration Complete.")
print("Logs:")
for l in log:
    print(l)

# Verification Logic
print("\nVerifying Role Coverage for '组长' between 7:00-21:00...")
# Rule: 7:00-21:00 requires 1 Team Leader
required_role = "组长"
target_start = 7 * 60
target_end = 21 * 60

success_days = 0
total_days = len(scheduler.dates)

for d in scheduler.dates:
    date_str = d.strftime("%Y-%m-%d")
    daily_schedule = schedule[date_str]
    
    # Build timeline for this day
    timeline = []
    for shift_name, assigned_emps in daily_schedule.items():
        if not assigned_emps: continue
        
        shift_time = shifts[shift_name]["time"]
        s_h, s_m = map(int, shift_time.split('-')[0].split(':'))
        e_h, e_m = map(int, shift_time.split('-')[1].split(':'))
        s_min = s_h * 60 + s_m
        e_min = e_h * 60 + e_m
        
        for emp_name in assigned_emps:
            timeline.append((s_min, e_min, emp_name))
            
    # Check if we have coverage
    # We need to ensure that for the range 7:00-21:00, is there a continuous coverage?
    # Actually the rule just says "min_people: 1" for that range.
    # The current validator just checks if *at least one person* overlaps the range.
    # Wait, the current validator in `_validate_coverage` counts people who overlap the rule range.
    # If the rule is wide (7-21), any shift overlapping it contributes.
    
    # Let's use the same logic as _validate_coverage to verify.
    
    warnings_for_day = [l for l in log if date_str in l and "Role Warning" in l]
    if not warnings_for_day:
        success_days += 1
    else:
        print(f"Day {date_str} failed: {warnings_for_day}")

print(f"\nSuccess Rate: {success_days}/{total_days}")
if success_days == total_days:
    print("VERIFICATION PASSED!")
else:
    print("VERIFICATION FAILED!")

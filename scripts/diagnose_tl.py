
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

# Diagnostic: Check how many Team Leaders are assigned per shift
print("\n--- Team Leader Distribution Analysis ---")
tl_names = [e['name'] for e in employees if "组长" in e.get('roles', [])]
print(f"Team Leaders: {tl_names}")

print("\n--- Checking Coverage (Early: 7-12, Mid: 14-17, Late: 18-21) ---")
for d in scheduler.dates[:7]: # Check first 7 days
    date_str = d.strftime("%Y-%m-%d")
    print(f"\nDate: {date_str}")
    
    daily_schedule = schedule[date_str]
    
    # Helper to count TLs in a time range
    def count_tls_in_range(start_m, end_m):
        count = 0
        for s_name, assigned in daily_schedule.items():
            if not assigned: continue
            s_time = shifts[s_name]["time"]
            try:
                s_h, s_m_ = map(int, s_time.split('-')[0].split(':'))
                e_h, e_m_ = map(int, s_time.split('-')[1].split(':'))
                s_min = s_h * 60 + s_m_
                e_min = e_h * 60 + e_m_
                
                if s_min < end_m and e_min > start_m:
                    count += sum(1 for emp in assigned if emp in tl_names)
            except: pass
        return count
        
    early = count_tls_in_range(7*60, 12*60)
    mid = count_tls_in_range(14*60, 17*60)
    late = count_tls_in_range(18*60, 21*60)
    
    print(f"  Early (7-12) : {early} TLs (Need >=1)")
    print(f"  Mid   (14-17): {mid} TLs (Need >=1)")
    print(f"  Late  (18-21): {late} TLs (Need >=1)")
    
    if early == 0 or mid == 0 or late == 0:
         print(f"  ⚠️  COVERAGE GAP DETECTED")
         
    # Check shift assignments
    day_workers = set()
    for s_name in ['A1', 'D', 'B', 'C', 'E', 'F', 'B-']:
         assigned = daily_schedule.get(s_name, [])
         day_workers.update(assigned)
         tls = [n for n in assigned if n in tl_names]
         
         if len(tls) > 1:
             print(f"  🚨 DUPLICATE TLs in {s_name}: {tls}")
         else:
             pass 
             # print(f"    {s_name}: {tls}")
             
    print(f"  Total Workers Today: {len(day_workers)}/15")

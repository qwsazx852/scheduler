from src.scheduler_logic import SchedulerLogic
import logging

# Mock Data
shifts = {
    "D": {"time": "06:20-12:05"},
    "A1": {"time": "07:00-14:00"},
    "A2C": {"time": "10:00-12:00,17:00-21:30"}
}
employees = [{"name": "Test", "roles": [], "allowed_shifts": ["D", "A1", "A2C"]}]
coverage_rules = [
    {"time_range": "06:20-12:00", "min_people": 1, "priority": "HIGH"},
    {"time_range": "10:00-14:00", "min_people": 1, "priority": "HIGH"},
    {"time_range": "17:00-21:00", "min_people": 1, "priority": "HIGH"}
]

def test_find_d():
    s = SchedulerLogic(2026, 1, employees, shifts, coverage_rules)
    need_range = "06:20-12:00"
    suitable = s._find_shifts_for_timerange(need_range)
    print(f"Suitable shifts for {need_range}: {suitable}")
    
    # Check manual
    d_segs = s._parse_shift_segments("06:20-12:05")
    print(f"D Segments: {d_segs}")
    need_s, need_e = s._parse_time_range(need_range)
    print(f"Need: {need_s}-{need_e}")
    # Overlap?
    for start, end in d_segs:
        print(f"Check {start}-{end} vs {need_s}-{need_e}")
        if start < need_e and end > need_s:
            print("Overlap!")

def test_utility():
    s = SchedulerLogic(2026, 1, employees, shifts, coverage_rules)
    needs = [
        {'time_range': '06:20-12:00', 'priority': 'HIGH'},
        {'time_range': '10:00-14:00', 'priority': 'HIGH'},
        {'time_range': '17:00-21:00', 'priority': 'HIGH'}
    ]
    
    score_d = s._calculate_shift_utility("D", needs)
    score_a1 = s._calculate_shift_utility("A1", needs)
    score_a2c = s._calculate_shift_utility("A2C", needs)
    
    print(f"Score D: {score_d}")
    print(f"Score A1: {score_a1}")
    print(f"Score A2C: {score_a2c}")

if __name__ == "__main__":
    print("--- Testing Find Shifts ---")
    test_find_d()
    print("\n--- Testing Utility ---")
    test_utility()

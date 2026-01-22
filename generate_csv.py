import csv
from datetime import date

# Configuration
YEAR = 2026
MONTH = 1
EMPLOYEE_NAME = "陈美娜"
OUTPUT_FILE = "schedule_2026_01.csv"

# Shift Code Mapping
SHIFT_RULES = {
    "A1": "07:00 - 14:00",
    "D": "06:20 - 12:05",
    "D1": "06:20 - 12:05",
    "A2": "07:00 - 10:00",
    "C": "16:50 - 21:35",
    "B": "11:50 - 17:05",
    "B.": "11:50 - 17:05",
    "B1": "11:50 - 17:05",
    "E": "16:50 - 21:00",
    "F": "10:00 - 17:00",
    "A2c": "07:00-10:00, 12:50-21:35",
    "B-": "11:50 - 18:00",
    "X": "休假",
    "休": "休假"
}

# Transcription (Row 1 to 31)
raw_schedule = {
    1: "B1", 2: "X", 3: "B1", 4: "B", 5: "A1",
    6: "B1", 7: "B", 8: "A1", 9: "X", 10: "X",
    11: "B1", 12: "B", 13: "D1", 14: "D", 15: "X",
    16: "X", 17: "B1", 18: "B1", 19: "X", 20: "D1",
    21: "A1", 22: "D1", 23: "A1", 24: "B1", 25: "E",
    26: "", 27: "", 28: "", 29: "", 30: "", 31: ""
}

# Write CSV with BOM for Excel compatibility (utf-8-sig)
with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile)
    # Header
    writer.writerow(['日期', '员工姓名', '代号', '时间'])
    
    # Rows
    for day in range(1, 32):
        try:
            current_date = date(YEAR, MONTH, day)
            date_str = current_date.strftime("%Y/%m/%d")
            
            shift_code = raw_schedule.get(day, "").strip()
            time_range = SHIFT_RULES.get(shift_code, shift_code)
            
            if not shift_code:
                time_range = ""
                
            writer.writerow([date_str, EMPLOYEE_NAME, shift_code, time_range])
            
        except ValueError:
            pass # Skip invalid dates

print(f"Success: {OUTPUT_FILE}")

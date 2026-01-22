import pandas as pd
from datetime import date, timedelta

# Configuration
YEAR = 2026
MONTH = 1
EMPLOYEE_NAME = "陈美娜"

# Shift Code Mapping (Based on user input)
# Note: D1 is mapped to D, B1 is mapped to B based on similarity/assumption if not explicitly defined.
SHIFT_RULES = {
    "A1": "07:00 - 14:00",
    "D": "06:20 - 12:05",
    "D1": "06:20 - 12:05", # Assuming D1 = D
    "A2": "07:00 - 10:00",
    "C": "16:50 - 21:35",
    "B": "11:50 - 17:05",
    "B.": "11:50 - 17:05",
    "B1": "11:50 - 17:05", # Assuming B1 = B
    "E": "16:50 - 21:00",
    "F": "10:00 - 17:00",
    "F.": "10:00 - 17:00",
    "A2c": "07:00-10:00, 12:50-21:35",
    "B-": "11:50 - 18:00",
    "X": "休假",
    "休": "休假"
}

# Manual Transcription from Image (Rows 1-31)
# Column: Chen Meina (3rd column)
# Please verify the "Unknown" or inferred values.
raw_schedule = {
    1: "B1",
    2: "X",
    3: "B1",
    4: "B",
    5: "A1",
    6: "B1",
    7: "B",
    8: "A1",
    9: "X",
    10: "X",
    11: "B1",
    12: "B",
    13: "D1", # User only gave D, assuming D1 = D
    14: "D",
    15: "X",
    16: "X",
    17: "B1",
    18: "B1",
    19: "X",
    20: "D1",
    21: "A1",
    22: "D1",
    23: "A1",
    24: "B1",
    25: "E", # Looks like E
    26: "", # Empty or Rest? Assuming empty for now
    27: "",
    28: "",
    29: "",
    30: "",
    31: ""
}

data = []

# Generate Data Rows
for day in range(1, 32):
    try:
        current_date = date(YEAR, MONTH, day)
        date_str = current_date.strftime("%Y/%m/%d")
        
        shift_code = raw_schedule.get(day, "").strip()
        time_range = SHIFT_RULES.get(shift_code, shift_code) # Use code itself if no map found
        
        if shift_code == "":
            time_range = "" # Empty
            
        data.append({
            "日期": date_str,
            "员工姓名": EMPLOYEE_NAME,
            "代号": shift_code,
            "时间": time_range
        })
    except ValueError:
        # Handle months with < 31 days (not the case for Jan, but good practice)
        pass

# Create DataFrame and Excel
df = pd.DataFrame(data)
output_file = "schedule_2026_01.xlsx"

# Write to Excel
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    
    # Simple formatting (adjust column width)
    worksheet = writer.sheets["Sheet1"]
    worksheet.column_dimensions['A'].width = 15
    worksheet.column_dimensions['B'].width = 10
    worksheet.column_dimensions['C'].width = 10
    worksheet.column_dimensions['D'].width = 30

print(f"Excel file created: {output_file}")

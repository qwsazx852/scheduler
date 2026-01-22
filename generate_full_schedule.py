import csv
from datetime import date
import os

OUTPUT_FILE = "full_schedule_2026_01.csv"
YEAR = 2026
MONTH = 1

# Columns based on the image
HEADERS = [
    "日期", "星期", 
    "黃素珠", "賴桂蘭", "陳美娜", "吳誼婷", "楊依如", "陳彥銘",
    "黃榮壹", "吳靜蕙", "林群皓", "陳怡芯",
    "李巧如", "鄭靜慧", "陳昱勳", "林宏諺"
]

# Transcription for "黃素珠" (Column 1)
ms_huang_data = {
    1: "A1", 2: "D", 3: "X", 4: "B1", 5: "B1", 
    6: "B1", 7: "休", 8: "X", 9: "D", 10: "D1", 
    11: "A1", 12: "B1", 13: "X", 14: "D1", 15: "D1", 
    16: "B1", 17: "B1", 18: "休", 19: "D1", 20: "D", 
    21: "X", 22: "B1", 23: "B1", 24: "休", 25: "B1", 
    26: "", 27: "", 28: "", 29: "", 30: "", 31: ""
}

WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]

try:
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(HEADERS)
        
        for day in range(1, 32):
            try:
                curr_date = date(YEAR, MONTH, day)
                date_str = curr_date.strftime("%Y/%m/%d")
                weekday_str = WEEKDAYS[curr_date.weekday()]
                
                row_data = [""] * 14
                row_data[0] = ms_huang_data.get(day, "") # Fill Huang Suzhu
                
                writer.writerow([date_str, weekday_str] + row_data)
            except ValueError:
                pass
    print(f"Successfully created {os.path.abspath(OUTPUT_FILE)}")
except Exception as e:
    print(f"Error creating file: {e}")

import pandas as pd

# 模擬 A2C 班別資料
shift_info = {"time": "7:00-10:00,16:50-21:35"}
emp_list = ["測試員工A"]
selected_date_str = "2026-01-23"

gantt_data = []
time_str = shift_info["time"]

# 解析邏輯（與 app_scheduler.py 相同）
parts = time_str.split(',')
print(f"時間字串: {time_str}")
print(f"分段數量: {len(parts)}")
print(f"分段內容: {parts}")

for part_idx, part in enumerate(parts):
    try:
        part = part.strip()
        print(f"\n處理時段 {part_idx+1}: '{part}'")
        
        if '-' not in part:
            print(f"  ❌ 錯誤: 缺少 '-'")
            continue
            
        start_str, end_str = part.split('-', 1)
        start_str = start_str.strip()
        end_str = end_str.strip()
        
        print(f"  開始: {start_str}, 結束: {end_str}")
        
        if ':' not in start_str or ':' not in end_str:
            print(f"  ❌ 錯誤: 時間格式不正確")
            continue
        
        for emp_name in emp_list:
            shift_display = "A2C" if len(parts) == 1 else f"A2C-{part_idx+1}"
            
            data = {
                "Person": emp_name,
                "Shift": shift_display,
                "Start": f"{selected_date_str}T{start_str}:00",
                "End": f"{selected_date_str}T{end_str}:00",
            }
            gantt_data.append(data)
            print(f"  ✅ 成功: {data}")
            
    except Exception as e:
        print(f"  ❌ 例外: {str(e)}")

print(f"\n總共生成 {len(gantt_data)} 筆資料")
if gantt_data:
    df = pd.DataFrame(gantt_data)
    print("\n甘特圖資料:")
    print(df)

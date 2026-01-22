from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
import json
from datetime import date

# 引入排班核心邏輯
try:
    from scheduler_logic import SchedulerLogic
except ImportError:
    raise ImportError("scheduler_logic.py not found. Please ensure it is in the same directory.")

app = FastAPI(title="Scheduler API Microservice")

# --- 輸入資料驗證模型 (Input Validation Models) ---
class Employee(BaseModel):
    name: str # 員工姓名
    available_weekdays: List[int] = [0,1,2,3,4,5,6] # 可工作日 (0=週一)
    allowed_shifts: List[str] = [] # 可排班別 ["A", "B", "C"]
    roles: List[str] = ["一般員工"] # 角色 ["組長", "一般員工"]

class ShiftInfo(BaseModel):
    time: str # 時間範圍 "HH:MM-HH:MM"
    required_people: int = 2 # 該班需要人數
    enforce_headcount: bool = True # 是否強制滿足人數

class CoverageRule(BaseModel):
    time_range: str # 時間範圍
    min_people: int # 最少人數
    max_people: Optional[int] = None # (選填) 最多人數 - 避免人力過剩
    required_roles: List[str] = [] # (選填) 必要角色列表 (例如: ["組長", "資深員工"])

class DailyLimit(BaseModel):
    max_staff_per_day: int = 8 # 每日最大上班員工數
    enforce_limit: bool = True

class BusinessHours(BaseModel):
    start: str = "07:00" # 營業開始時間
    end: str = "21:30" # 營業結束時間
    enforce_coverage: bool = True # 是否檢查覆蓋

class ScheduleRequest(BaseModel):
    """
    /generate 接口的請求格式
    """
    year: int
    month: int
    employees: List[Employee]
    shifts: Dict[str, ShiftInfo]
    coverage_rules: List[CoverageRule] = []
    daily_limits: DailyLimit = DailyLimit()
    business_hours: BusinessHours = BusinessHours()

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2026,
                "month": 1,
                "employees": [{"name": "TestEmp", "roles": ["組長"], "allowed_shifts": ["A"]}],
                "shifts": {"A": {"time": "08:00-16:00", "required_people": 1}},
                "coverage_rules": [],
                "daily_limits": {"max_staff_per_day": 5}
            }
        }

# --- API 端點 (Endpoints) ---

@app.get("/")
def health_check():
    """健康檢查端點，確認伺服器活著"""
    return {"status": "running", "service": "Scheduler API"}

@app.post("/generate")
def generate_schedule(req: ScheduleRequest):
    """
    主要排班接口：接收完整設定，回傳排班結果
    """
    try:
        # 轉換為舊版 dict 格式傳給 SchedulerLogic
        employees_config = [e.dict() for e in req.employees]
        shifts_config = {k: v.dict() for k, v in req.shifts.items()}
        coverage_rules = [c.dict() for c in req.coverage_rules]
        daily_limits = req.daily_limits.dict()
        business_hours = req.business_hours.dict()

        # 初始化排班引擎
        scheduler = SchedulerLogic(
            year=req.year,
            month=req.month,
            employees_config=employees_config,
            shifts_config=shifts_config,
            coverage_rules=coverage_rules,
            daily_limits=daily_limits,
            business_hours=business_hours
        )

        # 執行排班
        schedule, logs = scheduler.generate()

        # 格式化輸出
        # schedule_flat 是為了方便寫入 CSV 或 Google Sheet
        flat_list = []
        for date_str, shifts in schedule.items():
            for shift_name, people in shifts.items():
                for person in people:
                    flat_list.append({
                        "date": date_str,
                        "shift": shift_name,
                        "person": person
                    })

        # 生成矩陣視圖 (包含休假 X)
        matrix_list = []
        if hasattr(scheduler, 'get_employee_schedule_dataframe'):
            df_emp = scheduler.get_employee_schedule_dataframe()
            # 轉為 list of dict
            matrix_list = df_emp.to_dict(orient='records')

        return {
            "status": "success",
            "schedule_raw": schedule, # 原始結構
            "schedule_flat": flat_list, # 扁平化結構 (容易處理)
            "schedule_matrix": matrix_list, # 員工矩陣視圖 (包含 X)
            "logs": logs # 排班過程的警示與日誌
        }


    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class ChangeRequest(BaseModel):
    """
    /validate 接口的請求格式
    用於讓 LLM 或前端驗證某個「換班/排班」動作是否合法
    """
    action: str # 動作: ASSIGN (指派), REMOVE (移除), SWAP (交換)
    date_str: str # 日期 "YYYY-MM-DD"
    shift: str # 班別
    person: str # 主要操作對象
    target_person: Optional[str] = None # 交換對象 (只在 SWAP 使用)
    current_schedule: Dict[str, Dict[str, List[str]]] # 當前的完整班表狀態 (Context)
    employees: List[Employee] # 員工設定 (需要知道規則)
    daily_limits: DailyLimit = DailyLimit()

@app.post("/validate")
def validate_change(req: ChangeRequest):
    """
    驗證某個排班更動是否合規 (不執行更改，只檢查)
    """
    try:
        # 內部檢查 helper func
        def check_person_constraints(name: str, target_date_str: str, schedule_state: dict, emp_config: dict):
            # 1. 存在性檢查
            if name not in emp_config:
                return False, f"Employee '{name}' not found in configuration."
            
            emp = emp_config[name]
            from datetime import datetime
            t_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
            
            # 2. 星期幾限制
            if t_date.weekday() not in emp['available_weekdays']:
                return False, f"Warning: {name} is usually not available on weekday {t_date.weekday()}."

            # 3. 每日限制 (檢查當日是否已排班)
            assigned_today = set()
            if target_date_str in schedule_state:
                for s, ppl in schedule_state[target_date_str].items():
                    assigned_today.update(ppl)
            
            # 4. 連續上班天數檢查 (往回追溯 6 天)
            consecutive = 0
            check_date = t_date
            import datetime as dt
            
            for i in range(1, 8):
                check_date = t_date - dt.timedelta(days=i)
                check_str = check_date.strftime("%Y-%m-%d")
                worked = False
                if check_str in schedule_state:
                    for ppl in schedule_state[check_str].values():
                        if name in ppl:
                            worked = True
                            break
                if worked:
                    consecutive += 1
                else:
                    break
            
            if consecutive >= 6:
                return False, f"Violation: {name} has already worked {consecutive} consecutive days before {target_date_str}."

            return True, "OK"

        # 建立快速查找表
        emp_map = {e.name: e.dict() for e in req.employees}
        
        # 針對不同動作進行檢查
        if req.action == "ASSIGN":
            ok, msg = check_person_constraints(req.person, req.date_str, req.current_schedule, emp_map)
            if not ok:
                return {"valid": False, "message": msg}
            return {"valid": True, "message": f"Assigning {req.person} is valid."}

        elif req.action == "REMOVE":
            return {"valid": True, "message": f"Removing {req.person} is valid."}

        elif req.action == "SWAP":
            if not req.target_person:
                return {"valid": False, "message": "Target person required for SWAP."}
            
            # 驗證被換上來的人 (Target Person) 是否能上這個班
            ok, msg = check_person_constraints(req.target_person, req.date_str, req.current_schedule, emp_map)
            if not ok:
                return {"valid": False, "message": f"Swap rejected: {msg}"}
            
            return {"valid": True, "message": f"Swap between {req.person} and {req.target_person} is valid."}

        return {"valid": False, "message": f"Unknown action: {req.action}"}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/simulate")
def simulate_schedule():
    """
    模擬端點：讀取伺服器端的設定檔，直接產生下個月班表。
    用於測試 n8n 接收資料是否正常。
    """
    try:
        def load_json(path, default):
            try:
                import os
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return json.load(f)
            except:
                pass
            return default

        # 預設設定
        default_shifts = {
            "A": {"time": "07:00-14:00", "required_people": 2, "enforce_headcount": True}, 
            "B": {"time": "14:00-22:00", "required_people": 2, "enforce_headcount": True}
        }
        default_employees = [
            {"name": "Emp1", "available_weekdays": [0,1,2,3,4], "allowed_shifts": ["A", "B"], "roles": ["一般員工"]},
            {"name": "Emp2", "available_weekdays": [5,6], "allowed_shifts": ["A"], "roles": ["組長"]}
        ]
        
        # 讀取本地設定檔 (與 Streamlit App 共用)
        shifts_config = load_json("config_shifts.json", default_shifts)
        employees_config = load_json("config_employees.json", default_employees)
        coverage_rules = load_json("config_coverage.json", [{"time_range": "10:00-14:00", "min_people": 3}])
        daily_limits = load_json("config_daily_limits.json", {"max_staff_per_day": 8, "enforce_limit": True})
        business_hours = load_json("config_business_hours.json", {"start": "07:00", "end": "21:30", "enforce_coverage": True})

        # 設定排班月份 (下個月)
        today = date.today()
        year = today.year if today.month < 12 else today.year + 1
        month = today.month + 1 if today.month < 12 else 1
        
        # 執行排班
        scheduler = SchedulerLogic(
            year=year,
            month=month,
            employees_config=employees_config,
            shifts_config=shifts_config,
            coverage_rules=coverage_rules,
            daily_limits=daily_limits,
            business_hours=business_hours
        )

        schedule, logs = scheduler.generate()

        # 扁平化結果
        flat_list = []
        for date_str, shifts in schedule.items():
            for shift_name, people in shifts.items():
                for person in people:
                    flat_list.append({
                        "date": date_str,
                        "shift": shift_name,
                        "person": person
                    })

        # 生成矩陣視圖 (包含休假 X)
        matrix_list = []
        if hasattr(scheduler, 'get_employee_schedule_dataframe'):
            df_emp = scheduler.get_employee_schedule_dataframe()
            # 轉為 list of dict
            matrix_list = df_emp.to_dict(orient='records')

        return {
            "status": "success",
            "source": "simulation_from_local_config (讀取本地模擬檔)",
            "year": year,
            "month": month,
            "schedule_flat": flat_list,
            "logs": logs
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # 啟動伺服器，Port 設定為 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

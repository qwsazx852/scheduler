import streamlit as st
import pandas as pd
import json
import os
from datetime import date
import altair as alt
import traceback
from scheduler_logic import SchedulerLogic

# Page Config
st.set_page_config(page_title="自订排班神器", layout="wide")

# Constants
SHIFT_FILE = "config/config_shifts.json"
EMP_FILE = "config/config_employees.json"

# --- Helper Functions for Persistence ---
def load_data(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return default

def save_data(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- Initialize Session State ---
if 'shifts' not in st.session_state:
    st.session_state.shifts = load_data(SHIFT_FILE, {
        "A": {"time": "07:00-14:00", "required_people": 2, "enforce_headcount": True}, 
        "B": {"time": "14:00-22:00", "required_people": 2, "enforce_headcount": True}
    })

if 'employees' not in st.session_state:
    default_employees = [
        {"name": "Emp1", "available_weekdays": [0,1,2,3,4], "allowed_shifts": ["A", "B"], "roles": ["一般员工"]},
        {"name": "Emp2", "available_weekdays": [5,6], "allowed_shifts": ["A"], "roles": ["组长"]}
    ]
    st.session_state.employees = load_data(EMP_FILE, default_employees)

if 'available_roles' not in st.session_state:
    # Define available roles in the system
    st.session_state.available_roles = load_data("config/config_roles.json", ["组长", "一般员工", "储备干部"])

if 'coverage_rules' not in st.session_state:
    # Coverage rules: time ranges that require minimum headcount regardless of shift
    # Format: [{"time_range": "10:00-14:00", "min_people": 3}]
    st.session_state.coverage_rules = load_data("config/config_coverage.json", [
        {"time_range": "10:00-14:00", "min_people": 3}
    ])

if 'daily_limits' not in st.session_state:
    # Daily staff limits: control maximum number of staff per day
    st.session_state.daily_limits = load_data("config/config_daily_limits.json", {
        "max_staff_per_day": 8,
        "enforce_limit": True
    })

if 'business_hours' not in st.session_state:
    # Business hours: operating hours that must have coverage
    st.session_state.business_hours = load_data("config/config_business_hours.json", {
        "start": "07:00",
        "end": "21:30",
        "enforce_coverage": True
    })

# --- Globals & Sidebar ---
with st.sidebar:
    st.header("⚙️ 系統設定")
    if st.button("⚠️ 重置系統 (Hard Reset)", type="primary", help="如果系統卡住或報錯，請點擊此處清除所有狀態並重新整理"):
        st.session_state.clear()
        st.rerun()

# --- Main App Logic Wrapped in Try-Except ---
try:


    # --- UI Layout ---
    st.title("📅 自订排班神器 (Custom Scheduler)")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "1. 班别设定", 
        "2. 人员设定", 
        "3. 时段覆盖规则", 
        "4. 每日人数限制",
        "5. 营业时段",
        "6. 智慧排班"
    ])

    # === Tab 1: Shift Settings ===
    with tab1:
        st.header("定义班别 (Shift Definitions)")
    
        # Add new shift
        with st.expander("➕ 新增班别"):
            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
            with col1:
                new_code = st.text_input("班别代码", key="new_shift_code", placeholder="例如: C")
            with col2:
                new_time = st.text_input("时间范围", key="new_shift_time", placeholder="例如: 16:00-22:00")
            with col3:
                new_enforce = st.checkbox("启用人数限制", value=True, key="new_shift_enforce")
            with col4:
                new_people = st.number_input("需要人数", min_value=1, value=2, key="new_shift_people", disabled=not new_enforce)
        
            if st.button("新增", key="add_shift_btn"):
                if new_code and new_time:
                    st.session_state.shifts[new_code] = {
                        "time": new_time,
                        "required_people": new_people,  # Always save the value
                        "enforce_headcount": new_enforce
                    }
                    save_data(SHIFT_FILE, st.session_state.shifts)
                    st.success(f"已新增班别 {new_code}")
                    st.rerun()
    
        # Edit existing shifts
        st.subheader("现有班别")
        for shift_code, shift_info in list(st.session_state.shifts.items()):
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns([1.5, 3, 2, 2, 1])
            
                with col1:
                    st.markdown(f"**{shift_code}**")
            
                with col2:
                    new_time = st.text_input(
                        "时间范围", 
                        value=shift_info["time"], 
                        key=f"time_{shift_code}",
                        label_visibility="collapsed"
                    )
            
                with col3:
                    enforce = st.checkbox(
                        "启用人数限制", 
                        value=shift_info.get("enforce_headcount", True),
                        key=f"enforce_{shift_code}",
                        help="勾选后才能设定需要人数"
                    )
            
                with col4:
                    people = st.number_input(
                        "需要人数", 
                        min_value=1, 
                        value=max(1, shift_info.get("required_people", 2)),
                        key=f"people_{shift_code}",
                        disabled=not enforce,
                        label_visibility="collapsed"
                    )
            
                with col5:
                    if st.button("🗑️", key=f"del_{shift_code}", help="删除此班别"):
                        del st.session_state.shifts[shift_code]
                        save_data(SHIFT_FILE, st.session_state.shifts)
                        st.rerun()
            
                # Update in session state
                st.session_state.shifts[shift_code] = {
                    "time": new_time,
                    "required_people": people,  # Always save the value, enforcement flag controls behavior
                    "enforce_headcount": enforce
                }
    
        if st.button("💾 储存所有班别设定", type="primary"):
            save_data(SHIFT_FILE, st.session_state.shifts)
            st.success("班别设定已储存！")

    # === Tab 2: Employee Settings ===
    with tab2:
        st.header("人员规则 (Employee Constraints)")
    
        # We use a more custom UI for checkboxes since data_editor doesn't support complex multi-selects deeply easily
    
        # 1. Add New Employee
        with st.expander("新增人员"):
            new_name = st.text_input("姓名")
            new_roles = st.multiselect("身份/角色", options=st.session_state.available_roles, default=["一般员工"])
            if st.button("新增", key="add_employee_btn"):
                if new_name:
                    st.session_state.employees.append({
                        "name": new_name,
                        "available_weekdays": [0,1,2,3,4,5,6],
                        "allowed_shifts": list(st.session_state.shifts.keys()),
                        "roles": new_roles
                    })
                    save_data(EMP_FILE, st.session_state.employees)
                    st.rerun()

        # 2. Edit Existing
        st.write("编辑下方人员规则：")
    
        for i, emp in enumerate(st.session_state.employees):
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
            
                with col1:
                    # Allow editing name
                    edited_name = st.text_input("姓名", value=emp['name'], key=f"edit_name_{i}")
                    if edited_name != emp['name']:
                        st.session_state.employees[i]['name'] = edited_name
                        # Auto-save when changed
                        # We don't verify across all employees for duplicates here for simplicity,
                        # but user should be careful.
                    
                    if st.button("删除", key=f"del_{i}"):
                        st.session_state.employees.pop(i)
                        save_data(EMP_FILE, st.session_state.employees)
                        st.rerun()
            
                with col2:
                    # Weekdays (0=Mon)
                    days_map = {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"}
                    selected_days = st.multiselect(
                        "可上班星期",
                        options=list(days_map.keys()),
                        format_func=lambda x: days_map[x],
                        default=emp.get('available_weekdays', []),
                        key=f"days_{i}"
                    )
                
                with col3:
                    # Allowed Shifts
                    shifts_list = list(st.session_state.shifts.keys())
                    selected_shifts = st.multiselect(
                        "可上班班别",
                        options=shifts_list,
                        default=[s for s in emp.get('allowed_shifts', []) if s in shifts_list],
                        key=f"shifts_{i}"
                    )
            
                with col4:
                    # Roles
                    selected_roles = st.multiselect(
                        "身份/角色",
                        options=st.session_state.available_roles,
                        default=emp.get('roles', ["一般员工"]),
                        key=f"roles_{i}",
                        help="例如：组长、一般员工"
                    )
            
                # Auto-Save Logic (Detect Changes)
                has_changed = False
                
                if st.session_state.employees[i]['available_weekdays'] != selected_days:
                     st.session_state.employees[i]['available_weekdays'] = selected_days
                     has_changed = True
                
                if st.session_state.employees[i]['allowed_shifts'] != selected_shifts:
                     st.session_state.employees[i]['allowed_shifts'] = selected_shifts
                     has_changed = True
                     
                if st.session_state.employees[i]['roles'] != selected_roles:
                     st.session_state.employees[i]['roles'] = selected_roles
                     has_changed = True
                
                if has_changed:
                    save_data(EMP_FILE, st.session_state.employees)
                    st.toast(f"已自動儲存 {emp['name']} 的設定變更", icon="💾")

            
        if st.button("储存所有人员设定 (Save All Employees)"):
            save_data(EMP_FILE, st.session_state.employees)
            st.success("人员设定已储存！")

    # === Tab 3: Coverage Rules ===
    with tab3:
        st.header("时段覆盖规则 (Time Coverage Rules)")
        st.info("💡 设定特定时间段必须有**至少**几个人在场，确保营业时间全覆盖")
        st.warning("⚠️ 重要：请确保营业时间 (7:00-21:30) 的每个时段都有覆盖规则！")
    
        # Get all available roles from employees
        all_roles = set()
        for emp in st.session_state.employees:
            # 員工配置使用 "roles" (複數) 欄位
            emp_roles = emp.get("roles", [])
            if emp_roles:
                all_roles.update(emp_roles)
        all_roles = sorted(list(all_roles))

        
        # Display and edit coverage rules
        st.subheader("现有规则")
        for idx, rule in enumerate(st.session_state.coverage_rules):
            with st.expander(f"规则 {idx+1}: {rule['time_range']}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    time_range = st.text_input(
                        "时间范围 (格式: HH:MM-HH:MM)", 
                        value=rule["time_range"],
                        key=f"cov_time_{idx}"
                    )
                    min_people = st.number_input(
                        "最少人数", 
                        min_value=1, 
                        max_value=20,
                        value=rule["min_people"],
                        key=f"cov_min_{idx}"
                    )
                with col2:
                    required_roles = st.multiselect(
                        "必要角色 (可多选)",
                        options=all_roles,
                        default=rule.get("required_roles", []),
                        key=f"cov_roles_{idx}",
                        help="选择此时段必须在场的角色"
                    )
                
                if st.button(f"删除规则 {idx+1}", key=f"del_cov_{idx}"):
                    st.session_state.coverage_rules.pop(idx)
                    save_data("config/config_coverage.json", st.session_state.coverage_rules)
                    st.rerun()
                
                # Update rule
                st.session_state.coverage_rules[idx] = {
                    "time_range": time_range,
                    "min_people": min_people,
                    "required_roles": required_roles
                }
        
        # Add new rule
        st.subheader("添加新规则")
        col1, col2 = st.columns(2)
        with col1:
            new_time_range = st.text_input("时间范围", placeholder="例如: 7:00-12:00", key="new_cov_time")
            new_min_people = st.number_input("最少人数", min_value=1, value=1, key="new_cov_min")
        with col2:
            new_required_roles = st.multiselect(
                "必要角色",
                options=all_roles,
                key="new_cov_roles"
            )
        
        if st.button("添加规则"):
            if new_time_range:
                st.session_state.coverage_rules.append({
                    "time_range": new_time_range,
                    "min_people": new_min_people,
                    "required_roles": new_required_roles
                })
                save_data("config/config_coverage.json", st.session_state.coverage_rules)
                st.success("规则已添加！")
                st.rerun()
            else:
                st.error("请输入时间范围！")
        
        if st.button("儲存所有覆蓋規則 (Save All Coverage Rules)", type="primary"):
            save_data("config/config_coverage.json", st.session_state.coverage_rules)
            st.success("所有覆盖规则已储存！")
    
        with st.expander("📖 使用说明"):
            st.markdown("""
            **时间范围格式**: `HH:MM-HH:MM` (例如: `10:00-14:00`)
        
            **作用**: 排班系统会确保在这个时间段内，至少有指定人数的员工在上班。
        
            **范例**:
            - `10:00-14:00` 需要 3 人 → 午餐高峰时段
            - `18:00-22:00` 需要 4 人 → 晚间尖峰时段
        
            **注意**: 这个规则是**跨班别**的，系统会计算所有正在上班的人（无论什么班别）。
            """)

    # === Tab 4: Daily Limits ===
    with tab4:
        st.header("每日人数限制 (Daily Staff Limit)")
        st.info("💡 设定每日最大上班人数,避免过度排班")
    
        col1, col2 = st.columns(2)
    
        with col1:
            enforce_limit = st.checkbox(
                "启用每日人数限制",
                value=st.session_state.daily_limits.get("enforce_limit", True),
                help="勾选后才会限制每日最大人数"
            )
    
        with col2:
            max_staff = st.number_input(
                "每日最大人数",
                min_value=1,
                max_value=50,
                value=st.session_state.daily_limits.get("max_staff_per_day", 8),
                disabled=not enforce_limit,
                help="每天最多可以安排几个人上班"
            )
    
        if st.button("储存每日人数限制 (Save Daily Limits)"):
            st.session_state.daily_limits = {
                "max_staff_per_day": max_staff,
                "enforce_limit": enforce_limit
            }
            save_data("config/config_daily_limits.json", st.session_state.daily_limits)
            st.success("每日人数限制已储存！")
    
        with st.expander("📖 使用说明"):
            st.markdown("""
            **功能说明**: 控制每天最多有几个人上班,避免人力过剩。
        
            **优先级**: 系统会优先满足必需角色(如"组长")的需求,即使超过人数限制。
        
            **范例**:
            - 设定最大 8 人 → 每天最多安排 8 个不同的员工
            - 如果某时段必须有"组长",即使已达 8 人,系统仍会安排组长
        
            **注意**: 这个限制是计算**不同员工数量**,不是班次数量。
            """)

    # === Tab 5: Business Hours ===
    with tab5:
        st.header("营业时段设定 (Business Hours)")
        st.info("💡 设定营业时段，系统会检查是否有空窗期（没有人上班的时段）")
    
        col1, col2, col3 = st.columns(3)
    
        with col1:
            biz_start = st.text_input(
                "营业开始时间",
                value=st.session_state.business_hours.get("start", "07:00"),
                placeholder="HH:MM",
                help="例如: 07:00"
            )
    
        with col2:
            biz_end = st.text_input(
                "营业结束时间",
                value=st.session_state.business_hours.get("end", "21:30"),
                placeholder="HH:MM",
                help="例如: 21:30"
            )
    
        with col3:
            enforce_biz = st.checkbox(
                "启用覆盖检查",
                value=st.session_state.business_hours.get("enforce_coverage", True),
                help="勾选后，系统会警告营业时段内的空窗期"
            )
    
        if st.button("储存营业时段设定 (Save Business Hours)"):
            st.session_state.business_hours = {
                "start": biz_start,
                "end": biz_end,
                "enforce_coverage": enforce_biz
            }
            save_data("config/config_business_hours.json", st.session_state.business_hours)
            st.success("营业时段设定已储存！")
    
        with st.expander("📖 使用说明"):
            st.markdown("""
            **功能说明**: 设定公司的营业时段，系统会检查这段时间内是否每个小时都有人上班。
        
            **范例**:
            - 营业时段: 07:00-21:30
            - 如果 12:00-13:00 没有人上班，系统会发出警告
        
            **注意**: 这个检查是以「小时」为单位，确保每个小时至少有1人在班。
            """)

    # === Tab 6: Smart Scheduling ===
    with tab6:
        st.header("产生班表 (Generate Schedule)")
    
        today = date.today()
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            year = st.number_input("年份", value=2026, key="sched_year")
        with col_b:
            month = st.number_input("月份", value=1, key="sched_month")
        
        debug_mode = st.toggle("🐞 啟用逐步除錯模式 (Step-by-Step Debug Mode)")
    
        if debug_mode:
            import calendar
            from datetime import date
        
            # Initialize Debug Scheduler Session or Reset
            reset_clicked = st.button("🗑️ 重置除錯 (Reset Debug)")
        
            if 'debug_scheduler' not in st.session_state or reset_clicked:
                st.session_state.debug_scheduler = SchedulerLogic(
                    year=year,
                    month=month,
                    employees_config=st.session_state.employees,
                    shifts_config=st.session_state.shifts,
                    coverage_rules=st.session_state.coverage_rules,
                    daily_limits=st.session_state.daily_limits,
                    business_hours=st.session_state.business_hours
                )
                # Manually initialize empty structures
                st.session_state.debug_scheduler.schedule = {}
                st.session_state.debug_scheduler.history = {
                    emp['name']: {"worked_days": set(), "consecutive_days": 0} 
                    for emp in st.session_state.employees
                }
                st.session_state.current_debug_day = 1
                if reset_clicked:
                    st.rerun()
            
            scheduler = st.session_state.debug_scheduler
        
            # Auto-recover
            if not hasattr(scheduler, 'get_schedule_dataframe'):
                del st.session_state.debug_scheduler
                st.rerun()
            
            num_days = calendar.monthrange(year, month)[1]
            current_day = st.session_state.current_debug_day
        
            st.markdown(f"### 目前進度: {year}-{month:02d}-{current_day:02d}")
        
            col_next, col_auto = st.columns([1, 4])
        
            if current_day <= num_days:
                # DEBUG: Show internal state
                st.caption(f"Debug Info: Day {current_day}/{num_days} | Scheduled: {len(scheduler.schedule)} days")
            
                if col_next.button(f"🗓️ 排列 {year}-{month:02d}-{current_day:02d}", key=f"btn_next_day_{current_day}"):
                    current_date = date(year, month, current_day)
                    logs = scheduler.schedule_one_day(current_date)
                
                    # Update history and coverage check
                    # Note: schedule_one_day already updates schedule/history
                    # But we need to run the post-day cleanup (consecutive reset)
                    date_str = current_date.strftime("%Y-%m-%d")
                    for emp in scheduler.employees:
                        if date_str not in scheduler.history[emp['name']]["worked_days"]:
                            scheduler.history[emp['name']]["consecutive_days"] = 0
                
                    # Check coverage
                    warns = scheduler._validate_coverage(date_str)
                    logs.extend(warns)
                
                    start_msg = f"--- Day {current_day} Log ---"
                    st.toast(f"已完成第 {current_day} 天排班")
                    if logs:
                        for l in logs:
                            st.warning(l)
                
                    st.session_state.current_debug_day += 1
                    st.rerun()
            else:
                st.success("✅ 本月排班已完成！")
            
            # --- Visualization Area ---
            st.divider()
        
            # 1. Show Schedule So Far
            st.subheader("📊 目前班表 (Current Schedule)")
            df = scheduler.get_schedule_dataframe()
            st.dataframe(df, use_container_width=True)
        
            # 2. Show Employee Status Snapshot (For the NEXT day or LAST day)
            # Detailed view of the day just processed or about to be processed
            view_day = current_day - 1 if current_day > 1 else 1
            view_date = date(year, month, view_day)
        
            st.subheader(f"🔍 人員狀態檢查 (Status: {view_date})")
        
            # Get snapshot
            snapshot = scheduler.get_employee_status_snapshot(view_date)
            status_df = pd.DataFrame(snapshot)
        
            # Enforce column order for styling to work correctly
            cols_order = ["Name", "Roles", "Consecutive Days", "Available Today?", "Assigned Shifts", "Reason (If No)"]
            # Ensure all columns exist (handling empty case)
            for c in cols_order:
                if c not in status_df.columns:
                    status_df[c] = ""
            status_df = status_df[cols_order]
        
            # Highlight logic
            def highlight_status(row):
                colors = []
                # Name
                colors.append("") 
                # Roles
                colors.append("")
                # Consecutive
                val = row["Consecutive Days"]
                if val >= 6:
                    colors.append("background-color: #ffcccc; color: black") # Red warning
                elif val >= 5:
                    colors.append("background-color: #ffffcc; color: black") # Yellow warning
                else:
                    colors.append("")
            
                # Available
                if row["Available Today?"] == "No":
                    colors.append("color: gray")
                else:
                    colors.append("color: green; font-weight: bold")
            
                # Shifts
                colors.append("")
                # Reason
                colors.append("")
                return colors

            st.dataframe(
                status_df.style.apply(highlight_status, axis=1), 
                use_container_width=True,
                column_config={
                    "Consecutive Days": st.column_config.ProgressColumn(
                        "連上天數", min_value=0, max_value=6, format="%d"
                    )
                }
            )



        else:
            # 1. Generate Button
            if st.button("开始排班 (Start Scheduling)", type="primary"):
                with st.spinner("正在生成排班，請稍候... (Generating Schedule...)"):
                    scheduler = SchedulerLogic(
                        year=year,
                        month=month,
                        employees_config=st.session_state.employees,
                        shifts_config=st.session_state.shifts,
                        coverage_rules=st.session_state.coverage_rules,
                        daily_limits=st.session_state.daily_limits,
                        business_hours=st.session_state.business_hours
                    )
                
                    schedule_dict, log = scheduler.generate()
                    
                    # Save results to session_state
                    st.session_state.gen_schedule = schedule_dict
                    st.session_state.gen_log = log
                    st.session_state.gen_df = scheduler.get_schedule_dataframe()
                    st.session_state.gen_df_emp = scheduler.get_employee_schedule_dataframe() if hasattr(scheduler, 'get_employee_schedule_dataframe') else pd.DataFrame()
                    st.session_state.has_generated = True
                    
                    st.success("Generate Success! Reloading...")
                    st.rerun()

            # 2. Display Results (if exists in state)
            if st.session_state.get("has_generated"):
                schedule_dict = st.session_state.gen_schedule
                log = st.session_state.gen_log
                df = st.session_state.gen_df
                df_emp = st.session_state.gen_df_emp
                
                # Display Logs (Warnings)
                if log:
                    with st.expander("排班警示 (Warnings)", expanded=False):
                        for l in log:
                            st.warning(l)
                else:
                    st.success("完美排班！没有违反规则。")
                
                # Display Tables in Tabs
                tab1, tab2, tab3 = st.tabs(["📅 預設視圖 (By Date)", "👥 員工視圖 (By Employee)", "📊 統計報表 (Stats)"])
                
                with tab1:
                    st.dataframe(df, use_container_width=True)
                
                with tab2:
                    st.info("休息日以 'X' 顯示")
                    st.dataframe(df_emp, use_container_width=True)

                with tab3:
                    st.subheader("📈 員工排班統計 (Workload Fairness)")
                    if df_emp is not None and not df_emp.empty:
                        # 計算每位員工的總班數
                        stats_data = []
                        # Columns: Name, Roles, 2026-02-01, ...
                        # Identify date columns (exclude Name, Roles)
                        date_cols = [c for c in df_emp.columns if c not in ["Name", "Roles"]]
                        
                        for idx, row in df_emp.iterrows():
                            name = row["Name"]
                            count = 0
                            for d in date_cols:
                                if row[d] != "X" and row[d] != "":
                                    count += 1
                            stats_data.append({"Name": name, "Shift Count": count})
                        
                        if stats_data:
                            stats_df = pd.DataFrame(stats_data).sort_values("Shift Count", ascending=False)
                            
                            # Bar Chart
                            c = alt.Chart(stats_df).mark_bar().encode(
                                x=alt.X('Name', sort='-y'),
                                y='Shift Count',
                                color=alt.Color('Shift Count', scale=alt.Scale(scheme='blues')),
                                tooltip=['Name', 'Shift Count']
                            ).interactive()
                            
                            st.altair_chart(c, use_container_width=True)
                            
                            # Data Table
                            st.caption("詳細統計數據")
                            st.dataframe(stats_df.set_index("Name").T)
                        else:
                            st.info("無數據")
                    else:
                        st.warning("請先生成排班")

            
                # Download
                # Convert to Excel
                excel_file = "schedule_export.xlsx"
                # Save default df to excel
                df.to_excel(excel_file, index=False)
            
                with open(excel_file, "rb") as f:
                    st.download_button(
                        label="📥 下载 Excel 档案",
                        data=f,
                        file_name=f"schedule_{year}_{month}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                # --- NEW: Visualization Feature ---
                st.divider()
                st.subheader("📊 每日人力分佈檢查 (Daily Staff Distribution)")
                
                # 1. Select Date
                date_options = sorted(list(schedule_dict.keys()))
                # Use session state to remember selection if needed, but selectbox implies its own state within rerun
                selected_date_str = st.selectbox("選擇日期 (Select Date)", date_options)
                
                if selected_date_str:
                    # 2. Calculate Hourly Distribution
                    # Initialize 24-hour buckets
                    hourly_counts = {f"{h:02d}:00": 0 for h in range(24)}
                    
                    # Get time parser helper
                    def parse_time_range(range_str):
                        try:
                            start_str, end_str = range_str.split('-')
                            s_h, s_m = map(int, start_str.split(':'))
                            e_h, e_m = map(int, end_str.split(':'))
                            return s_h * 60 + s_m, e_h * 60 + e_m
                        except:
                            return 0, 0

                    daily_sched = schedule_dict.get(selected_date_str, {})
                    
                    for shift_name, emp_list in daily_sched.items():
                        count = len(emp_list)
                        if count == 0: continue
                        
                        shift_info = st.session_state.shifts.get(shift_name)
                        if not shift_info: continue
                        
                        s_min, e_min = parse_time_range(shift_info.get("time", "00:00-00:00"))
                        
                        # Increment counts for each hour that this shift covers
                        for h in range(24):
                            current_min = h * 60
                            hour_start = current_min
                            hour_end = current_min + 60
                            
                            if s_min < hour_end and e_min > hour_start:
                                hourly_counts[f"{h:02d}:00"] += count
                    
                    # 3. Display Chart
                    chart_df = pd.DataFrame(list(hourly_counts.items()), columns=["Time", "Staff Count"])
                    st.bar_chart(chart_df.set_index("Time"))
                    
                    # 4. Show Details
                    st.write(f"**{selected_date_str} 詳細名單:**")
                    for s_name, e_list in daily_sched.items():
                        if e_list:
                            st.write(f"- **{s_name}**: {', '.join(e_list)}")

                    # 5. Gantt Chart (甘特圖)
                    st.divider()
                    st.subheader("🗓️ 人員排班甘特圖 (Staff Schedule Gantt Chart)")
                    
                    gantt_data = []
                    # Create Map for fast role lookup
                    emp_role_map = {e['name']: ",".join(e.get('roles', [])) for e in st.session_state.employees}

                    for shift_name, emp_list in daily_sched.items():
                        if not emp_list: continue
                        shift_info = st.session_state.shifts.get(shift_name)
                        if not shift_info: continue
                        
                        time_str = shift_info.get("time", "00:00-00:00")
                        try:
                            start_str, end_str = time_str.split('-')
                            dummy_date = selected_date_str 
                            
                            for emp_name in emp_list:
                                role_str = emp_role_map.get(emp_name, "")
                                display_name = f"{emp_name} ({role_str})" if role_str else emp_name
                                
                                gantt_data.append({
                                    "Person": display_name,
                                    "Role": role_str,
                                    "Shift": shift_name,
                                    "Start": f"{dummy_date}T{start_str}:00",
                                    "End": f"{dummy_date}T{end_str}:00",
                                    "Color": shift_name 
                                })
                        except:
                            continue
                            
                    if gantt_data:
                        gantt_df = pd.DataFrame(gantt_data)
                        
                        # Create Chart
                        c = alt.Chart(gantt_df).mark_bar().encode(
                            x=alt.X('Start:T', title='Time', axis=alt.Axis(format='%H:%M')),
                            x2='End:T',
                            y=alt.Y('Person:N', title='Employee (Role)'),
                            color=alt.Color('Shift:N', legend=alt.Legend(title="Shift")),
                            tooltip=['Person', 'Role', 'Shift', 'Start', 'End']
                        ).properties(
                            title=f"{selected_date_str} Schedule",
                            height=300 + (len(gantt_df['Person'].unique()) * 20) 
                        ).interactive()
                        
                        st.altair_chart(c, use_container_width=True)
                    else:
                        st.info("No shifts assigned for this date.")


except Exception as e:
    st.error("❌ 系統發生錯誤 (System Error)")
    st.markdown(f"**錯誤訊息:** `{str(e)}`")
    with st.expander("查看詳細除錯資訊 (Traceback)"):
        st.code(traceback.format_exc())

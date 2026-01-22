import pandas as pd
import random
from datetime import date, timedelta
import calendar

class SchedulerLogic:
    def __init__(self, year, month, employees_config, shifts_config, coverage_rules=None, daily_limits=None, business_hours=None):
        """
        排班邏輯核心類別 (Scheduler Core Logic)

        :param year: 排班年份 (int)
        :param month: 排班月份 (int)
        :param employees_config: 員工設定列表 (List[Dict])
               範例: [{"name": "Jun", "available_days": [0,1,2], "shifts": ["A", "B"], "roles": ["組長"]}]
        :param shifts_config: 班別設定字典 (Dict)
               範例: {"A": {"time": "07:00-14:00", "required_people": 2, "enforce_headcount": True}}
        :param coverage_rules: 時段覆蓋規則 (List[Dict]) - 確保特定時段有足夠人數
               範例: [{"time_range": "10:00-14:00", "min_people": 3, "required_role": "組長"}]
        :param daily_limits: 每日限制設定 (Dict)
               範例: {"max_staff_per_day": 8, "enforce_limit": True}
        :param business_hours: 營業時段設定 (Dict)
               範例: {"start": "07:00", "end": "21:30", "enforce_coverage": True}
        """
        self.year = year
        self.month = month
        self.employees = employees_config
        self.shifts = shifts_config
        self.coverage_rules = coverage_rules or []
        self.daily_limits = daily_limits or {"max_staff_per_day": 999, "enforce_limit": False}
        self.business_hours = business_hours or {"start": "07:00", "end": "21:30", "enforce_coverage": False}
        self.num_days = calendar.monthrange(year, month)[1]
        self.dates = [date(year, month, d) for d in range(1, self.num_days + 1)]
        
        # 追蹤排班狀態 (Tracking state)
        # 結構: schedule[date_str][shift_name] = [employee_name1, employee_name2]
        self.schedule = {d.strftime("%Y-%m-%d"): {s: [] for s in self.shifts} for d in self.dates}
        
        # 追蹤員工歷史紀錄 (用於驗證連續上班等規則)
        # worked_days: 已經上班的日期集合
        # consecutive_days: 當前連續上班天數
        # last_shift_end_minutes: 最後一次下班時間（分鐘數，用於檢查休息時間）
        self.history = {
            emp['name']: {
                "consecutive_days": 0, 
                "last_shift_end": 0, 
                "worked_days": set(),
                "last_shift_end_minutes": None  # NEW: 防止花花班
            } 
            for emp in self.employees
        }

    @staticmethod
    def _parse_time(time_str):
        """將 HH:MM 格式轉換為分鐘數 (例如 01:00 -> 60)"""
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    
    @staticmethod
    def _parse_time_range(range_str):
        """解析 'HH:MM-HH:MM' 為 (開始分鐘, 結束分鐘)"""
        start, end = range_str.split('-')
        return SchedulerLogic._parse_time(start.strip()), SchedulerLogic._parse_time(end.strip())

    def _get_required_roles_for_shift(self, shift_name):
        """
        辨識此班別是否與任何'需要特定角色'的覆蓋規則重疊
        例如: 如果早班是 08:00-16:00，而規則規定 10:00-12:00 必須有組長，則早班需要考慮組長。
        """
        required_roles = set()
        if shift_name not in self.shifts:
            return required_roles
        shift_time = self.shifts[shift_name].get("time")
        if not shift_time:
            return required_roles
        
        try:
            s_start, s_end = self._parse_time_range(shift_time)
            
            for rule in self.coverage_rules:
                # 獲取角色列表
                roles_to_check = rule.get("required_roles", [])
                # 兼容舊版單一角色欄位
                if not roles_to_check and rule.get("required_role"):
                    roles_to_check = [rule.get("required_role")]
                
                if not roles_to_check:
                    continue
                
                try:
                    r_start, r_end = self._parse_time_range(rule["time_range"])
                    # 檢查時間重疊
                    if s_start < r_end and s_end > r_start:
                        for role in roles_to_check:
                            if role:
                                required_roles.add(role)
                except:
                    continue
        except:
            pass
            
        return required_roles

    def _calculate_current_coverage(self, date_str, start_time, end_time, role):
        """
        計算在指定時間範圍內，擁有特定角色且已經被安排上班的人數
        (用於計算還缺多少人)
        """
        count = 0
        daily_schedule = self.schedule[date_str]
        
        # 檢查當天所有已安排的班別
        for s_name, assigned_emps in daily_schedule.items():
            if not assigned_emps:
                continue
                
            # 檢查時間是否有重疊
            if s_name not in self.shifts:
                continue
            s_time = self.shifts[s_name].get("time")
            if not s_time: continue
            
            try:
                s_start, s_end = self._parse_time_range(s_time)
                # 重疊邏輯: (StartA < EndB) and (EndA > StartB)
                if s_start < end_time and s_end > start_time:
                    # 檢查被安排的人是否有該角色
                    for emp_name in assigned_emps:
                        emp = next((e for e in self.employees if e['name'] == emp_name), None)
                        if emp and role in emp.get('roles', []):
                            count += 1
            except:
                continue
        return count

    def _is_available(self, employee, current_date, shift_name):
        """
        核心限制檢查：檢查員工是否可以上這個班

        想要修改限制邏輯，請修改這裡！
        """
        emp_name = employee['name']
        
        # 1. 星期幾檢查 (Day of Week Check) (0=週一, 6=週日)
        weekday = current_date.weekday()
        if weekday not in employee.get('available_weekdays', list(range(7))):
            return False, "非可上班日 (Day of week mismatch)"

        # 2. 允許班別檢查 (Allowed Shift Type)
        if shift_name not in employee.get('allowed_shifts', []):
            return False, "不可上此班別 (Shift type not allowed)"

        # 3. 勞基法/連續上班限制 (7天內必須休1天)
        # 簡化版: 不能連續上班超過 6 天
        if self.history[emp_name]["consecutive_days"] >= 6:
            return False, "已達連續上班上限 (Max consecutive days reached)"

        # 4. 休息時間間隔檢查 (Rest Interval) - 防止花花班 (Clopening)
        # 確保員工有至少 11 小時的休息時間
        last_shift_end = self.history[emp_name].get("last_shift_end_minutes")
        if last_shift_end is not None:
            try:
                shift_time = self.shifts[shift_name].get("time", "00:00-23:59")
                shift_start_min, shift_end_min = self._parse_time_range(shift_time)
                
                # 計算距離上次下班的時間
                # 處理跨日情況：如果上次下班時間 > 今天上班時間，表示跨日了
                if last_shift_end > shift_start_min:
                    # 跨日：例如昨天 22:00 下班 (1320分)，今天 07:00 上班 (420分)
                    # 休息時間 = (24*60 - 1320) + 420 = 180 + 420 = 600 分鐘 = 10 小時
                    time_since_last = (24 * 60 - last_shift_end) + shift_start_min
                else:
                    # 同日或正常間隔
                    time_since_last = shift_start_min - last_shift_end
                
                MIN_REST_HOURS = 11
                MIN_REST_MINUTES = MIN_REST_HOURS * 60
                
                if time_since_last < MIN_REST_MINUTES:
                    hours_rest = time_since_last / 60
                    return False, f"休息時間不足 ({hours_rest:.1f}小時，需要{MIN_REST_HOURS}小時)"
            except:
                pass  # 如果解析失敗，跳過此檢查
        
        # 5. 當日是否已排班 (Already worked today?)
        if current_date.strftime("%Y-%m-%d") in self.history[emp_name]["worked_days"]:
            return False, "當日已排班 (Already worked today)"

        return True, "OK"

    def generate(self):
        """
        執行排班算法 (Greedy Algorithm with Randomization)
        回傳: (schedule, log)
        """
        success = True
        log = []
        
        # 重置排班狀態與歷史紀錄
        self.schedule = {}
        self.history = {
            emp['name']: {
                "worked_days": set(), 
                "consecutive_days": 0,
                "last_shift_end_minutes": None  # CRITICAL FIX: 防止花花班檢查需要此欄位
            } 
            for emp in self.employees
        }
        
        for current_date in self.dates:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # 1. 排定當天班表
            day_log = self.schedule_one_day(current_date)
            log.extend(day_log)
            
            # 2. 重置沒上班的人的連續天數計數器
            for emp in self.employees:
                if date_str not in self.history[emp['name']]["worked_days"]:
                    self.history[emp['name']]["consecutive_days"] = 0
            
            # 3. 驗證當天覆蓋率規則 (Coverage Rules)
            coverage_warnings = self._validate_coverage(date_str)
            log.extend(coverage_warnings)
            
            # 4. 驗證營業時段覆蓋 (Business Hours Coverage)
            business_hours_warnings = self._validate_business_hours_coverage(date_str)
            log.extend(business_hours_warnings)
            
        return self.schedule, log
    
    def _validate_coverage(self, date_str):
        """驗證特定日期的覆蓋規則是否有被滿足 (例如: 10點到14點要有3人)"""
        warnings = []
        
        if not self.coverage_rules:
            return warnings
        
        # 建立時間軸 (Timeline)
        # 格式: [(start_min, end_min, employee_name)]
        timeline = [] 
        
        if date_str not in self.schedule:
            return warnings
            
        for shift_name, employees in self.schedule[date_str].items():
            if not employees:
                continue
            
            shift_time = self.shifts[shift_name].get("time", "00:00-23:59")
            try:
                start_min, end_min = self._parse_time_range(shift_time)
                for emp_name in employees:
                    timeline.append((start_min, end_min, emp_name))
            except:
                continue
        
        # 檢查每一條規則
        for rule in self.coverage_rules:
            try:
                rule_start, rule_end = self._parse_time_range(rule["time_range"])
                min_required = rule["min_people"]
                
                # 計算此時段有多少人上班
                working_people = set()
                for start_min, end_min, emp_name in timeline:
                    # 判斷時間重疊
                    if start_min < rule_end and end_min > rule_start:
                        working_people.add(emp_name)
                
                actual_count = len(working_people)
                if actual_count < min_required:
                    warnings.append(
                        f"Coverage Warning: {date_str} {rule['time_range']} 只有 {actual_count} 人 (需要 {min_required} 人)"
                    )
                
                # NEW: 檢查是否超過最大人數限制
                max_allowed = rule.get("max_people")
                if max_allowed and actual_count > max_allowed:
                    warnings.append(
                        f"⚠️ 人數超標: {date_str} {rule['time_range']} 有 {actual_count} 人 (最多 {max_allowed} 人)"
                    )
                
                # 檢查是否有必要角色列表 (例如: ["組長", "資深員工"])
                required_roles = rule.get("required_roles", [])
                # 兼容舊版單一角色欄位
                if not required_roles and rule.get("required_role"):
                    required_roles = [rule.get("required_role")]
                
                for role in required_roles:
                    if not role: continue
                    role_present = False
                    for start_min, end_min, emp_name in timeline:
                        if start_min < rule_end and end_min > rule_start:
                            emp_data = next((e for e in self.employees if e['name'] == emp_name), None)
                            if emp_data and role in emp_data.get('roles', []):
                                role_present = True
                                break
                    
                    if not role_present:
                        warnings.append(
                            f"Role Warning: {date_str} {rule['time_range']} 缺少必要角色 '{role}'"
                        )
            except:
                continue
        
        return warnings

    def _validate_business_hours_coverage(self, date_str):
        """
        驗證營業時段是否有完整覆蓋 (Business Hours Coverage Validation)
        檢查營業時段內每個小時是否至少有1人上班
        """
        warnings = []
        
        if not self.business_hours.get("enforce_coverage", False):
            return warnings
        
        try:
            biz_start = self._parse_time(self.business_hours["start"])
            biz_end = self._parse_time(self.business_hours["end"])
        except:
            return warnings
        
        # 建立時間軸
        timeline = []
        if date_str not in self.schedule:
            return warnings
            
        for shift_name, employees in self.schedule[date_str].items():
            if not employees:
                continue
            
            shift_time = self.shifts[shift_name].get("time", "00:00-23:59")
            try:
                start_min, end_min = self._parse_time_range(shift_time)
                for emp_name in employees:
                    timeline.append((start_min, end_min, emp_name))
            except:
                continue
        
        # 檢查每個小時是否有人
        gap_hours = []
        current_hour = biz_start
        
        while current_hour < biz_end:
            hour_end = min(current_hour + 60, biz_end)
            
            # 檢查這個小時是否有人上班
            has_coverage = False
            for start_min, end_min, emp_name in timeline:
                # 檢查重疊: shift開始 < hour結束 AND shift結束 > hour開始
                if start_min < hour_end and end_min > current_hour:
                    has_coverage = True
                    break
            
            if not has_coverage:
                gap_hours.append(f"{current_hour//60:02d}:00-{hour_end//60:02d}:00")
            
            current_hour += 60
        
        if gap_hours:
            warnings.append(
                f"⚠️ 營業時段空窗警告 ({date_str}): {', '.join(gap_hours)} 沒有人上班！"
            )
        
        return warnings

    def _would_violate_max_people(self, date_str, shift_name, emp_name):
        """
        檢查分配此員工是否會違反 max_people 規則
        回傳: (would_violate: bool, reason: str)
        """
        if not self.coverage_rules:
            return False, ""
        
        # 取得此班別的時間範圍
        if shift_name not in self.shifts:
            return False, ""
        
        shift_time = self.shifts[shift_name].get("time")
        if not shift_time:
            return False, ""
        
        try:
            shift_start, shift_end = self._parse_time_range(shift_time)
        except:
            return False, ""
        
        # 檢查每一條有 max_people 的規則
        for rule in self.coverage_rules:
            max_allowed = rule.get("max_people")
            if not max_allowed:
                continue  # 沒有最大限制，跳過
            
            try:
                rule_start, rule_end = self._parse_time_range(rule["time_range"])
                
                # 檢查此班別是否與規則時段重疊
                if shift_start < rule_end and shift_end > rule_start:
                    # 計算目前此時段有多少人（假設分配了這個員工）
                    working_people = set()
                    working_people.add(emp_name)  # 加入即將分配的人
                    
                    for s_name, employees in self.schedule[date_str].items():
                        if not employees:
                            continue
                        s_time = self.shifts.get(s_name, {}).get("time")
                        if not s_time:
                            continue
                        
                        try:
                            s_start, s_end = self._parse_time_range(s_time)
                            if s_start < rule_end and s_end > rule_start:
                                working_people.update(employees)
                        except:
                            continue
                    
                    if len(working_people) > max_allowed:
                        return True, f"會違反 {rule['time_range']} 最大人數限制 ({max_allowed}人)"
            except:
                continue
        
        return False, ""

    def _analyze_daily_coverage_needs(self, date_str):
        """
        分析當日的覆蓋需求,回傳優先級排序的需求列表
        回傳: List[Dict] 每個需求包含 time_range, min_people, required_roles, priority
        """
        needs = []
        
        # 1. 從覆蓋規則提取需求
        for rule in self.coverage_rules:
            roles = rule.get('required_roles', [])
            # 兼容舊版單一角色欄位
            if not roles and rule.get('required_role'):
                roles = [rule.get('required_role')]
            
            needs.append({
                'time_range': rule['time_range'],
                'min_people': rule.get('min_people', 0),
                'max_people': rule.get('max_people', 999),
                'required_roles': roles,
                'priority': 'HIGH' if roles else 'MEDIUM'
            })
        
        # 2. 確保營業時段完整覆蓋
        if self.business_hours.get('enforce_coverage'):
            needs.append({
                'time_range': f"{self.business_hours['start']}-{self.business_hours['end']}",
                'min_people': 1,
                'max_people': 999,
                'required_roles': [],
                'priority': 'MEDIUM'
            })
        
        # 按優先級排序: HIGH > MEDIUM
        return sorted(needs, key=lambda x: 0 if x['priority'] == 'HIGH' else 1)

    def _find_shifts_for_timerange(self, time_range):
        """
        找出能覆蓋指定時段的所有班別
        回傳: List[str] 班別名稱列表
        """
        suitable = []
        try:
            need_start, need_end = self._parse_time_range(time_range)
            for shift_name, shift_info in self.shifts.items():
                s_time = shift_info.get('time')
                if not s_time:
                    continue
                s_start, s_end = self._parse_time_range(s_time)
                # 檢查時間重疊
                if s_start < need_end and s_end > need_start:
                    suitable.append(shift_name)
        except:
            pass
        return suitable

    def _count_coverage_in_timerange(self, date_str, time_range, required_roles=None):
        """
        計算指定時段當前已有多少人(可選:符合特定角色)
        回傳: int 人數
        """
        if required_roles is None:
            required_roles = []
        
        try:
            need_start, need_end = self._parse_time_range(time_range)
        except:
            return 0
        
        covered_people = set()
        
        if date_str not in self.schedule:
            return 0
        
        for shift_name, emp_list in self.schedule[date_str].items():
            if not emp_list:
                continue
            
            # 檢查此班別是否覆蓋需求時段
            shift_info = self.shifts.get(shift_name)
            if not shift_info:
                continue
            
            s_time = shift_info.get('time')
            if not s_time:
                continue
            
            try:
                s_start, s_end = self._parse_time_range(s_time)
                # 檢查重疊
                if s_start < need_end and s_end > need_start:
                    for emp_name in emp_list:
                        # 如果有角色要求,檢查員工是否符合
                        if required_roles:
                            emp = next((e for e in self.employees if e['name'] == emp_name), None)
                            if emp and any(r in emp.get('roles', []) for r in required_roles):
                                covered_people.add(emp_name)
                        else:
                            covered_people.add(emp_name)
            except:
                continue
        
        return len(covered_people)

    def _get_available_candidates(self, current_date, shift_name, required_roles=None):
        """
        取得可用候選人列表,優先有角色的,按公平性排序
        回傳: List[Dict] 員工列表
        """
        if required_roles is None:
            required_roles = []
        
        role_holders = []
        regular_candidates = []
        
        for emp in self.employees:
            # 檢查是否可上此班別
            if shift_name not in emp.get('allowed_shifts', []):
                continue
            
            # 檢查是否有需要的角色
            has_role = any(r in emp.get('roles', []) for r in required_roles)
            if has_role:
                role_holders.append(emp)
            else:
                regular_candidates.append(emp)
        
        # 按公平性排序 (已排班數少的優先)
        def get_shift_count(e):
            return len(self.history[e['name']]['worked_days'])
        
        role_holders.sort(key=get_shift_count)
        regular_candidates.sort(key=get_shift_count)
        
        # 有角色的優先
        return role_holders + regular_candidates

    def _update_employee_history(self, emp_name, date_str, shift_name):
        """更新員工歷史紀錄"""
        self.history[emp_name]['worked_days'].add(date_str)
        self.history[emp_name]['consecutive_days'] += 1
        
        # 更新最後下班時間
        try:
            shift_time = self.shifts[shift_name].get('time', '00:00-23:59')
            _, shift_end_min = self._parse_time_range(shift_time)
            self.history[emp_name]['last_shift_end_minutes'] = shift_end_min
        except:
            pass

    def get_schedule_dataframe(self):
        """將排班結果轉換為 Pandas DataFrame，方便顯示或匯出"""
        data = []
        for d in self.dates:
            d_str = d.strftime("%Y-%m-%d")
            row = {"Date": d_str, "Weekday": d.strftime("%a")}
            for s in self.shifts:
                if d_str in self.schedule:
                    row[s] = ", ".join(self.schedule[d_str].get(s, []))
                else:
                    row[s] = ""
            data.append(row)
        
        return pd.DataFrame(data)

    def schedule_one_day(self, current_date):
        """
        排列單一天的班表 (覆蓋驅動算法 - Coverage-Driven Algorithm)
        回傳: log list
        """
        date_str = current_date.strftime("%Y-%m-%d")
        day_log = []
        
        if date_str not in self.schedule:
            self.schedule[date_str] = {s: [] for s in self.shifts}
        
        # 分析當日覆蓋需求
        coverage_needs = self._analyze_daily_coverage_needs(date_str)
        
        # 追蹤已分配人員
        assigned_people = set()
        max_daily_staff = self.daily_limits.get('max_staff_per_day', 8)
        enforce_daily_limit = self.daily_limits.get('enforce_limit', True)
        
        # 階段1: 滿足所有覆蓋需求
        for need in coverage_needs:
            if enforce_daily_limit and len(assigned_people) >= max_daily_staff:
                day_log.append(f"⚠️ {date_str} 已達每日人數上限 ({max_daily_staff}人),停止分配")
                break
            
            # 找出能覆蓋此時段的班別
            suitable_shifts = self._find_shifts_for_timerange(need['time_range'])
            
            if not suitable_shifts:
                day_log.append(f"⚠️ {date_str} {need['time_range']} 沒有合適的班別可覆蓋")
                continue
            
            # 計算此時段還需要多少人
            current_coverage = self._count_coverage_in_timerange(
                date_str, need['time_range'], need.get('required_roles', [])
            )
            still_needed = max(0, need['min_people'] - current_coverage)
            
            if still_needed == 0:
                continue  # 此時段需求已滿足
            
            # 嘗試為每個合適的班別分配人員
            for shift_name in suitable_shifts:
                if still_needed <= 0:
                    break
                if enforce_daily_limit and len(assigned_people) >= max_daily_staff:
                    break
                
                # 取得候選人 (優先有角色的)
                candidates = self._get_available_candidates(
                    current_date, shift_name, need.get('required_roles', [])
                )
                
                for emp in candidates:
                    if still_needed <= 0:
                        break
                    if enforce_daily_limit and len(assigned_people) >= max_daily_staff:
                        break
                    
                    # 跳過已排班的人
                    if emp['name'] in assigned_people:
                        continue
                    
                    # 檢查可用性 (勞基法規則等)
                    is_ok, reason = self._is_available(emp, current_date, shift_name)
                    if not is_ok:
                        continue
                    
                    # 檢查是否違反 max_people 規則
                    would_violate, violation_reason = self._would_violate_max_people(
                        date_str, shift_name, emp['name']
                    )
                    if would_violate:
                        continue
                    
                    # 分配成功!
                    self.schedule[date_str][shift_name].append(emp['name'])
                    assigned_people.add(emp['name'])
                    
                    # 更新歷史紀錄
                    self._update_employee_history(emp['name'], date_str, shift_name)
                    
                    # 重新計算覆蓋 (因為新增了人)
                    current_coverage = self._count_coverage_in_timerange(
                        date_str, need['time_range'], need.get('required_roles', [])
                    )
                    still_needed = max(0, need['min_people'] - current_coverage)
                    
                    # 記錄角色分配
                    if need.get('required_roles'):
                        for role in need['required_roles']:
                            if role in emp.get('roles', []):
                                day_log.append(
                                    f"✓ {date_str} {shift_name} 分配 '{role}': {emp['name']}"
                                )
        
        # 階段2: 如果還沒達到每日人數目標,繼續填補
        # 目標: 盡量接近 max_daily_staff (例如8人)
        if not enforce_daily_limit or len(assigned_people) < max_daily_staff:
            # 隨機打亂班別順序,增加多樣性
            remaining_shifts = list(self.shifts.keys())
            random.shuffle(remaining_shifts)
            
            for shift_name in remaining_shifts:
                if enforce_daily_limit and len(assigned_people) >= max_daily_staff:
                    break
                
                # 取得所有候選人
                candidates = self._get_available_candidates(current_date, shift_name, [])
                
                for emp in candidates:
                    if enforce_daily_limit and len(assigned_people) >= max_daily_staff:
                        break
                    
                    if emp['name'] in assigned_people:
                        continue
                    
                    # 檢查可用性
                    is_ok, reason = self._is_available(emp, current_date, shift_name)
                    if not is_ok:
                        continue
                    
                    # 檢查 max_people 限制
                    would_violate, violation_reason = self._would_violate_max_people(
                        date_str, shift_name, emp['name']
                    )
                    if would_violate:
                        continue
                    
                    # 分配
                    self.schedule[date_str][shift_name].append(emp['name'])
                    assigned_people.add(emp['name'])
                    self._update_employee_history(emp['name'], date_str, shift_name)
        
        # 記錄當日總人數
        day_log.append(f"📊 {date_str} 共分配 {len(assigned_people)} 人上班")
        
        return day_log

    def get_employee_status_snapshot(self, current_date):
        """
        取得當天所有員工的狀態快照 (Status Snapshot)
        用於除錯介面，顯示誰可以上班、誰不行及其原因。
        """
        snapshot = []
        date_str = current_date.strftime("%Y-%m-%d")
        
        for emp in self.employees:
            name = emp['name']
            
            # 重新檢查可用性邏輯以供顯示
            weekday = current_date.weekday()
            is_weekday_ok = weekday in emp.get('available_weekdays', [])
            
            cons_days = self.history[name]["consecutive_days"]
            is_cons_ok = cons_days < 6
            
            assigned_shifts = []
            if date_str in self.schedule:
                for s, ppl in self.schedule[date_str].items():
                    if name in ppl:
                        assigned_shifts.append(s)
            
            snapshot.append({
                "Name": name,
                "Roles": ",".join(emp.get('roles', [])),
                "Consecutive Days": cons_days,
                "Available Today?": "Yes" if (is_weekday_ok and is_cons_ok) else "No",
                "Assigned Shifts": ",".join(assigned_shifts) if assigned_shifts else "-",
                "Reason (If No)": "休假日" if not is_weekday_ok else ("達到連續上班限制" if not is_cons_ok else "-")
            })
        return snapshot

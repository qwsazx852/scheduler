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
                "last_shift_end_minutes": None,  # NEW: 防止花花班
                "weekend_count": 0 # 週末班計數 (公平性)
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

    @staticmethod
    def _parse_shift_segments(time_str):
        """解析班別時間，支援多段式 (例如 '10:00-14:00, 17:00-21:00')"""
        segments = []
        if not time_str: return segments
        parts = time_str.split(',')
        for part in parts:
            try:
                start_str, end_str = part.strip().split('-')
                s = SchedulerLogic._parse_time(start_str)
                e = SchedulerLogic._parse_time(end_str)
                segments.append((s, e))
            except:
                pass
        return segments

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
            segments = self._parse_shift_segments(shift_time)
            
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
                    # 檢查任何一段時間是否重疊
                    is_overlap = False
                    for s_start, s_end in segments:
                        if s_start < r_end and s_end > r_start:
                            is_overlap = True
                            break
                    
                    if is_overlap:
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
                segments = self._parse_shift_segments(s_time)
                # 檢查任何一段時間是否重疊
                is_overlap = False
                for s_start, s_end in segments:
                    if s_start < end_time and s_end > start_time:
                        is_overlap = True
                        break
                
                if is_overlap:
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
                segments = self._parse_shift_segments(shift_time)
                if not segments:
                     # Fallback
                     shift_start_min = 0
                else:
                     # 取第一段的開始時間
                     shift_start_min = segments[0][0]
                
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

    def generate(self, max_retries=5):
        """
        執行排班算法 (Constraint-First with Per-Day Retry)
        每一天都必須成功排班，否則重試
        回傳: (schedule, log)
        """
        import random
        
        log = []
        
        # 重置排班狀態與歷史紀錄
        self.schedule = {}
        self.history = {
            emp['name']: {
                "worked_days": set(), 
                "consecutive_days": 0,
                "last_shift_end_minutes": None
            } 
            for emp in self.employees
        }
        
        # 逐日排班
        for current_date in self.dates:
            date_str = current_date.strftime("%Y-%m-%d")
            day_success = False
            
            # 對每一天進行重試
            for attempt in range(max_retries):
                # 保存當前狀態（用於回滾）
                saved_schedule = {k: {s: list(v) for s, v in shifts.items()} for k, shifts in self.schedule.items()}
                saved_history = {
                    name: {
                        "worked_days": set(hist["worked_days"]),
                        "consecutive_days": hist["consecutive_days"],
                        "last_shift_end_minutes": hist["last_shift_end_minutes"]
                    }
                    for name, hist in self.history.items()
                }
                
                if attempt > 0:
                    log.append(f"🔄 {date_str} 第 {attempt + 1} 次嘗試...")
                    # 恢復到本日開始前的狀態
                    self.schedule = saved_schedule
                    self.history = saved_history
                    # 打亂員工順序以探索不同解
                    random.shuffle(self.employees)
                
                # 1. 排定當天班表
                day_log = self.schedule_one_day(current_date)
                
                # 2. 重置沒上班的人的連續天數計數器
                for emp in self.employees:
                    if date_str not in self.history[emp['name']]["worked_days"]:
                        self.history[emp['name']]["consecutive_days"] = 0
                
                # 3. 驗證當天覆蓋率規則
                coverage_warnings = self._validate_coverage(date_str)
                
                # 4. 驗證營業時段覆蓋
                business_hours_warnings = self._validate_business_hours_coverage(date_str)
                
                # 檢查是否有違規
                violations = []
                
                # 只計算關鍵的覆蓋不足問題，忽略其他警告
                for line in coverage_warnings + business_hours_warnings:
                    # 只有真正的覆蓋不足才算違規
                    if "Coverage Warning" in line or "營業時段空窗" in line:
                        violations.append(line)
                    # 角色缺失也算違規
                    elif "Role Warning" in line and "缺少必要角色" in line:
                        violations.append(line)
                
                # 如果本日成功（無關鍵違規）
                if len(violations) == 0:
                    log.append(f"✅ {date_str} 排班成功 (嘗試 {attempt + 1} 次)")
                    # 記錄所有日誌（包括非關鍵警告）
                    log.extend(day_log)
                    if coverage_warnings:
                        log.extend([w for w in coverage_warnings if w not in violations])
                    if business_hours_warnings:
                        log.extend([w for w in business_hours_warnings if w not in violations])
                    day_success = True
                    break
                else:
                    if attempt < max_retries - 1:
                        log.append(f"⚠️ {date_str} 有 {len(violations)} 個問題，重試中...")
                    else:
                        # 最後一次嘗試也失敗
                        log.append(f"❌ {date_str} 經過 {max_retries} 次嘗試仍無法完美排班")
                        log.extend(day_log)
                        log.extend(coverage_warnings)
                        log.extend(business_hours_warnings)
                        log.append("")
                        log.append(f"🔍 {date_str} 違規項目:")
                        for v in violations[:5]:  # 只顯示前5個
                            log.append(f"  {v}")
                        if len(violations) > 5:
                            log.append(f"  ... 還有 {len(violations) - 5} 個問題")
            
            # 如果本日失敗，提供建議
            if not day_success:
                log.append("")
                log.append(f"💡 {date_str} 建議:")
                log.append("  1. 檢查該日是否有足夠的可用員工")
                log.append("  2. 確認班別時間能覆蓋所有需求時段")
                log.append("  3. 考慮放寬該日的人數限制")
                log.append("")
        
        # 統計整體成功率
        total_days = len(self.dates)
        success_days = sum(1 for d in self.dates if d.strftime("%Y-%m-%d") in self.schedule and any(self.schedule[d.strftime("%Y-%m-%d")].values()))
        
        log.insert(0, "")
        log.insert(0, f"📊 整體排班結果: {success_days}/{total_days} 天成功")
        if success_days == total_days:
            log.insert(0, "🎉 完美！所有日期都成功排班！")
        else:
            log.insert(0, f"⚠️ 有 {total_days - success_days} 天無法完美排班")
        log.insert(0, "")
        
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
                segments = self._parse_shift_segments(shift_time)
                for start_min, end_min in segments:
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
                segments = self._parse_shift_segments(shift_time)
                for start_min, end_min in segments:
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
            segments = self._parse_shift_segments(shift_time)
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
                is_overlap = False
                for s_start, s_end in segments:
                    if s_start < rule_end and s_end > rule_start:
                        is_overlap = True
                        break
                        
                if is_overlap:
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
                            s_segments = self._parse_shift_segments(s_time)
                            s_overlap = False
                            for ss_start, ss_end in s_segments:
                                if ss_start < rule_end and ss_end > rule_start:
                                    s_overlap = True
                                    break
                            
                            if s_overlap:
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
        
        # 1. 從覆蓋規則提取需求 (拆解為每小時區塊以確保連續性)
        for rule in self.coverage_rules:
            roles = rule.get('required_roles', [])
            # 兼容舊版單一角色欄位
            if not roles and rule.get('required_role'):
                roles = [rule.get('required_role')]
            
            try:
                # 解析時間範圍
                range_start, range_end = self._parse_time_range(rule['time_range'])
                
                # 如果時間範圍無效或長度為0
                if range_end <= range_start:
                    continue

                current = range_start
                while current < range_end:
                    # 每小時一個區塊 (確保不會無限迴圈: step至少為1)
                    step = 60
                    block_end = min(current + step, range_end)
                    
                    if block_end <= current: # Safety check
                        block_end = current + 1

                    # 格式化
                    h1, m1 = divmod(current, 60)
                    h2, m2 = divmod(block_end, 60)
                    sub_range = f"{h1:02d}:{m1:02d}-{h2:02d}:{m2:02d}"
                    
                    needs.append({
                        'time_range': sub_range,
                        'min_people': rule.get('min_people', 0),
                        'required_roles': roles,
                        'priority': 'HIGH' if roles else 'MEDIUM'
                    })
                    
                    current = block_end
            except:
                # 如果解析失敗，退回到舊邏輯 (直接添加原始範圍)
                needs.append({
                    'time_range': rule['time_range'],
                    'min_people': rule.get('min_people', 0),
                    'required_roles': roles,
                    'priority': 'HIGH' if roles else 'MEDIUM'
                })

        
        # 2. 確保營業時段完整覆蓋 (拆分為每小時檢查, 確保連續性)
        if self.business_hours.get('enforce_coverage'):
            try:
                start_min = self._parse_time(self.business_hours['start'])
                end_min = self._parse_time(self.business_hours['end'])
                
                current = start_min
                while current < end_min:
                    block_end = min(current + 60, end_min) # 1小時一塊
                    
                    # 格式化回 HH:MM
                    h1, m1 = divmod(current, 60)
                    h2, m2 = divmod(block_end, 60)
                    time_range = f"{h1:02d}:{m1:02d}-{h2:02d}:{m2:02d}"
                    
                    needs.append({
                        'time_range': time_range,
                        'min_people': 1,
                        'required_roles': [],
                        'priority': 'CRITICAL'
                    })
                    
                    current = block_end
            except:
                # Fallback if parsing fails
                needs.append({
                    'time_range': f"{self.business_hours['start']}-{self.business_hours['end']}",
                    'min_people': 1,
                    'required_roles': [],
                    'priority': 'CRITICAL'
                })

        
        # 按優先級排序: CRITICAL > HIGH > MEDIUM
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
        return sorted(needs, key=lambda x: priority_order.get(x['priority'], 999))


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
                
                try:
                    segments = self._parse_shift_segments(s_time)
                    is_overlap = False
                    for s_start, s_end in segments:
                        if s_start < need_end and s_end > need_start:
                            is_overlap = True
                            break
                    if is_overlap:
                        suitable.append(shift_name)
                except:
                    continue
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
                segments = self._parse_shift_segments(s_time)
                is_overlap = False
                for s_start, s_end in segments:
                    if s_start < need_end and s_end > need_start:
                        is_overlap = True
                        break
                
                if is_overlap:
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
        
        perfect_matches = [] # 符合特定需求 (或一般需求的一般員工)
        overqualified = []   # 符合一般需求，但擁有特殊角色 (應保留)
        
        for emp in self.employees:
            # 檢查是否可上此班別
            if shift_name not in emp.get('allowed_shifts', []):
                continue
            
            emp_roles = emp.get('roles', [])
            
            # 1. 如果有特定角色需求
            if required_roles:
                if any(r in emp_roles for r in required_roles):
                    perfect_matches.append(emp)
                continue # 如果有需求限制，不符合者直接略過 (Strict Filtering)
            
            # 2. 如果是一般需求 (無特定角色)
            # 檢查是否為"持有特殊角色的員工" (例如組長)
            # 定義：持有非 '一般員工' 的角色視為特殊
            is_special = any(r != "一般員工" and r != "一般員工" for r in emp_roles)
            
            if is_special:
                overqualified.append(emp) # 保留實力，最後才用
            else:
                perfect_matches.append(emp) # 優先使用
        
        # 按公平性排序 (已排班數少的優先，且週末班加權扣分)
        def get_shift_count(e):
            hist = self.history[e['name']]
            # 優先級分數 = 總班數 + (週末班數 * 1.5)
            # 這樣可以讓已經上過週末班的人，排序往後移
            return len(hist['worked_days']) + (hist.get('weekend_count', 0) * 1.5)
        
        perfect_matches.sort(key=get_shift_count)
        overqualified.sort(key=get_shift_count)
        
        # 當沒有特定需求時，優先使用 perfect_matches (一般員工)，用光了才用 overqualified (組長)
        # 這樣可以避免組長被一般勤務消耗掉
        return perfect_matches + overqualified


    def _update_employee_history(self, emp_name, date_str, shift_name):
        """更新員工歷史紀錄"""
        self.history[emp_name]['worked_days'].add(date_str)
        self.history[emp_name]['consecutive_days'] += 1
        
        # 檢查是否為週末 (Sat=5, Sun=6)
        try:
            y, m, d = map(int, date_str.split('-'))
            if date(y, m, d).weekday() >= 5:
                self.history[emp_name]['weekend_count'] = self.history[emp_name].get('weekend_count', 0) + 1
        except:
            pass

        # 更新最後下班時間
        try:
            shift_time = self.shifts[shift_name].get('time', '00:00-23:59')
            segments = self._parse_shift_segments(shift_time)
            if segments:
                self.history[emp_name]['last_shift_end_minutes'] = segments[-1][1]
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

    def get_employee_schedule_dataframe(self):
        """
        生成以員工為主的班表 (Rows: Employees, Cols: Dates)
        休息日顯示 'X'
        """
        import pandas as pd
        dates_cols = [d.strftime("%Y-%m-%d") for d in self.dates]
        
        data = []
        
        # 建立快速查找表: Date -> Shift -> People
        # 但我們需要 Employee -> Date -> Shift
        emp_schedule = {e['name']: {} for e in self.employees}
        
        for d_str, shifts in self.schedule.items():
            for s_name, people in shifts.items():
                for p in people:
                    if p in emp_schedule:
                        # 假設一人一天一班
                        emp_schedule[p][d_str] = s_name
        
        # 2. 填充資料
        for emp in self.employees:
            row = {"Name": emp['name'], "Roles": ",".join(emp.get('roles', []))}
            
            for d_str in dates_cols:
                # 如果有排班顯示班別，否則顯示 'X' (休息)
                val = emp_schedule[emp['name']].get(d_str, "X")
                row[d_str] = val
            
            data.append(row)
            
        return pd.DataFrame(data)


    def _calculate_shift_utility(self, shift_name, needs):
        """Calculates utility score of a shift based on how many needs it covers."""
        score = 0
        shift_info = self.shifts.get(shift_name)
        if not shift_info: return 0
        
        try:
            segments = self._parse_shift_segments(shift_info.get("time"))
        except:
            return 0
            
        for need in needs:
            # Need info: time_range, priority, min_people
            # Calculate overlap duration
            try:
                n_start, n_end = self._parse_time_range(need['time_range'])
                
                overlap_min = 0
                for s_start, s_end in segments:
                    # Overlap logic
                    o_start = max(s_start, n_start)
                    o_end = min(s_end, n_end)
                    if o_end > o_start:
                        overlap_min += (o_end - o_start)
                
                if overlap_min > 0:
                    # Weight by priority
                    # CRITICAL (Biz Hours) = 3
                    # HIGH (Rule with Role) = 2
                    # MEDIUM (Rule no Role) = 1
                    prio_weight = 3 if need.get('priority') == 'CRITICAL' else (2 if need.get('priority') == 'HIGH' else 1)
                    score += overlap_min * prio_weight
                    
                    # Heuristic: Bonus for aligning with start time (reduces gaps)
                    # If shift starts at or before need start, it fills the beginning optimally.
                    if s_start <= n_start:
                        score += overlap_min * 0.5
            except:
                continue
        
        return score

    def _get_shift_timeline(self, shift_name):
        """Get 5-min resolution timeline for a shift (1=active, 0=inactive)"""
        timeline = [0] * 289 # 00:00 to 24:00 (last index 288 for 24:00)
        shift_info = self.shifts.get(shift_name)
        if not shift_info: return timeline
        
        try:
            segments = self._parse_shift_segments(shift_info.get("time"))
            for start, end in segments:
                s_idx = max(0, int(start // 5))
                e_idx = min(288, int(end // 5))
                for i in range(s_idx, e_idx):
                    timeline[i] = 1
        except:
            pass
        return timeline

    def schedule_one_day(self, current_date):
        """
        Constraint-First Scheduling Algorithm (Constraints -> Shifts -> People)
        """
        date_str = current_date.strftime("%Y-%m-%d")
        day_log = []
        
        # Global Limits
        max_daily_staff = self.daily_limits.get('max_staff_per_day', 50)
        enforce_daily_limit = self.daily_limits.get('enforce_limit', True)

        # Initialize schedule structure for today
        self.schedule[date_str] = {s: [] for s in self.shifts}

        # 1. Build Demand Profile (5-min resolution)
        # 288 slots (5 mins per slot). 
        T_MAX = 288
        general_demand = [0] * T_MAX
        role_demands = {} # role -> [0]*T_MAX
        
        # Helper to add demand
        def add_demand(target_timeline, start, end, count):
             s = max(0, int(start // 5))
             e = min(T_MAX, int(end // 5))
             for i in range(s, e):
                 target_timeline[i] = max(target_timeline[i], count)

        # 1.1 Business Hours (Min 1 person) - General Demand
        if self.business_hours.get("enforce_coverage", False):
             try:
                 bs = self._parse_time(self.business_hours["start"])
                 be = self._parse_time(self.business_hours["end"])
                 add_demand(general_demand, bs, be, 1)
             except: pass

        # 1.2 Coverage Rules
        for rule in self.coverage_rules:
             try:
                 rs, re = self._parse_time_range(rule["time_range"])
                 needed = rule["min_people"]
                 roles = rule.get("required_roles", [])
                 if not roles and rule.get("required_role"):
                     roles = [rule.get("required_role")]
                 
                 add_demand(general_demand, rs, re, needed)
                 
                 for r in roles:
                     if r not in role_demands: role_demands[r] = [0] * T_MAX
                     add_demand(role_demands[r], rs, re, 1) 
             except: pass

        # 2. Comparison Logic for Shifts
        all_shift_timelines = {s: self._get_shift_timeline(s) for s in self.shifts}
        
        # Skeleton: List of (shift_name, assigned_role_filter)
        skeleton = []
        current_general_coverage = [0] * T_MAX
        current_role_coverage = {r: [0]*T_MAX for r in role_demands}
        
        # Helper: Check Shift Limits
        def can_add_shift(s_name):
            # 1. Daily Limit
            if enforce_daily_limit and len(skeleton) >= max_daily_staff:
                return False
            # 2. Shift Specific Limit
            s_info = self.shifts.get(s_name)
            if s_info and s_info.get("enforce_headcount", False):
                limit = s_info.get("required_people", 99)
                current_count = sum(1 for s, _ in skeleton if s == s_name)
                if current_count >= limit:
                    return False
            return True

        # 3. Solve Role Demands First
        for role, r_demand in role_demands.items():
             while True:
                 # Check Limit
                 if enforce_daily_limit and len(skeleton) >= max_daily_staff:
                     day_log.append(f"⚠️ 達到每日人數上限 ({max_daily_staff})，停止排班 (角色: {role})")
                     break

                 # Check Unmet Role Demand
                 unmet = [max(0, r_demand[i] - current_role_coverage[role][i]) for i in range(T_MAX)]
                 if sum(unmet) == 0: break
                 
                 # Find best shift covering unmet
                 best_s, best_score = None, -1
                 
                 for s_name, timeline in all_shift_timelines.items():
                     if not self.shifts[s_name].get('time'): continue
                     if not can_add_shift(s_name): continue # CHECK LIMITS

                     # Utility: How much UNMET demand does it cover?
                     score = 0
                     covered_minutes = 0
                     
                     first_unmet = -1
                     for k in range(T_MAX):
                         if timeline[k] and unmet[k]:
                             score += 10 # Base score per slot covered
                             covered_minutes += 5
                             if first_unmet == -1: first_unmet = k
                     
                     if covered_minutes == 0: continue
                     
                     # Start Alignment Bonus
                     if first_unmet > 0 and timeline[first_unmet-1] == 0:
                         score += 500 
                     
                     # A2C Bonus
                     if "A2C" in s_name: score += 5
                     
                     if score > best_score:
                         best_score = score
                         best_s = s_name
                 
                 if not best_s:
                     # Attempted all shifts, none valid (often due to limits)
                     day_log.append(f"⚠️ 無法滿足角色需求: {role} (可能因班別限制)")
                     break
                 
                 # Commit Shift
                 skeleton.append((best_s, role))
                 # Update coverages
                 tl = all_shift_timelines[best_s]
                 for i in range(T_MAX):
                     if tl[i]:
                         current_general_coverage[i] += 1
                         current_role_coverage[role][i] += 1
        
        # 4. Solve General Demands
        while True:
            # Check Limit
            if enforce_daily_limit and len(skeleton) >= max_daily_staff:
                 day_log.append(f"⚠️ 達到每日人數上限 ({max_daily_staff})，停止排班 (一般覆蓋)")
                 break

            unmet = [max(0, general_demand[i] - current_general_coverage[i]) for i in range(T_MAX)]
            if sum(unmet) == 0: break
            
            best_s, best_score = None, -1
            
            for s_name, timeline in all_shift_timelines.items():
                if not self.shifts[s_name].get('time'): continue
                if not can_add_shift(s_name): continue # CHECK LIMITS

                score = 0
                first_unmet = -1
                for k in range(T_MAX):
                    if timeline[k] and unmet[k]:
                        score += 10
                        if first_unmet == -1: first_unmet = k
                
                if score == 0: continue
                
                if first_unmet > 0 and timeline[first_unmet-1] == 0:
                     score += 500 # Alignment Bonus
                
                if score > best_score:
                    best_score = score
                    best_s = s_name
            
            if not best_s:
                day_log.append("⚠️ 無法滿足覆蓋需求 (一般) - 可能因班別限制或無合適班次")
                break
            
            skeleton.append((best_s, None))
            tl = all_shift_timelines[best_s]
            for i in range(T_MAX):
                if tl[i]: current_general_coverage[i] += 1
        
        # 5. Assign People to Skeleton
        assigned_peeps = set()

        skeleton.sort(key=lambda x: 0 if x[1] else 1) 
        
        for shift_name, required_role in skeleton:
            # Hard Safety Check (Should be handled by skeleton limiting, but safe to keep)
            if enforce_daily_limit and len(assigned_peeps) >= max_daily_staff:
                day_log.append(f"⚠️ (Assign) 已達最大人數 {max_daily_staff}，略過 {shift_name}")
                continue

            # Find Candidate
            role_filter = [required_role] if required_role else []
            candidates = self._get_available_candidates(current_date, shift_name, role_filter)
            
            # Enhanced Fairness Sorting: 
            # 1. Total workload (fewer days worked = higher priority)
            # 2. Shift diversity (penalize if person worked this shift type recently)
            def fairness_score(c):
                name = c['name']
                total_days = len(self.history[name]['worked_days'])
                
                # Check shift diversity: count how many times this person worked THIS shift
                shift_count = 0
                for d_str in self.history[name]['worked_days']:
                    if d_str in self.schedule:
                        if name in self.schedule[d_str].get(shift_name, []):
                            shift_count += 1
                
                # Penalty for shift repetition (encourage variety)
                diversity_penalty = shift_count * 10
                
                return total_days + diversity_penalty
            
            candidates.sort(key=fairness_score)
            
            picked = None
            for cand in candidates:
                if cand['name'] not in assigned_peeps:
                    is_ok, reason = self._is_available(cand, current_date, shift_name)
                    if is_ok:
                        if required_role and required_role not in cand.get('roles', []):
                             continue
                        picked = cand
                        break
            
            if picked:
                self.schedule[date_str][shift_name].append(picked['name'])
                assigned_peeps.add(picked['name'])
                self._update_employee_history(picked['name'], date_str, shift_name)
                
                if required_role:
                    day_log.append(f"✓ {date_str} {shift_name} 指定 '{required_role}': {picked['name']}")
            else:
                role_msg = f"({required_role})" if required_role else ""
                day_log.append(f"⚠️ 缺工警示: 無法找到人值班 {shift_name} {role_msg}")

        day_log.append(f"📊 {date_str} 共分配 {len(assigned_peeps)} 人")
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

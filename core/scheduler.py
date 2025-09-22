"""
核心排班演算法 (Scheduler Algorithm)
--- 最終章：智慧排班引擎 ---
"""
import datetime
from calendar import monthrange
from typing import List, Dict, Optional
from collections import defaultdict
import random

from .models import Employee, Rule, Shift

# 班別定義
SHIFTS = [
    Shift(name="9-17.5", start_time="09:00", end_time="17:30", color="#AED9E0"),
    Shift(name="9.5-18", start_time="09:30", end_time="18:00", color="#FFA69E"),
    Shift(name="10.5-18", start_time="10:30", end_time="18:00", color="#CDB4DB"),
    Shift(name="10.5-19", start_time="10:30", end_time="19:00", color="#B8F2E6"),
    Shift(name="10.5-20.5", start_time="10:30", end_time="20:30", color="#FFB4A2"),
    Shift(name="13-21.5", start_time="13:00", end_time="21:30", color="#FFC8DD"),
    Shift(name="14-22", start_time="14:00", end_time="22:00", color="#D0F4DE"),
    Shift(name="10-18.5", start_time="10:00", end_time="18:30", color="#CDB4DB"),
    Shift(name="休", start_time="", end_time="", color="#B5EAEA"),
    Shift(name="例休", start_time="", end_time="", color="#FFABAB"),
]

class Scheduler:
    """
    智慧排班引擎，能夠理解並執行複雜的排班規則。
    """
    def __init__(self, emp_controller, rule_controller, assignments):
        self.emp_controller = emp_controller
        self.rule_controller = rule_controller
        self.assignments = assignments

        self.all_employees = {emp.id: emp for emp in self.emp_controller.get_all_employees()}
        self.all_rules = {rule.id: rule for rule in self.rule_controller.get_all_rules()}
        
        self.shift_map = {s.name: s for s in SHIFTS}
        self.work_shifts = [s for s in SHIFTS if s.name not in ["休", "例休"]]
        self._calculate_shift_durations()

        print("\n--- 🧠 智慧排班引擎已啟動 ---")

    def _calculate_shift_durations(self):
        self.shift_durations = {}
        for shift in self.work_shifts:
            try:
                start = datetime.datetime.strptime(shift.start_time, "%H:%M")
                end = datetime.datetime.strptime(shift.end_time, "%H:%M")
                duration = (end - start).total_seconds() / 3600
                if duration < 0: duration += 24 # 處理跨夜班
                self.shift_durations[shift.name] = duration
            except ValueError:
                self.shift_durations[shift.name] = 0

    def _get_employee_rules(self, emp_id: str) -> List[Rule]:
        """獲取應用於某位員工的所有規則（個人規則 + 全域規則）"""
        rule_ids = self.assignments["global"] + self.assignments["employees"].get(emp_id, [])
        return [self.all_rules[rid] for rid in set(rule_ids) if rid in self.all_rules]

    def generate_schedule(self, year: int, month: int) -> Dict:
        print(f"--- 正在為 {year}年 {month:02d}月 生成智慧班表 ---")
        
        num_days = monthrange(year, month)[1]
        dates = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
        
        employee_ids = list(self.assignments["employees"].keys())
        
        # 1. 初始化班表
        schedule = {emp_id: {day: None for day in dates} for emp_id in employee_ids}
        
        # 2. 應用「硬規則」(預先排定)
        self._apply_hard_constraints(schedule, dates)

        # 3. 主排班迴圈
        for day in dates:
            # 規則 6: 處理班別連動
            count_13_21_5 = sum(1 for emp_id in employee_ids if schedule[emp_id][day] == "13-21.5")
            
            for emp_id in employee_ids:
                if schedule[emp_id][day] is not None: # 已被硬規則排定
                    continue

                employee = self.all_employees[emp_id]
                rules = self._get_employee_rules(emp_id)
                
                # 獲取今天所有合法的班別選項
                valid_shifts = self._get_valid_shifts_for_employee_on_day(
                    employee, day, schedule, rules, count_13_21_5
                )

                # 選擇一個班別
                if valid_shifts:
                    # 簡單策略：從合法選項中隨機選一個
                    # TODO: 未來可優化為基於工時平衡等更複雜的策略
                    chosen_shift = random.choice(valid_shifts)
                    schedule[emp_id][day] = chosen_shift.name
                else:
                    # 如果沒有任何合法班別，暫時標記為未排定
                    schedule[emp_id][day] = "未排定"
        
        # 4. 格式化輸出
        return self._format_schedule_for_gui(schedule, dates, employee_ids)

    def _apply_hard_constraints(self, schedule, dates):
        """處理指定休息日和指定班別的規則"""
        for emp_id, rules_ids in self.assignments["employees"].items():
            rules = [self.all_rules[rid] for rid in rules_ids if rid in self.all_rules]
            for rule in rules:
                params = rule.params
                if rule.rule_type == "ASSIGN_FIXED_OFF_DAYS":
                    for date_str in params.get("dates", []):
                        day = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                        if day in dates:
                            schedule[emp_id][day] = params.get("shift_name", "休")
                
                elif rule.rule_type == "ASSIGN_SPECIFIC_SHIFT":
                    date_str = params.get("date")
                    day = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    if day in dates:
                        schedule[emp_id][day] = params.get("shift_name")

    def _get_valid_shifts_for_employee_on_day(self, employee, day, schedule, rules, count_13_21_5):
        """根據所有規則，過濾出某人某天可以上的所有班別"""
        possible_shifts = self.work_shifts + [self.shift_map["休"]]
        valid_shifts = []

        for shift in possible_shifts:
            is_valid = True
            
            # 規則 3: 檢查級別限制
            for rule in rules:
                if rule.rule_type == "REQUIRED_LEVEL_FOR_SHIFT":
                    if shift.name == rule.params["shift_name"] and employee.level != rule.params["level"]:
                        is_valid = False; break
            if not is_valid: continue

            # 規則 5: 檢查晚班接早班
            yesterday = day - datetime.timedelta(days=1)
            if yesterday in schedule[employee.id]:
                yesterday_shift = schedule[employee.id][yesterday]
                for rule in rules:
                    if rule.rule_type == "LATE_SHIFT_THEN_EARLY_SHIFT":
                        if yesterday_shift in rule.params["late_shifts"] and shift.name != rule.params["early_shift"]:
                           # 這是一個軟性規則，表示"優先"，暫時不在此做硬性過濾
                           pass

            # 規則 6: 班別連動
            if shift.name == "10.5-20.5" and count_13_21_5 >= 2:
                is_valid = False; continue
            if shift.name == "10.5-19" and count_13_21_5 < 2:
                # 假設條件是 "如果當天有兩位13-21.5，則安排為10.5-19"
                # 這代表當人數不足2位時，10.5-19 不應是優先選項
                pass # 軟性規則

            # TODO: 增加更多規則檢查...
            # 例如：最低工時需要在排班結束後統一計算和調整

            if is_valid:
                valid_shifts.append(shift)
        
        return valid_shifts

    def _format_schedule_for_gui(self, schedule, dates, employee_ids):
        """將內部班表格式轉換為 GUI 表格需要的格式"""
        employee_names = [self.all_employees[eid].name for eid in employee_ids]
        headers = ["日期"] + employee_names
        data = []

        for day in dates:
            row = [day.strftime("%Y-%m-%d (%a)")]
            for emp_id in employee_ids:
                shift_name = schedule[emp_id].get(day, "錯誤")
                row.append(shift_name)
            data.append(row)
            
        return {"headers": headers, "data": data}


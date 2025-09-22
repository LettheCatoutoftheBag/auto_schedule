"""
核心排班演算法 (Scheduler Algorithm)
--- 已升級為可接收個人化規則指派的結構 ---
"""
from typing import List, Dict
import random
from calendar import monthrange
import datetime
from .models import Employee, Rule, Shift

# 暫時定義一些班別用於測試
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
    核心排班演算法類別。
    """
    def __init__(self, employees: List[Employee], rules: List[Rule], assignments: Dict[str, List[str]]):
        self.all_employees = {emp.id: emp for emp in employees}
        self.all_rules = {rule.id: rule for rule in rules}
        self.assignments = assignments # 結構: { "員工ID": ["規則ID1", "規則ID2", ...] }

        print("\n--- 🧠 排班核心 (Scheduler) 已初始化 (拼圖模式) ---")
        print("  - 員工與規則的對應關係:")
        for emp_id, rule_ids in self.assignments.items():
            emp_name = self.all_employees[emp_id].name if emp_id in self.all_employees else "未知員工"
            rule_names = [self.all_rules[rid].name for rid in rule_ids if rid in self.all_rules]
            print(f"    - {emp_name}: {rule_names}")
        print("---------------------------------")

    def generate_schedule(self, year: int, month: int) -> Dict:
        """
        為指定的年份和月份生成班表。
        """
        print(f"--- 正在為 {year}年 {month:02d}月 生成班表 ---")
        
        # 準備日期範圍
        num_days = monthrange(year, month)[1]
        date_range = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
        
        # 僅為有被指派規則的員工排班（或所有員工，可調整）
        employee_ids_to_schedule = list(self.assignments.keys())
        employee_names_to_schedule = [self.all_employees[eid].name for eid in employee_ids_to_schedule]

        headers = ["日期"] + employee_names_to_schedule
        schedule_data = []

        # 執行排班演算法 (目前仍為隨機，但已準備好接收個人化規則)
        # TODO: 下一步就是將 self.assignments 傳入真正的 CSP 演算法
        for day in date_range:
            daily_schedule = [day.strftime("%Y-%m-%d (%a)")]
            for emp_id in employee_ids_to_schedule:
                # 這裡的演算法未來會檢查 self.assignments[emp_id] 來套用規則
                assigned_shift = random.choice(SHIFTS)
                daily_schedule.append(assigned_shift.name)
            schedule_data.append(daily_schedule)

        print(f"--- ✅ 班表生成完畢 ---")
        return {"headers": headers, "data": schedule_data}


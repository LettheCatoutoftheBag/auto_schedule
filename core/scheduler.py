"""
核心排班演算法 (Scheduler Algorithm)
這裡是專案的「大腦」，負責根據所有條件來生成班表。
"""
from typing import List, Dict
import random
from calendar import monthrange
import datetime
from .models import Employee, Rule, Shift

# 暫時定義一些班別用於測試
SHIFTS = [
    Shift(name="早班", start_time="09:00", end_time="17:00", color="#AED9E0"),
    Shift(name="晚班", start_time="14:00", end_time="22:00", color="#FFA69E"),
    Shift(name="休息", start_time="", end_time="", color="#B8F2E6"),
]

class Scheduler:
    """
    核心排班演算法類別。
    負責根據員工、規則和日期範圍來生成班表。
    """
    def __init__(self, employees: List[Employee], rules: List[Rule]):
        self.employees = employees
        self.rules = rules # 註：目前演算法尚未使用規則
        self.employee_names = [emp.name for emp in self.employees]
        print("\n--- 🧠 排班核心 (Scheduler) 已初始化 ---")
        print(f"  - 參與排班員工: {self.employee_names}")
        print(f"  - 套用規則數量: {len(self.rules)}")
        print("---------------------------------")

    def generate_schedule(self, year: int, month: int) -> Dict:
        """
        為指定的年份和月份生成班表。

        Args:
            year (int): 目標年份
            month (int): 目標月份

        Returns:
            dict: 生成的班表。格式為：
                  { "headers": ["日期", "員工1", "員工2", ...],
                    "data": [
                        ["2025-09-01", "早班", "休息", ...],
                        ...
                    ]
                  }
        """
        print(f"--- 正在為 {year}年 {month:02d}月 生成班表 ---")
        
        # 準備日期範圍
        num_days = monthrange(year, month)[1]
        date_range = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
        
        headers = ["日期"] + self.employee_names
        schedule_data = []

        # 執行排班演算法 (目前為隨機)
        for day in date_range:
            daily_schedule = [day.strftime("%Y-%m-%d (%a)")]
            for _ in self.employees:
                assigned_shift = random.choice(SHIFTS)
                daily_schedule.append(assigned_shift.name)
            schedule_data.append(daily_schedule)

        print(f"--- ✅ 班表生成完畢 ---")
        return {"headers": headers, "data": schedule_data}


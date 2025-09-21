"""
核心排班演算法 (Scheduler Algorithm)
這裡是專案的「大腦」，負責根據所有條件來生成班表。
"""
from typing import List, Dict
import random
from .models import Employee, Rule, Shift

# 暫時定義一些班別用於測試
SHIFTS = [
    Shift(name="早班", start_time="09:00", end_time="17:00", color="#AED9E0"),
    Shift(name="晚班", start_time="14:00", end_time="22:00", color="#FFA69E"),
    Shift(name="休息", start_time="", end_time="", color="#B8F2E6"),
]

def generate_schedule(employees: List[Employee], rules: List[Rule], date_range: List[str]) -> Dict:
    """
    根據員工、規則和日期範圍來生成班表。
    
    階段二：實現一個基礎的隨機演算法作為原型。
    它會為每個員工在每一天隨機指派一個班別。
    """
    print("\n--- 🧠 開始生成班表 (基礎隨機演算法) ---")
    
    schedule_result = {}  # 最終的排班結果, 結構: { '日期': { '員工ID': Shift } }

    for date in date_range:
        schedule_result[date] = {}
        for emp in employees:
            # TODO: 在後續階段，這裡會被複雜的規則檢查所取代
            # 目前只是隨機選擇一個班別
            assigned_shift = random.choice(SHIFTS)
            schedule_result[date][emp.id] = assigned_shift
    
    print("--- ✅ 班表生成完畢 ---")
    
    # 為了方便檢視，印出結果的預覽
    print("\n--- 📊 班表預覽 ---")
    for date, daily_shifts in list(schedule_result.items()):
        print(f"📅 日期: {date}")
        for emp_id, shift in daily_shifts.items():
            # 在員工列表中找到對應的員工名字
            emp_name = next((e.name for e in employees if e.id == emp_id), "未知員工")
            print(f"  - {emp_name}: {shift.name}")
    print("------------------\n")

    return schedule_result


"""
新增檔案：員工控制器 (Employee Controller)
這是專門用來處理所有「員工相關操作」的商業邏輯中心。
"""
from typing import List, Optional
from .models import Employee
from .data_manager import DataManager

class EmployeeController:
    """
    封裝了所有員工資料的增、刪、改、查 (CRUD) 操作。
    """
    def __init__(self, data_path: str = "data/employees.json"):
        # 加入診斷訊息
        print(f"\n--- 正在初始化 EmployeeController ---")
        print(f"  - 目標資料檔案: '{data_path}'")
        self.manager = DataManager(data_path)
        self.employees: List[Employee] = self._load_employees()
        print(f"  - 從檔案成功載入 {len(self.employees)} 位員工資料。")
        print(f"--- EmployeeController 初始化完畢 ---")

    def _load_employees(self) -> List[Employee]:
        """從檔案載入員工資料並轉換成 Employee 物件列表"""
        data = self.manager.load_data()
        return [Employee(**emp_data) for emp_data in data]

    def _save_employees(self):
        """將目前的員工物件列表轉換成字典並存檔"""
        data_to_save = [emp.__dict__ for emp in self.employees]
        self.manager.save_data(data_to_save)

    def add_employee(self, name: str, level: str) -> Employee:
        """新增一位員工"""
        new_employee = Employee(name=name, level=level)
        self.employees.append(new_employee)
        self._save_employees()
        print(f"  ✅ 已新增員工: {name} (級別: {level})")
        return new_employee

    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """透過 ID 尋找員工"""
        for emp in self.employees:
            if emp.id == employee_id:
                return emp
        return None

    def update_employee(self, employee_id: str, new_name: str, new_level: str) -> bool:
        """更新員工資訊"""
        employee = self.get_employee_by_id(employee_id)
        if employee:
            employee.name = new_name
            employee.level = new_level
            self._save_employees()
            print(f"  🔄️  已更新員工 ID {employee_id[:6]}... 為: {new_name}, {new_level}")
            return True
        print(f"  ❌ 更新失敗: 找不到員工 ID {employee_id[:6]}...")
        return False

    def delete_employee(self, employee_id: str) -> bool:
        """刪除一位員工"""
        employee = self.get_employee_by_id(employee_id)
        if employee:
            self.employees.remove(employee)
            self._save_employees()
            print(f"  🗑️  已刪除員工: {employee.name}")
            return True
        print(f"  ❌ 刪除失敗: 找不到員工 ID {employee_id[:6]}...")
        return False

    def get_all_employees(self) -> List[Employee]:
        """獲取所有員工的列表"""
        return self.employees


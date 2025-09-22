"""
新增檔案：規則控制器 (Rule Controller)
專門處理所有「排班規則」的商業 logique 中心。
"""
from typing import List, Optional, Dict
# --- 修正點 1: 匯入 PyQt 的信號機制 ---
from PyQt6.QtCore import QObject, pyqtSignal
from .models import Rule
from .data_manager import DataManager

# --- 修正點 2: 讓 Controller 繼承 QObject 才能使用信號 ---
class RuleController(QObject):
    """
    封裝了所有排班規則的增、刪、改、查 (CRUD) 操作。
    """
    # --- 修正點 3: 定義一個信號，當規則庫有變動時發出 ---
    rules_changed = pyqtSignal()

    def __init__(self, data_path: str = "data/rules_library.json"):
        super().__init__() # <-- QObject 的初始化
        print(f"\n--- 正在初始化 RuleController ---")
        print(f"  - 目標資料檔案: '{data_path}'")
        self.manager = DataManager(data_path)
        self.rules: List[Rule] = self._load_rules()
        print(f"  - 從檔案成功載入 {len(self.rules)} 條規則。")
        print(f"--- RuleController 初始化完畢 ---")

    def _load_rules(self) -> List[Rule]:
        data = self.manager.load_data()
        return [Rule(**rule_data) for rule_data in data]

    def _save_rules_and_notify(self):
        """
        一個新的內部函式，負責存檔並發出變更信號。
        """
        data_to_save = [rule.__dict__ for rule in self.rules]
        self.manager.save_data(data_to_save)
        # --- 修正點 4: 在每次存檔後，發射信號通知所有監聽者 ---
        self.rules_changed.emit()

    def add_rule(self, name: str, rule_type: str, params: Dict) -> Rule:
        new_rule = Rule(name=name, rule_type=rule_type, params=params)
        self.rules.append(new_rule)
        self._save_rules_and_notify() # 使用新函式
        print(f"  ✅ 已新增規則: {name}")
        return new_rule

    def get_rule_by_id(self, rule_id: str) -> Optional[Rule]:
        return next((rule for rule in self.rules if rule.id == rule_id), None)

    def update_rule(self, rule_id: str, new_name: str, new_type: str, new_params: Dict) -> bool:
        rule = self.get_rule_by_id(rule_id)
        if rule:
            rule.name = new_name
            rule.rule_type = new_type
            rule.params = new_params
            self._save_rules_and_notify() # 使用新函式
            print(f"  🔄️ 已更新規則 ID {rule_id[:6]}...")
            return True
        print(f"  ❌ 更新失敗: 找不到規則 ID {rule_id[:6]}...")
        return False

    def delete_rule(self, rule_id: str) -> bool:
        rule = self.get_rule_by_id(rule_id)
        if rule:
            self.rules.remove(rule)
            self._save_rules_and_notify() # 使用新函式
            print(f"  🗑️ 已刪除規則: {rule.name}")
            return True
        print(f"  ❌ 刪除失敗: 找不到規則 ID {rule_id[:6]}...")
        return False

    def get_all_rules(self) -> List[Rule]:
        return self.rules


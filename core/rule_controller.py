"""
新增檔案：規則控制器 (Rule Controller)
專門處理所有「排班規則」的商業邏輯中心。
"""
from typing import List, Optional, Dict
from .models import Rule
from .data_manager import DataManager

class RuleController:
    """
    封裝了所有排班規則的增、刪、改、查 (CRUD) 操作。
    """
    def __init__(self, data_path: str = "data/rules_library.json"):
        print(f"\n--- 正在初始化 RuleController ---")
        print(f"  - 目標資料檔案: '{data_path}'")
        self.manager = DataManager(data_path)
        self.rules: List[Rule] = self._load_rules()
        print(f"  - 從檔案成功載入 {len(self.rules)} 條規則。")
        print(f"--- RuleController 初始化完畢 ---")

    def _load_rules(self) -> List[Rule]:
        """從檔案載入規則資料並轉換成 Rule 物件列表"""
        data = self.manager.load_data()
        return [Rule(**rule_data) for rule_data in data]

    def _save_rules(self):
        """將目前的規則物件列表轉換成字典並存檔"""
        data_to_save = [rule.__dict__ for rule in self.rules]
        self.manager.save_data(data_to_save)

    def add_rule(self, name: str, rule_type: str, params: Dict) -> Rule:
        """新增一條規則"""
        new_rule = Rule(name=name, rule_type=rule_type, params=params)
        self.rules.append(new_rule)
        self._save_rules()
        print(f"  ✅ 已新增規則: {name}")
        return new_rule

    def get_rule_by_id(self, rule_id: str) -> Optional[Rule]:
        """透過 ID 尋找規則"""
        return next((rule for rule in self.rules if rule.id == rule_id), None)

    def update_rule(self, rule_id: str, new_name: str, new_type: str, new_params: Dict) -> bool:
        """更新規則資訊"""
        rule = self.get_rule_by_id(rule_id)
        if rule:
            rule.name = new_name
            rule.rule_type = new_type
            rule.params = new_params
            self._save_rules()
            print(f"  🔄️ 已更新規則 ID {rule_id[:6]}...")
            return True
        print(f"  ❌ 更新失敗: 找不到規則 ID {rule_id[:6]}...")
        return False

    def delete_rule(self, rule_id: str) -> bool:
        """刪除一條規則"""
        rule = self.get_rule_by_id(rule_id)
        if rule:
            self.rules.remove(rule)
            self._save_rules()
            print(f"  🗑️ 已刪除規則: {rule.name}")
            return True
        print(f"  ❌ 刪除失敗: 找不到規則 ID {rule_id[:6]}...")
        return False

    def get_all_rules(self) -> List[Rule]:
        """獲取所有規則的列表"""
        return self.rules

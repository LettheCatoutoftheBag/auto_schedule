"""
定義專案中所有核心的資料結構 (Data Models)。
這就像是定義了「員工」、「班別」、「規則」等物件的藍圖。
"""
from dataclasses import dataclass, field
from typing import List, Any
from abc import ABC, abstractmethod
import uuid

# 使用 dataclass 來簡潔地定義資料結構
# field(default_factory=...) 讓每個新建立的員工都有一個獨一無二的 ID
@dataclass
class Employee:
    """代表一位員工的資料結構"""
    name: str
    level: str  # 例如: "吧檯手", "門職人員"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Shift:
    """代表一個班別的資料結構"""
    name: str       # 例如: "早班", "晚班", "例休"
    start_time: str
    end_time: str
    color: str      # 用於 GUI 顯示的顏色, e.g., "#A0E7E5"

# --- 規則系統的基礎 ---
class Rule(ABC):
    """
    所有排班規則的「抽象基礎類別」。
    這定義了每一個「規則拼圖」都必須具備的功能。
    """
    @abstractmethod
    def get_description(self) -> str:
        """回傳這個規則的文字描述"""
        pass

    @abstractmethod
    def evaluate(self, schedule: Any) -> bool:
        """
        評估一個排班表是否滿足此規則。
        這是規則的核心邏輯。
        """
        pass

# 範例規則：你可以基於 Rule 類別創造各式各樣的規則
@dataclass
class MaxHoursPerWeekRule(Rule):
    """一週最大工時規則"""
    employee_id: str
    max_hours: int

    def get_description(self) -> str:
        return f"員工({self.employee_id[:6]}...)每週工時不超過 {self.max_hours} 小時"

    def evaluate(self, schedule: Any) -> bool:
        # TODO: 未來在此實現檢查邏輯
        print(f"正在檢查 {self.get_description()}...")
        return True # 暫時總是回傳 True


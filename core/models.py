"""
核心資料模型 (Core Data Models)
定義專案中所有核心物件的結構，例如：員工、班別、規則。
"""
import uuid
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Employee:
    """定義一位員工的資料模型"""
    name: str
    level: str  # e.g., "吧檯手", "門職人員"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Shift:
    """定義一個班別的資料模型"""
    name: str
    start_time: str
    end_time: str
    color: str # 用於在 GUI 中顯示的顏色

@dataclass
class Rule:
    """
    定義一條排班規則的資料模型
    這是我們「拼圖」的核心。
    """
    name: str      # 給使用者看的規則名稱, e.g., "單週工時上限"
    rule_type: str # 給程式看的規則類型, e.g., "MAX_HOURS_PER_WEEK"
    params: Dict   # 規則的具體參數, e.g., {"hours": 40, "level": "吧檯手"}
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


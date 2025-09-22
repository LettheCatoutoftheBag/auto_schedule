"""
新增檔案：規則引擎 (Rule Engine)
這是專案中所有「規則定義」和「邏輯翻譯」的中央儲存庫。
任何需要理解或顯示規則的模組，都應該從這裡引用。
"""
from .models import Rule

# --- 規則定義層 (翻譯機) ---
# 將程式邏輯對應到使用者看得懂的選項和輸入框
# 格式: "顯示名稱": {"type": "內部類型", "params": {"參數名": ("顯示標籤", [選項] 或 "number")}}
RULE_DEFINITIONS = {
    "單週工時上限": {
        "type": "MAX_HOURS_PER_WEEK",
        "params": {"hours": ("小時", "number")},
        "description": "設定員工每週最多工作幾小時。"
    },
    "最長連續上班天數": {
        "type": "MAX_CONSECUTIVE_DAYS",
        "params": {"days": ("天", "number")},
        "description": "設定員工最多可以連續上班幾天。"
    },
    "指定班別所需級別": {
        "type": "REQUIRED_LEVEL",
        "params": {
            "level": ("所需級別", ["吧檯手"]),
            "shift": ("指定班別", ["9.5-18"])
        },
        "description": "設定某個班別必須由特定級別的員工擔任。"
    }
}

# --- 輔助函式：將 Rule 物件轉為易讀的字串 (超．升級版) ---
def get_rule_display_text(rule: Rule) -> str:
    """將規則物件轉換成一行易於理解的描述文字"""
    
    # 建立一個描述句
    description = f"【{rule.name}】 "
    params = rule.params

    # 根據規則類型，生成不同的自然語言描述
    if rule.rule_type == "MAX_HOURS_PER_WEEK":
        description += f"單週工時上限為 {params.get('hours', '?')} 小時"
    elif rule.rule_type == "MAX_CONSECUTIVE_DAYS":
        description += f"最多連續上班 {params.get('days', '?')} 天"
    elif rule.rule_type == "REQUIRED_LEVEL":
        description += f"{params.get('shift', '?')} 必須由 {params.get('level', '?')} 擔任"
    else:
        # 如果有新的、未定義的規則類型，使用備用顯示方式
        param_texts = []
        for key, value in rule.params.items():
            param_texts.append(f"{key}: {value}")
        description += f" => ({', '.join(param_texts)})"
        
    return description

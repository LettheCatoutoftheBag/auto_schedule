"""
核心規則引擎 (Core Rule Engine)
負責定義、解釋、翻譯所有排班規則的核心模組。
"""
from core.models import Rule

# --- 規則定義層 (翻譯機) ---
# 將所有排班邏輯，定義成使用者看得懂的選項和輸入框
# 這是整個專案的「大腦」，所有新規則都必須先在這裡定義
RULE_DEFINITIONS = {
    # --- 需求 1 & 2 ---
    "指定多個休息日": {
        "type": "ASSIGN_FIXED_OFF_DAYS",
        "params": {"dates": ("日期 (可多選)", "dates"), "shift_name": ("休假類型", ["休", "例休"])},
        "description": "為員工預先排定固定的休息日(可指定'休'或'例休')。"
    },
    # --- 需求 7 ---
    "指定特定日期班別": {
        "type": "ASSIGN_SPECIFIC_SHIFT",
        "params": {"date": ("日期", "date"), "shift_name": ("班別", "shift_options")},
        "description": "強制指定某位員工在特定某一天的班別。"
    },
    # --- 需求 3 (修改舊規則) ---
    "指定班別所需級別": {
        "type": "REQUIRED_LEVEL_FOR_SHIFT",
        "params": {
            "level": ("所需級別", ["吧檯手", "門職", "時薪人員"]),
            "shift_name": ("指定班別", ["9.5-18"])
        },
        "description": "設定某個班別必須由特定級別的員工擔任。"
    },
    # --- 需求 4 (替換舊規則) ---
    "每月最低工時": {
        "type": "MIN_MONTHLY_HOURS",
        "params": {"hours": ("小時", "number")},
        "description": "設定員工每月最低應達到的總工時。"
    },
    # --- 需求 5 ---
    "晚班隔天接早班限制": {
        "type": "LATE_SHIFT_THEN_EARLY_SHIFT",
        "params": {
            "late_shifts": ("前一天的晚班 (可多選)", "multi_shift_options"),
            "early_shift": ("隔天的早班", ["9-17.5"])
        },
        "description": "若前一天上了指定的晚班，隔天優先安排特定早班。"
    },
    # --- 需求 6 ---
    "班別連動規則": {
        "type": "SHIFT_INTERDEPENDENCE",
        "params": {}, # 此規則為硬編碼邏輯，無需參數
        "description": "系統會自動處理 '10.5-19' 和 '10.5-20.5' 之間的連動關係。"
    }
}

# --- 輔助函式：將 Rule 物件轉為易讀的字串 (超．升級版) ---
def get_rule_display_text(rule: Rule) -> str:
    """將規則物件轉換成一行易於理解的描述文字"""
    description = f"【{rule.name}】 "
    params = rule.params if isinstance(rule.params, dict) else {}

    try:
        if rule.rule_type == "ASSIGN_FIXED_OFF_DAYS":
            dates_str = ', '.join(params.get('dates', ['?']))
            shift_name = params.get('shift_name', '?')
            description += f"在 [{dates_str}] 排定為 '{shift_name}'"
        
        elif rule.rule_type == "ASSIGN_SPECIFIC_SHIFT":
            date = params.get('date', '?')
            shift_name = params.get('shift_name', '?')
            description += f"在 {date} 必須上 '{shift_name}'"

        elif rule.rule_type == "REQUIRED_LEVEL_FOR_SHIFT":
            level = params.get('level', '?')
            shift_name = params.get('shift_name', '?')
            description += f"班別 '{shift_name}' 必須由 '{level}' 擔任"

        elif rule.rule_type == "MIN_MONTHLY_HOURS":
            hours = params.get('hours', '?')
            description += f"每月最低工時需達 {hours} 小時"

        elif rule.rule_type == "LATE_SHIFT_THEN_EARLY_SHIFT":
            early = params.get('early_shift', '?')
            lates = ', '.join(params.get('late_shifts', ['?']))
            description += f"若前一天上 [{lates}]，隔天優先排 '{early}'"
        
        elif rule.rule_type == "SHIFT_INTERDEPENDENCE":
            description += "自動處理 '10.5-19' 與 '10.5-20.5' 的連動"

        else:
            description += f"未知規則類型 ({rule.rule_type})"
    except Exception:
        description += "規則參數格式錯誤，請重新編輯"
        
    return description


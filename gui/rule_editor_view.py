"""
規則編輯器介面 (Rule Editor View)
使用者在這裡建立和管理可重複使用的排班規則。
"""
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QDialog, QLineEdit, QComboBox, QFormLayout,
                             QDialogButtonBox, QLabel, QStackedLayout,
                             QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt
from core.models import Rule
from core.rule_controller import RuleController

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
            "level": ("所需級別", ["吧檯手", "門職人員", "儲備幹部"]),
            "shift": ("指定班別", ["早班", "晚班", "大夜班"])
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


# --- 對話方塊：用於新增或編輯規則 (已升級) ---
class RuleDialog(QDialog):
    def __init__(self, rule: Rule = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增規則" if rule is None else "編輯規則")
        self.setMinimumWidth(450)
        
        self.param_widgets = {} # 用來儲存每個規則對應的輸入框

        # --- 主要元件 ---
        self.name_input = QLineEdit(rule.name if rule else "")
        self.type_input = QComboBox()
        self.type_input.addItems(RULE_DEFINITIONS.keys())

        # --- 動態參數區 ---
        self.param_stack = QStackedLayout()
        self.setup_param_layouts()
        
        param_groupbox = QGroupBox("規則參數設定")
        param_groupbox.setLayout(self.param_stack)

        self.type_input.currentTextChanged.connect(self.on_type_changed)

        # --- 按鈕與整體佈局 ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.addRow("規則名稱 (例如: 正職班表)", self.name_input)
        form_layout.addRow("選擇規則類型", self.type_input)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(param_groupbox)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        # --- 如果是編輯模式，初始化表單 ---
        if rule:
            self.initialize_for_editing(rule)

    def setup_param_layouts(self):
        """根據 RULE_DEFINITIONS 建立所有可能的參數輸入介面"""
        for display_name, definition in RULE_DEFINITIONS.items():
            param_form = QFormLayout()
            container_widget = QWidget()
            container_widget.setLayout(param_form)
            
            self.param_widgets[display_name] = {}

            for param_key, (label, param_type) in definition["params"].items():
                if isinstance(param_type, list): # 如果是選項列表
                    widget = QComboBox()
                    widget.addItems(param_type)
                elif param_type == "number": # 如果是數字
                    widget = QSpinBox()
                    widget.setRange(0, 1000)
                else: # 備用
                    widget = QLineEdit()
                
                param_form.addRow(f"{label}:", widget)
                self.param_widgets[display_name][param_key] = widget

            self.param_stack.addWidget(container_widget)

    def on_type_changed(self, text):
        """當規則類型改變時，切換顯示對應的參數輸入介面"""
        index = self.type_input.findText(text)
        self.param_stack.setCurrentIndex(index)

    def initialize_for_editing(self, rule: Rule):
        """編輯時，根據傳入的 rule 物件設定好介面的初始值"""
        display_name_to_set = ""
        for name, definition in RULE_DEFINITIONS.items():
            if definition["type"] == rule.rule_type:
                display_name_to_set = name
                break
        
        if display_name_to_set:
            self.type_input.setCurrentText(display_name_to_set)
            for param_key, widget in self.param_widgets[display_name_to_set].items():
                if param_key in rule.params:
                    value = rule.params[param_key]
                    if isinstance(widget, QComboBox):
                        widget.setCurrentText(str(value))
                    elif isinstance(widget, QSpinBox):
                        widget.setValue(int(value))
                    else:
                        widget.setText(str(value))

    def get_data(self):
        """從當前介面讀取資料，組合成控制器需要的格式"""
        name = self.name_input.text().strip()
        if not name:
            return None

        selected_display_name = self.type_input.currentText()
        definition = RULE_DEFINITIONS[selected_display_name]
        
        params = {}
        current_param_widgets = self.param_widgets[selected_display_name]
        for param_key, widget in current_param_widgets.items():
            if isinstance(widget, QComboBox):
                params[param_key] = widget.currentText()
            elif isinstance(widget, QSpinBox):
                params[param_key] = widget.value()
            else:
                params[param_key] = widget.text()

        return {
            "name": name,
            "rule_type": definition["type"],
            "params": params
        }


# --- 主視圖：整合列表、按鈕和所有邏輯 ---
class RuleEditorView(QWidget):
    def __init__(self, rule_controller: RuleController, parent=None):
        super().__init__(parent)
        self.controller = rule_controller

        # --- 介面元件 ---
        self.rule_list = QListWidget()
        self.add_button = QPushButton("➕ 新增規則")
        self.edit_button = QPushButton("✏️ 編輯規則")
        self.delete_button = QPushButton("🗑️ 刪除規則")

        # --- 佈局 ---
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("這裡是您的規則庫，定義好的規則將可以像拼圖一樣套用給員工。"))
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.rule_list)
        self.setLayout(main_layout)

        # --- 連接信號與槽 ---
        self.add_button.clicked.connect(self.add_rule)
        self.edit_button.clicked.connect(self.edit_rule)
        self.delete_button.clicked.connect(self.delete_rule)
        self.rule_list.itemDoubleClicked.connect(self.edit_rule)
        
        self.refresh_view() # 初始載入
        print("✅ 規則編輯器介面已升級並載入。")

    def refresh_view(self):
        """重新整理規則列表的顯示"""
        self.rule_list.clear()
        for rule in self.controller.get_all_rules():
            display_text = get_rule_display_text(rule)
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, rule.id) # 將真實 ID 存在 item 中
            self.rule_list.addItem(item)

    def add_rule(self):
        """處理新增規則的邏輯"""
        dialog = RuleDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                self.controller.add_rule(data["name"], data["rule_type"], data["params"])
                self.refresh_view()
            else:
                QMessageBox.warning(self, "輸入錯誤", "規則名稱不能為空。")

    def edit_rule(self):
        """處理編輯規則的邏輯"""
        selected_item = self.rule_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "提示", "請先選擇一條要編輯的規則。")
            return
        
        rule_id = selected_item.data(Qt.ItemDataRole.UserRole)
        rule_to_edit = self.controller.get_rule_by_id(rule_id)

        dialog = RuleDialog(rule=rule_to_edit, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                self.controller.update_rule(rule_id, data["name"], data["rule_type"], data["params"])
                self.refresh_view()
            else:
                QMessageBox.warning(self, "輸入錯誤", "規則名稱不能為空。")
                
    def delete_rule(self):
        """處理刪除規則的邏輯"""
        selected_item = self.rule_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "提示", "請先選擇一條要刪除的規則。")
            return
            
        rule_id = selected_item.data(Qt.ItemDataRole.UserRole)
        rule_to_delete = self.controller.get_rule_by_id(rule_id)

        # 跳出確認對話方塊
        reply = QMessageBox.question(self, "確認刪除", 
            f"您確定要刪除規則「{rule_to_delete.name}」嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        # 如果使用者確認，則執行刪除
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.delete_rule(rule_id)
            self.refresh_view()
        # 此函式到此結束，整個類別定義也已完整。


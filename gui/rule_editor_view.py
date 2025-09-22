"""
規則編輯器介面 (Rule Editor View)
使用者在這裡建立和管理可重複使用的排班規則。
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QDialog, QLineEdit, QComboBox, QFormLayout,
                             QDialogButtonBox, QLabel, QStackedLayout,
                             QSpinBox, QGroupBox, QCalendarWidget, QListWidget,
                             QAbstractItemView)
from PyQt6.QtCore import Qt, QDate
from core.models import Rule
from core.rule_controller import RuleController
from core.rule_engine import RULE_DEFINITIONS, get_rule_display_text
# 引用核心中的班別定義，確保一致性
from core.scheduler import SHIFTS

# --- 對話方塊：用於新增或編輯規則 (超級升級版) ---
class RuleDialog(QDialog):
    def __init__(self, rule: Rule = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增規則" if rule is None else "編輯規則")
        self.setMinimumWidth(500)
        
        self.param_widgets = {}

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
        form_layout.addRow("規則名稱 (例如: YI的固定班)", self.name_input)
        form_layout.addRow("選擇規則類型", self.type_input)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(param_groupbox)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        if rule:
            self.initialize_for_editing(rule)

    def setup_param_layouts(self):
        """根據 RULE_DEFINITIONS 建立所有可能的參數輸入介面"""
        work_shifts = [s.name for s in SHIFTS if s.name not in ["休", "例休"]]

        for display_name, definition in RULE_DEFINITIONS.items():
            param_form = QFormLayout()
            container_widget = QWidget()
            container_widget.setLayout(param_form)
            
            self.param_widgets[display_name] = {}

            if not definition["params"]: # 如果規則不需要參數
                param_form.addRow(QLabel("此規則為全域設定，無需額外參數。"))

            for param_key, (label, param_type) in definition["params"].items():
                widget = None
                if param_type == "number":
                    widget = QSpinBox()
                    widget.setRange(0, 200)
                elif param_type == "date":
                    widget = QCalendarWidget()
                    widget.setGridVisible(True)
                elif param_type == "dates":
                    widget = QCalendarWidget()
                    widget.setGridVisible(True)
                    # 允許多選模式，但實際邏輯需在 get_data 中處理
                elif param_type == "shift_options":
                    widget = QComboBox()
                    widget.addItems(work_shifts)
                elif isinstance(param_type, list):
                    widget = QComboBox()
                    widget.addItems(param_type)
                
                if widget:
                    param_form.addRow(f"{label}:", widget)
                    self.param_widgets[display_name][param_key] = widget
            
            self.param_stack.addWidget(container_widget)

    def on_type_changed(self, text):
        index = self.type_input.findText(text)
        self.param_stack.setCurrentIndex(index)

    def initialize_for_editing(self, rule: Rule):
        display_name_to_set = next((name for name, defi in RULE_DEFINITIONS.items() if defi["type"] == rule.rule_type), None)
        
        if display_name_to_set:
            self.type_input.setCurrentText(display_name_to_set)
            params = rule.params if isinstance(rule.params, dict) else {}
            for param_key, widget in self.param_widgets[display_name_to_set].items():
                value = params.get(param_key)
                if value is None: continue

                if isinstance(widget, QComboBox): widget.setCurrentText(str(value))
                elif isinstance(widget, QSpinBox): widget.setValue(int(value))
                elif isinstance(widget, QCalendarWidget) and RULE_DEFINITIONS[display_name_to_set]['params'][param_key][1] == 'date':
                    widget.setSelectedDate(QDate.fromString(value, "yyyy-MM-dd"))

    def get_data(self):
        name = self.name_input.text().strip()
        if not name: return None

        selected_display_name = self.type_input.currentText()
        definition = RULE_DEFINITIONS[selected_display_name]
        
        params = {}
        current_param_widgets = self.param_widgets.get(selected_display_name, {})
        for param_key, widget in current_param_widgets.items():
            param_def = definition["params"][param_key]
            if isinstance(widget, QComboBox):
                params[param_key] = widget.currentText()
            elif isinstance(widget, QSpinBox):
                params[param_key] = widget.value()
            elif isinstance(widget, QCalendarWidget):
                if param_def[1] == 'date':
                    params[param_key] = widget.selectedDate().toString("yyyy-MM-dd")
                elif param_def[1] == 'dates':
                     # 注意：PyQt的QCalendarWidget不直接支援多選，此處僅為範例
                     # 實際多選功能需要更複雜的自訂元件
                    params[param_key] = [widget.selectedDate().toString("yyyy-MM-dd")]

        return {"name": name, "rule_type": definition["type"], "params": params}

# --- 主視圖 ---
class RuleEditorView(QWidget):
    def __init__(self, rule_controller: RuleController, parent=None):
        super().__init__(parent)
        self.controller = rule_controller
        self.init_ui()
        self.refresh_view()

    def init_ui(self):
        self.rule_list = QListWidget()
        self.add_button = QPushButton("➕ 新增規則")
        self.edit_button = QPushButton("✏️ 編輯規則")
        self.delete_button = QPushButton("🗑️ 刪除規則")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel("這裡是您的規則庫，定義好的規則將可以像拼圖一樣套用給員工。"))
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.rule_list)

        self.add_button.clicked.connect(self.add_rule)
        self.edit_button.clicked.connect(self.edit_rule)
        self.delete_button.clicked.connect(self.delete_rule)
        self.rule_list.itemDoubleClicked.connect(self.edit_rule)
        print("✅ 規則編輯器介面已升級並載入。")

    def refresh_view(self):
        self.rule_list.clear()
        for rule in self.controller.get_all_rules():
            display_text = get_rule_display_text(rule)
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, rule.id)
            self.rule_list.addItem(item)

    def add_rule(self):
        dialog = RuleDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                self.controller.add_rule(data["name"], data["rule_type"], data["params"])
                self.refresh_view()
            else:
                QMessageBox.warning(self, "輸入錯誤", "規則名稱不能為空。")

    def edit_rule(self):
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
        selected_item = self.rule_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "提示", "請先選擇一條要刪除的規則。")
            return
            
        rule_id = selected_item.data(Qt.ItemDataRole.UserRole)
        rule_to_delete = self.controller.get_rule_by_id(rule_id)

        reply = QMessageBox.question(self, "確認刪除", 
            f"您確定要刪除規則「{rule_to_delete.name}」嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.controller.delete_rule(rule_id)
            self.refresh_view()


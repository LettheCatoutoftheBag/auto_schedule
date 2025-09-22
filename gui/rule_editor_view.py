"""
規則編輯器介面 (Rule Editor View)
使用者在這裡建立和管理可重複使用的排班規則。
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QDialog, QLineEdit, QComboBox, QFormLayout,
                             QDialogButtonBox, QLabel, QStackedLayout,
                             QSpinBox, QGroupBox, QCalendarWidget, 
                             QAbstractItemView)
from PyQt6.QtCore import Qt, QDate
from core.models import Rule
from core.rule_controller import RuleController
from core.rule_engine import RULE_DEFINITIONS, get_rule_display_text
from core.scheduler import SHIFTS


class MultiDateSelectionWidget(QWidget):
    """一個用於多選日期的自訂元件"""
    def __init__(self, initial_dates=None, parent=None):
        super().__init__(parent)
        self.selected_dates = set(QDate.fromString(d, "yyyy-MM-dd") for d in (initial_dates or []))

        layout = QHBoxLayout(self)
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.toggle_date)

        self.list_widget = QListWidget()
        
        layout.addWidget(self.calendar, 2)
        layout.addWidget(self.list_widget, 1)

        self.refresh_list()

    def toggle_date(self, date):
        if date in self.selected_dates:
            self.selected_dates.remove(date)
        else:
            self.selected_dates.add(date)
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        sorted_dates = sorted(list(self.selected_dates))
        for date in sorted_dates:
            self.list_widget.addItem(date.toString("yyyy-MM-dd"))

    def get_selected_dates(self):
        return [d.toString("yyyy-MM-dd") for d in sorted(list(self.selected_dates))]

class RuleDialog(QDialog):
    def __init__(self, rule: Rule = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增規則" if rule is None else "編輯規則")
        self.setMinimumWidth(600)
        
        self.param_widgets = {}

        self.name_input = QLineEdit(rule.name if rule else "")
        self.type_input = QComboBox()
        self.type_input.addItems(RULE_DEFINITIONS.keys())

        self.param_stack = QStackedLayout()
        self.setup_param_layouts()
        
        param_groupbox = QGroupBox("規則參數設定")
        param_groupbox.setLayout(self.param_stack)

        self.type_input.currentTextChanged.connect(self.on_type_changed)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout(self)
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
        work_shifts = [s.name for s in SHIFTS if s.name not in ["休", "例休"]]
        late_shifts = ["10.5-19", "10.5-20.5", "13-21.5", "14-22"]

        for display_name, definition in RULE_DEFINITIONS.items():
            param_form = QFormLayout()
            container_widget = QWidget()
            container_widget.setLayout(param_form)
            self.param_widgets[display_name] = {}

            if not definition["params"]:
                param_form.addRow(QLabel("此規則為系統內建邏輯，無需額外參數。"))

            for param_key, (label, param_type) in definition["params"].items():
                widget = None
                if param_type == "number":
                    widget = QSpinBox()
                    widget.setRange(0, 200)
                elif param_type == "date":
                    widget = QCalendarWidget()
                    widget.setGridVisible(True)
                elif param_type == "dates":
                    widget = MultiDateSelectionWidget()
                elif param_type == "shift_options":
                    widget = QComboBox()
                    widget.addItems(work_shifts)
                elif param_type == "multi_shift_options":
                    widget = QListWidget()
                    widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
                    widget.addItems(late_shifts)
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
                elif isinstance(widget, QCalendarWidget): widget.setSelectedDate(QDate.fromString(value, "yyyy-MM-dd"))
                elif isinstance(widget, MultiDateSelectionWidget):
                    widget.selected_dates = set(QDate.fromString(d, "yyyy-MM-dd") for d in value)
                    widget.refresh_list()
                elif isinstance(widget, QListWidget):
                    for i in range(widget.count()):
                        if widget.item(i).text() in value:
                            widget.item(i).setSelected(True)

    def get_data(self):
        name = self.name_input.text().strip()
        if not name: return None

        selected_display_name = self.type_input.currentText()
        definition = RULE_DEFINITIONS[selected_display_name]
        
        params = {}
        current_param_widgets = self.param_widgets.get(selected_display_name, {})
        for param_key, widget in current_param_widgets.items():
            if isinstance(widget, QComboBox):
                params[param_key] = widget.currentText()
            elif isinstance(widget, QSpinBox):
                params[param_key] = widget.value()
            elif isinstance(widget, QCalendarWidget):
                params[param_key] = widget.selectedDate().toString("yyyy-MM-dd")
            elif isinstance(widget, MultiDateSelectionWidget):
                params[param_key] = widget.get_selected_dates()
            elif isinstance(widget, QListWidget):
                params[param_key] = [item.text() for item in widget.selectedItems()]

        return {"name": name, "rule_type": definition["type"], "params": params}

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
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.rule_list)

        self.add_button.clicked.connect(self.add_rule)
        self.edit_button.clicked.connect(self.edit_rule)
        self.delete_button.clicked.connect(self.delete_rule)
        self.rule_list.itemDoubleClicked.connect(self.edit_rule)

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


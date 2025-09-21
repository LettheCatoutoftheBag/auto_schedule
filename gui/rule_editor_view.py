"""
規則編輯器介面 (Rule Editor View)
使用者在這裡建立和管理可重複使用的排班規則。
"""
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QDialog, QLineEdit, QComboBox, QFormLayout,
                             QDialogButtonBox, QLabel, QTextEdit)
from PyQt6.QtGui import QFont
from core.models import Rule
from core.rule_controller import RuleController

# --- 對話方塊：用於新增或編輯規則 ---
class RuleDialog(QDialog):
    def __init__(self, rule: Rule = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增規則" if rule is None else "編輯規則")
        self.setMinimumWidth(400)

        # --- 元件定義 ---
        self.name_input = QLineEdit(rule.name if rule else "")
        
        self.type_input = QComboBox()
        # 這些是我們預先定義好，演算法會認識的規則類型
        self.type_input.addItems([
            "MAX_HOURS_PER_WEEK",
            "MIN_HOURS_PER_WEEK",
            "MAX_CONSECUTIVE_DAYS",
            "REQUIRED_LEVEL",
            "AVOID_SHIFT_PATTERN"
        ])
        if rule:
            self.type_input.setCurrentText(rule.rule_type)

        # 參數使用 JSON 格式輸入，提供高度彈性
        params_text = json.dumps(rule.params, indent=2, ensure_ascii=False) if rule else '{\n  "key": "value"\n}'
        self.params_input = QTextEdit(params_text)
        self.params_input.setFont(QFont("Courier New", 10))

        # --- 佈局 ---
        form_layout = QFormLayout()
        form_layout.addRow("規則名稱 (顯示用):", self.name_input)
        form_layout.addRow("規則類型 (程式用):", self.type_input)
        form_layout.addRow("規則參數 (JSON):", self.params_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def get_data(self):
        try:
            params = json.loads(self.params_input.toPlainText())
            return {
                "name": self.name_input.text().strip(),
                "rule_type": self.type_input.currentText(),
                "params": params
            }
        except json.JSONDecodeError:
            return None # 表示 JSON 格式錯誤

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
        
        self.refresh_view() # 初始載入
        print("✅ 規則編輯器介面已載入。")

    def refresh_view(self):
        self.rule_list.clear()
        for rule in self.controller.get_all_rules():
            # 使用 QListWidgetItem 來儲存 ID
            item = QListWidgetItem(f"{rule.name} ({rule.rule_type})")
            item.setData(Qt.ItemDataRole.UserRole, rule.id) # 將真實 ID 存在 item 中
            self.rule_list.addItem(item)

    def add_rule(self):
        dialog = RuleDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data is None:
                QMessageBox.warning(self, "格式錯誤", "規則參數的 JSON 格式不正確，請檢查。")
                return
            if data["name"]:
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
            if data is None:
                QMessageBox.warning(self, "格式錯誤", "規則參數的 JSON 格式不正確，請檢查。")
                return
            if data["name"]:
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
            self.controller.delete_employee(rule_to_delete.id)
            self.refresh_view()


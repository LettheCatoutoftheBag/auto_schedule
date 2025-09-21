"""
員工管理介面 (Employee Management View)
這是使用者操作員工資料的圖形介面。
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableView, QAbstractItemView, QMessageBox,
                             QDialog, QLineEdit, QComboBox, QFormLayout,
                             QDialogButtonBox, QHeaderView)
from PyQt6.QtCore import Qt, QAbstractTableModel
from typing import List, Any
from core.models import Employee
from core.employee_controller import EmployeeController


# --- 資料模型：用於連接 GUI 表格和我們的員工資料 ---
class EmployeeTableModel(QAbstractTableModel):
    def __init__(self, data: List[Employee]):
        super().__init__()
        self._data = data
        self.headers = ["姓名", "級別", "員工 ID"]

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            emp = self._data[index.row()]
            col = index.column()
            if col == 0: return emp.name
            if col == 1: return emp.level
            if col == 2: return emp.id
        return None

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self.headers)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None
    
    def refreshData(self, new_data: List[Employee]):
        """當外部資料變動時，刷新整個表格視圖"""
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()


# --- 對話方塊：用於新增或編輯員工 ---
class EmployeeDialog(QDialog):
    def __init__(self, employee: Employee = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增員工" if employee is None else "編輯員工")
        
        self.name_input = QLineEdit(employee.name if employee else "")
        self.level_input = QComboBox()
        self.level_input.addItems(["吧檯手", "門職人員", "儲備幹部", "其他"])
        if employee:
            self.level_input.setCurrentText(employee.level)

        form_layout = QFormLayout()
        form_layout.addRow("姓名:", self.name_input)
        form_layout.addRow("級別:", self.level_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "level": self.level_input.currentText()
        }


# --- 主視圖：整合表格、按鈕和所有邏輯 ---
class EmployeeView(QWidget):
    def __init__(self, emp_controller: EmployeeController, parent=None):
        super().__init__(parent)
        self.controller = emp_controller

        # --- 介面元件 ---
        self.table_view = QTableView()
        self.model = EmployeeTableModel(self.controller.get_all_employees())
        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # ID欄位自動調整寬度

        self.add_button = QPushButton("➕ 新增員工")
        self.edit_button = QPushButton("✏️ 編輯員工")
        self.delete_button = QPushButton("🗑️ 刪除員工")
        
        # --- 佈局 ---
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table_view)
        self.setLayout(main_layout)

        # --- 連接信號與槽 (Signal & Slot) ---
        self.add_button.clicked.connect(self.add_employee)
        self.edit_button.clicked.connect(self.edit_employee)
        self.delete_button.clicked.connect(self.delete_employee)
        
        print("✅ 員工管理介面已載入。")

    def refresh_view(self):
        """重新從控制器獲取最新資料並更新表格"""
        self.model.refreshData(self.controller.get_all_employees())

    def add_employee(self):
        dialog = EmployeeDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data["name"]:
                self.controller.add_employee(data["name"], data["level"])
                self.refresh_view()
            else:
                QMessageBox.warning(self, "輸入錯誤", "員工姓名不能為空。")

    def edit_employee(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "請先選擇一位要編輯的員工。")
            return

        row = selected_rows[0].row()
        employee_to_edit = self.model._data[row]
        
        dialog = EmployeeDialog(employee=employee_to_edit, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data["name"]:
                self.controller.update_employee(employee_to_edit.id, data["name"], data["level"])
                self.refresh_view()
            else:
                QMessageBox.warning(self, "輸入錯誤", "員工姓名不能為空。")

    def delete_employee(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "請先選擇一位要刪除的員工。")
            return
        
        row = selected_rows[0].row()
        employee_to_delete = self.model._data[row]

        reply = QMessageBox.question(self, "確認刪除", 
            f"您確定要刪除員工「{employee_to_delete.name}」嗎？\n此操作無法復原。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.controller.delete_employee(employee_to_delete.id)
            self.refresh_view()


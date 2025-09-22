"""
互動式班表顯示與編輯介面 (Schedule View)
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDateEdit,
                             QTableWidget, QAbstractItemView, QSplitter, QGroupBox,
                             QTreeWidget, QTreeWidgetItem, QHeaderView, QLabel,
                             QTableWidgetItem)
from PyQt6.QtCore import Qt, QDate, QMimeData
from PyQt6.QtGui import QDrag, QColor
from core.employee_controller import EmployeeController
from core.rule_controller import RuleController
from core.rule_engine import get_rule_display_text
from core.scheduler import Scheduler

class RuleListWidget(QTreeWidget):
    """可供拖曳的規則庫列表"""
    def __init__(self, rule_controller: RuleController, parent=None):
        super().__init__(parent)
        self.rule_controller = rule_controller
        self.setDragEnabled(True)
        self.setHeaderHidden(True)
        self.populate_rules()

    def populate_rules(self):
        self.clear()
        for rule in self.rule_controller.get_all_rules():
            display_text = get_rule_display_text(rule)
            item = QTreeWidgetItem(self, [display_text])
            item.setData(0, Qt.ItemDataRole.UserRole, rule.id)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item: return
        
        rule_id = item.data(0, Qt.ItemDataRole.UserRole)
        mime_data = QMimeData()
        mime_data.setText(rule_id)
        
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction)

class AssignmentTreeWidget(QTreeWidget):
    """可接收拖曳的員工規則設定樹 (拼圖區)"""
    def __init__(self, emp_controller: EmployeeController, rule_controller: RuleController, parent=None):
        super().__init__(parent)
        self.emp_controller = emp_controller
        self.rule_controller = rule_controller
        self.setAcceptDrops(True)
        self.setHeaderLabels(["設定項目"])
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def populate_employees(self):
        self.clear()
        # 修正點：建立節點時，同時將 ID 存入 UserRole
        global_item = QTreeWidgetItem(self, ["🌐 全域規則"])
        global_item.setData(0, Qt.ItemDataRole.UserRole, "GLOBAL_RULES")
        global_item.setExpanded(True)
        global_item.setBackground(0, QColor("#E0E0E0"))

        for emp in self.emp_controller.get_all_employees():
            emp_item = QTreeWidgetItem(self, [emp.name])
            emp_item.setData(0, Qt.ItemDataRole.UserRole, emp.id)
            emp_item.setExpanded(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    # 修正點：新增 dragMoveEvent 確保拖曳過程順暢
    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        item_at_drop = self.itemAt(event.position().toPoint())
        if not item_at_drop: return

        rule_id = event.mimeData().text()
        rule = self.rule_controller.get_rule_by_id(rule_id)
        if not rule: return

        parent_item = item_at_drop.parent() if item_at_drop.parent() else item_at_drop
        
        display_text = get_rule_display_text(rule)
        new_rule_item = QTreeWidgetItem(parent_item, [display_text])
        # 修正點：將 rule_id 存入新節點的 UserRole
        new_rule_item.setData(0, Qt.ItemDataRole.UserRole, rule_id)
        event.acceptProposedAction()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.selectedItems()
            if not selected_items: return
            
            for item in selected_items:
                # 這個判斷式確保了只有子節點(規則)可以被刪除
                if item.parent():
                    item.parent().removeChild(item)
        else:
            super().keyPressEvent(event)

class ScheduleView(QWidget):
    def __init__(self, emp_controller: EmployeeController, rule_controller: RuleController, parent=None):
        super().__init__(parent)
        self.emp_controller = emp_controller
        self.rule_controller = rule_controller
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        date_layout = QHBoxLayout()
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM")
        date_layout.addWidget(QLabel("選擇月份:"))
        date_layout.addWidget(self.date_edit)
        
        assignment_group = QGroupBox("排班設定 (可將右側規則拖曳至此)")
        assignment_layout = QVBoxLayout(assignment_group)
        self.assignment_tree = AssignmentTreeWidget(self.emp_controller, self.rule_controller)
        self.assignment_tree.populate_employees()
        assignment_layout.addWidget(self.assignment_tree)
        assignment_layout.addWidget(QLabel("提示：選取規則後按 Delete 鍵可移除"))

        rule_lib_group = QGroupBox("規則庫")
        rule_lib_layout = QVBoxLayout(rule_lib_group)
        self.rule_list_widget = RuleListWidget(self.rule_controller)
        rule_lib_layout.addWidget(self.rule_list_widget)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.schedule_table = QTableWidget()

        left_layout.addLayout(date_layout)
        left_layout.addWidget(assignment_group)
        generate_button = QPushButton("🚀 一鍵生成班表")
        generate_button.clicked.connect(self.generate_schedule)
        left_layout.addWidget(generate_button)
        
        right_layout.addWidget(self.schedule_table)

        splitter.addWidget(left_panel)
        splitter.addWidget(rule_lib_group)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 200, 500])
        main_layout.addWidget(splitter)

    def generate_schedule(self):
        year = self.date_edit.date().year()
        month = self.date_edit.date().month()
        
        assignments = {"global": [], "employees": {}}
        root = self.assignment_tree.invisibleRootItem()
        
        # 修正點：從 UserRole 讀取 global 的規則 ID
        global_item = root.child(0)
        for i in range(global_item.childCount()):
            rule_item = global_item.child(i)
            assignments["global"].append(rule_item.data(0, Qt.ItemDataRole.UserRole))
            
        # 修正點：從 UserRole 讀取員工 ID 和其對應的規則 ID
        for i in range(1, root.childCount()):
            emp_item = root.child(i)
            emp_id = emp_item.data(0, Qt.ItemDataRole.UserRole)
            if emp_id is None: continue # 保護機制
            
            assignments["employees"][emp_id] = []
            for j in range(emp_item.childCount()):
                rule_item = emp_item.child(j)
                rule_id = rule_item.data(0, Qt.ItemDataRole.UserRole)
                if rule_id:
                    assignments["employees"][emp_id].append(rule_id)

        scheduler = Scheduler(self.emp_controller, self.rule_controller, assignments)
        schedule_result = scheduler.generate_schedule(year, month)

        headers = schedule_result["headers"]
        data = schedule_result["data"]
        self.schedule_table.setColumnCount(len(headers))
        self.schedule_table.setHorizontalHeaderLabels(headers)
        self.schedule_table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                self.schedule_table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))
        self.schedule_table.resizeColumnsToContents()


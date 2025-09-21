"""
互動式班表顯示與編輯介面 (Schedule View)
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QDateEdit, QLabel, QGroupBox,
                             QListWidget, QListWidgetItem, QHeaderView)
from PyQt6.QtCore import QDate
from core.employee_controller import EmployeeController
from core.rule_controller import RuleController
from core.scheduler import Scheduler
from core.rule_engine import get_rule_display_text


class ScheduleView(QWidget):
    def __init__(self, employee_controller: EmployeeController, rule_controller: RuleController, parent=None):
        super().__init__(parent)
        self.employee_controller = employee_controller
        self.rule_controller = rule_controller
        
        self.init_ui()
        self._populate_initial_data()
        print("✅ 班表生成介面已載入。")

    def init_ui(self):
        # --- 整體佈局 ---
        main_layout = QHBoxLayout(self)
        
        # --- 左側：設定面板 ---
        settings_layout = QVBoxLayout()
        settings_group = QGroupBox("排班設定")
        
        # 月份選擇
        self.date_selector = QDateEdit()
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.setDisplayFormat("yyyy 年 MM 月")
        
        # 員工列表
        self.employee_list = QListWidget()
        self.employee_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        # 規則列表
        self.rule_list = QListWidget()
        self.rule_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        # 生成按鈕
        self.generate_button = QPushButton("🚀 一鍵生成班表")
        self.generate_button.clicked.connect(self._generate_schedule_clicked)
        
        # 將元件加入左側佈局
        settings_form_layout = QVBoxLayout()
        settings_form_layout.addWidget(QLabel("1. 選擇目標月份:"))
        settings_form_layout.addWidget(self.date_selector)
        settings_form_layout.addWidget(QLabel("2. 選擇參與排班的員工 (預設全選):"))
        settings_form_layout.addWidget(self.employee_list)
        settings_form_layout.addWidget(QLabel("3. 選擇要套用的規則 (預設全選):"))
        settings_form_layout.addWidget(self.rule_list)
        settings_form_layout.addStretch()
        settings_form_layout.addWidget(self.generate_button)
        
        settings_group.setLayout(settings_form_layout)
        settings_layout.addWidget(settings_group)
        
        # --- 右側：班表顯示 ---
        schedule_layout = QVBoxLayout()
        self.schedule_table = QTableWidget()
        self.schedule_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        schedule_layout.addWidget(QLabel("排班結果預覽:"))
        schedule_layout.addWidget(self.schedule_table)
        
        # --- 組合左右佈局 ---
        main_layout.addLayout(settings_layout, 1) # 左側佔 1/3 寬度
        main_layout.addLayout(schedule_layout, 3) # 右側佔 2/3 寬度

    def _populate_initial_data(self):
        """從控制器載入初始資料並填充列表"""
        # 填充員工列表
        employees = self.employee_controller.get_all_employees()
        for emp in employees:
            item = QListWidgetItem(f"{emp.name} ({emp.level})")
            item.setSelected(True) # 預設全選
            self.employee_list.addItem(item)
            
        # 填充規則列表
        rules = self.rule_controller.get_all_rules()
        for rule in rules:
            display_text = get_rule_display_text(rule)
            item = QListWidgetItem(display_text)
            item.setSelected(True) # 預設全選
            self.rule_list.addItem(item)

    def _generate_schedule_clicked(self):
        """點擊生成按鈕時觸發的函式"""
        # 獲取設定 (目前僅使用日期)
        selected_date = self.date_selector.date()
        year = selected_date.year()
        month = selected_date.month()
        
        # 獲取所有員工和規則 (未來可根據選擇來篩選)
        all_employees = self.employee_controller.get_all_employees()
        all_rules = self.rule_controller.get_all_rules()

        # 執行排班演算法
        scheduler = Scheduler(all_employees, all_rules)
        schedule_result = scheduler.generate_schedule(year, month)
        
        # 將結果顯示在表格上
        self._display_schedule(schedule_result)

    def _display_schedule(self, schedule_data: dict):
        """將排班結果字典渲染到 QTableWidget"""
        headers = schedule_data.get("headers", [])
        data = schedule_data.get("data", [])
        
        self.schedule_table.clear()
        self.schedule_table.setRowCount(len(data))
        self.schedule_table.setColumnCount(len(headers))
        self.schedule_table.setHorizontalHeaderLabels(headers)
        
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                self.schedule_table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))
        
        # 調整欄寬以適應內容
        self.schedule_table.resizeColumnsToContents()
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


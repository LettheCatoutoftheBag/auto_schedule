"""
主視窗框架 (Main Window Frame)
這是整個應用程式最外層的視窗容器。
"""
from PyQt6.QtWidgets import QMainWindow, QTabWidget
from .employee_view import EmployeeView
from .rule_editor_view import RuleEditorView
from .schedule_view import ScheduleView
from core.employee_controller import EmployeeController
from core.rule_controller import RuleController

class MainWindow(QMainWindow):
    """
    主視窗類別，負責組織應用程式的所有 UI 元件。
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智慧排班小幫手")
        self.setGeometry(100, 100, 1200, 700)

        self.employee_controller = EmployeeController()
        self.rule_controller = RuleController()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- 建立各個頁籤 ---
        employee_tab = EmployeeView(self.employee_controller)
        rule_editor_tab = RuleEditorView(self.rule_controller)
        schedule_tab = ScheduleView(self.employee_controller, self.rule_controller)

        self.tabs.addTab(employee_tab, "🧑‍🤝‍🧑 員工管理")
        self.tabs.addTab(rule_editor_tab, "📚 規則庫管理")
        self.tabs.addTab(schedule_tab, "📅 班表生成與編輯")
        
        # --- 修正點: 建立信號與槽的連接 ---
        # 當 rule_controller 發出 rules_changed 信號時，
        # 會自動觸發另外兩個頁籤的 refresh/populate 方法。
        self.rule_controller.rules_changed.connect(rule_editor_tab.refresh_view)
        self.rule_controller.rules_changed.connect(schedule_tab.rule_list_widget.populate_rules)
        
        print("🎨 主視窗 MainWindow 初始化完畢，已啟用頁籤介面並建立資料同步信號。")


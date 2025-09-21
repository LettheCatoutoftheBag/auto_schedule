"""
主視窗框架 (Main Window Frame)
這是整個應用程式最外層的視窗容器。
"""
from PyQt6.QtWidgets import QMainWindow, QTabWidget
from .employee_view import EmployeeView
from .rule_editor_view import RuleEditorView
# --- 修改點：匯入新的 ScheduleView ---
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
        self.setGeometry(100, 100, 1200, 700) # 加大視窗尺寸以容納新介面

        # --- 初始化核心控制器 ---
        self.employee_controller = EmployeeController()
        self.rule_controller = RuleController()

        # --- 建立頁籤式主介面 ---
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- 建立並加入各個頁籤 ---
        employee_tab = EmployeeView(self.employee_controller)
        self.tabs.addTab(employee_tab, "🧑‍🤝‍🧑 員工管理")

        rule_editor_tab = RuleEditorView(self.rule_controller)
        self.tabs.addTab(rule_editor_tab, "📚 規則庫管理")
        
        # --- 修改點：建立並加入「班表生成」頁籤 ---
        schedule_tab = ScheduleView(self.employee_controller, self.rule_controller)
        self.tabs.addTab(schedule_tab, "📅 班表生成與編輯")
        
        print("🎨 主視窗 MainWindow 初始化完畢，已啟用頁籤介面。")


"""
主視窗框架 (Main Window Frame)
這是整個應用程式最外層的視窗容器。
"""
from PyQt6.QtWidgets import QMainWindow, QTabWidget
from .employee_view import EmployeeView
from .rule_editor_view import RuleEditorView
from core.employee_controller import EmployeeController
from core.rule_controller import RuleController

class MainWindow(QMainWindow):
    """
    主視窗類別，負責組織應用程式的所有 UI 元件。
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智慧排班小幫手")
        self.setGeometry(100, 100, 800, 600)

        # --- 初始化核心控制器 ---
        # 這些控制器是 GUI 和後端資料之間的橋樑
        self.employee_controller = EmployeeController()
        self.rule_controller = RuleController()

        # --- 建立頁籤式主介面 (QTabWidget) ---
        # 這是實現頁籤功能的關鍵元件
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs) # 將頁籤設為主視窗的中心

        # --- 建立並加入「員工管理」頁籤 ---
        # 我們將 EmployeeView 實例作為一個頁籤加進去
        employee_view = EmployeeView(self.employee_controller)
        self.tabs.addTab(employee_view, "🧑‍🤝‍🧑 員工管理")

        # --- 建立並加入「規則庫管理」頁籤 ---
        # 我們將 RuleEditorView 實例作為另一個頁籤加進去
        rule_editor_view = RuleEditorView(self.rule_controller)
        self.tabs.addTab(rule_editor_view, "📚 規則庫管理")
        
        print("🎨 主視窗 MainWindow 初始化完畢，已啟用頁籤介面。")


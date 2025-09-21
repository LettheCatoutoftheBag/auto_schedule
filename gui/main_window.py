"""
主視窗框架 (Main Window Frame)
這是整個應用程式最外層的視窗容器。
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from .employee_view import EmployeeView
from core.employee_controller import EmployeeController

class MainWindow(QMainWindow):
    """
    主視窗類別，負責組織應用程式的所有 UI 元件。
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智慧排班小幫手")
        self.setGeometry(100, 100, 800, 600)  # 設定視窗位置和大小

        # --- 初始化核心控制器 ---
        # 這是整個應用程式的資料中樞
        self.employee_controller = EmployeeController()

        # --- 建立主佈局和中心元件 ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 建立並加入員工管理視圖 ---
        # 將控制器傳遞給視圖，讓視圖可以操作資料
        employee_view = EmployeeView(self.employee_controller)
        main_layout.addWidget(employee_view)
        
        print("🎨 主視窗 MainWindow 初始化完畢。")


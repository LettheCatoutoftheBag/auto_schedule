"""
應用程式主進入點 (Main Entry Point)
執行此檔案即可啟動整個應用程式。
"""
import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """
    主函式，用於初始化並執行 PyQt6 應用程式。
    """
    print("="*50)
    print("🚀 應用程式啟動中...")
    print("="*50)

    # --- GUI 啟動代碼 ---
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    print("\n✅ 應用程式已準備就緒！")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


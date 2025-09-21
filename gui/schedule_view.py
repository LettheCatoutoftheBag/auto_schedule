"""
互動式班表顯示與編輯介面 (Schedule View) 的佔位檔案。
"""
from PyQt6.QtWidgets import QWidget

class ScheduleView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # TODO: 在階段三和四中，我們將在此建立班表表格，並實現拖曳換班功能


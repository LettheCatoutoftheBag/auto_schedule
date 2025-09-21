"""
新增檔案：資料管理器 (Data Manager)
負責所有檔案的讀取與寫入，讓核心邏輯與「如何存檔」這件事分離。
"""
import json
import os
from typing import List, Dict, Any

class DataManager:
    """處理 JSON 檔案的讀取和儲存"""
    def __init__(self, filepath: str):
        self.filepath = filepath
        # 如果檔案所在的目錄不存在，則建立它
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

    def load_data(self) -> List[Dict[str, Any]]:
        """從 JSON 檔案載入資料"""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_data(self, data: List[Dict[str, Any]]):
        """將資料儲存到 JSON 檔案"""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

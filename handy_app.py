import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from database.db_manager import DatabaseManager

def setup_database():
    db_manager = DatabaseManager("izakaya.db")
    
    # メニューをクリアしてから再登録
    db_manager.clear_menu()
    
    # メニューデータのリスト
    menu_items = [
        ("ビール", 500),
        ("枝豆", 300),
        ("唐揚げ", 600),
        ("ポテトサラダ", 450),
        ("刺身", 800),
        ("焼き魚", 750),
        ("もつ煮", 650),
        ("きゅうりの一本漬け", 350),
        ("日本酒", 700),
        ("焼酎", 600),
    ]

    for item, price in menu_items:
        db_manager.add_menu_item(item, price)

    db_manager.close()

if __name__ == "__main__":
    setup_database()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
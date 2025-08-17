# gui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QGridLayout, QHBoxLayout, QScrollArea
from gui.components import OrderButton, MenuItem
from database.db_manager import DatabaseManager
from ml.handwriting_recognizer import HandwritingRecognizer
from ml.recommendation import RecommendationEngine
import os
import sys
from PyQt6.QtCore import QCoreApplication

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ウィンドウサイズをスマホサイズに変更
        self.setWindowTitle("居酒屋Handyアプリ")
        self.setGeometry(100, 100, 400, 800)
        self.current_table = None
        self.current_order = []

        self.db_manager = DatabaseManager("izakaya.db")
        self.recognizer = HandwritingRecognizer()
        self.recommender = RecommendationEngine()
        self.menu_items = self.db_manager.search_menu("")
        
        self.stacked_widget = QWidget()
        self.setCentralWidget(self.stacked_widget)
        self.main_layout = QVBoxLayout()
        self.stacked_widget.setLayout(self.main_layout)
        
        # 席番号ボタンを辞書で管理
        self.table_buttons = {}

        self.create_table_selection_view()
        self.create_order_view()
        self.create_order_details_view()
        
        self.show_table_selection_view()

    def create_table_selection_view(self):
        """席番号選択画面を構築する"""
        self.table_selection_widget = QWidget()
        table_layout = QGridLayout()
        self.table_selection_widget.setLayout(table_layout)

        # 「席番号を選んでください」のラベルを削除
        
        # 席の数を36席に変更し、グリッドの列数を調整
        for i in range(1, 37):
            button = QPushButton(str(i))
            button.setStyleSheet("font-size: 18px; height: 50px;")
            button.clicked.connect(self.select_table)
            # グリッドレイアウトを6列で表示
            row = (i - 1) // 6
            col = (i - 1) % 6
            table_layout.addWidget(button, row, col)
            self.table_buttons[str(i)] = button
            
        self.main_layout.addWidget(self.table_selection_widget)
        self.table_selection_widget.hide()

    def create_order_view(self):
        """注文入力画面を構築する"""
        self.order_widget = QWidget()
        order_layout = QVBoxLayout()
        self.order_widget.setLayout(order_layout)

        # 戻るボタン
        back_button = QPushButton("戻る")
        back_button.setStyleSheet("font-size: 16px; padding: 10px;")
        back_button.clicked.connect(self.show_table_selection_view)
        order_layout.addWidget(back_button)

        self.table_number_label = QLabel("")
        self.table_number_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        order_layout.addWidget(self.table_number_label)

        # 商品リスト
        menu_scroll_area = QScrollArea()
        menu_scroll_area.setWidgetResizable(True)
        menu_widget = QWidget()
        menu_layout = QGridLayout()
        menu_widget.setLayout(menu_layout)
        
        for i, (name, price) in enumerate(self.menu_items):
            button = QPushButton(f"{name} ({int(price)}円)")
            button.clicked.connect(self.add_to_order)
            button.setProperty("item_name", name)
            # グリッドレイアウトを2列で表示
            row = i // 2
            col = i % 2
            menu_layout.addWidget(button, row, col)
        
        menu_scroll_area.setWidget(menu_widget)
        order_layout.addWidget(menu_scroll_area)

        # 注文済み商品リスト
        self.ordered_items_label = QLabel("注文済みの商品:")
        self.ordered_items_label.setStyleSheet("font-weight: bold;")
        order_layout.addWidget(self.ordered_items_label)

        self.ordered_items_list = QLabel("")
        order_layout.addWidget(self.ordered_items_list)

        # 注文確定ボタン
        order_complete_button = QPushButton("注文を確定")
        order_complete_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #4CAF50; color: white; padding: 15px;")
        order_complete_button.clicked.connect(self.save_order)
        order_layout.addWidget(order_complete_button)
        
        self.main_layout.addWidget(self.order_widget)
        self.order_widget.hide()

    def create_order_details_view(self):
        """注文内容確認画面を構築する"""
        self.order_details_widget = QWidget()
        details_layout = QVBoxLayout()
        self.order_details_widget.setLayout(details_layout)

        # 戻るボタン
        back_button = QPushButton("戻る")
        back_button.setStyleSheet("font-size: 16px; padding: 10px;")
        back_button.clicked.connect(self.show_table_selection_view)
        details_layout.addWidget(back_button)

        self.details_table_label = QLabel("")
        self.details_table_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        details_layout.addWidget(self.details_table_label)

        self.details_list_label = QLabel("")
        details_layout.addWidget(self.details_list_label)

        # 追加ボタンと会計ボタンを水平に配置する
        button_layout = QHBoxLayout()

        # 追加ボタン
        add_button = QPushButton("追加")
        add_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #FFA500; color: white; padding: 15px;")
        add_button.clicked.connect(self.add_to_existing_order)
        button_layout.addWidget(add_button)
        
        # 会計ボタン
        checkout_button = QPushButton("会計")
        checkout_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #28a745; color: white; padding: 15px;")
        checkout_button.clicked.connect(self.checkout_table)
        button_layout.addWidget(checkout_button)

        details_layout.addLayout(button_layout)
        
        self.main_layout.addWidget(self.order_details_widget)
        self.order_details_widget.hide()

    def show_table_selection_view(self):
        """席番号選択画面を表示する"""
        self.table_selection_widget.show()
        self.order_widget.hide()
        self.order_details_widget.hide()
        self.current_order = []
        self.update_ordered_list()
        self.update_table_colors()

    def show_order_view(self, table_number):
        """注文入力画面を表示する"""
        self.current_table = table_number
        self.table_number_label.setText(f"席番号: {self.current_table}")
        self.table_selection_widget.hide()
        self.order_details_widget.hide()
        self.order_widget.show()
        
    def show_order_details_view(self, table_number):
        """注文内容確認画面を表示する"""
        self.current_table = table_number
        self.details_table_label.setText(f"席番号: {table_number} の注文")
        orders = self.db_manager.get_orders_by_table(table_number)
        ordered_items = [item[0] for item in orders]
        details_text = "\n".join(ordered_items)
        self.details_list_label.setText(details_text)
        
        self.table_selection_widget.hide()
        self.order_widget.hide()
        self.order_details_widget.show()

    def select_table(self):
        """席番号ボタンのクリックイベントハンドラー"""
        sender = self.sender()
        table_number = sender.text()
        
        if self.db_manager.is_table_occupied(table_number):
            # 注文がある場合は、注文確認画面へ
            self.show_order_details_view(table_number)
        else:
            # 注文がない場合は、注文入力画面へ
            self.show_order_view(table_number)

    def add_to_order(self):
        """メニューボタンが押されたときに注文リストに追加する"""
        sender = self.sender()
        item_name = sender.property("item_name")
        self.current_order.append(item_name)
        self.update_ordered_list()

    def update_ordered_list(self):
        """注文リストの表示を更新する"""
        if not self.current_order:
            self.ordered_items_list.setText("---")
        else:
            ordered_text = "\n".join(self.current_order)
            self.ordered_items_list.setText(ordered_text)

    def save_order(self):
        """注文を保存して席番号選択画面に戻る"""
        if not self.current_order:
            print("注文する商品がありません。")
            return

        self.db_manager.add_order(self.current_table, self.current_order)
        print(f"席番号 {self.current_table} の注文を保存しました。")
        
        self.show_table_selection_view()

    def update_table_colors(self):
        """席番号ボタンの色を更新する"""
        for table_number, button in self.table_buttons.items():
            if self.db_manager.is_table_occupied(table_number):
                button.setStyleSheet("background-color: #FF6347; font-size: 18px; height: 50px;")
            else:
                button.setStyleSheet("background-color: #F0F0F0; font-size: 18px; height: 50px;")

    def add_to_existing_order(self):
        """追加注文のために注文入力画面に戻る"""
        self.show_order_view(self.current_table)

    def checkout_table(self):
        """会計処理を実行し、席を空席に戻す"""
        self.db_manager.clear_table_orders(self.current_table)
        print(f"席番号 {self.current_table} の会計が完了しました。")
        self.show_table_selection_view()

    def recognize_handwriting(self):
        pass
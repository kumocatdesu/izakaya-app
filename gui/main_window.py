# gui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QGridLayout, QHBoxLayout, QScrollArea, QListWidget, QListWidgetItem, QTableWidget, QHeaderView, QTableWidgetItem
from gui.components import OrderButton, MenuItem
from database.db_manager import DatabaseManager
from ml.handwriting_recognizer import HandwritingRecognizer
from ml.recommendation import RecommendationEngine
import os
import sys
from PyQt6.QtCore import QCoreApplication
from collections import OrderedDict

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("居酒屋Handyアプリ")
        self.setGeometry(100, 100, 400, 800)
        self.current_table = None
        self.current_order = OrderedDict() # 注文内容を OrderedDict で管理

        self.db_manager = DatabaseManager("izakaya.db")
        self.recognizer = HandwritingRecognizer()
        self.recommender = RecommendationEngine()
        self.menu_items = self.db_manager.search_menu("")
        self.menu_dict = {item[0]: item[1] for item in self.menu_items} # メニュー名をキーにした辞書
        
        self.stacked_widget = QWidget()
        self.setCentralWidget(self.stacked_widget)
        self.main_layout = QVBoxLayout()
        self.stacked_widget.setLayout(self.main_layout)
        
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

        for i in range(1, 37):
            button = QPushButton(str(i))
            button.setStyleSheet("font-size: 18px; height: 50px;")
            button.clicked.connect(self.select_table)
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

        back_button = QPushButton("戻る")
        back_button.setStyleSheet("font-size: 16px; padding: 10px;")
        back_button.clicked.connect(self.show_table_selection_view)
        order_layout.addWidget(back_button)

        self.table_number_label = QLabel("")
        self.table_number_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        order_layout.addWidget(self.table_number_label)

        menu_scroll_area = QScrollArea()
        menu_scroll_area.setWidgetResizable(True)
        menu_widget = QWidget()
        menu_layout = QGridLayout()
        menu_widget.setLayout(menu_layout)
        
        for i, (name, price) in enumerate(self.menu_items):
            button = QPushButton(f"{name} ({int(price)}円)")
            button.clicked.connect(self.add_to_order)
            button.setProperty("item_name", name)
            row = i // 2
            col = i % 2
            menu_layout.addWidget(button, row, col)
        
        menu_scroll_area.setWidget(menu_widget)
        order_layout.addWidget(menu_scroll_area)

        self.ordered_items_label = QLabel("注文済みの商品:")
        self.ordered_items_label.setStyleSheet("font-weight: bold;")
        order_layout.addWidget(self.ordered_items_label)

        # QListWidget を使用して、注文リストと削除ボタンを管理
        self.ordered_items_list_widget = QListWidget()
        order_layout.addWidget(self.ordered_items_list_widget)

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

        back_button = QPushButton("戻る")
        back_button.setStyleSheet("font-size: 16px; padding: 10px;")
        back_button.clicked.connect(self.show_table_selection_view)
        details_layout.addWidget(back_button)

        self.details_table_label = QLabel("")
        self.details_table_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        details_layout.addWidget(self.details_table_label)

        # 注文内容詳細表示にQTableWidgetを使用
        self.details_table_widget = QTableWidget()
        self.details_table_widget.setColumnCount(4)
        self.details_table_widget.setHorizontalHeaderLabels(["商品名", "個数", "単価", "合計"])
        header = self.details_table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        details_layout.addWidget(self.details_table_widget)
        
        self.total_summary_label = QLabel("")
        self.total_summary_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        details_layout.addWidget(self.total_summary_label)

        button_layout = QHBoxLayout()

        add_button = QPushButton("追加")
        add_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #FFA500; color: white; padding: 15px;")
        add_button.clicked.connect(self.add_to_existing_order)
        button_layout.addWidget(add_button)
        
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
        self.current_order = OrderedDict()
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

        # 注文内容を商品ごとに集計
        order_summary = OrderedDict()
        if orders:
            for item in orders:
                if isinstance(item, tuple) and len(item) > 0:
                    item_name = item[0]
                else:
                    item_name = str(item)
                order_summary[item_name] = order_summary.get(item_name, 0) + 1
            
        self.details_table_widget.setRowCount(len(order_summary))
        total_items = 0
        total_price = 0
        
        for row, (item_name, count) in enumerate(order_summary.items()):
            price = self.menu_dict.get(item_name, 0)
            subtotal = price * count
            
            self.details_table_widget.setItem(row, 0, QTableWidgetItem(item_name))
            self.details_table_widget.setItem(row, 1, QTableWidgetItem(str(count)))
            self.details_table_widget.setItem(row, 2, QTableWidgetItem(str(int(price)) + "円"))
            self.details_table_widget.setItem(row, 3, QTableWidgetItem(str(int(subtotal)) + "円"))
            
            total_items += count
            total_price += subtotal
            
        self.total_summary_label.setText(f"合計：{total_items}個 / {int(total_price)}円")
        
        self.table_selection_widget.hide()
        self.order_widget.hide()
        self.order_details_widget.show()

    def select_table(self):
        """席番号ボタンのクリックイベントハンドラー"""
        sender = self.sender()
        table_number = sender.text()
        
        if self.db_manager.is_table_occupied(table_number):
            self.show_order_details_view(table_number)
        else:
            self.show_order_view(table_number)

    def add_to_order(self):
        """メニューボタンが押されたときに注文リストに追加する"""
        sender = self.sender()
        item_name = sender.property("item_name")
        self.current_order[item_name] = self.current_order.get(item_name, 0) + 1
        self.update_ordered_list()

    def remove_order_item(self, item_name):
        """注文リストから商品を削除する"""
        if self.current_order[item_name] > 1:
            self.current_order[item_name] -= 1
        else:
            del self.current_order[item_name]
        self.update_ordered_list()

    def update_ordered_list(self):
        """注文リストの表示を更新する"""
        self.ordered_items_list_widget.clear()
        if not self.current_order:
            item = QListWidgetItem("---")
            self.ordered_items_list_widget.addItem(item)
        else:
            for item_name, count in self.current_order.items():
                item_widget = QWidget()
                h_layout = QHBoxLayout()
                
                label = QLabel(f"{item_name} ({count})")
                delete_button = QPushButton("削除")
                delete_button.clicked.connect(lambda _, name=item_name: self.remove_order_item(name))
                
                h_layout.addWidget(label)
                h_layout.addStretch()
                h_layout.addWidget(delete_button)
                h_layout.setContentsMargins(0, 0, 0, 0)
                item_widget.setLayout(h_layout)
                
                list_item = QListWidgetItem()
                list_item.setSizeHint(item_widget.sizeHint())
                self.ordered_items_list_widget.addItem(list_item)
                self.ordered_items_list_widget.setItemWidget(list_item, item_widget)

    def save_order(self):
        """注文を保存して席番号選択画面に戻る"""
        if not self.current_order:
            print("注文する商品がありません。")
            return

        order_list_to_save = []
        for item_name, count in self.current_order.items():
            order_list_to_save.extend([item_name] * count)
            
        self.db_manager.add_order(self.current_table, order_list_to_save)
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
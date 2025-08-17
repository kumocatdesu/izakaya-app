# gui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QGridLayout, QHBoxLayout, QScrollArea, QListWidget, QListWidgetItem, QTableWidget, QHeaderView, QTableWidgetItem, QInputDialog, QDialog, QDialogButtonBox, QMessageBox
from gui.components import OrderButton, MenuItem
from database.db_manager import DatabaseManager
from ml.handwriting_recognizer import HandwritingRecognizer
from ml.recommendation import RecommendationEngine
import os
import sys
from PyQt6.QtCore import QCoreApplication
from collections import OrderedDict
import pykakasi

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("居酒屋Handyアプリ")
        self.setFixedSize(360, 640)
        
        self.current_table = None
        self.current_order = OrderedDict()

        self.db_manager = DatabaseManager("izakaya.db")
        self.recognizer = HandwritingRecognizer()
        self.recommender = RecommendationEngine()

        self.menu_items = [
            ("焼き鳥", 180), ("豚バラ串", 180), ("鶏皮串", 150), ("つくね串", 200),
            ("牛タン串", 300), ("ラムチョップ", 780), ("若鶏の唐揚げ", 480), ("手羽先の唐揚げ", 420),
            ("牛すじ煮込み", 550), ("もつ煮込み", 500), ("ホルモン炒め", 650), ("ソーセージ盛り", 680),
            ("チーズタッカルビ", 850), ("鶏の炭火焼き", 700), ("豚キムチ炒め", 600), ("鉄板ステーキ", 980),
            ("刺身三点盛り", 980), ("アジの開き", 650), ("ホッケの塩焼き", 800), ("イカの一夜干し", 550),
            ("カニクリームコロッケ", 450), ("海老チリ", 750), ("マグロのユッケ", 680), ("サーモンカルパッチョ", 700),
            ("海鮮丼", 900), ("イクラ丼", 1200), ("エビフライ", 650), ("タコの唐揚げ", 520),
            ("枝豆", 280), ("冷奴", 250), ("シーザーサラダ", 500), ("大根サラダ", 450),
            ("ポテトサラダ", 380), ("トマトスライス", 300), ("きゅうりの一本漬け", 350), ("なすの揚げ浸し", 400),
            ("厚揚げ", 350), ("フライドポテト", 320), ("焼きおにぎり", 200), ("お茶漬け", 400),
            ("バニラアイス", 300), ("抹茶アイス", 320), ("ティラミス", 450), ("わらび餅", 400),
            ("白米", 200), ("味噌汁", 150),
            ("生ビール", 500), ("瓶ビール", 600), ("ノンアルコールビール", 400),
            ("八海山", 800), ("久保田", 900), ("獺祭", 1200), ("熱燗", 550), ("冷や", 550),
            ("黒霧島（芋）", 450), ("いいちこ（麦）", 420), ("鍛高譚（紫蘇）", 480),
            ("グラス（芋）", 400), ("グラス（麦）", 380),
            ("グラスワイン（赤）", 500), ("グラスワイン（白）", 500), ("ボトルワイン（赤）", 2500), ("ボトルワイン（白）", 2500),
            ("レモンサワー", 450), ("グレープフルーツサワー", 450), ("ライムサワー", 450), ("梅サワー", 480),
            ("巨峰サワー", 480), ("カルピスサワー", 420), ("ウーロンハイ", 400), ("緑茶ハイ", 400),
            ("ハイボール", 480), ("コークハイ", 500), ("ジンジャーハイ", 500), ("水割り", 450),
            ("コーラ", 250), ("オレンジジュース", 250), ("ウーロン茶", 200), ("緑茶", 200),
            ("カルピス", 250), ("ジンジャーエール", 250),
            ("おしぼり", 50), ("割り箸", 20), ("小皿", 10)
        ]
        self.menu_dict = {item[0]: item[1] for item in self.menu_items}

        self.categorized_menu = {
            "肉": [
                ("焼き鳥", 180), ("豚バラ串", 180), ("鶏皮串", 150), ("つくね串", 200),
                ("牛タン串", 300), ("ラムチョップ", 780), ("若鶏の唐揚げ", 480), ("手羽先の唐揚げ", 420),
                ("牛すじ煮込み", 550), ("もつ煮込み", 500), ("ホルモン炒め", 650), ("ソーセージ盛り", 680),
                ("チーズタッカルビ", 850), ("鶏の炭火焼き", 700), ("豚キムチ炒め", 600), ("鉄板ステーキ", 980),
            ],
            "魚": [
                ("刺身三点盛り", 980), ("アジの開き", 650), ("ホッケの塩焼き", 800), ("イカの一夜干し", 550),
                ("カニクリームコロッケ", 450), ("海老チリ", 750), ("マグロのユッケ", 680), ("サーモンカルパッチョ", 700),
                ("海鮮丼", 900), ("イクラ丼", 1200), ("エビフライ", 650), ("タコの唐揚げ", 520),
            ],
            "サラダ": [
                ("シーザーサラダ", 500), ("大根サラダ", 450), ("ポテトサラダ", 380),
                ("トマトスライス", 300), ("冷奴", 250), ("枝豆", 280), ("きゅうりの一本漬け", 350),
            ],
            "その他": [
                ("フライドポテト", 320), ("厚揚げ", 350), ("なすの揚げ浸し", 400),
                ("焼きおにぎり", 200), ("お茶漬け", 400), ("白米", 200), ("味噌汁", 150),
            ],
            "デザート": [
                ("バニラアイス", 300), ("抹茶アイス", 320), ("ティラミス", 450), ("わらび餅", 400),
            ],
            "ビール": [("生ビール", 500), ("瓶ビール", 600), ("ノンアルコールビール", 400)],
            "日本酒": [("八海山", 800), ("久保田", 900), ("獺祭", 1200), ("熱燗", 550), ("冷や", 550)],
            "焼酎": [("黒霧島（芋）", 450), ("いいちこ（麦）", 420), ("鍛高譚（紫蘇）", 480), ("グラス（芋）", 400), ("グラス（麦）", 380)],
            "ワイン": [("グラスワイン（赤）", 500), ("グラスワイン（白）", 500), ("ボトルワイン（赤）", 2500), ("ボトルワイン（白）", 2500)],
            "サワー": [("レモンサワー", 450), ("グレープフルーツサワー", 450), ("ライムサワー", 450), ("梅サワー", 480), ("巨峰サワー", 480), ("カルピスサワー", 420), ("ウーロンハイ", 400), ("緑茶ハイ", 400)],
            "ウィスキー": [("ハイボール", 480), ("コークハイ", 500), ("ジンジャーハイ", 500), ("水割り", 450)],
            "ソフトドリンク": [("コーラ", 250), ("オレンジジュース", 250), ("ウーロン茶", 200), ("緑茶", 200), ("カルピス", 250), ("ジンジャーエール", 250)],
            "備品": [("おしぼり", 50), ("割り箸", 20), ("小皿", 10)]
        }
        
        self.kks = pykakasi.kakasi()
        self.menu_hiragana_dict = self.generate_hiragana_map()

        self.stacked_widget = QWidget()
        self.setCentralWidget(self.stacked_widget)
        self.main_layout = QVBoxLayout()
        self.stacked_widget.setLayout(self.main_layout)
        
        self.table_buttons = {}

        self.create_table_selection_view()
        self.create_order_view()
        self.create_order_details_view()
        self.create_checkout_view()
        
        self.show_table_selection_view()

    def generate_hiragana_map(self):
        """メニュー名とひらがな読みをマッピングする辞書を生成"""
        hiragana_map = {}
        for category, items in self.categorized_menu.items():
            for name, price in items:
                result = self.kks.convert(name)
                hiragana_map[name] = ''.join([item['hira'] for item in result])
        return hiragana_map

    def create_table_selection_view(self):
        """席番号選択画面を構築する"""
        self.table_selection_widget = QWidget()
        table_layout = QGridLayout()
        self.table_selection_widget.setLayout(table_layout)
        
        for i in range(1, 37):
            button = QPushButton(str(i))
            button.setFixedSize(60, 60)
            button.setStyleSheet("font-size: 18px;")
            button.clicked.connect(self.select_table)
            row = (i - 1) // 4
            col = (i - 1) % 4
            table_layout.addWidget(button, row, col)
            self.table_buttons[str(i)] = button
            
        self.main_layout.addWidget(self.table_selection_widget)
        self.table_selection_widget.hide()

    def create_order_view(self):
        """注文入力画面を構築する"""
        self.order_widget = QWidget()
        order_layout = QVBoxLayout()
        self.order_widget.setLayout(order_layout)
        
        self.table_number_label = QLabel("")
        self.table_number_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        order_layout.addWidget(self.table_number_label)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("メニュー名を検索...")
        self.search_input.textChanged.connect(self.search_menu)
        search_button = QPushButton("検索")
        search_button.clicked.connect(self.search_menu)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        order_layout.addLayout(search_layout)

        self.menu_scroll_area = QScrollArea()
        self.menu_scroll_area.setWidgetResizable(True)
        self.menu_container_widget = QWidget()
        self.menu_container_layout = QVBoxLayout()
        self.menu_container_widget.setLayout(self.menu_container_layout)
        self.menu_scroll_area.setWidget(self.menu_container_widget)
        order_layout.addWidget(self.menu_scroll_area)
        
        self.ordered_items_label = QLabel("注文済みの商品:")
        self.ordered_items_label.setStyleSheet("font-weight: bold;")
        order_layout.addWidget(self.ordered_items_label)

        self.ordered_items_list_widget = QListWidget()
        self.ordered_items_list_widget.setFixedSize(340, 150)
        order_layout.addWidget(self.ordered_items_list_widget)

        self.order_total_label = QLabel("合計金額: 0円")
        self.order_total_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        order_layout.addWidget(self.order_total_label)
        
        bottom_button_layout = QHBoxLayout()
        back_to_details_button = QPushButton("戻る")
        back_to_details_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #f44336; color: white; padding: 15px;")
        back_to_details_button.clicked.connect(self.go_back_from_order_view)

        save_order_button = QPushButton("追加")
        save_order_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #4CAF50; color: white; padding: 15px;")
        save_order_button.clicked.connect(self.save_or_update_order)
        
        checkout_from_order_view_button = QPushButton("会計")
        checkout_from_order_view_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #28a745; color: white; padding: 15px;")
        checkout_from_order_view_button.clicked.connect(self.show_checkout_view)

        bottom_button_layout.addWidget(back_to_details_button)
        bottom_button_layout.addWidget(save_order_button)
        bottom_button_layout.addWidget(checkout_from_order_view_button)
        order_layout.addLayout(bottom_button_layout)
        
        self.main_layout.addWidget(self.order_widget)
        self.order_widget.hide()

    def populate_menu_buttons(self, menu_dict):
        """メニューボタンを動的に生成する"""
        for i in reversed(range(self.menu_container_layout.count())):
            item = self.menu_container_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                self.menu_container_layout.removeItem(item)
        
        for category, items in menu_dict.items():
            category_label = QLabel(category)
            category_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
            self.menu_container_layout.addWidget(category_label)
            
            menu_layout = QGridLayout()
            self.menu_container_layout.addLayout(menu_layout)
            
            for i, (name, price) in enumerate(items):
                button = QPushButton(f"{name} ({int(price)}円)")
                button.clicked.connect(lambda _, n=name: self.add_to_order_list(n))
                button.setProperty("item_name", name)
                row = i // 2
                col = i % 2
                menu_layout.addWidget(button, row, col)

    def search_menu(self):
        """
        検索機能を実行する (ひらがな予測対応)
        """
        query = self.search_input.text().strip().lower()
        if not query:
            self.populate_menu_buttons(self.categorized_menu)
            return
            
        filtered_menu = {}
        for category, items in self.categorized_menu.items():
            filtered_items = []
            for name, price in items:
                if (query in name.lower() or query in self.menu_hiragana_dict.get(name, "")):
                    filtered_items.append((name, price))
            if filtered_items:
                filtered_menu[category] = filtered_items
        
        self.populate_menu_buttons(filtered_menu)

    def create_order_details_view(self):
        """注文内容確認画面を構築する"""
        self.order_details_widget = QWidget()
        self.details_layout = QVBoxLayout()
        self.order_details_widget.setLayout(self.details_layout)

        self.details_table_label = QLabel("")
        self.details_table_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.details_layout.addWidget(self.details_table_label)
        
        self.details_scroll_area = QScrollArea()
        self.details_scroll_area.setWidgetResizable(True)
        self.details_container_widget = QWidget()
        self.details_container_layout = QVBoxLayout()
        self.details_container_widget.setLayout(self.details_container_layout)
        self.details_scroll_area.setWidget(self.details_container_widget)
        self.details_layout.addWidget(self.details_scroll_area)

        self.total_summary_label = QLabel("")
        self.total_summary_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.details_layout.addWidget(self.total_summary_label)

        bottom_button_layout = QHBoxLayout()

        back_button = QPushButton("戻る")
        back_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #f44336; color: white; padding: 15px;")
        back_button.clicked.connect(self.show_table_selection_view)
        
        add_button = QPushButton("追加")
        add_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #FFA500; color: white; padding: 15px;")
        add_button.clicked.connect(self.add_to_existing_order)
        
        checkout_button = QPushButton("会計")
        checkout_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #28a745; color: white; padding: 15px;")
        checkout_button.clicked.connect(self.show_checkout_view)
        
        bottom_button_layout.addWidget(back_button)
        bottom_button_layout.addWidget(add_button)
        bottom_button_layout.addWidget(checkout_button)

        self.details_layout.addLayout(bottom_button_layout)
        
        self.main_layout.addWidget(self.order_details_widget)
        self.order_details_widget.hide()

    def create_checkout_view(self):
        """会計確認画面を構築する"""
        self.checkout_widget = QWidget()
        checkout_layout = QVBoxLayout()
        self.checkout_widget.setLayout(checkout_layout)

        self.checkout_table_label = QLabel("")
        self.checkout_table_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        checkout_layout.addWidget(self.checkout_table_label)

        self.checkout_list_widget = QListWidget()
        checkout_layout.addWidget(self.checkout_list_widget)

        self.checkout_total_label = QLabel("")
        self.checkout_total_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        checkout_layout.addWidget(self.checkout_total_label)

        bottom_button_layout = QHBoxLayout()
        back_button = QPushButton("戻る")
        back_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #f44336; color: white; padding: 15px;")
        back_button.clicked.connect(lambda: self.show_order_details_view(self.current_table))
        
        checkout_button = QPushButton("会計")
        checkout_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #28a745; color: white; padding: 15px;")
        checkout_button.clicked.connect(self.prompt_checkout_confirmation)

        bottom_button_layout.addWidget(back_button)
        bottom_button_layout.addWidget(checkout_button)
        checkout_layout.addLayout(bottom_button_layout)

        self.main_layout.addWidget(self.checkout_widget)
        self.checkout_widget.hide()

    def show_table_selection_view(self):
        """席番号選択画面を表示する"""
        self.table_selection_widget.show()
        self.order_widget.hide()
        self.order_details_widget.hide()
        self.checkout_widget.hide()
        self.current_order = OrderedDict()
        self.update_ordered_list()
        self.update_table_colors()

    def show_order_view(self, table_number):
        """注文入力画面を表示する"""
        self.current_table = table_number
        self.table_number_label.setText(f"席番号: {self.current_table}")
        self.table_selection_widget.hide()
        self.order_details_widget.hide()
        self.checkout_widget.hide()
        self.order_widget.show()
        self.search_input.clear()
        self.populate_menu_buttons(self.categorized_menu)
    
    def go_back_from_order_view(self):
        """注文入力画面から戻る際の遷移を制御する"""
        if self.db_manager.is_table_occupied(self.current_table):
            self.show_order_details_view(self.current_table)
        else:
            self.show_table_selection_view()

    def show_order_details_view(self, table_number):
        """注文内容確認画面を構築する"""
        self.current_table = table_number
        self.details_table_label.setText(f"席番号: {table_number} の注文")
        
        # 既存のウィジェットをすべて削除
        for i in reversed(range(self.details_container_layout.count())):
            item = self.details_container_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                self.details_container_layout.removeItem(item)

        orders = self.db_manager.get_orders_by_table(table_number)
        
        order_summary = OrderedDict()
        if orders:
            for item in orders:
                if isinstance(item, tuple) and len(item) > 0:
                    item_name = item[0]
                else:
                    item_name = str(item)
                order_summary[item_name] = order_summary.get(item_name, 0) + 1
        
        self.current_order = order_summary
        
        total_items = 0
        total_price = 0

        # レイアウトの間隔を0に設定
        self.details_container_layout.setSpacing(0)
        
        # 商品を一つずつ追加し、＋－削除ボタンを配置
        for item_name, count in order_summary.items():
            item_widget = QWidget()
            h_layout = QHBoxLayout()
            
            price = self.menu_dict.get(item_name, 0)
            subtotal = price * count
            
            label = QLabel(f"{item_name}")
            count_label = QLabel(f"x {count}")
            price_label = QLabel(f"({int(price)}円)")
            
            label.setStyleSheet("font-weight: bold; min-width: 80px;")
            count_label.setStyleSheet("min-width: 30px;")
            price_label.setStyleSheet("min-width: 60px;")

            plus_button = QPushButton("+")
            plus_button.clicked.connect(lambda _, n=item_name: self.add_to_order_list_from_details(n))
            plus_button.setFixedSize(25, 25)
            
            minus_button = QPushButton("-")
            minus_button.clicked.connect(lambda _, n=item_name: self.remove_order_item_from_details(n))
            minus_button.setFixedSize(25, 25)

            delete_button = QPushButton("削除")
            delete_button.clicked.connect(lambda _, n=item_name: self.delete_order_item_from_details(n))

            h_layout.addWidget(label)
            h_layout.addWidget(count_label)
            h_layout.addWidget(price_label)
            h_layout.addStretch(1)
            h_layout.addWidget(plus_button)
            h_layout.addWidget(minus_button)
            h_layout.addWidget(delete_button)
            h_layout.setContentsMargins(0, 0, 0, 0)
            item_widget.setLayout(h_layout)
            
            self.details_container_layout.addWidget(item_widget)

            total_items += count
            total_price += subtotal
        
        # レイアウトの下部にスペースを追加して、要素を上部に寄せる
        self.details_container_layout.addStretch(1)

        self.total_summary_label.setText(f"合計：{total_items}個 / {int(total_price)}円")
        
        self.table_selection_widget.hide()
        self.order_widget.hide()
        self.checkout_widget.hide()
        self.order_details_widget.show()

    def add_to_order_list_from_details(self, item_name):
        self.db_manager.add_order(self.current_table, [item_name])
        self.show_order_details_view(self.current_table)

    def remove_order_item_from_details(self, item_name):
        self.db_manager.remove_order_item(self.current_table, item_name)
        self.show_order_details_view(self.current_table)

    def delete_order_item_from_details(self, item_name):
        self.db_manager.delete_order_item(self.current_table, item_name)
        self.show_order_details_view(self.current_table)

    def update_total_price(self):
        """注文リストの合計金額を更新する"""
        total = sum(self.menu_dict.get(item_name, 0) * count for item_name, count in self.current_order.items())
        self.order_total_label.setText(f"合計金額: {int(total)}円")

    def save_or_update_order(self):
        """注文を保存または更新する"""
        if not self.current_order:
            print("注文する商品がありません。")
            return

        order_list_to_save = []
        for item_name, count in self.current_order.items():
            order_list_to_save.extend([item_name] * count)

        self.db_manager.add_order(self.current_table, order_list_to_save)
        print(f"席番号 {self.current_table} に注文を追加しました。")
        
        self.show_table_selection_view()

    def select_table(self):
        """席番号ボタンのクリックイベントハンドラー"""
        sender = self.sender()
        table_number = sender.text()
        
        if self.db_manager.is_table_occupied(table_number):
            self.show_order_details_view(table_number)
        else:
            self.show_order_view(table_number)

    def add_to_order_list(self, item_name):
        """メニューボタンが押されたときに注文リストに追加する"""
        self.current_order[item_name] = self.current_order.get(item_name, 0) + 1
        self.update_ordered_list()
        self.update_total_price()

    def remove_order_item(self, item_name):
        """注文リストから商品を減らす"""
        if self.current_order[item_name] > 1:
            self.current_order[item_name] -= 1
        else:
            del self.current_order[item_name]
        self.update_ordered_list()
        self.update_total_price()

    def delete_order_item(self, item_name):
        """注文リストから商品を完全に削除する"""
        if item_name in self.current_order:
            del self.current_order[item_name]
        self.update_ordered_list()
        self.update_total_price()

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
                
                price = self.menu_dict.get(item_name, 0)
                subtotal = price * count
                
                label = QLabel(f"{item_name}")
                count_label = QLabel(f"x {count}")
                price_label = QLabel(f"({int(price)}円)")
                subtotal_label = QLabel(f"合計: {int(subtotal)}円")
                
                label.setStyleSheet("font-weight: bold; min-width: 80px;")
                count_label.setStyleSheet("min-width: 30px;")
                price_label.setStyleSheet("min-width: 60px;")
                subtotal_label.setStyleSheet("font-weight: bold; min-width: 80px;")

                plus_button = QPushButton("+")
                plus_button.clicked.connect(lambda _, n=item_name: self.add_to_order_list(n))
                plus_button.setFixedSize(25, 25)
                
                minus_button = QPushButton("-")
                minus_button.clicked.connect(lambda _, n=item_name: self.remove_order_item(n))
                minus_button.setFixedSize(25, 25)

                delete_button = QPushButton("完全削除")
                delete_button.clicked.connect(lambda _, n=item_name: self.delete_order_item(n))

                h_layout.addWidget(label)
                h_layout.addWidget(count_label)
                h_layout.addWidget(price_label)
                h_layout.addStretch(1)
                h_layout.addWidget(subtotal_label)
                h_layout.addWidget(plus_button)
                h_layout.addWidget(minus_button)
                h_layout.addWidget(delete_button)
                h_layout.setContentsMargins(0, 0, 0, 0)
                item_widget.setLayout(h_layout)
                
                list_item = QListWidgetItem()
                list_item.setSizeHint(item_widget.sizeHint())
                self.ordered_items_list_widget.addItem(list_item)
                self.ordered_items_list_widget.setItemWidget(list_item, item_widget)
        
        self.update_total_price()

    def update_table_colors(self):
        """席番号ボタンの色を更新する"""
        for table_number, button in self.table_buttons.items():
            if self.db_manager.is_table_occupied(table_number):
                button.setStyleSheet("background-color: #FF6347; font-size: 18px; height: 50px;")
            else:
                button.setStyleSheet("background-color: #F0F0F0; font-size: 18px; height: 50px;")

    def add_to_existing_order(self):
        """追加注文のために注文入力画面に戻る"""
        self.current_order = OrderedDict()
        self.show_order_view(self.current_table)

    def show_checkout_view(self):
        """会計確認画面を表示する"""
        self.checkout_table_label.setText(f"席番号: {self.current_table} の会計")
        self.checkout_list_widget.clear()

        orders = self.db_manager.get_orders_by_table(self.current_table)
        
        order_summary = OrderedDict()
        for item in orders:
            item_name = item[0] if isinstance(item, tuple) else str(item)
            order_summary[item_name] = order_summary.get(item_name, 0) + 1

        total_price = 0
        for item_name, count in order_summary.items():
            price = self.menu_dict.get(item_name, 0)
            subtotal = price * count
            self.checkout_list_widget.addItem(f"{item_name} x {count} ({int(subtotal)}円)")
            total_price += subtotal

        self.checkout_total_label.setText(f"合計金額: {int(total_price)}円")
        
        self.table_selection_widget.hide()
        self.order_widget.hide()
        self.order_details_widget.hide()
        self.checkout_widget.show()

    def prompt_checkout_confirmation(self):
        """会計確認ダイアログを表示する"""
        reply = QMessageBox.question(self, '会計確認', 
            "本当に会計を完了しますか？", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.checkout_table()

    def checkout_table(self):
        """会計処理を実行し、席を空席に戻す"""
        self.db_manager.clear_table_orders(self.current_table)
        print(f"席番号 {self.current_table} の会計が完了しました。")
        self.show_table_selection_view()
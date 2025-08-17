# gui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QGridLayout, QHBoxLayout, QScrollArea, QListWidget, QListWidgetItem, QTableWidget, QHeaderView, QTableWidgetItem, QInputDialog
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
        # 修正1: ウィンドウのサイズを固定する
        self.setFixedSize(360, 640)
        
        self.current_table = None
        self.current_order = OrderedDict()

        self.db_manager = DatabaseManager("izakaya.db")
        self.recognizer = HandwritingRecognizer()
        self.recommender = RecommendationEngine()

        # 大量のメニューデータをコード内で直接定義
        self.menu_items = [
            # 食事（肉）
            ("焼き鳥", 180), ("豚バラ串", 180), ("鶏皮串", 150), ("つくね串", 200),
            ("牛タン串", 300), ("ラムチョップ", 780), ("若鶏の唐揚げ", 480), ("手羽先の唐揚げ", 420),
            ("牛すじ煮込み", 550), ("もつ煮込み", 500), ("ホルモン炒め", 650), ("ソーセージ盛り", 680),
            ("チーズタッカルビ", 850), ("鶏の炭火焼き", 700), ("豚キムチ炒め", 600), ("鉄板ステーキ", 980),
            # 食事（魚）
            ("刺身三点盛り", 980), ("アジの開き", 650), ("ホッケの塩焼き", 800), ("イカの一夜干し", 550),
            ("カニクリームコロッケ", 450), ("海老チリ", 750), ("マグロのユッケ", 680), ("サーモンカルパッチョ", 700),
            ("海鮮丼", 900), ("イクラ丼", 1200), ("エビフライ", 650), ("タコの唐揚げ", 520),
            # 食事（サラダ・野菜）
            ("枝豆", 280), ("冷奴", 250), ("シーザーサラダ", 500), ("大根サラダ", 450),
            ("ポテトサラダ", 380), ("トマトスライス", 300), ("きゅうりの一本漬け", 350), ("なすの揚げ浸し", 400),
            ("厚揚げ", 350), ("フライドポテト", 320), ("焼きおにぎり", 200), ("お茶漬け", 400),
            # 食事（デザート・その他）
            ("バニラアイス", 300), ("抹茶アイス", 320), ("ティラミス", 450), ("わらび餅", 400),
            ("白米", 200), ("味噌汁", 150),
            # ドリンク（ビール）
            ("生ビール", 500), ("瓶ビール", 600), ("ノンアルコールビール", 400),
            # ドリンク（日本酒）
            ("八海山", 800), ("久保田", 900), ("獺祭", 1200), ("熱燗", 550), ("冷や", 550),
            # ドリンク（焼酎）
            ("黒霧島（芋）", 450), ("いいちこ（麦）", 420), ("鍛高譚（紫蘇）", 480),
            ("グラス（芋）", 400), ("グラス（麦）", 380),
            # ドリンク（ワイン）
            ("グラスワイン（赤）", 500), ("グラスワイン（白）", 500), ("ボトルワイン（赤）", 2500), ("ボトルワイン（白）", 2500),
            # ドリンク（サワー）
            ("レモンサワー", 450), ("グレープフルーツサワー", 450), ("ライムサワー", 450), ("梅サワー", 480),
            ("巨峰サワー", 480), ("カルピスサワー", 420), ("ウーロンハイ", 400), ("緑茶ハイ", 400),
            # ドリンク（ウィスキー）
            ("ハイボール", 480), ("コークハイ", 500), ("ジンジャーハイ", 500), ("水割り", 450),
            # ドリンク（ソフトドリンク）
            ("コーラ", 250), ("オレンジジュース", 250), ("ウーロン茶", 200), ("緑茶", 200),
            ("カルピス", 250), ("ジンジャーエール", 250),
            # 備品
            ("おしぼり", 50), ("割り箸", 20), ("小皿", 10)
        ]
        self.menu_dict = {item[0]: item[1] for item in self.menu_items}

        # カテゴリー分けされたメニュー辞書を作成
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

        back_button = QPushButton("戻る")
        back_button.setStyleSheet("font-size: 16px; padding: 10px;")
        back_button.clicked.connect(self.show_table_selection_view)
        order_layout.addWidget(back_button)

        self.table_number_label = QLabel("")
        self.table_number_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        order_layout.addWidget(self.table_number_label)

        menu_scroll_area = QScrollArea()
        menu_scroll_area.setWidgetResizable(True)
        menu_container_widget = QWidget()
        menu_container_layout = QVBoxLayout()
        menu_container_widget.setLayout(menu_container_layout)
        
        # カテゴリーごとにメニューボタンを配置
        for category, items in self.categorized_menu.items():
            category_label = QLabel(category)
            category_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
            menu_container_layout.addWidget(category_label)
            
            menu_layout = QGridLayout()
            menu_container_layout.addLayout(menu_layout)
            
            for i, (name, price) in enumerate(items):
                button = QPushButton(f"{name} ({int(price)}円)")
                button.clicked.connect(lambda _, n=name: self.add_to_order(n))
                button.setProperty("item_name", name)
                row = i // 2
                col = i % 2
                menu_layout.addWidget(button, row, col)
        
        menu_scroll_area.setWidget(menu_container_widget)
        order_layout.addWidget(menu_scroll_area)

        self.ordered_items_label = QLabel("注文済みの商品:")
        self.ordered_items_label.setStyleSheet("font-weight: bold;")
        order_layout.addWidget(self.ordered_items_label)

        self.ordered_items_list_widget = QListWidget()
        # 修正2: 注文リストの高さを固定し、スクロール可能にする
        self.ordered_items_list_widget.setFixedSize(340, 150)
        order_layout.addWidget(self.ordered_items_list_widget)

        # 合計金額表示用ラベルを追加
        self.order_total_label = QLabel("合計金額: 0円")
        self.order_total_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        order_layout.addWidget(self.order_total_label)
        
        # 手書き認識ボタンを追加
        handwriting_button = QPushButton("手書き注文")
        handwriting_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #8B4513; color: white; padding: 15px;")
        handwriting_button.clicked.connect(self.recognize_handwriting)
        order_layout.addWidget(handwriting_button)
        
        order_complete_button = QPushButton("注文を確定")
        order_complete_button.setObjectName("order_complete_button") 
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
        
        self.details_scroll_area = QScrollArea()
        self.details_scroll_area.setWidgetResizable(True)
        self.details_container_widget = QWidget()
        self.details_container_layout = QVBoxLayout()
        self.details_container_widget.setLayout(self.details_container_layout)
        self.details_scroll_area.setWidget(self.details_container_widget)
        details_layout.addWidget(self.details_scroll_area)

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
        """注文内容確認画面を構築する"""
        self.current_table = table_number
        self.details_table_label.setText(f"席番号: {table_number} の注文")
        
        for i in reversed(range(self.details_container_layout.count())):
            widget = self.details_container_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        orders = self.db_manager.get_orders_by_table(table_number)

        self.current_order = OrderedDict()
        order_summary = OrderedDict()
        if orders:
            for item in orders:
                if isinstance(item, tuple) and len(item) > 0:
                    item_name = item[0]
                else:
                    item_name = str(item)
                
                order_summary[item_name] = order_summary.get(item_name, 0) + 1
        
        total_items = 0
        total_price = 0

        for category, menu_list in self.categorized_menu.items():
            category_items = {item_name: count for item_name, count in order_summary.items() if any(item_name == m[0] for m in menu_list)}
            if not category_items:
                continue
            
            category_label = QLabel(category)
            category_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
            self.details_container_layout.addWidget(category_label)
            
            category_table = QTableWidget()
            category_table.setColumnCount(4)
            category_table.setHorizontalHeaderLabels(["商品名", "個数", "単価", "合計"])
            header = category_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            category_table.setRowCount(len(category_items))

            for row, (item_name, count) in enumerate(category_items.items()):
                price = self.menu_dict.get(item_name, 0)
                subtotal = price * count
                
                category_table.setItem(row, 0, QTableWidgetItem(item_name))
                category_table.setItem(row, 1, QTableWidgetItem(str(count)))
                category_table.setItem(row, 2, QTableWidgetItem(str(int(price)) + "円"))
                category_table.setItem(row, 3, QTableWidgetItem(str(int(subtotal)) + "円"))
                
                total_items += count
                total_price += subtotal
            
            category_table.setFixedHeight(category_table.rowHeight(0) * (category_table.rowCount() + 1))
            self.details_container_layout.addWidget(category_table)
            
        self.current_order = order_summary

        self.total_summary_label.setText(f"合計：{total_items}個 / {int(total_price)}円")
        
        edit_button = QPushButton("編集")
        edit_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #FFA500; color: white; padding: 15px;")
        edit_button.clicked.connect(self.show_edit_view)
        self.details_container_layout.addWidget(edit_button)

        self.table_selection_widget.hide()
        self.order_widget.hide()
        self.order_details_widget.show()

    def show_edit_view(self):
        """編集画面を表示する (注文リスト画面を再利用)"""
        order_complete_button = self.order_widget.findChild(QPushButton, "order_complete_button")

        try:
            order_complete_button.clicked.disconnect()
        except TypeError:
            pass 
        
        order_complete_button.clicked.connect(self.save_edited_order)
        
        self.update_ordered_list()
        
        self.order_details_widget.hide()
        self.order_widget.show()

    def update_total_price(self):
        """注文リストの合計金額を更新する"""
        total = sum(self.menu_dict.get(item_name, 0) * count for item_name, count in self.current_order.items())
        self.order_total_label.setText(f"合計金額: {int(total)}円")

    def save_edited_order(self):
        """編集後の注文を保存する"""
        if not self.current_order:
            self.db_manager.clear_table_orders(self.current_table)
            print("注文が空のため、テーブルをクリアしました。")
        else:
            order_list_to_save = []
            for item_name, count in self.current_order.items():
                order_list_to_save.extend([item_name] * count)
            
            self.db_manager.clear_table_orders(self.current_table)
            self.db_manager.add_order(self.current_table, order_list_to_save)
            print(f"席番号 {self.current_table} の注文を編集・保存しました。")
        
        self.show_table_selection_view()

    def add_to_order_from_details(self, item_name):
        self.current_order[item_name] = self.current_order.get(item_name, 0) + 1
        self.show_edit_view()

    def remove_order_item_from_details(self, item_name):
        if self.current_order[item_name] > 1:
            self.current_order[item_name] -= 1
        else:
            del self.current_order[item_name]
        self.show_edit_view()

    def delete_order_item_from_details(self, item_name):
        if item_name in self.current_order:
            del self.current_order[item_name]
        self.show_edit_view()

    def select_table(self):
        """席番号ボタンのクリックイベントハンドラー"""
        sender = self.sender()
        table_number = sender.text()
        
        if self.db_manager.is_table_occupied(table_number):
            self.show_order_details_view(table_number)
        else:
            self.show_order_view(table_number)

    def add_to_order(self, item_name=None):
        """メニューボタンまたはリストの+ボタンが押されたときに注文リストに追加する"""
        if item_name is None:
            sender = self.sender()
            item_name = sender.property("item_name")
            
        self.current_order[item_name] = self.current_order.get(item_name, 0) + 1
        self.update_ordered_list()
        self.update_total_price()

    def remove_order_item(self, item_name=None):
        """注文リストから商品を減らす"""
        if item_name is None:
            return
            
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
                plus_button.clicked.connect(lambda _, n=item_name: self.add_to_order(n))
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
        """
        手書き認識機能を実行する。
        - 実際の認識処理は self.recognizer に委ねる。
        - 認識結果をメニュー項目と照合し、注文に追加する。
        """
        text, ok = QInputDialog.getText(self, "手書き認識", "ここに手書きした文字を入力してください:")
        
        if ok and text:
            recognized_items = []
            
            all_menu_names = [item[0] for category, items in self.categorized_menu.items() for item in items]
            
            for menu_item in all_menu_names:
                if menu_item in text:
                    recognized_items.append(menu_item)

            if recognized_items:
                for item_name in recognized_items:
                    self.add_to_order(item_name)
                print(f"手書き認識: {', '.join(recognized_items)} を注文に追加しました。")
                self.update_ordered_list()
            else:
                print("手書き認識: 該当するメニューが見つかりませんでした。")
        else:
            print("手書き入力がキャンセルされました。")
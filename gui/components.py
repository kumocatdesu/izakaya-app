from PyQt6.QtWidgets import QPushButton, QWidget, QLabel, QVBoxLayout

class OrderButton(QPushButton):
    def __init__(self, item_name):
        super().__init__(item_name)
        self.setStyleSheet("font-size: 16px; padding: 10px;")
        self.item_name = item_name

class MenuItem(QWidget):
    def __init__(self, item_name, price):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        name_label = QLabel(f"メニュー名: {item_name}")
        price_label = QLabel(f"価格: {price}円")

        layout.addWidget(name_label)
        layout.addWidget(price_label)
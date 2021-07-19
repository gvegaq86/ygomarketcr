import sys

import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from urllib.request import urlopen
from helper.tyt_utils import TYTUtils
from helper.wcapi_utils import WCAPIUtils

wcapi = WCAPIUtils()
tyt = TYTUtils()


class MainApp(QMainWindow):
    def __init__(self, parent=None, *args):
        super(MainApp, self).__init__(parent=parent)
        self.setFixedSize(700, 500)
        self.setWindowTitle("Ingresar Cartas")

        # Elementos
        self.card_code = QLineEdit(self)
        self.card_code.setPlaceholderText("codigo")
        self.card_code.setText("THSF-EN053")
        self.condition = QComboBox(self)
        self.condition.addItems(["NM (Near Mint)", "LP (Lightly Played)"])
        self.edition = QComboBox(self)
        self.edition.addItems(["1st Edition", "Unlimited", "Limited Edition"])
        self.rarity = QComboBox(self)
        self.rarity.addItems(["Super Rare", "Ultra Rare", "Super Rare", "Rare", "Common"])
        self.prize = QLineEdit(self)
        self.prize.setPlaceholderText("Precio")
        self.quantity = QLineEdit(self)
        self.quantity.setPlaceholderText("Cantidad")
        self.name = QLineEdit(self)
        self.name.setPlaceholderText("Nombre")
        self.image = QLabel(self)
        self.message = QLabel(self)

        self.buscar = QPushButton("Buscar", self)

        # Posiciones
        self.card_code.setGeometry(10, 10, 80, 40)
        self.image.setGeometry(400, 10, 250, 350)
        self.image.setScaledContents(True)
        self.condition.setGeometry(10, 50, 80, 40)
        self.edition.setGeometry(10, 90, 130, 40)
        self.rarity.setGeometry(10, 130, 80, 40)
        self.buscar.setGeometry(10, 170, 80, 40)
        self.message.setGeometry(10, 210, 200, 40)
        self.quantity.setGeometry(10, 270, 80, 40)
        self.prize.setGeometry(10, 310, 80, 40)
        self.name.setGeometry(10, 350, 350, 40)
        self.buscar.clicked.connect(self.slot)

    def slot(self):
        code = self.card_code.text()
        condition = self.condition.currentText()
        edition = self.edition.currentText()
        rarity = self.rarity.currentText()
        info = [[], [], []]
        product_from_inventory = wcapi.get_product_by_filter(codigo=code, condition=condition, edition=edition,
                                                             rarity=rarity)

        if product_from_inventory:
            precio = product_from_inventory['price']
            image_url = product_from_inventory['images'][0]['src']
            nombre = product_from_inventory['name']
            cantidad = str(product_from_inventory['stock_quantity'])
            self.quantity.setText(cantidad)
            self.message.setText("Carta en Inventario")
        else:
            info = tyt.get_card_info(set_code=code, edition=edition,
                                     condition=condition.split(" ")[0], hide_oos=False,
                                     rarity=rarity)
            if info[0]:
                precio = tyt.get_rounded_price(info[0][0]["price"])
                image_url = info[0][0]["image"]
                nombre = info[0][0]["card_name"]
                self.quantity.setText("")
                self.message.setText("Carta en T&T")

        if info[0] or product_from_inventory:
            image = QImage()
            image.loadFromData(requests.get(image_url).content)

            self.image.setPixmap(QPixmap(image))
            self.image.show()
            nombre = nombre.replace(code + " ", "").replace(f" - {edition}", "").\
                replace(f" - {condition.split(' ')[0]}", "").replace(f" - {rarity}", "")
            self.name.setText(nombre)
            self.prize.setText("CRC" + precio)
        else:
            self.message.setText("Carta no encontrada")
            self.quantity.setText("")


if __name__ == "__main__":
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec_()

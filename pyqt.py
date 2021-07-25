import requests
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from helper.tyt_utils import TYTUtils
from helper.utils import Utils
from helper.wcapi_utils import WCAPIUtils

wcapi = WCAPIUtils()
tyt = TYTUtils()
utils = Utils()


class Validator(QtGui.QValidator):
    def validate(self, string, pos):
        return QtGui.QValidator.Acceptable, string.upper(), pos


class MainApp(QMainWindow):
    id = ""

    def __init__(self, parent=None, *args):
        super(MainApp, self).__init__(parent=parent)
        rarity_terms = wcapi.get_rarity_terms()
        edition_terms = wcapi.get_edition_terms()
        condition_terms = wcapi.get_condition_terms()
        card_type_terms = wcapi.get_card_type_terms()
        self.image_path = ""
        self.setFixedSize(620, 520)
        self.setWindowTitle("YgoMarketCR")

        # Elementos
        self.image = QLabel(self)

        # Card Code
        self.card_code_label = QLabel(self)
        self.card_code_label.setText("Codigo de carta")
        self.card_code = QLineEdit(self)
        self.card_code.setPlaceholderText("codigo")
        self.card_code.setText("GFTP-EN038")
        self.card_code_label.setGeometry(10, 10, 100, 10)
        self.card_code.setGeometry(10, 30, 95, 30)
        self.card_code.setValidator(Validator(self))
        self.card_code.setMaxLength(10)

        # Image
        self.image.setGeometry(370, 10, 240, 350)
        self.image.setScaledContents(True)
        self.load_image = QPushButton("Cargar Imagen...", self)
        self.load_image.clicked.connect(self.slot_load_image)
        self.load_image.setGeometry(420, 370, 130, 30)

        # Condition
        self.condition_label = QLabel(self)
        self.condition_label.setText("Condicion")
        self.condition = QComboBox(self)
        self.condition.addItems(condition_terms)
        self.condition_label.setGeometry(10, 50, 80, 40)
        self.condition.setGeometry(5, 70, 100, 40)

        # Edition
        self.edition_label = QLabel(self)
        self.edition_label.setText("Edicion")
        self.edition = QComboBox(self)
        self.edition.addItems(edition_terms)
        self.edition_label.setGeometry(10, 90, 130, 40)
        self.edition.setGeometry(5, 110, 130, 40)

        # Rareza
        self.rarity_label = QLabel(self)
        self.rarity_label.setText("Rareza")
        self.rarity = QComboBox(self)
        self.rarity.addItems(rarity_terms)
        self.rarity_label.setGeometry(10, 130, 130, 40)
        self.rarity.setGeometry(5, 150, 180, 40)

        # Boton buscar
        self.buscar = QPushButton("Buscar", self)
        self.buscar.setGeometry(50, 190, 80, 40)
        self.buscar.clicked.connect(self.slot_load)

        # Info label
        self.info_label = QLabel(self)
        self.info_label.setText("Datos de la carta:")
        self.info_label.setGeometry(10, 260, 180, 40)

        # Name of the card
        self.name_label = QLabel(self)
        self.name_label.setText("Nombre de la Carta")
        self.name = QLineEdit(self)
        self.name_label.setGeometry(10, 290, 350, 40)
        self.name.setGeometry(10, 320, 400, 30)

        # Stock
        self.stock = QComboBox(self)
        self.stock_label = QLabel(self)
        self.stock_label.setText("Stock")
        self.stock_label.setGeometry(10, 350, 80, 40)
        self.stock.setGeometry(5, 380, 80, 30)
        self.stock.addItems([str(i) for i in range(0, 100)])

        # Prize
        self.prize = QLineEdit(self)
        self.prize_label = QLabel(self)
        self.prize_label.setText("Precio")
        self.prize_label.setGeometry(100, 350, 80, 40)
        self.prize.setGeometry(100, 380, 80, 30)
        self.prize.setText("0")

        # Tipo de Carta
        self.card_type_label = QLabel(self)
        self.card_type_label.setText("Tipo de Carta")
        self.card_type = QComboBox(self)
        self.card_type.addItems(card_type_terms)
        self.card_type_label.setGeometry(180, 350, 180, 40)
        self.card_type.setGeometry(180, 370, 100, 40)

        # Message
        self.message = QLabel(self)
        self.message.setGeometry(250, 430, 200, 40)

        # Botones de ingresar y actualizar
        self.insert_button = QPushButton("Ingresar", self)
        self.update_button = QPushButton("Actualizar", self)
        self.insert_button.setGeometry(200, 470, 100, 50)
        self.insert_button.clicked.connect(self.slot_insert)
        self.update_button.setGeometry(300, 470, 100, 50)
        self.update_button.clicked.connect(self.slot_update)
        self.insert_button.setDisabled(True)
        self.update_button.setDisabled(True)

    def slot_update(self):
        data = {
            "name": self.name.text(),
            "stock_quantity": self.stock.currentText(),
            "regular_price": self.prize.text()
        }

        wcapi.update_product(id=self.id, data=data)

    def slot_load_image(self):
        # Select an image
        file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Selecciona una imagen", '.',
                                                          "(*.jpeg *.png *.jpg *.bmp)")[0]
        if file_name:
            image = QImage(file_name)
            self.image.setPixmap(QPixmap(image))
            self.image.show()
        self.image_path = file_name

    def slot_insert(self):
        image_url = (wcapi.upload_image(self.image_path) if self.image_path else "")
        im = ([{"src": image_url, "position": 0}] if image_url else [])

        data = {
            "images": im,
            "attributes": [
                {
                    "id": 4,
                    "name": "Código",
                    "position": 0,
                    "visible": True,
                    "variation": False,
                    "options": [
                        self.card_code.text()
                    ]
                },
                {
                    "id": 6,
                    "name": "Edición",
                    "position": 1,
                    "visible": True,
                    "variation": False,
                    "options": [
                        self.edition.currentText()
                    ]
                },
                {
                    "id": 7,
                    "name": "Expansión",
                    "position": 2,
                    "visible": True,
                    "variation": False,
                    "options": [
                        self.card_code.text().split("-")[0]
                    ]
                },
                {
                    "id": 5,
                    "name": "Rareza",
                    "position": 3,
                    "visible": True,
                    "variation": False,
                    "options": [
                        self.rarity.currentText()
                    ]
                },
                {
                    "id": 0,
                    "name": "Estado",
                    "position": 4,
                    "visible": True,
                    "variation": False,
                    "options": [
                        utils.get_condition(self.condition.currentText())
                    ]
                },
                {
                    "id": 8,
                    "name": "Tipo",
                    "position": 5,
                    "visible": True,
                    "variation": False,
                    "options": [
                        self.card_type.currentText()
                    ]
                }
            ],
            "name": self.name.text(),
            "manage_stock": True,
            "stock_quantity": int(self.stock.currentText()),
            "regular_price": self.prize.text()
        }

        wcapi.insert_product(data=data)
        self.insert_button.setDisabled(True)
        self.update_button.setDisabled(False)
        self.message.setText("")
        self.image_path = ""

    def slot_load(self):
        self.id = ""
        code = self.card_code.text()
        condition = self.condition.currentText()
        edition = self.edition.currentText()
        rarity = self.rarity.currentText()
        info = [[], [], []]
        product_from_inventory = wcapi.get_product_by_filter(codigo=code, condition=condition, edition=edition,
                                                             rarity=rarity)

        # If card exists from inventory
        if product_from_inventory:
            precio = product_from_inventory['price']
            images = product_from_inventory['images']
            image_url = (images[0]["src"] if len(images) > 0 else "")
            nombre = product_from_inventory['name']
            cantidad = str(product_from_inventory['stock_quantity'])
            self.stock.setCurrentText(cantidad)
            self.message.setText("Carta en Inventario")
            self.insert_button.setDisabled(True)
            self.update_button.setDisabled(False)
            self.id = product_from_inventory["id"]
            self.card_type.setCurrentText(product_from_inventory["attributes"][5]["options"][0])
        else:
            info = tyt.get_card_info(set_code=code, edition=edition,
                                     condition=condition.split(" ")[0], hide_oos=False,
                                     rarity=rarity)
            if info and info[0]:
                precio = tyt.get_rounded_price(info[0][0]["price"])
                image_url = info[0][0]["image"]
                nombre = info[0][0]["card_name"]
                self.stock.setCurrentText("0")
                self.message.setText("Carta en T&T")
                self.insert_button.setDisabled(False)
                self.update_button.setDisabled(True)

        if (info and info[0]) or product_from_inventory:
            if image_url:
                image = QImage()
                image.loadFromData(requests.get(image_url).content)
                self.image.setPixmap(QPixmap(image))
                self.image.show()
                self.image_path = image_url
            else:
                self.image.clear()

            self.name.setText(f"{code} {nombre} - {edition} - {condition} - {rarity}")
            self.prize.setText(precio)
        else:
            self.message.setText("Carta no encontrada")
            self.stock.setCurrentText("0")
            self.name.setText(f"{code}  - {edition} - {condition} - {rarity}")
            self.prize.setText("0")
            self.image.clear()
            self.insert_button.setDisabled(False)
            self.update_button.setDisabled(True)


if __name__ == "__main__":
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec_()

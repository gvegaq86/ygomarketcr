import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from helper.tyt_utils import TYTUtils
from helper.wcapi_utils import WCAPIUtils

wcapi = WCAPIUtils()
tyt = TYTUtils()


class MainApp(QMainWindow):
    id = ""

    def __init__(self, parent=None, *args):
        super(MainApp, self).__init__(parent=parent)
        rarity_terms = wcapi.get_rarity_terms()
        edition_terms = wcapi.get_edition_terms()
        condition_terms = wcapi.get_condition_terms()

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

        # Image
        self.image.setGeometry(370, 10, 240, 350)
        self.image.setScaledContents(True)
        self.load_image = QPushButton("Cargar Imagen...", self)
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
        self.info_label.setGeometry(10, 240, 180, 40)

        # Name of the card
        self.name_label = QLabel(self)
        self.name_label.setText("Nombre de la Carta")
        self.name = QLineEdit(self)
        self.name_label.setGeometry(10, 270, 350, 40)
        self.name.setGeometry(10, 300, 320, 30)

        # Stock
        self.stock = QLineEdit(self)
        self.stock_label = QLabel(self)
        self.stock_label.setText("Stock")
        self.stock_label.setGeometry(10, 330, 80, 40)
        self.stock.setGeometry(10, 360, 80, 30)

        # Prize
        self.prize = QLineEdit(self)
        self.prize_label = QLabel(self)
        self.prize_label.setText("Precio")
        self.prize_label.setGeometry(100, 330, 80, 40)
        self.prize.setGeometry(100, 360, 80, 30)

        # Message
        self.message = QLabel(self)
        self.message.setGeometry(250, 390, 200, 40)

        # Botones de ingresar y actualizar
        self.insert_button = QPushButton("Ingresar", self)
        self.update_button = QPushButton("Actualizar", self)
        self.insert_button.setGeometry(200, 450, 100, 50)
        self.insert_button.clicked.connect(self.slot_load)
        self.update_button.setGeometry(300, 450, 100, 50)
        self.update_button.clicked.connect(self.slot_update)
        self.insert_button.setDisabled(True)
        self.update_button.setDisabled(True)

    def slot_update(self):
        data = {
            "name": self.name.text(),
            "stock_quantity": self.stock.text(),
            "regular_price": self.prize.text()
        }

        wcapi.update_product(id=self.id, data=data)

    def slot_insert(self):
        data = {
            "attributes": self.card_code.text(),
            "code": self.card_code.text(),
            "name": self.name.text(),
            "stock_quantity": self.stock.text(),
            "regular_price": self.prize.text()
        }

        wcapi.insert_product(id=self.id, data=data)

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
            image_url = product_from_inventory['images'][0]['src']
            nombre = product_from_inventory['name']
            cantidad = str(product_from_inventory['stock_quantity'])
            self.stock.setText(cantidad)
            self.message.setText("Carta en Inventario")
            self.insert_button.setDisabled(True)
            self.update_button.setDisabled(False)
            self.id = product_from_inventory["id"]
        else:
            info = tyt.get_card_info(set_code=code, edition=edition,
                                     condition=condition.split(" ")[0], hide_oos=False,
                                     rarity=rarity)
            if info and info[0]:
                precio = tyt.get_rounded_price(info[0][0]["price"])
                image_url = info[0][0]["image"]
                nombre = info[0][0]["card_name"]
                self.stock.setText("")
                self.message.setText("Carta en T&T")
                self.insert_button.setDisabled(False)
                self.update_button.setDisabled(True)

        if (info and info[0]) or product_from_inventory:
            image = QImage()
            image.loadFromData(requests.get(image_url).content)

            self.image.setPixmap(QPixmap(image))
            self.image.show()

            self.name.setText(nombre)
            self.prize.setText(precio)
        else:
            self.message.setText("Carta no encontrada")
            self.stock.setText("")
            self.name.setText("")
            self.prize.setText("")
            self.image.clear()
            self.insert_button.setDisabled(True)
            self.update_button.setDisabled(False)


if __name__ == "__main__":
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec_()

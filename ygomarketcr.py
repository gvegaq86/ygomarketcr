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
        completer = QCompleter(wcapi.code_list)
        rarity_terms = wcapi.get_rarity_terms()
        edition_terms = wcapi.get_edition_terms()
        condition_terms = wcapi.get_condition_terms()
        card_type_terms = wcapi.get_card_type_terms()
        self.categories_terms = wcapi.get_categories_terms()
        self.edit_tags_terms = wcapi.get_edit_tags_terms()
        self.image_path = ""
        self.i = 1
        self.image_list = []
        self.setFixedSize(620, 500)
        self.setWindowTitle("YgoMarketCR")
        self.selected_categories = []
        self.selected_tags = []

        # Elementos
        self.image = QLabel(self)

        # Card Code
        self.card_code_label = QLabel(self)
        self.card_code_label.setText("Codigo de carta")
        self.card_code = QLineEdit(self)
        self.card_code.setPlaceholderText("codigo")
        self.card_code.setValidator(Validator(self))
        self.card_code_label.setGeometry(10, 10, 100, 10)
        self.card_code.setGeometry(10, 30, 95, 30)
        self.card_code.setMaxLength(10)
        self.card_code.textChanged.connect(self.update_card_code)
        self.card_code.setCompleter(completer)

        # Image
        self.image.setGeometry(370, 10, 240, 350)
        self.image.setScaledContents(True)
        self.load_image = QPushButton("Cargar Imagen...", self)
        self.load_image.clicked.connect(self.slot_load_image)
        self.load_image.setGeometry(320, 360, 130, 30)

        # Image google
        self.load_image_google = QPushButton("Buscar imagen en google", self)
        self.load_image_google.clicked.connect(self.slot_load_image_from_google)
        self.load_image_google.setGeometry(440, 360, 175, 30)

        # Siguiente imagen google
        self.next_image = QPushButton("Siguiente imagen", self)
        self.next_image.clicked.connect(self.slot_next_image)
        self.next_image.setGeometry(440, 390, 130, 30)

        # Condition
        self.condition_label = QLabel(self)
        self.condition_label.setText("Condicion")
        self.condition = QComboBox(self)
        self.condition.addItems(condition_terms)
        self.condition_label.setGeometry(115, -5, 80, 40)
        self.condition.setGeometry(110, 20, 100, 40)
        self.condition.currentIndexChanged.connect(self.update_name)

        # Edition
        self.edition_label = QLabel(self)
        self.edition_label.setText("Edicion")
        self.edition = QComboBox(self)
        self.edition.addItems(edition_terms)
        self.edition_label.setGeometry(215, -5, 130, 40)
        self.edition.setGeometry(210, 20, 130, 40)
        self.edition.currentIndexChanged.connect(self.update_name)

        # Rareza
        self.rarity_label = QLabel(self)
        self.rarity_label.setText("Rareza")
        self.rarity = QComboBox(self)
        self.rarity.addItems(rarity_terms)
        self.rarity_label.setGeometry(10, 60, 130, 40)
        self.rarity.setGeometry(5, 80, 180, 40)
        self.rarity.currentIndexChanged.connect(self.update_name)

        # Boton buscar
        self.buscar = QPushButton("Buscar", self)
        self.buscar.setGeometry(190, 80, 80, 40)
        self.buscar.clicked.connect(self.slot_load)

        # Boton Limpiar
        self.clear = QPushButton("Limpiar", self)
        self.clear.setGeometry(260, 80, 80, 40)
        self.clear.clicked.connect(self.slot_clear)

        # Info label
        self.info_label = QLabel(self)
        self.info_label.setText("Datos de la carta:")
        self.info_label.setGeometry(10, 130, 180, 40)

        # Name of the card
        self.card_name_label = QLabel(self)
        self.card_name_label.setText("Nombre de la Carta")
        self.card_name = QLineEdit(self)
        self.card_name_label.setGeometry(10, 160, 350, 40)
        self.card_name.setGeometry(10, 165, 350, 25)
        self.card_name.setPlaceholderText("Nombre de la carta")
        self.card_name.textChanged.connect(self.update_name)
        self.card_name.setValidator(Validator(self))

        # Nombre del  Item
        self.item_name_label = QLabel(self)
        self.item_name_label.setText("Nombre del Item")
        self.item_name = QLineEdit(self)
        self.item_name_label.setGeometry(10, 195, 350, 40)
        self.item_name.setGeometry(10, 200, 350, 25)
        self.item_name.setPlaceholderText("Nombre del Item")
        self.item_name.setDisabled(True)

        # Stock
        self.stock = QLineEdit(self)
        self.stock_label = QLabel(self)
        self.stock_label.setText("Stock")
        self.stock_label.setGeometry(10, 220, 80, 40)
        self.stock.setGeometry(10, 245, 40, 30)
        self.stock.setText("0")

        # Prize
        self.prize = QLineEdit(self)
        self.prize_label = QLabel(self)
        self.prize_label.setText("Precio")
        self.prize_label.setGeometry(60, 220, 80, 40)
        self.prize.setGeometry(60, 245, 80, 25)
        self.prize.setText("0")

        # Tipo de Carta
        self.card_type_label = QLabel(self)
        self.card_type_label.setText("Tipo de Carta")
        self.card_type = QComboBox(self)
        self.card_type.addItems(card_type_terms)
        self.card_type_label.setGeometry(145, 220, 180, 40)
        self.card_type.setGeometry(140, 240, 100, 40)

        # Categorias
        self.categories_label = QLabel(self)
        self.categories_label.setText("Categorias")
        self.categories_label.setGeometry(30, 290, 100, 40)

        self.frame = QFrame(self)
        self.frame.setGeometry(30, 330, 100, 100)
        self.avanzado = QCheckBox("Avanzado", self.frame)
        self.avanzado.setChecked(True)

        self.frame2 = QFrame(self)
        self.frame2.setGeometry(30, 350, 100, 100)
        self.old_school = QCheckBox("Old School", self.frame2)

        self.frame3 = QFrame(self)
        self.frame3.setGeometry(30, 370, 100, 100)
        self.high_end = QCheckBox("High-End", self.frame3)

        # Etiquetas
        self.tag_label = QLabel(self)
        self.tag_label.setText("Etiquetas")
        self.tag_label.setGeometry(130, 290, 100, 40)

        self.frame4 = QFrame(self)
        self.frame4.setGeometry(130, 330, 100, 100)
        self.goat = QCheckBox("goat", self.frame4)

        self.frame5 = QFrame(self)
        self.frame5.setGeometry(130, 350, 100, 100)
        self.jck = QCheckBox("jck", self.frame5)

        # Botones de ingresar y actualizar
        self.insert_button = QPushButton("Ingresar", self)
        self.update_button = QPushButton("Actualizar", self)
        self.delete_button = QPushButton("Eliminar", self)
        self.insert_button.setGeometry(10, 420, 100, 50)
        self.insert_button.clicked.connect(self.slot_insert)
        self.update_button.setGeometry(110, 420, 100, 50)
        self.update_button.clicked.connect(self.slot_update)
        self.delete_button.setGeometry(210, 420, 100, 50)
        self.delete_button.clicked.connect(self.slot_delete)
        self.clear_form()

    def update_card_code(self, event):
        self.card_name.setText("")
        self.update_name(event)

    def check_checkboxes(self, options):
        for o in options:
            if o == "High-End":
                self.high_end.setChecked(True)
            if o == "Avanzado":
                self.avanzado.setChecked(True)
            if o == "Old School":
                self.old_school.setChecked(True)
            if o == "jck":
                self.jck.setChecked(True)
            if o == "goat":
                self.goat.setChecked(True)

    def get_category_list(self):
        categories = []
        if self.avanzado.checkState():
            categories.append("Avanzado")
        if self.high_end.checkState():
            categories.append("High-End")
        if self.old_school.checkState():
            categories.append("Old School")
        return categories

    def get_tags_list(self):
        tags = []
        if self.jck.checkState():
            tags.append("jck")
        if self.goat.checkState():
            tags.append("goat")
        return tags


    def update_name(self, event):
        self.item_name.setText(f"{self.card_code.text()} {self.card_name.text()} - {self.edition.currentText()} - "
                               f"{self.condition.currentText()} - {self.rarity.currentText()}")

    def display_dialog(self, message):
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec_()

    def clear_form(self):
        self.card_code.clear()
        self.condition.setCurrentText("NM")
        self.edition.setCurrentText("1st Edition")
        self.rarity.setCurrentText("Ultra Rare")
        self.card_name.clear()
        self.stock.setText("0")
        self.prize.setText("0")
        self.card_type.setCurrentText("Mounstruo")
        self.insert_button.setDisabled(True)
        self.update_button.setDisabled(True)
        self.delete_button.setDisabled(True)
        self.card_code.setFocus()
        self.id = ""
        self.image_path = ""
        self.image.clear()
        self.avanzado.setChecked(False)
        self.high_end.setChecked(False)
        self.old_school.setChecked(False)
        self.jck.setChecked(False)
        self.goat.setChecked(False)
        self.item_name.setText(f"{self.card_code.text()} - {self.edition.currentText()} - "
                               f"{self.condition.currentText()} - {self.rarity.currentText()}")

    def slot_update(self):
        try:
            tags = []
            categories = []

            selected_tags = self.get_tags_list()
            selected_categories = self.get_category_list()

            for tag in selected_tags:
                t = list(filter(lambda x: x["name"] == tag, self.edit_tags_terms))[0]
                tags.append({'id': t["id"], 'name': t["name"], 'slug': t["slug"]})

            for cat in selected_categories:
                t = list(filter(lambda x: x["name"] == cat, self.categories_terms))[0]
                categories.append({'id': t["id"], 'name': t["name"], 'slug': t["slug"]})

            data = {
                "name": self.item_name.text(),
                "stock_quantity": self.stock.text(),
                "regular_price": self.prize.text()
            }

            if tags:
                data["tags"] = tags

            if categories:
                data["categories"] = categories

            if self.image_path:
                image_url = wcapi.upload_image(self.image_path)
                data["images"] = [{"src": image_url, "position": 0}]

            wcapi.update_product(id=self.id, data=data)
            self.display_dialog(f"La carta '{self.item_name.text()}' ha sido actualizada correctamente.")
        except Exception as e:
            self.display_dialog(f"Ocurrio el siguiente error actualizando la carta '{self.item_name.text()}' del "
                                f"inventario: {str(e)}.")

    def slot_delete(self):
        try:
            item = wcapi.get_products_by_id(id=self.id)
            wcapi.delete_product(id=self.id)
            if item["images"]:
                wcapi.delete_image(id=item["images"][0]["id"])
            self.display_dialog(f"La carta '{self.item_name.text()}' ha sido eliminada del inventario.")
            self.clear_form()
        except Exception as e:
            self.display_dialog(f"Ocurrio el siguiente error eliminando la carta '{self.item_name.text()}' del "
                                f"inventario: {str(e)}.")

    def slot_load_image(self):
        # Select an image
        file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Selecciona una imagen", '.',
                                                          "(*.jpeg *.png *.jpg *.bmp)")[0]
        if file_name:
            image = QImage(file_name)
            self.image.setPixmap(QPixmap(image))
            self.image.show()
        self.image_path = file_name

    def slot_next_image(self):
        self.next_image.setDisabled(True)
        try:
            if self.image_list and len(self.image_list) > self.i:
                self.image_path = self.image_list[self.i]["link"]
                if self.image_path:
                    image = QImage()
                    image.loadFromData(requests.get(self.image_path, timeout=2).content)
                    self.image.setPixmap(QPixmap(image))
                    self.image.show()
                if len(self.image_list) - 1 == self.i:
                    self.i = 0
                else:
                    self.i += 1
        except:
            pass
        finally:
            self.next_image.setDisabled(False)

    def slot_load_image_from_google(self):
        self.i = 1
        self.image_list = utils.get_image_from_google(
            self.item_name.text().replace(f" - {self.condition.currentText()}", ""))
        if self.image_list:
            self.image_path = self.image_list[0]["link"]
            if self.image_path:
                image = QImage()
                image.loadFromData(requests.get(self.image_path).content)
                self.image.setPixmap(QPixmap(image))
                self.image.show()
            else:
                self.image.clear()
        else:
            self.image_path = ""
            self.image.clear()

    def slot_insert(self):
        try:
            tags = []
            categories = []

            image_url = self.image_path
            im = ([{"src": image_url, "position": 0}] if image_url else [])

            selected_tags = self.get_tags_list()
            selected_categories = self.get_category_list()

            for tag in selected_tags:
                t = list(filter(lambda x: x["name"] == tag, self.edit_tags_terms))[0]
                tags.append({'id': t["id"], 'name': t["name"], 'slug': t["slug"]})

            for cat in selected_categories:
                t = list(filter(lambda x: x["name"] == cat, self.categories_terms))[0]
                categories.append({'id': t["id"], 'name': t["name"], 'slug': t["slug"]})

            data = {
                "tags": tags,
                "categories": categories,
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
                "name": self.item_name.text(),
                "manage_stock": True,
                "stock_quantity": int(self.stock.text()),
                "regular_price": self.prize.text()
            }

            response = wcapi.insert_product(data=data)
            wcapi.codes.append(list(filter(lambda x: x["name"] == self.card_code.text(),
                                           wcapi.get_codes(page=1, per_page=10, order_by="id")))[0])
            self.id = response["id"]
            self.insert_button.setDisabled(True)
            self.update_button.setDisabled(False)
            self.delete_button.setDisabled(False)
            self.image_path = ""
            self.display_dialog(f"La carta '{self.item_name.text()}' ha sido ingresada correctamente al inventario.")
        except Exception as e:
            self.display_dialog(f"Ocurrio el siguiente error insertando la carta '{self.item_name.text()}' en el "
                                f"inventario: {str(e)}.")

    def slot_clear(self):
        self.clear_form()

    def slot_load(self):
        self.item_name.setText(f"{self.card_code.text()} - {self.edition.currentText()} - "
                               f"{self.condition.currentText()} - {self.rarity.currentText()}")

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
            self.selected_categories = [c["name"] for c in product_from_inventory["categories"]]
            self.selected_tags = [c["name"] for c in product_from_inventory["tags"]]

            self.check_checkboxes(self.selected_categories)
            self.check_checkboxes(self.selected_tags)

            precio = product_from_inventory['price']
            images = product_from_inventory['images']
            image_url = (images[0]["src"] if len(images) > 0 else "")
            nombre = product_from_inventory['name']
            cantidad = str(product_from_inventory['stock_quantity'])
            self.stock.setText(cantidad)
            self.insert_button.setDisabled(True)
            self.update_button.setDisabled(False)
            self.delete_button.setDisabled(False)
            self.id = product_from_inventory["id"]
            self.card_type.setCurrentText(product_from_inventory["attributes"][5]["options"][0])
            self.card_name.setText(
                nombre.split(" - ")[0].replace(product_from_inventory["attributes"][0]["options"][0], ""))
            self.item_name.setText(f"{code} {self.card_name.text()} - {edition} - {condition} - {rarity}")
        else:
            info = tyt.get_card_info(set_code=code, edition=edition,
                                     condition=condition.split(" ")[0], hide_oos=False,
                                     rarity=rarity)
            if info and info[0]:
                precio = tyt.get_rounded_price(info[0][0]["price"])
                image_url = info[0][0]["image"]
                nombre = info[0][0]["card_name"]
                self.stock.setText("0")
                self.insert_button.setDisabled(False)
                self.update_button.setDisabled(True)
                self.image_path = image_url
                self.card_type.setFocus()
                self.card_name.setText(nombre)
                self.display_dialog(f"La carta '{self.item_name.text()}' no existe en el inventario pero si en T&T.")
        if (info and info[0]) or product_from_inventory:
            if image_url:
                image = QImage()
                image.loadFromData(requests.get(image_url).content)
                self.image.setPixmap(QPixmap(image))
                self.image.show()
            else:
                self.image.clear()
            self.prize.setText(precio)
        else:
            self.stock.setText("0")
            self.item_name.setText(f"{code}  - {edition} - {condition} - {rarity}")
            self.prize.setText("0")
            self.image.clear()
            item_info = utils.get_card_info_from_set_code(code)
            if item_info:
                self.rarity.setCurrentText(item_info["set_rarity"])
                self.card_name.setText(item_info["name"])
            self.slot_load_image_from_google()
            self.insert_button.setDisabled(False)
            self.update_button.setDisabled(True)
            self.delete_button.setDisabled(True)
            self.display_dialog(f"La carta '{self.item_name.text()}' no existe en el inventario ni en T&T.")


if __name__ == "__main__":
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec_()

import json
import os
import sys
import platform

import requests
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from helper.tyt_utils import TYTUtils
from helper.utils import Utils
from helper.wcapi_utils import WCAPIUtils

wcapi = WCAPIUtils()
tyt = TYTUtils()
utils = Utils()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Validator(QtGui.QValidator):
    def validate(self, string, pos):
        return QtGui.QValidator.Acceptable, string.upper(), pos


class MainApp(QMainWindow):
    id = ""
    item_info = None

    def __init__(self):
        super().__init__()
        qApp.installEventFilter(self)
        self.setStyleSheet("background-color: #27282c;")
        self.setWindowIcon(QtGui.QIcon(resource_path("images/icon.ico")))
        edition_terms = ['1st Edition', 'Duel Terminal', 'Limited Edition', 'Unlimited']
        condition_terms = ['LP', 'NM', 'PL', 'MP', 'HP']
        languages = ['', 'English', 'Spanish', 'French', 'Italian', 'Korean', 'Japanese', 'Portuguese', 'German']
        card_type_terms = ['', 'Monstruo', 'Magia', 'Trampa', 'Fusión', 'Link', 'XYZ', 'Token', 'Ritual', 'Synchro',
                           'Pendulum', 'Skill', 'Token']
        completer = QCompleter(wcapi.code_list)
        self.dash_was_pressed = False

        rarity_terms = wcapi.get_rarity_terms()
        self.categories_terms = wcapi.get_categories_terms()
        self.edit_tags_terms = wcapi.get_edit_tags_terms()

        # Elementos
        self.selected_tags = []
        self.image = QLabel(self)
        self.setWindowTitle("YgoMarketCR")
        self.setFixedSize(620, 500)

        # Card Code
        self.card_code_label = QLabel(self)
        self.card_code_label.setStyleSheet("color: #98c379;")
        self.card_code_label.setText("Código de carta")
        self.card_code = QLineEdit(self)
        self.card_code.setStyleSheet("color: black; background-color: hsla(0,0%,100%,0.8); font: 15px;")
        self.card_code.setPlaceholderText("Código")
        self.card_code.setValidator(Validator(self))
        self.card_code_label.setGeometry(10, 10, 100, 10)
        self.card_code.setGeometry(10, 25, 95, 30)
        self.card_code.setMaxLength(10)
        self.card_code.textEdited.connect(self.update_card_code)
        self.card_code.setCompleter(completer)
        self.card_code.returnPressed.connect(self.slot_load)
        self.card_code.setAlignment(Qt.AlignCenter)

        # Agregar "EN" checkbox
        self.frame00 = QFrame(self)
        self.frame00.setGeometry(5, 55, 130, 20)
        self.add_en_checkbox = QCheckBox("Agregar 'EN'", self.frame00)
        self.add_en_checkbox.setStyleSheet("color: white;")
        self.add_en_checkbox.setChecked(True)

        # Image
        self.image.setGeometry(370, 10, 240, 350)
        self.image.setStyleSheet("border-color: white;")
        self.image.setScaledContents(True)
        self.load_image = QPushButton("Cargar Imagen...", self)
        self.load_image.setStyleSheet(":enabled { color: black"
                                      + "; background-color: white"
                                      + "; border-color: black"
                                      + " } :hover { color: black"
                                      + "; border-color: black"
                                      + "; background-color: lightgray"
                                      + " } :disabled { color: black"
                                      + "; border-color: black"
                                      + "; background-color: gray" + " }")
        self.load_image.clicked.connect(self.slot_load_image)
        self.load_image.setGeometry(325, 370, 120, 30)

        # Image google
        self.load_image_google = QPushButton("Buscar imagen en google", self)
        self.load_image_google.setStyleSheet(":enabled { color: black"
                                             + "; background-color: white"
                                             + "; border-color: black"
                                             + " } :hover { color: black"
                                             + "; border-color: black"
                                             + "; background-color: lightgray"
                                             + " } :disabled { color: black"
                                             + "; border-color: black"
                                             + "; background-color: gray" + " }")
        self.load_image_google.clicked.connect(self.slot_load_image_from_google)
        self.load_image_google.setGeometry(445, 370, 160, 30)

        # Siguiente imagen google
        self.next_image = QPushButton("Siguiente imagen", self)
        self.next_image.setStyleSheet(":enabled { color: black"
                                      + "; background-color: white"
                                      + "; border-color: black"
                                      + " } :hover { color: black"
                                      + "; border-color: black"
                                      + "; background-color: lightgray"
                                      + " } :disabled { color: black"
                                      + "; border-color: black"
                                      + "; background-color: gray" + " }")
        self.next_image.clicked.connect(self.slot_next_image)
        self.next_image.setGeometry(445, 400, 160, 30)

        # Consultar en T&T
        self.ask_tyt = QPushButton("", self)
        self.ask_tyt.setStyleSheet(":enabled { color: black"
                                   + "; background-color: white"
                                   + "; border-color: black"
                                   + " } :hover { color: black"
                                   + "; border-color: black"
                                   + "; background-color: lightgray"
                                   + " } :disabled { color: black"
                                   + "; border-color: black"
                                   + "; background-color: gray" + " }")
        self.ask_tyt.setIcon(QIcon(resource_path("images/trollandtoad.com.jpg")))
        self.ask_tyt.setIconSize(QtCore.QSize(70, 70))
        self.ask_tyt.clicked.connect(self.go_tyt)
        self.ask_tyt.setGeometry(325, 440, 80, 50)

        # Consultar en TCGPlayer
        self.ask_tcgp = QPushButton("", self)
        self.ask_tcgp.setStyleSheet(":enabled { color: black"
                                    + "; background-color: white"
                                    + "; border-color: black"
                                    + " } :hover { color: black"
                                    + "; border-color: black"
                                    + "; background-color: lightgray"
                                    + " } :disabled { color: black"
                                    + "; border-color: black"
                                    + "; background-color: gray" + " }")
        self.ask_tcgp.setIcon(QIcon(resource_path("images/TCGplayer.png")))
        self.ask_tcgp.setIconSize(QtCore.QSize(60, 60))
        self.ask_tcgp.clicked.connect(self.go_tcgp)
        self.ask_tcgp.setGeometry(410, 440, 80, 50)

        # Consultar en Ebay
        self.ask_ebay = QPushButton("", self)
        self.ask_ebay.setStyleSheet(":enabled { color: black"
                                    + "; background-color: white"
                                    + "; border-color: black"
                                    + " } :hover { color: black"
                                    + "; border-color: black"
                                    + "; background-color: lightgray"
                                    + " } :disabled { color: black"
                                    + "; border-color: black"
                                    + "; background-color: gray" + " }")
        self.ask_ebay.setIcon(QIcon(resource_path("images/ebay.png")))
        self.ask_ebay.setIconSize(QtCore.QSize(60, 60))
        self.ask_ebay.clicked.connect(self.go_ebay)
        self.ask_ebay.setGeometry(495, 440, 80, 50)

        # Condition
        self.condition_label = QLabel(self)
        self.condition_label.setStyleSheet("color: #98c379;")
        self.condition_label.setText("Condición")
        self.condition = QComboBox(self)
        self.condition.setStyleSheet("color: black; background-color: hsla(0,0%,100%,0.8); "
                                     "selection-background-color: lightgray;")
        self.condition.addItems(condition_terms)
        self.condition_label.setGeometry(115, 10, 80, 10)
        self.condition.setGeometry(115, 25, 100, 30)
        self.condition.currentIndexChanged.connect(self.update_name)

        # Edition
        self.edition_label = QLabel(self)
        self.edition_label.setStyleSheet("color: #98c379;")
        self.edition_label.setText("Edición")
        self.edition = QComboBox(self)
        self.edition.setStyleSheet("color: black; background-color: hsla(0,0%,100%,0.8); "
                                   "selection-background-color: lightgray;")
        self.edition.addItems(edition_terms)
        self.edition_label.setGeometry(225, 10, 130, 10)
        self.edition.setGeometry(225, 25, 130, 30)
        self.edition.currentIndexChanged.connect(self.update_name)

        # Rareza
        self.rarity_label = QLabel(self)
        self.rarity_label.setStyleSheet("color: #98c379;")
        self.rarity_label.setText("Rareza")
        self.rarity = QComboBox(self)
        self.rarity.setStyleSheet("color: black; background-color: hsla(0,0%,100%,0.8); "
                                  "selection-background-color: lightgray;")
        self.rarity.addItems(rarity_terms)
        self.rarity_label.setGeometry(10, 80, 130, 10)
        self.rarity.setGeometry(10, 95, 150, 30)
        self.rarity.currentIndexChanged.connect(self.update_name)

        # Boton buscar
        self.buscar = QPushButton("", self)
        self.buscar.setStyleSheet(":enabled { color: black"
                                  + "; background-color: white"
                                  + "; border-color: black"
                                  + " } :hover { color: black"
                                  + "; border-color: black"
                                  + "; background-color: lightgray"
                                  + " } :disabled { color: black"
                                  + "; border-color: black"
                                  + "; background-color: gray" + " }")
        self.buscar.setIcon(QIcon(resource_path("images/search.png")))
        self.buscar.setGeometry(200, 70, 50, 50)
        self.buscar.setIconSize(QtCore.QSize(35, 35))
        self.buscar.clicked.connect(self.slot_load)

        # Boton Limpiar
        self.clear = QPushButton("", self)
        self.clear.setStyleSheet(":enabled { color: black"
                                 + "; background-color: white"
                                 + "; border-color: black"
                                 + " } :hover { color: black"
                                 + "; border-color: black"
                                 + "; background-color: lightgray"
                                 + " } :disabled { color: black"
                                 + "; border-color: black"
                                 + "; background-color: gray" + " }")
        self.clear.setIcon(QIcon(resource_path("images/clear.png")))
        self.clear.setIconSize(QtCore.QSize(35, 35))
        self.clear.setGeometry(255, 70, 50, 50)
        self.clear.clicked.connect(self.slot_clear)

        # Info label
        self.info_label = QLabel(self)
        self.info_label.setStyleSheet("color: #d19a66;")
        self.info_label.setText("Datos de la carta:")
        self.info_label.setGeometry(10, 150, 180, 10)

        # Idioma
        self.language_label = QLabel(self)
        self.language_label.setStyleSheet("color: #98c379;")
        self.language_label.setText("Idioma")
        self.languages_combo = QComboBox(self)
        self.languages_combo.setStyleSheet("color: black; background-color: hsla(0,0%,100%,0.8); "
                                           "selection-background-color: lightgray;")
        self.languages_combo.addItems(languages)
        self.language_label.setGeometry(250, 145, 50, 10)
        self.languages_combo.setGeometry(250, 160, 110, 20)
        self.languages_combo.currentIndexChanged.connect(self.language_combo_select)

        # Name of the card
        self.card_name_label = QLabel(self)
        self.card_name_label.setStyleSheet("color: #98c379;")
        self.card_name_label.setText("Nombre de la Carta")
        self.card_name = QLineEdit(self)
        self.card_name.setStyleSheet("color: black; background-color: hsla(0,0%,100%,0.8);")
        self.card_name_label.setGeometry(10, 170, 150, 10)
        self.card_name.setGeometry(10, 185, 350, 25)
        self.card_name.setPlaceholderText("Nombre de la carta")
        self.card_name.textChanged.connect(self.update_name)
        self.card_name.setValidator(Validator(self))

        # Nombre del  Item
        self.item_name_label = QLabel(self)
        self.item_name_label.setStyleSheet("color: #98c379;")
        self.item_name_label.setText("Nombre del Item")
        self.item_name = QLineEdit(self)
        self.item_name.setStyleSheet("color: black; background-color: hsla(0,0%,100%,0.8);")
        self.item_name_label.setGeometry(10, 220, 350, 10)
        self.item_name.setGeometry(10, 235, 350, 25)
        self.item_name.setPlaceholderText("Nombre del Item")
        self.item_name.setDisabled(True)
        self.item_name.setAlignment(QtCore.Qt.AlignLeft)

        # Stock
        self.stock = QLineEdit(self)
        self.stock.setStyleSheet("color: black; background-color: hsla(0,0%,100%,0.8);")
        self.stock_label = QLabel(self)
        self.stock_label.setStyleSheet("color: #98c379;")
        self.stock_label.setText("Stock")
        self.stock_label.setGeometry(10, 270, 80, 10)
        self.stock.setGeometry(10, 285, 40, 30)
        self.stock.setText("0")

        # Prize
        self.prize = QLineEdit(self)
        self.prize.setStyleSheet("color: black; background-color: hsla(0,0%,100%,0.8);")
        self.prize_label = QLabel(self)
        self.prize_label.setStyleSheet("color: #98c379;")
        self.prize_label.setText("Precio")
        self.prize_label.setGeometry(60, 270, 80, 10)
        self.prize.setGeometry(60, 285, 80, 30)
        self.prize.setText("0")
        self.prize.setValidator(QDoubleValidator(self))
        self.prize.setInputMask("₡0000000")

        # Tipo de Carta
        self.card_type_label = QLabel(self)
        self.card_type_label.setStyleSheet("color: #98c379;")
        self.card_type_label.setText("Tipo de Carta")
        self.card_type = QComboBox(self)
        self.card_type.setStyleSheet("color: black; background-color: hsla(0,0%,100%,0.8); "
                                     "selection-background-color: lightgray;")
        self.card_type.addItems(card_type_terms)
        self.card_type_label.setGeometry(150, 270, 180, 10)
        self.card_type.setGeometry(150, 285, 100, 30)

        # Categorias
        self.categories_label = QLabel(self)
        self.categories_label.setStyleSheet("color: #d19a66;")
        self.categories_label.setText("Categorias")
        self.categories_label.setGeometry(30, 330, 100, 10)

        self.frame = QFrame(self)
        self.frame.setGeometry(30, 350, 100, 100)
        self.avanzado = QCheckBox("Avanzado", self.frame)
        self.avanzado.setStyleSheet("color: white;")
        self.avanzado.setChecked(True)

        self.frame2 = QFrame(self)
        self.frame2.setGeometry(30, 370, 100, 100)
        self.old_school = QCheckBox("Old School", self.frame2)
        self.old_school.setStyleSheet("color: white;")

        self.frame3 = QFrame(self)
        self.frame3.setGeometry(30, 390, 100, 100)
        self.high_end = QCheckBox("High-End", self.frame3)
        self.high_end.setStyleSheet("color: white;")

        # Etiquetas
        self.tag_label = QLabel(self)
        self.tag_label.setStyleSheet("color: #d19a66;")
        self.tag_label.setText("Etiquetas")
        self.tag_label.setGeometry(130, 330, 100, 10)

        self.frame4 = QFrame(self)
        self.frame4.setGeometry(130, 350, 100, 100)
        self.goat = QCheckBox("goat", self.frame4)
        self.goat.setStyleSheet("color: white;")

        self.frame5 = QFrame(self)
        self.frame5.setGeometry(130, 370, 100, 100)
        self.jcg = QCheckBox("jcg", self.frame5)
        self.jcg.setStyleSheet("color: white;")

        self.frame6 = QFrame(self)
        self.frame6.setGeometry(130, 390, 100, 100)
        self.gvq = QCheckBox("gvq", self.frame6)
        self.gvq.setStyleSheet("color: white;")

        # Fecha Ultima Actualizacion
        self.last_update_text_label = QLabel(self)
        self.last_update_text_label.setStyleSheet("color: #d19a66;")
        self.last_update_text_label.setText("Ultima Actualizacion:")
        self.last_update_text_label.setGeometry(30, 415, 130, 10)

        self.last_update_label = QLabel(self)
        self.last_update_label.setStyleSheet("color: #98c379;")
        self.last_update_label.setText("")
        self.last_update_label.setGeometry(160, 415, 135, 10)

        # Botones de ingresar y actualizar
        self.insert_button = QPushButton("", self)
        self.insert_button.setStyleSheet(":enabled { color: black"
                                         + "; background-color: white"
                                         + "; border-color: black"
                                         + " } :hover { color: black"
                                         + "; border-color: black"
                                         + "; background-color: lightgray"
                                         + " } :disabled { color: black"
                                         + "; border-color: black"
                                         + "; background-color: gray" + " }")
        self.insert_button.setIcon(QIcon(resource_path("images/add.ico")))
        self.insert_button.setIconSize(QtCore.QSize(35, 35))
        self.update_button = QPushButton("", self)
        self.update_button.setStyleSheet(":enabled { color: black"
                                         + "; background-color: white"
                                         + "; border-color: black"
                                         + " } :hover { color: black"
                                         + "; border-color: black"
                                         + "; background-color: lightgray"
                                         + " } :disabled { color: black"
                                         + "; border-color: black"
                                         + "; background-color: gray" + " }")
        self.update_button.setIconSize(QtCore.QSize(35, 35))
        self.update_button.setIcon(QIcon(resource_path("images/save.ico")))
        self.delete_button = QPushButton("", self)
        self.delete_button.setStyleSheet(":enabled { color: black"
                                         + "; background-color: white"
                                         + "; border-color: black"
                                         + " } :hover { color: black"
                                         + "; border-color: black"
                                         + "; background-color: lightgray"
                                         + " } :disabled { color: black"
                                         + "; border-color: black"
                                         + "; background-color: gray" + " }")
        self.delete_button.setIcon(QIcon(resource_path("images/remove.ico")))
        self.delete_button.setIconSize(QtCore.QSize(35, 35))
        self.insert_button.setGeometry(55, 435, 50, 50)
        self.insert_button.clicked.connect(self.slot_insert)
        self.update_button.setGeometry(110, 435, 50, 50)
        self.update_button.clicked.connect(self.slot_update)
        self.delete_button.setGeometry(165, 435, 50, 50)
        self.delete_button.clicked.connect(self.slot_delete)
        self.clear_form()
        self.rarity.setCurrentText("Ultra Rare")

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == 45:
                self.dash_was_pressed = True
            else:
                self.dash_was_pressed = False

        return super(QWidget, self).eventFilter(obj, event)

    def update_card_code(self, event):
        if self.add_en_checkbox.checkState() and self.card_code.text() and \
                self.dash_was_pressed and self.card_code.text()[-1] == "-":
            self.card_code.setText(self.card_code.text() + "EN0")
        self.card_name.setText("")
        self.update_name(event)

    def language_combo_select(self):
        text = f"{self.card_code.text()} {self.card_name.text()} - {self.edition.currentText()} - " \
               f"{self.condition.currentText()} - {self.rarity.currentText()}"

        if self.languages_combo.currentText() == "Spanish":
            text = text + f" (SPANISH{' ' + self.card_code.text().replace('EN', 'SP') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "Italian":
            text = text + f" (ITALIAN{' ' + self.card_code.text().replace('EN', 'IT') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "Korean":
            text = text + f" (KOREAN{' ' + self.card_code.text().replace('EN', 'KR') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "Japanese":
            text = text + f" (JAPANESE{' ' + self.card_code.text().replace('EN', 'JP') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "Portuguese":
            text = text + f" (PORTUGUESE{' ' + self.card_code.text().replace('EN', 'PT') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "German":
            text = text + f" (GERMAN{' ' + self.card_code.text().replace('EN', 'DE') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "French":
            text = text + f" (FRENCH{' ' + self.card_code.text().replace('EN', 'FR') if '-EN' in self.card_code.text() else ''})"

        self.item_name.setText(text)

    def set_checkboxes(self, options):
        for o in options:
            if o == "High-End":
                self.high_end.setChecked(True)
            if o == "Avanzado":
                self.avanzado.setChecked(True)
            if o == "Old School":
                self.old_school.setChecked(True)
            if o == "jcg":
                self.jcg.setChecked(True)
                #self.display_dialog("La carta pertenece a Juan Carlos, se se requiere actualizar la cantidad de items, "
                #                    "debera ingresarse directamente en Woocommerce como un item completamente nuevo.")
            if o == "goat":
                self.goat.setChecked(True)
            if o == "gvq":
                self.gvq.setChecked(True)
                self.display_dialog("La carta pertenece a Giovanni, se se requiere actualizar la cantidad de items, "
                                    "debera ingresarse directamente en Woocommerce como un item completamente nuevo.")

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
        if self.jcg.checkState():
            tags.append("jcg")
        if self.goat.checkState():
            tags.append("goat")
        if self.gvq.checkState():
            tags.append("gvq")
        return tags

    def update_name(self, event):
        text = f"{self.card_code.text()} {self.card_name.text()} - {self.edition.currentText()} - " \
               f"{self.condition.currentText()} - {self.rarity.currentText()}"
        if self.languages_combo.currentText() == "Spanish":
            text = text + f" (SPANISH{' ' + self.card_code.text().replace('EN', 'SP') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "Italian":
            text = text + f" (ITALIAN{' ' + self.card_code.text().replace('EN', 'IT') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "Korean":
            text = text + f" (KOREAN{' ' + self.card_code.text().replace('EN', 'KR') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "Japanese":
            text = text + f" (JAPANESE{' ' + self.card_code.text().replace('EN', 'JP') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "Portuguese":
            text = text + f" (PORTUGUESE{' ' + self.card_code.text().replace('EN', 'PT') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "German":
            text = text + f" (GERMAN{' ' + self.card_code.text().replace('EN', 'DE') if '-EN' in self.card_code.text() else ''})"
        elif self.languages_combo.currentText() == "French":
            text = text + f" (FRENCH{' ' + self.card_code.text().replace('EN', 'FR') if '-EN' in self.card_code.text() else ''})"

        self.item_name.setText(text)

    def display_dialog(self, message):
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec_()

    def display_option_dialog(self, message):
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.buttonClicked.connect(self.option_dialog)
        returnValue = msg_box.exec()
        if returnValue == QMessageBox.Ok:
            return True
        else:
            return False

    def option_dialog(self, i):
        if i.text() == "OK":
            self.rarity.setCurrentText(self.item_info["set_rarity"])
            self.card_name.setText(self.item_info["name"])
            self.slot_load()

    def clear_form(self):
        self.card_code.clear()
        self.card_type.setCurrentText("")
        self.condition.setCurrentText("NM")
        self.edition.setCurrentText("1st Edition")
        self.card_name.clear()
        self.stock.setText("0")
        self.prize.setText("500")
        self.card_type.setCurrentText("Mounstruo")
        self.insert_button.setDisabled(True)
        self.update_button.setDisabled(True)
        self.delete_button.setDisabled(True)
        self.card_code.setFocus()
        self.id = ""
        self.image_path = ""
        self.image.clear()
        self.last_update_label.setText("")
        self.languages_combo.setCurrentText("English")
        self.item_name.setText(f"{self.card_code.text()} - {self.edition.currentText()} - "
                               f"{self.condition.currentText()} - {self.rarity.currentText()}")

    def slot_update(self):
        try:
            if self.card_name.text() == "":
                self.display_dialog("El nombre de la carta no puede estar en blanco.")
                self.card_name.setFocus()
                return None
            elif self.card_type.currentText() == "":
                self.display_dialog("El tipo de carta no puede estar en blanco.")
                self.card_type.showPopup()
                return None

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
                    },
                    {
                        "id": 9,
                        "name": "Idioma",
                        "position": 6,
                        "visible": True,
                        "variation": False,
                        "options": [
                            self.languages_combo.currentText()
                        ]
                    }
                ],
                "name": self.item_name.text(),
                "manage_stock": True,
                "stock_quantity": int(self.stock.text()),
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
            #self.display_dialog(f"La carta '{self.item_name.text()}' ha sido actualizada correctamente.")
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

    def go_tyt(self):
        if self.card_code.text() != "":
            edition = self.edition.currentText()
            if edition == "Unlimited":
                edition = "+"
            else:
                edition = edition.replace(" ", "+")

            link = f'https://www.trollandtoad.com/yugioh/all-yu-gi-oh-singles/7087?sort-order=L-H&item-condition=' \
                   f'{"NM" if self.condition.currentText() == "NM" else "PL"}&search-words=' \
                   f'{self.card_code.text()}+{self.card_name.text().replace(" ", "+")}+' \
                   f'{edition}+{self.rarity.currentText().replace(" ", "+")}'

            if platform.system() != "Windows":
                os.system(f'open -a "Google Chrome" "{link}"')
            else:
                os.system(f'start "chrome" "{link}"')
        else:
            self.display_dialog("El codigo de la carta debe ser ingresado.")
            self.card_code.setFocus()

    def go_ebay(self):
        if self.card_code.text() != "":
            link = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw=' \
                   f'{self.card_code.text()}+{self.card_name.text().replace(" ", "+")}+' \
                   f'{self.rarity.currentText().replace(" ", "+")}+{self.rarity.currentText().replace(" ", "+")}' \
                   f'&_sacat=183454&LH_TitleDesc=0&LH_BIN=1&_sop=15'
            if platform.system() != "Windows":
                os.system(f'open -a "Google Chrome" "{link}"')
            else:
                os.system(f'start "chrome" "{link}"')
        else:
            self.display_dialog("El codigo de la carta debe ser ingresado.")
            self.card_code.setFocus()

    def go_tcgp(self):
        if self.card_name.text() != "":
            rarity = self.rarity.currentText()
            if rarity == "Common":
                rarity = "Common%20%2F%20Short%20Print"
            else:
                rarity = rarity.replace(" ", "%20")
            link = f'https://www.tcgplayer.com/search/yugioh/product?productLineName=yugioh&' \
                   f'q={self.card_name.text().replace(" ", "%20")}&ProductTypeName=Cards&page=1&' \
                   f'RarityName={rarity}'

            if platform.system() != "Windows":
                os.system(f'open -a "Google Chrome" "{link}"')
            else:
                os.system(f'start "chrome" "{link}"')
        else:
            self.display_dialog("El nombre de la carta debe ser ingresada.")
            self.card_name.setFocus()

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
            (self.item_name.text().replace(f" - {self.condition.currentText()}", "").replace("-SP", "-EN")).split("(")[
                0])
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
            if self.card_name.text() == "":
                self.display_dialog("El nombre de la carta no puede estar en blanco.")
                self.card_name.setFocus()
                return None
            elif self.card_type.currentText() == "":
                self.display_dialog("El tipo de carta no puede estar en blanco.")
                self.card_type.showPopup()
                return None

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
                    },
                    {
                        "id": 9,
                        "name": "Idioma",
                        "position": 6,
                        "visible": True,
                        "variation": False,
                        "options": [
                            self.languages_combo.currentText()
                        ]
                    }
                ],
                "name": self.item_name.text(),
                "manage_stock": True,
                "stock_quantity": int(self.stock.text()),
                "regular_price": self.prize.text()
            }

            response = wcapi.insert_product(data=data)
            cc = list(filter(lambda x: x["name"] == self.card_code.text(),
                             wcapi.get_codes(page=1, per_page=10, order_by="id")))

            if cc:
                wcapi.codes.append(cc[0])
                with open('card_codes.json', 'w') as convert_file:
                    convert_file.write(json.dumps(wcapi.codes, indent=4))

            self.id = response["id"]
            self.insert_button.setDisabled(True)
            self.update_button.setDisabled(False)
            self.delete_button.setDisabled(False)
            self.image_path = ""
            # self.display_dialog(f"La carta '{self.item_name.text()}' ha sido ingresada correctamente al inventario.")
        except Exception as e:
            self.display_dialog(f"Ocurrio el siguiente error insertando la carta '{self.item_name.text()}' en el "
                                f"inventario: {str(e)}.")

    def slot_clear(self):
        self.clear_form()

    def reset_checkboxes(self):
        self.avanzado.setChecked(True)
        self.old_school.setChecked(False)
        self.high_end.setChecked(False)
        self.jcg.setChecked(False)
        self.gvq.setChecked(False)
        self.goat.setChecked(False)

    def slot_load(self):
        self.reset_checkboxes()
        self.id = ""
        message = ""
        image_url = ""
        code = self.card_code.text()
        condition = self.condition.currentText()
        edition = self.edition.currentText()
        rarity = self.rarity.currentText()
        language = self.languages_combo.currentText()
        info = [[], [], []]
        jcg = (True if self.jcg.checkState() == 2 else False)
        product_from_inventory = wcapi.get_product_by_filter(codigo=code, condition=condition, edition=edition,
                                                             rarity=rarity, language=language, jcg=jcg)

        # If card exists from inventory
        if product_from_inventory:
            self.selected_categories = [c["name"] for c in product_from_inventory["categories"]]
            self.selected_tags = [c["name"] for c in product_from_inventory["tags"]]

            self.set_checkboxes(self.selected_categories)
            self.set_checkboxes(self.selected_tags)

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
            self.last_update_label.setText(product_from_inventory["date_modified"])
            self.card_type.setCurrentText(product_from_inventory["attributes"][5]["options"][0])
            self.card_name.setText(
                nombre.split(" - ")[0].replace(product_from_inventory["attributes"][0]["options"][0], ""))
            self.item_name.setText(f"{code} {self.card_name.text()} - {edition} - {condition} - {rarity}")
            self.languages_combo.setCurrentText(product_from_inventory["attributes"][6]["options"][0])
        else:
            info = tyt.get_card_info(set_code=code, edition=edition,
                                     condition=condition.split(" ")[0], hide_oos=False,
                                     rarity=rarity)
            if info and info[0]:
                self.avanzado.setChecked(True)
                precio = tyt.get_rounded_price(info[0][0]["price"])
                image_url = info[0][0]["image"]
                nombre = info[0][0]["card_name"]
                self.stock.setText("1")
                self.insert_button.setDisabled(False)
                self.update_button.setDisabled(True)
                self.image_path = image_url
                self.card_type.setCurrentText("")
                self.card_name.setText(nombre)
                message = f"La carta '{self.item_name.text()}' no existe en el inventario pero si en T&T."
        if (info and info[0]) or product_from_inventory:
            if image_url:
                image = QImage()
                image.loadFromData(requests.get(image_url).content)
                self.image.setPixmap(QPixmap(image))
                self.image.show()
            else:
                self.image.clear()
            self.prize.setText(precio)
            if message:
                self.display_dialog(message)
                self.card_type.showPopup()
        else:
            self.avanzado.setChecked(False)
            self.stock.setText("1")
            # self.item_name.setText(f"{code}  - {edition} - {condition} - {rarity}")
            self.prize.setText("500")
            self.image.clear()
            #self.item_info = utils.get_card_info_from_set_code(code)
            self.item_info = None
            response = False
            if self.item_info and self.card_name.text() != self.item_info['name'] and \
                    self.rarity.currentText() != self.item_info['set_rarity']:
                response = self.display_option_dialog(
                    f"Al parecer la rareza deberia ser '{self.item_info['set_rarity']}' y "
                    f"el nombre de la carta '{self.item_info['name']}',  desea hacer la busqueda "
                    f"con estos parametros?")
            self.card_name.setText(self.item_info["name"]) if self.item_info else None
            if not response:
                self.slot_load_image_from_google()
                self.insert_button.setDisabled(False)
                self.update_button.setDisabled(True)
                self.delete_button.setDisabled(True)
                self.card_type.setCurrentText("")
                #self.display_dialog(f"La carta '{self.item_name.text()}' no existe en el inventario ni en T&T.")
                self.card_type.showPopup()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()

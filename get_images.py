import os
import requests

from helper.tyt_utils_old import TYTUtils
from helper.utils import Utils

utils = Utils()
tyt = TYTUtils(exchange_rate=585)


def get_images(set_code, edition, condition):
    keywords = ''
    language = 'English'
    website = 'TYT'
    hide_oos = False

    tyt_card_list = tyt.get_prices(set_code=set_code, edition=edition, condition=condition, language=language,
                                   hide_oos=hide_oos)
    card_list = tyt_card_list

    if card_list:
        card_image = card_list[0]['image']
        r = requests.get(card_image, allow_redirects=True)
        open(f'card_images/{set_code}-{edition}-{condition}.jpg', 'wb').write(r.content)
        return True
    else:
        return False


get_images("MAGO-EN006", " 1st Edition", "NM")

# Give the location of the file
loc = ("C:\YgoPriceApi\YugiPriceFinder\InventarioSegunda.xlsx")
from openpyxl import load_workbook

wb = load_workbook(loc)
ws = wb['Sheet1']
ws['A1'] = 'A1'

rows = int(ws.max_row)

for i in range(0, rows-1):
    n = ws[i + 2][2].value
    code = n.split( )[0]
    imagenes = ws[i + 2][5].value
    codigo = ws[i + 2][0].value
    edition =ws[i + 2][7].value
    condition = ws[i + 2][8].value
    item_found = False

    if code is not None:
        for file_name in os.listdir('C:\YgoPriceApi\YugiPriceFinder\card_images'):
            s = file_name
            a = file_name.split("-")
            code2 = f'{a[0]}-{a[1]}'
            expansion = code2.split("-")[0]
            edition2 = a[2]
            print(a)
            condition2 = a[3].replace(".jpg", "")

            if code == code2 and edition == edition2 and condition == condition2:
                item_found = True
                break

        if not item_found:
            if edition == None:
                edition = ""

            if condition == None:
                condition = ""

            a = get_images(set_code=code, edition=edition, condition=condition)
            if a:
               print(f"Imagen Descargada para el codigo {code}")
            else:
                print(f"Imagen NO fue descargada para el codigo {code}")

from time import sleep

from helper.tcgplayer_utils import TCGPlayerUtils
from helper.tyt_utils import TYTUtils
import sys

from helper.utils import Utils
from helper.wcapi_utils import WCAPIUtils

sys.stdout.flush()
wcapi = WCAPIUtils()
found_card_list = []
oos_card_list = []
not_found_card_list = []
utils = Utils()

# Get All the Products
products = wcapi.get_all_products()
# products = [wcapi.get_products_by_id(id=24457)]

tyt = TYTUtils()
tcgp = TCGPlayerUtils()

for product in products:
    try:
        if product['stock_status'] == 'outofstock':
            wcapi.delete_product(product['id'])
            wcapi.delete_image(product['images'][0]['id'])

            print(f"id {product[id]} was deleted")

    except Exception as e:
        print(f"Ocurrio un problema procesando el item: {product}")
        pass


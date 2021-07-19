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
#products = wcapi.get_all_products()
products = [wcapi.get_products_by_id(id=6646)]
tyt = TYTUtils()
tcgp = TCGPlayerUtils()

# a = tcgp.get_prices(set_code="DUOV-EN014", edition="1st Edition", condition="Near Mint")
# print(a)
# Get Card Lists

# products.sort(key=lambda x: x["date_created"], reverse=True)

for product in products:
    if product['stock_quantity'] and product['stock_quantity'] > 0:
        condition = product["attributes"][4]["options"][0].split(" ")[0]

        if condition in ("NM", "LP"):
            rounded_price = 0
            code = product["attributes"][0]["options"][0]
            edition = product["attributes"][1]["options"][0]
            rarity = product["attributes"][3]["options"][0]
            current_price = product["regular_price"]
            card_found, oos_card, not_found_card = tyt.get_card_info(set_code=code, edition=edition,
                                                                     condition=condition, hide_oos=False,
                                                                     rarity=rarity)
            if card_found:
                rounded_price = tyt.get_rounded_price(card_found[0]["price"])
                seller = card_found[0]["seller"]

                if current_price != rounded_price:
                    data = {
                        "regular_price": rounded_price
                    }
                    differencia = int(rounded_price) - int(current_price)
                    print(f"Se va a actualizar {code}, condicion: {condition}, edicion: {edition}, rareza: {rarity}, " \
                          f"precio_anterior: {current_price}, precio_nuevo: {rounded_price}, "
                          f"diferencia: {differencia}" +
                          (" ***NO T&T***" if seller != "TrollAndToad Com" else ""))

                    message = {"codigo": code, "condicion": condition, "edicion": edition, "rareza": rarity,
                               "precio_anterior": current_price, "precio_actualizado": rounded_price,
                               "diferencia": differencia,  "seller": seller}

                    found_card_list.append(message)
                    wcapi.update_product(product["id"], data)
                else:
                    print("Current price matches with T&T")
            elif oos_card:
                seller = oos_card[0]["seller"]

                rounded_price = tyt.get_rounded_price(oos_card[0]["price"])

                card = {"codigo": code, "condicion": oos_card[0]["condition"], "edicion": edition,
                        "rareza": oos_card[0]["rarity"], "precio_anterior": current_price, "precio_actualizado":
                            rounded_price, "diferencia": int(rounded_price) - int(current_price), "seller": seller}

                oos_card_list.append(card)
            elif not_found_card:
                card = {"codigo": code, "condicion": not_found_card[0].condition,
                        "edicion": not_found_card[0].edition,
                        "rareza": not_found_card[0].rarity, "precio_tienda": current_price}

                not_found_card_list.append(card)
            print(f"{len(not_found_card_list) + len(oos_card_list) + len(found_card_list)} cards processed")

# Send results by email
tyt.send_results(found_card_list, oos_card_list, not_found_card_list)

import requests
from woocommerce import API
from helper.tyt_utils import TYTUtils
from helper.utils import send_mail

wcapi = API(
    url="https://ygomarketcr.com",
    consumer_key="ck_b7254f31da371ea5c5c3641989e0591f0bb5ea0a",
    consumer_secret="cs_f0634c862d71b393735fc4d440841edaa2132cd0",
    version="wc/v3",
    timeout=60
)
print("nuevos cambios")
products = []
messages = []
i = 1
while True:
    items = wcapi.get("products", params={"per_page": 100, "page": i}).json()
    if items:
        products.extend(items)
        i += 1
    else:
        break

tipo_cambio = requests.get("https://tipodecambio.paginasweb.cr/api").json()
tyt = TYTUtils(exchange_rate=tipo_cambio["venta"])

for product in products:
    if product['stock_quantity'] and product['stock_quantity'] > 0:
        rounded_price = 0
        codigo = product["attributes"][0]["options"][0]
        edicion = product["attributes"][1]["options"][0]
        rareza = product["attributes"][3]["options"][0]

        try:
            condicion = product["attributes"][4]["options"][0].split("(")[1].replace(")", "")
        except:
            condicion = product["attributes"][4]["options"][0]

        if condicion in ("NM", "LP"):
            current_price = product["regular_price"]
            price = tyt.get_prices(set_code=codigo, edition=edicion, condition=condicion, language="English",
                                   hide_oos=True, rarity=rareza)

            if price:
                rounded_price = str(round(float(price[0]["price"].replace("$", "")) * tipo_cambio["venta"] / 500.0) * 500)
                rounded_price = ("500" if rounded_price == "0" else rounded_price)

            if rounded_price and current_price != rounded_price:
                data = {
                    "regular_price": rounded_price
                }
                message = f"Se va a actualizar {codigo}, condicion: {condicion}, edicion: {edicion}, rareza: {rareza}, " \
                          f"precio anterior: {current_price}, precio nuevo: {rounded_price}"
                print(message)
                messages.append(message)
                wcapi.put(f"products/{product['id']}", data).json()

message = ""
for m in messages:
    print(m)
    message += m + "\n"

if message:
    send_mail("ygomarketcr@gmail.com", "gvegaq86@gmail.com", "Actualizacion ygomarketcr", message)


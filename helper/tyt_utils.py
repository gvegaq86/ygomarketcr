from time import sleep
import requests
from bs4 import BeautifulSoup
from models.card_info import CardInfo
from helper.utils import Utils, send_mail

utils = Utils()


class TYTUtils:
    def __init__(self):
        self.time_out = 60
        self.exchange_rate = requests.get("https://tipodecambio.paginasweb.cr/api", timeout=self.time_out).json()
        self.colones_sign = 'CR'
        self.aa = 1

    def get_html_card_info(self, card_key, edition, condition, rarity=None, hide_oos=False, counter=0):
        try:
            base_url = 'https://www.trollandtoad.com'

            search_words = f'{card_key}+{edition.replace(" ", "+")}+{rarity.replace(" ", "+")}'.replace("++", "+")

            if condition == 'HP' or condition == 'MP' or condition == 'D' or condition == 'LP':
                c = 'PL'
            else:
                c = condition

            url = f'{base_url}/category.php?' \
                  f'min-price=&' \
                  f'max-price=&' \
                  f'items-pp=240&' \
                  f'search-words={search_words}&' \
                  f'selected-cat=4736&' \
                  f'sort-order=L-H&' \
                  f'page-no=1&' \
                  f'view=list&' \
                  f'subproduct=0'

            if hide_oos:
                url += '&hide-oos=on'
            try:
                try:
                    html = requests.get(url=url, timeout=self.time_out).text
                except:
                    sleep(60)
                    html = requests.get(url=url, timeout=self.time_out).text
            except:
                sleep(60)
                html = requests.get(url=url, timeout=self.time_out).text

            parsed_html = BeautifulSoup(html, 'html.parser')
            if 'Sorry, you have exceeded your' in parsed_html.text:
                cards = "exceeded"
            else:
                cards = parsed_html.find_all("div", class_="card h-100 p-3")

            # print(f'T&T - cards: {cards}')
            if cards:
                return cards
            elif counter == 0:
                return self.get_html_card_info(card_key=card_key, edition="", condition=condition, rarity=rarity,
                                               hide_oos=hide_oos, counter=1)
            else:
                return []

        except Exception as e:
            print(f'TYT - Occurred the following error trying to get card infoxx: {e}')
            raise Exception(e)

    def get_rounded_price(self, price):
        price = round(float((price).replace("$", "")) * self.exchange_rate["venta"])

        if price <= 250:
            price = 300
        elif 300 <= price <= 650:
            price = 500
        elif 650 < price <= 750:
            price = 750
        else:
            price = round(price / 500) * 500

        return str(price)

    def get_ref_link(self, codigo):
        tcgp_link = ""
        card_info = utils.get_card_info_from_set_code(codigo)
        if card_info:
            rarity = card_info["set_rarity"]
            rarity = rarity.replace(" ", "%20") if rarity != "Common" else "Common%20%2F%20Short%20Print"
            tcgp_link = f'https://www.tcgplayer.com/search/yugioh/product?Language=English&q={card_info["name"].replace(" ", "%20")}&productLineName=yugioh&view=grid&page=1&RarityName={rarity}'
        return tcgp_link

    def send_results(self, found_card_list, oos_card_list, not_found_card_list):
        found_card_results = ""
        oos_card_results = ""
        not_found_card_results = ""
        full_results_message = ""

        found_card_list.sort(key=lambda x: abs(x.get("diferencia")), reverse=True)
        oos_card_list.sort(key=lambda x: abs(x.get("diferencia")), reverse=True)

        if found_card_list:
            for m in found_card_list:
                a = f"Se actualizó {m['codigo']}, {m['condicion']}, {m['edicion']}, {m['rareza']}, " \
                    f"precio anterior: {m['precio_anterior']}, precio actualizado: {m['precio_actualizado']}," \
                    f" diferencia: {m['diferencia']}" + \
                    (" ***NO T&T***" if m["seller"] != "TrollAndToad Com" else "")
                print(a)
                found_card_results += a + "\n"

        else:
            print("No cards to update")

        a = ""
        for m in oos_card_list:
            # tcgp_link = self.get_ref_link(m['codigo'])
            tcgp_link = None

            a = f"{m['codigo']}, {m['condicion']}, {m['edicion']}, {m['rareza']}, " \
                f"precio de la pagina: {m['precio_anterior']}, precio T&T OOS: {m['precio_actualizado']}," \
                f" diferencia: {m['diferencia']}" + (f"\n tcgp: {tcgp_link}" if tcgp_link else "")
            print(a)
            oos_card_results += a + "\n"

        a = ""
        for m in not_found_card_list:
            # tcgp_link = self.get_ref_link(m['codigo'])
            tcgp_link = None

            a = f"{m['codigo']}, {m['condicion']}, {m['edicion']}, {m['rareza']}, " \
                f"precio_tienda: {m['precio_tienda']}" + (f"\n tcgp: {tcgp_link}" if tcgp_link else "")
            print(a)
            not_found_card_results += a + "\n"

        if found_card_results:
            full_results_message += f"Precios actualizados (Encontrados en T&T y con stock:) ({len(found_card_list)} cartas)" + "\n"
            full_results_message += found_card_results + "\n" + "\n"

        if oos_card_results:
            full_results_message += f"Cartas pendientes de actualizar manualmente (Sin stock en T&T) ({len(oos_card_list)} cartas)" + "\n"
            full_results_message += oos_card_results + "\n" + "\n"

        if not_found_card_results:
            full_results_message += f"Cartas pendientes de actualizar manualmente (No se encuentra en T&T del todo) ({len(not_found_card_list)} cartas)" + "\n"
            full_results_message += not_found_card_results + "\n" + "\n"

        if full_results_message:
            print("Emailing results...")
            # send_mail("ygomarketcr@gmail.com", ["gvegaq86@gmail.com"],
            send_mail("gvegaq86@gmail.com", ["gvegaq86@gmail.com", "juangamboa16201@gmail.com"],
                      "Resumen de Precios a actualizar - YgoMarketCR", full_results_message)

    def get_card_info(self, set_code, edition, condition, language="English", rarity=None, hide_oos=False):
        try:
            print(f'T&T - Getting prices from set code: {set_code}')
            # Get card info
            if "LCJW" in set_code:
                edition = "Unlimited"

            cards = self.get_html_card_info(card_key=set_code, edition=edition, condition=condition, rarity=rarity,
                                            hide_oos=hide_oos)
            seller = ""
            card_list = []
            oos_card_list = []
            not_found_card_list = []
            card_image = ""

            if len(cards) > 0 and 'exceeded' not in str(cards):
                for card in cards:
                    card_text = card.find("a", "card-text").text
                    card_image = card.find_all("img")[0]['data-src']
                    if set_code in card.text:
                        items = card.find_all("div", "row position-relative align-center py-2 m-auto")
                        for item in items:
                            e = item.contents[1].text

                            if "PROMO" in card_text:
                                displayed_edition = "Limited Edition"
                            elif "LCJW" in card_text:
                                displayed_edition = "Unlimited"
                            elif "Limited Edition" in card_text:
                                displayed_edition = "Limited Edition"
                            elif "1st Edition" in card_text or "1st Edition" in e:
                                displayed_edition = "1st Edition"
                            elif "Unlimited" in card_text or "Unlimited" in e:
                                displayed_edition = "Unlimited"
                            else:
                                displayed_edition = "Limited Edition"

                            card_name = card_text.split(" - ")[0]
                            if "Near Mint" in item.text:
                                displayed_condition = "NM"
                            else:
                                displayed_condition = "LP"

                            displayed_rarity = \
                                card_text.replace(displayed_edition, "").replace("Limited", "").replace("1st Ed", "").\
                            replace("1st", "").replace(set_code, "").split(" - ")[-1]. \
                                    replace("-", "").strip().replace("(Sealed)", "").strip().title()

                            if not displayed_rarity:
                                displayed_rarity = utils.get_rarity(card_text)

                            quantity = int(item.contents[2].text)
                            displayed_code = card_text.replace(rarity, "").replace(edition, "").replace("- ", "")

                            p = float(item.contents[3].next.replace("$", "").replace(",", ""))
                            seller = item.contents[0].contents[0].attrs["title"]
                            seller_image = item.contents[0].contents[0].attrs["src"].split("/")[-1]
                            card1 = CardInfo(card_name=card_name, card_key=displayed_code,
                                             condition=displayed_condition,
                                             price=p, pricec="0", edition=displayed_edition, rarity=rarity, quantity=1,
                                             expansion="", image=card_image, web_site='T&T', seller=seller)

                            if displayed_edition in (
                                    ["Limited Edition", "Unlimited"] if edition in ["Limited Edition",
                                                                                    "Unlimited"] else edition) and \
                                    displayed_rarity == rarity and set_code in displayed_code:
                                if quantity > 0:
                                    card_list.append(card1.get_dict_card_info())
                                else:
                                    oos_card_list.append(card1.get_dict_card_info())

            elif 'exceeded' in str(cards):
                if 'exceeded' in str(cards) and self.aa == 1:
                    print("Waiting 180 seconds")
                    sleep(180)
                    self.aa = 2
                    card_list, oos_card_list, not_found_card_list = self.get_card_info(set_code=set_code,
                                                                                       edition=edition,
                                                                                       condition=condition,
                                                                                       language=language, rarity=rarity)

                elif self.aa == 1:
                    self.aa = 0
                    card_list, oos_card_list, not_found_card_list = self.get_card_info(set_code=set_code, edition="",
                                                                                       condition="", language=language,
                                                                                       rarity=rarity)

                self.aa = 1

            if not card_list and not oos_card_list:
                card1 = CardInfo(card_name="", card_key=set_code, condition=condition, price=0, pricec="0",
                                 edition=edition, rarity=rarity, quantity=0, expansion="", image=card_image, web_site='T&T',
                                 seller=seller)
                not_found_card_list.append(card1)

            # If there are results
            if len(card_list) > 1:
                # If there are more than 2 conditions of the same item and the condition card is LP
                conditions = []
                [conditions.append(x["condition"]) if x["condition"] not in conditions else None for x in card_list]
                if condition == "LP" and len(conditions) > 1:
                    # sorted(card_list, key=lambda x: float(x["price"].replace("$", " ")))
                    lp_lowest_price_item = sorted(list(filter(lambda x: x["condition"] == condition, card_list)), key=lambda x:float(x["price"].replace("$", "")))[0]
                    nm_lowest_price_item = sorted(list(filter(lambda x: x["condition"] == "NM", card_list)), key=lambda x:float(x["price"].replace("$", "")))[0]

                    if float(lp_lowest_price_item["price"].replace("$", "")) >= \
                            float(nm_lowest_price_item["price"].replace("$", "")):
                        card_list = [nm_lowest_price_item]
                    else:
                        card_list = [lp_lowest_price_item]
                else:
                    card_list = sorted(list(filter(lambda x: x["condition"] == condition, card_list)),
                                       key=lambda x:float(x["price"].replace("$", "")))
            else:
                card_list = sorted(list(filter(lambda x: x["condition"] == condition, card_list)),
                                   key=lambda x: float(x["price"].replace("$", "")))

            return card_list, oos_card_list, not_found_card_list
        except Exception as e:
            print(f'TYT - Occurred the following error trying to get prices: {e}')
            # raise Exception(e)
            return []

from time import sleep

import requests
from bs4 import BeautifulSoup
from models.card_info import CardInfo
from helper.utils import Utils

utils = Utils()


class TYTUtils:
    def __init__(self, exchange_rate):
        self.exchange_rate = exchange_rate
        self.colones_sign = 'CR'
        self.aa=1

    def get_card_info(self, card_key, edition, condition, rarity=None, hide_oos=False):
        try:
            print(f'T&T - Get card Info: {card_key}')
            base_url = 'https://www.trollandtoad.com'

            search_words = f'{card_key}+{edition.replace(" ", "+")}+{rarity.replace(" ","+")}'

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

            html = requests.get(url=url).text
            parsed_html = BeautifulSoup(html, 'html.parser')
            if 'Sorry, you have exceeded your' in parsed_html.text:
               cards = "exceeded"
            else:
                cards = parsed_html.find_all("div", class_="card h-100 p-3")

            #print(f'T&T - cards: {cards}')
            return cards

        except Exception as e:
            print(f'TYT - Occurred the following error trying to get card info: {e}')
            raise Exception(e)

    def get_prices(self, set_code, edition, condition, language, rarity=None, hide_oos=False):
        try:
            print(f'T&T - Getting prices from set code: {set_code}')
            # Get card info
            cards = self.get_card_info(card_key=set_code, edition=edition, condition=condition, rarity=rarity,
                                       hide_oos=hide_oos)
            card_list = []

            if len(cards) > 0 and 'exceeded' not in str(cards):
                for card in cards:
                    card_text = card.find("a", "card-text").text
                    if set_code in card.text:
                        items = card.find_all("div", "row position-relative align-center py-2 m-auto")
                        for item in items:
                            e = item.contents[1].text

                            if "1st Edition" in e:
                                displayed_edition = "1st Edition"
                            elif "Unlimited" in e:
                                displayed_edition = "Unlimited"
                            else:
                                displayed_edition = "Limited Edition"

                            card_name = card_text.split(" - ")[0]
                            if "Near Mint" in item.text:
                                displayed_condition = "NM"
                            else:
                                displayed_condition = "LP"

                            displayed_rarity = card_text.replace(displayed_edition, "").replace(set_code, "").split(" - ")[-1].strip()

                            p = float(item.contents[3].next.replace("$", ""))
                            seller = item.contents[0].contents[0].attrs["title"]
                            card1 = CardInfo(card_name=card_name, card_key=set_code, condition=displayed_condition,
                                             price=p, pricec="0", edition=displayed_edition, rarity=rarity, quantity=1,
                                             expansion="", image="", web_site='T&T')
                            if seller == "TrollAndToad Com" and condition == displayed_condition and \
                                    displayed_edition == edition and displayed_rarity == rarity:
                                card_list.append(card1.get_dict_card_info())
                                break
            else:
                # print(f'La carta "{set_code}" {edition} {condition} "NO" tiene stock en T&T!')

                if 'exceeded' in str(cards) and self.aa == 1:
                    print("Waiting 180 seconds")
                    sleep(180)
                    self.aa = 2
                    card_list = self.get_prices(set_code=set_code, edition=edition, condition=condition, language=language, rarity=rarity)

                elif self.aa == 1:
                    self.aa = 0
                    card_list = self.get_prices(set_code=set_code, edition="", condition="", language=language, rarity=rarity)

                self.aa = 1

            print(f'Card list: {card_list}')
            return card_list
        except Exception as e:
            print(f'TYT - Occurred the following error trying to get prices: {e}')
            # raise Exception(e)
            return []
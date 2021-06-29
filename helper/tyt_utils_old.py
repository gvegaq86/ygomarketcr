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

            if edition == 'Unlimited':
                search_words = card_key
            else:
                search_words = f'{card_key}+{edition.replace(" ", "+")}'

            if condition == 'HP' or condition == 'MP' or condition == 'D':
                c = 'P'
            else:
                c = condition

            url = f'{base_url}/category.php?' \
                  f'min-price=&' \
                  f'max-price=&' \
                  f'items-pp=240&' \
                  f'item-condition={c}&' \
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

            print(f'T&T - cards: {cards}')
            return cards

        except Exception as e:
            print(f'TYT - Occurred the following error trying to get card info: {e}')
            raise Exception(e)

    def get_prices(self, set_code, edition, condition, language, rarity=None, hide_oos=False):
        try:
            print(f'T&T - Getting prices from set code: {set_code}')
            # Get card info
            cards = self.get_card_info(card_key=set_code, edition=edition, condition=condition, rarity=rarity, hide_oos=hide_oos)
            card_list = []

            if len(cards) > 0 and 'exceeded' not in str(cards):
                for card in cards:
                    card_info = card.find_all("a", class_="card-text")[0].text

                    if set_code not in str(card_info.upper()):
                        continue

                    card_info = card_info.replace(set_code, "")

                    if language == 'English' and 'Asian' in card_info or 'Spanish' in card_info:
                        continue
                    elif edition == '1st Edition' and 'Unlimited' in card_info:
                        continue
                    elif edition == 'Unlimited' and '1st' in card_info:
                        continue

                    edition_ = utils.get_edition(text=card_info)
                    card_info = card_info.replace(edition_, "").replace(set_code, "")

                    rarity = ""
                    for a in card_info.split("-"):
                        if "rare" in a.lower() or "common" in a.lower():
                            rarity = a.strip()

                    card_name = card_info.replace(rarity, "").replace('-', '').strip()

                    items = card.find_all("div", class_="row position-relative align-center py-2 m-auto")

                    expansion = card.find_all("a")[2].text.replace(set_code, '') \
                        .replace(edition_, '').replace('Singles', '').replace('-', '') \
                        .replace(f'[{set_code.split("-")[0]}]', '').strip()

                    image = card.find_all("img")[0].attrs['data-src']
                    for item in items:
                        c = utils.get_condition(item.find_all("div", class_="col-3 text-center p-1")[1].text)
                        if c == 'See Image For Condition':
                            c += f': https://www.trollandtoad.com{item.find_all("div", class_="col-3 text-center p-1")[1].find_all("a")[0].attrs["href"]}'
                        p = float(
                            item.find_all("div", class_="col-2 text-center p-1")[0].text.replace('$', '').replace(',', ''))
                        pc = f'{self.colones_sign}{format(float(p) * self.exchange_rate, ",.0f")}'
                        seller = item.find_all("div", class_="col-3 text-center p-1")[0].next_element.attrs["title"]


                        quantity = int(item.find_all("option")[len(item.find_all("option")) - 1].attrs['value'])
                        card1 = CardInfo(card_name=card_name, card_key=set_code, condition=c,
                                         price=p, pricec=pc, edition=edition_, rarity=rarity, quantity=quantity,
                                         expansion=expansion, image=image, web_site='T&T')
                        if seller == "TrollAndToad Com":
                            card_list.append(card1.get_dict_card_info())
                        break
            else:
                # print(f'La carta "{set_code}" {edition} {condition} "NO" tiene stock en T&T!')

                if 'exceeded' in str(cards) and self.aa == 1:
                    print("Waiting 180 seconds")
                    sleep(180)
                    self.aa = 2
                    card_list = self.get_prices(set_code=set_code, edition=edition, condition=condition, language=language)

                elif self.aa == 1:
                    self.aa = 0
                    card_list = self.get_prices(set_code=set_code, edition="", condition="", language=language)

                self.aa = 1

            print(f'Card list: {card_list}')
            return card_list
        except Exception as e:
            print(f'TYT - Occurred the following error trying to get prices: {e}')
            # raise Exception(e)
            return []
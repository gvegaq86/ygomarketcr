import json
import math

import requests
from models.card_info import CardInfo
from helper.utils import Utils

utils = Utils()


class TCGPlayerUtils:
    def __init__(self, exchange_rate):
        self.exchange_rate = exchange_rate
        self.colones_sign = 'CR'

    def get_items(self, set_code, card_name, edition="", condition="", image="", expansion="", rarity="",product_id=""):
        try:
            print(f'Getting items from set code: {set_code}')
            card_list = []

            url2 = f"https://shop.tcgplayer.com/productcatalog/product/changepricetablepagesize?" \
                   f"pageSize=50&" \
                   f"productId={product_id}&" \
                   f"gameName=yugioh&" \
                   f"useV2Listings=true"

            url2 += f"&filterName=Condition&" \
                    f"filterValue={condition.replace(' ', '')}"

            parsed_html = utils.get_parsed_html(url2)
            total_items = int(parsed_html.find_all("span", "sort-toolbar__total-item-count")[0].text.split(" ")[-2])

            for page in range(5, math.ceil(total_items / 10) + 1):
                if page > 5:
                    url = f"https://shop.tcgplayer.com/productcatalog/product/changepricetablepage?" \
                          f"productId={product_id}" \
                          f"&gameName=yugioh" \
                          f"&useV2Listings=true" \
                          f"&page={page}"

                    url += f"&filterName=Condition&" \
                           f"filterValue={condition.replace(' ', '')}"

                    parsed_html = utils.get_parsed_html(url)

                items = parsed_html.find_all("div", class_="product-listing")
                for item in items:
                    aa = item.find_all("a", "product-listing__photo-title")
                    if aa:
                        cn = aa[0].text.upper()
                        if 'SPANISH' in cn or 'ASIAN' in cn:
                            continue

                    edition_ = utils.get_edition(item.find_all('a', class_='condition')[0].text)
                    condition_ = utils.get_condition(item.find_all('a', class_='condition')[0].text)
                    price = float(item.find_all('span', class_='product-listing__price')[0].text
                                  .replace('$', '').replace(',', ''))
                    pc = f'{self.colones_sign}{format(float(price) * self.exchange_rate, ",.0f")}'
                    quantity = len(item.find_all('select', id='quantityToBuy')[0].find_all('option'))

                    card1 = CardInfo(card_name=card_name, card_key=set_code, condition=condition_,
                                     price=price, pricec=pc, edition=edition_, rarity=rarity, quantity=quantity,
                                     expansion=expansion, image=image, web_site='TCGPlayer')

                    if edition:
                        if edition != edition_:
                            continue

                    if condition:
                        if condition != condition_:
                            continue

                    card_list.append(card1.get_dict_card_info())

            print(f'Card list: {card_list}')
            return card_list
        except Exception as e:
            print(f'TCGPlayer - Occurred the following error trying to get items: {e}')
            return []

    def get_card_info_from_set_code(self, set_code):
        try:
            print(f'Getting card info from set code: {set_code}')
            url = f'https://db.ygoprodeck.com/api/v6/cardsetsinfo.php?setcode={set_code}'
            results = requests.get(url=url)
            card_info = json.loads(results.content)

            if 'error' in str(card_info):
                card_info = None

            print(f'Card info: {card_info}')
            return card_info
        except Exception as e:
            print(f'TCGP - Occurred the following error trying to get card info from set code: {e}')
            raise Exception(e)

    def get_card_info_from_card_name(self, card_name, set_code):
        try:
            print(f'Getting card info from card name {card_name}')
            # Get TCGPlayer card info

            product_id = ""
            rarity = ""
            expansion = ""
            image = ""

            url = f'https://mpapi.tcgplayer.com/v2/search/request?q={card_name.replace(" ", "%20")}&isList=false'
            image_url_base = "https://6d4be195623157e28848-7697ece4918e0a73861de0eb37d08968.ssl.cf1.rackcdn.com/"

            body = {"algorithm": "", "from": 0, "size": 200,
                    "filters": {"term": {"productLineName": ["yugioh"], "productTypeName": ["Cards"]}, "range": {}},
                    "listingSearch": {"filters": {"term": {}, "range": {}, "exclude": {"channelExclusion": 0}}},
                    "context": {"cart": {}, "shippingCountry": "US"}, "sort": {}}

            headers = {'Content-Type': 'application/json'}

            results = requests.post(url=url, json=body, headers=headers)
            results = json.loads(results.content)

            cards = results['results'][0]['results']

            for card in cards:
                if card['customAttributes']['number'] == set_code:
                    product_id = int(card['productId'])
                    image = image_url_base + f'{product_id}_200w.jpg'
                    rarity = card['rarityName'].replace(' / Short Print', '')
                    expansion = card['setName']
                    print(
                        f'get_card_info_from_card_name, product_id={product_id}, rarity={rarity}, expansion={expansion},'
                        f'image={image}')
                    break

            return product_id, rarity, expansion, image
        except Exception as e:
            print(f'TCGP - Occurred the following error trying to get card from card name: {e}')
            raise Exception(e)

    def get_card_info_from_card_name_selenium(self, card_name):
        print(f'Getting card info from card name {card_name}')
        # Get TCGPlayer card info
        url = f'https://www.tcgplayer.com/search/all/product?' \
              f'productLineName=yugioh&' \
              f'productTypeName=Cards&' \
              f'page=1&' \
              f'q={card_name.replace(" ", "%20")}'

        print(f'get_card_info_from_card_name, url: {url}')
        parsed_html = utils.get_parsed_html(url=url, use_selenium=True)
        cards = parsed_html.find_all("div", class_="search-result")
        print(f'Cards: {cards}')
        return cards

    def get_prices(self, set_code, edition="", condition=""):
        try:
            print('Getting prices from TCGPlayer')
            card_list = []

            condition = utils.convert_condition(condition=condition)

            # Get card info from set code
            card_info = self.get_card_info_from_set_code(set_code=set_code)

            if card_info:
                card_name = card_info['name']

                # Get card info from card name
                product_id, rarity, expansion, image = self.get_card_info_from_card_name(card_name=card_name,
                                                                                         set_code=set_code)

                if product_id:
                    # Get card list
                    card_list = self.get_items(set_code=set_code, card_name=card_name,
                                               edition=edition, condition=condition,
                                               product_id=product_id, rarity=rarity, expansion=expansion, image=image)
                else:
                    print(f'La carta "{set_code}" {edition} {condition} "NO" tiene stock en TCGPlayer!')
            print(f'Card list: {card_list}')
            return card_list
        except Exception as e:
            print(f'TCGPlayer - Occurred the following error trying to get prices: {e}')
            raise Exception(e)

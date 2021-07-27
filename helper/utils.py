import json

import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import yagmail
from models.card_sets import CardSets
from models.set import Set
from difflib import SequenceMatcher


class Utils:
    time_out = 60
    def get_image_from_google(self, text):
        try:
            api_key = "AIzaSyAz_k0dKF3ckMbweP8EWFKZm4Sydl6qAbw"
            response = requests.get(f"https://customsearch.googleapis.com/customsearch/v1?cx=16d525520d0929aea&"
                                    f"searchType=image&num=10&imgSize=LARGE&imgType=photo&q={'YUGI ' + text}&key={api_key}",
                                    timeout=20)
            response = response.json()
            card_code = text.split(" - ")[0].split(" ")[0]
            condition = text.split(" - ")[-2]

            items = list(filter(lambda x: (card_code in x["title"] or card_code.replace("-", " ")
                                           in x["title"]) and condition in x["title"],
                                response["items"]))

            if not items and condition == "Unlimited":
                items = list(filter(lambda x: (card_code in x["title"] or card_code.replace("-", " ")
                                           in x["title"]) and
                                              not any(word in x["title"].upper() for word in ['1ST EDITION',
                                                                                              'LIMITED EDITION']),
                                    response["items"]))
            else:
                items = list(filter(lambda x: (card_code in x["title"] or card_code.replace("-", " ")
                                           in x["title"]), response["items"]))
            return items
        except:
            return ""

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def get_condition(self, text):
        text = text.upper()
        condition = ''

        if 'DAMAGED' in text:
            condition = 'Damaged'
        elif 'HEAVILY' in text:
            condition = 'Heavily Played'
        elif 'LIGHTLY' in text:
            condition = 'Lightly Played'
        elif 'MODERATELY' in text:
            condition = 'Moderately Played'
        elif 'NEAR' in text:
            condition = 'Near Mint'
        elif 'PLAYED' in text:
            condition = 'Played'
        elif 'SEE IMAGE FOR CONDITION' in text:
            condition = 'See Image For Condition'

        return condition

    def convert_condition(self, condition):
        condition = condition.upper()
        if condition == 'NM':
            condition = 'Near Mint'
        elif condition == 'LP':
            condition = 'Lightly Played'
        elif condition == 'MP':
            condition = 'Moderately Played'
        elif condition == 'PL':
            condition = 'Played'
        elif condition == 'HP':
            condition = 'Heavily Played'
        elif condition == 'D':
            condition = 'Damaged'

        return condition

    def get_condition(self, condition):
        condition = condition.upper()
        if condition == 'NM':
            condition = 'NM (Near Mint)'
        elif condition == 'LP':
            condition = 'LP (Lightly Played)'
        elif condition == 'MP':
            condition = 'MP (Moderately Played)'
        elif condition == 'PL':
            condition = 'PL (Played)'
        elif condition == 'HP':
            condition = 'HP (Heavily Played)'
        elif condition == 'D':
            condition = 'D (Damaged)'

        return condition

    def get_card_info_from_set_code(self, set_code):
        try:
            print(f'Getting card info from set code: {set_code}')
            url = f'https://db.ygoprodeck.com/api/v7/cardsetsinfo.php?setcode={set_code}'
            results = requests.get(url=url, timeout=self.time_out)
            card_info = json.loads(results.content)

            if 'error' in str(card_info):
                card_info = None

            print(f'Card info: {card_info}')
            return card_info
        except Exception as e:
            print(f'TCGP - Occurred the following error trying to get card info from set code: {e}')
            raise Exception(e)

    def get_edition(self, text):
        text = text.upper()
        edition = ''

        if '1ST' in text:
            edition = '1st Edition'
        elif 'UNLIMITED' in text:
            edition = 'Unlimited'
        elif 'LIMITED' in text:
            edition = 'Limited Edition'
        else:
            edition = 'Unlimited'

        return edition

    def create_web_driver(self, headless=True):
        print('Creating web driver')
        chrome_options = Options()

        if headless:
            chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)
        print('Webdriver was created correctly')
        return driver

    def get_parsed_html(self, url, use_selenium=False):
        if use_selenium:
            driver = self.create_web_driver()
            driver.get(url)
            html = driver.page_source
            parsed_html = BeautifulSoup(html, 'html.parser')
            driver.close()
        else:
            session = HTMLSession()
            html = session.get(url).content
            parsed_html = BeautifulSoup(html, 'html.parser')

        return parsed_html

    def filter_list(self, card_list):
        new_card_list = []
        fe = None
        ue = None
        le = None
        for card in card_list:
            if card['edition'] == '1st Edition':
                if not fe:
                    fe = card
                elif fe['price'] > card['price']:
                    fe = card
            elif card['edition'] == 'Unlimited':
                if not ue:
                    ue = card
                elif ue['price'] > card['price']:
                    ue = card
            elif card['edition'] == 'Limited Edition':
                if not le:
                    le = card
                elif le['price'] > card['price']:
                    le = card

        if fe:
            new_card_list.append(fe)
        if ue:
            new_card_list.append(ue)
        if le:
            new_card_list.append(le)

        if new_card_list:
            new_card_list = sorted(new_card_list, key=lambda k: (float(k['price'].replace('$', '').replace(',', ''))))

        return new_card_list

    def get_prices_by_condition(self, card_list):
        damaged_list = []
        heavily_list = []
        lightly_list = []
        played_list = []
        moderately_list = []
        mint_list = []
        unknown_list = []
        for card in card_list:
            if card['condition'] == 'Damaged':
                damaged_list.append(card)
            if card['condition'] == 'Heavily Played':
                heavily_list.append(card)
            if card['condition'] == 'Moderately Played':
                moderately_list.append(card)
            if card['condition'] == 'Lightly Played':
                lightly_list.append(card)
            if card['condition'] == 'Played':
                played_list.append(card)
            if card['condition'] == 'Near Mint':
                mint_list.append(card)
            if 'See Image For Condition' in card['condition']:
                unknown_list.append(card)

        damaged_list = self.filter_list(card_list=damaged_list)
        heavily_list = self.filter_list(card_list=heavily_list)
        moderately_list = self.filter_list(card_list=moderately_list)
        lightly_list = self.filter_list(card_list=lightly_list)
        played_list = self.filter_list(card_list=played_list)
        mint_list = self.filter_list(card_list=mint_list)
        unknown_list = self.filter_list(card_list=unknown_list)

        return {
            'Damaged': damaged_list,
            'HeavilyPlayed': heavily_list,
            'ModeratelyPlayed': moderately_list,
            'LightlyPlayed': lightly_list,
            'Played': played_list,
            'NearMint': mint_list,
            'SeeImageForCondition': unknown_list
        }

    def get_prices_by_condition2(self, card_list):
        damaged_list = []
        heavily_list = []
        lightly_list = []
        played_list = []
        moderately_list = []
        mint_list = []
        unknown_list = []
        for card in card_list:
            if card['condition'] == 'Damaged':
                damaged_list.append(card)
            if card['condition'] == 'Heavily Played':
                heavily_list.append(card)
            if card['condition'] == 'Moderately Played':
                moderately_list.append(card)
            if card['condition'] == 'Lightly Played':
                lightly_list.append(card)
            if card['condition'] == 'Played':
                played_list.append(card)
            if card['condition'] == 'Near Mint':
                mint_list.append(card)
            if 'See Image For Condition' in card['condition']:
                unknown_list.append(card)

        damaged_list = self.filter_list(card_list=damaged_list)
        heavily_list = self.filter_list(card_list=heavily_list)
        moderately_list = self.filter_list(card_list=moderately_list)
        lightly_list = self.filter_list(card_list=lightly_list)
        played_list = self.filter_list(card_list=played_list)
        mint_list = self.filter_list(card_list=mint_list)
        unknown_list = self.filter_list(card_list=unknown_list)

        return damaged_list + heavily_list + moderately_list + lightly_list + played_list + mint_list + unknown_list

    def get_prices_by_edition(self, card_list):
        first_edition_list = []
        unlimited_list = []
        limited_list = []

        count = 0
        card_key = ""
        card_name = ""
        expansion = ""
        image = ""

        for card in card_list:
            if count == 0:
                card_key = card['card_key']
                card_name = card['card_name']
                expansion = card['expansion']
                image = card['image']

            if card['edition'] == '1st Edition':
                first_edition_list.append(card)
            if card['edition'] == 'Unlimited':
                unlimited_list.append(card)
            if card['edition'] == 'Limited Edition':
                limited_list.append(card)
            count += 1

        card_list = self.get_prices_by_condition2(first_edition_list) + self.get_prices_by_condition2 \
            (unlimited_list) + self.get_prices_by_condition2(limited_list)

        return {
            "card_key": card_key,
            "card_name": card_name,
            "expansion": expansion,
            "image": image,
            "card_list": card_list
        }

    def filter_card_list(self, card_list):
        filtered_card_list = []

        card_key = ""
        card_name = ""
        expansion = ""
        image = ""

        for card in card_list:

            if len(filtered_card_list) == 0:
                filtered_card_list.append(card)
                card_key = card['card_key']
                card_name = card['card_name']
                expansion = card['expansion']
                image = card['image']
            else:
                item_founded = False
                for card2 in filtered_card_list:
                    if card['card_key'] == card2['card_key'] and card['edition'] == card2['edition'] and \
                            card['condition'] == card2['condition'] and card['rarity'] == card2['rarity']:
                        item_founded = True
                        if (card['quantity'] > 0 and float(card['price'].replace('$', '')) <
                                float(card2['price'].replace('$', '')) or
                                (card2['quantity'] == 0 and card['quantity'] > 0)):
                            filtered_card_list.remove(card2)
                            filtered_card_list.append(card)
                            break

                if not item_founded:
                    filtered_card_list.append(card)
                    item_founded = True

        if len(filtered_card_list) > 1:
            filtered_card_list = sorted(filtered_card_list,
                                        key=lambda k: (float(k['price'].replace('$', '').replace(',', ''))))

        return {
            "card_key": card_key,
            "card_name": card_name,
            "expansion": expansion,
            "image": image,
            "card_list": filtered_card_list
        }

    def get_best_prices(self, card_list):
        damaged_list = []
        heavily_list = []
        lightly_list = []
        played_list = []
        moderately_list = []
        mint_list = []
        unknown_list = []
        for card in card_list:
            if card['condition'] == 'Damaged':
                damaged_list.append(card)
            if card['condition'] == 'Heavily Played':
                heavily_list.append(card)
            if card['condition'] == 'Moderately Played':
                moderately_list.append(card)
            if card['condition'] == 'Lightly Played':
                lightly_list.append(card)
            if card['condition'] == 'Played':
                played_list.append(card)
            if card['condition'] == 'Near Mint':
                mint_list.append(card)
            if 'See Image For Condition' in card['condition']:
                unknown_list.append(card)

        damaged_list = self.filter_list(card_list=damaged_list)
        heavily_list = self.filter_list(card_list=heavily_list)
        moderately_list = self.filter_list(card_list=moderately_list)
        lightly_list = self.filter_list(card_list=lightly_list)
        played_list = self.filter_list(card_list=played_list)
        mint_list = self.filter_list(card_list=mint_list)
        unknown_list = self.filter_list(card_list=unknown_list)

        return damaged_list + heavily_list + moderately_list + lightly_list + played_list + mint_list + unknown_list

    def get_exchange_rate(self):
        url = 'https://tipodecambio.paginasweb.cr/api'
        results = requests.get(url=url, timeout=self.time_out)
        exchange_rate = float(json.loads(results.content)['venta'])

        return exchange_rate

    def get_card_info_from_name(self, name):
        try:
            print(f'Getting card info from name: {name}')
            name = name.replace(' ', '%20')
            url = f'https://db.ygoprodeck.com/api/v6/cardinfo.php?fname={name}'
            results = requests.get(url=url, timeout=self.time_out)
            card_info = json.loads(results.content)

            card_sets = []

            if not 'No card matching your query was found in the database' in str(card_info):
                for card_set in card_info:
                    sets = []
                    if 'card_sets' in str(card_set):
                        cs = card_set['card_sets']
                        for s in cs:
                            if len(sets) == 0:
                                sets.append(Set(set_name=s['set_name'],
                                                set_code=s['set_code']).get_dict_sets())
                            else:
                                item_found = False
                                for ss in sets:
                                    if s['set_code'] == ss['set_code']:
                                        item_found = True
                                        break

                                if not item_found:
                                    sets.append(Set(set_name=s['set_name'],
                                                    set_code=s['set_code']).get_dict_sets())

                        sets = sorted(sets, key=lambda k: (len(k['set_code']), k['set_code']))
                        card_sets.append(CardSets(card_name=card_set['name'],
                                                  image=card_set['card_images'][0]['image_url_small'],
                                                  sets=sets).get_dict_card_sets())

            print(f'Card sets: {card_sets}')
            return card_sets
        except Exception as e:
            print(f'TCGP - Occurred the following error trying to get card sets from name: {e}')
            raise Exception(e)

    def get_rarity(self, card_text):
        card_text = card_text.upper()
        rarity = ""

        if "ULTIMATE RARE" in card_text:
            rarity = "Ultimate Rare"
        elif "PRISMATIC  SECRET RARE" in card_text:
            rarity = "Prismatic Secret Rare"
        elif "SECRET RARE" in card_text:
            rarity = "Secret Rare"
        elif "ULTRA RARE" in card_text:
            rarity = "Ultra Rare"
        elif "SUPER RARE" in card_text:
            rarity = "Super Rare"

        return rarity


def send_mail(FROM, TO, SUBJECT, TEXT):
    try:
        yag = yagmail.SMTP(FROM, 'Cyberdragon78%')
        yag.send(TO, SUBJECT, TEXT)
    except Exception as e:
        print(f"Ocurredthe following error sending email: {e}")

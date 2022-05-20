import os
from time import sleep

import requests as requests
from woocommerce import API
import json


class WCAPIUtils:
    def __init__(self, consumer_key="ck_0d88e046fbbacea08525bbf74f77cfd5794ada29",
                 consumer_secret="cs_683c187a8a5a809e7753a74cd4daf57514986165", ignore_code_file=False):
        self.wcapi = API(
            url="https://ygomarketcr.com",
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            version="wc/v3",
            timeout=320
        )

        data = []
        if not ignore_code_file:
            if os.path.exists("card_codes.json"):
                with open('card_codes.json') as json_file:
                    data = json.load(json_file)
                start_from_page = round(len(data) / 100)
            else:
                start_from_page = 1

            self.codes = self.get_all_codes(data=data, start_from_page=start_from_page)

            with open('card_codes.json', 'w') as convert_file:
                convert_file.write(json.dumps(self.codes, indent=4))

            self.code_list = list(dict.fromkeys([c["name"].split("-")[0] for c in self.codes]))
        self.base_url = "https://ygomarketcr.com"
        self.wp_username = "gvegaq86@gmail.com"
        self.wp_password = "Cyberdragon78%"

    def get_products(self, page=1, per_page=100, retries=3):
        for n in range(0, retries):
            try:
                return self.wcapi.get("products", params={"per_page": per_page, "page": page}).json()
            except Exception as e:
                print(str(e))
                sleep(3)
        return None


    def get_codes(self, page=1, per_page=100, order_by=None):
        params = {"per_page": per_page, "page": page, "order": "desc"}

        if order_by:
            params["orderby"] = order_by

        return self.wcapi.get("products/attributes/4/terms", params=params).json()

    def get_all_codes(self, data=None, start_from_page=1):

        codes = []

        for x in range(start_from_page, 20):
            codes.extend(self.get_codes(x, 100))

        return codes

    def get_all_codes(self, data=None, start_from_page=1):

        if data:
            codes = data
        else:
            codes = []

        if codes:
            for x in range(start_from_page, 100):
                c = self.get_codes(x, 100)
                if c:
                    cl = []
                    [cl.append(ccc) if len(list(filter(lambda x: x["id"] == ccc["id"], codes))) == 0 else None for ccc
                     in c]

                    if cl:
                        codes.extend(cl)
                else:
                    break
        else:
            for x in range(start_from_page, 100):
                c = self.get_codes(x, 100)
                if c:
                    codes.extend(c)
                else:
                    break

        return codes

    def get_id_from_code(self, codigo):
        codigo = list(filter(lambda x: x['name'] == codigo, self.codes))

        if codigo:
            return codigo[0]['id']
        else:
            return None

    def get_product_by_filter(self, codigo, condition, edition, rarity, language=None, jcg=False):
        products = self.get_products_by_code_id(self.get_id_from_code(codigo))
        products = list(filter(lambda x: x['attributes'][1]['options'][0] == edition and
                                         condition in x['attributes'][4]['options'][0] and
                                         x['attributes'][3]['options'][0] == rarity, products))
        if language:
            products = list(filter(lambda x: x["attributes"][6]["options"][0] == language, products))
        else:
            products = list(filter(lambda x: x["attributes"][6]["options"][0] == "English", products))

        if jcg:
            products = list(filter(lambda x: 'jcg' in str(x['tags']), products))

        products = sorted(products, key=lambda item: hasattr(item, "tags") and str(item["tags"]))

        if products:
            for i in products:
                if i['tags'] is [] or ('jcg' not in str(i['tags']) and 'gvq' not in str(i['tags'])):
                    return i
        else:
            return None

    def get_products_by_code_id(self, id, page=1, per_page=100):
        return self.wcapi.get(f"products?attribute=pa_codigo&attribute_term={id}", params={"per_page": per_page,
                                                                                           "page": page}).json()

    def get_rarity_terms(self, page=1, per_page=100):
        results = self.wcapi.get(f"products/attributes/5/terms", params={"per_page": per_page, "page": page}).json()
        results = sorted(results, key=lambda x: x["name"])
        return [r["name"] for r in results]

    def get_edition_terms(self, page=1, per_page=100):
        results = self.wcapi.get(f"products/attributes/6/terms", params={"per_page": per_page, "page": page}).json()
        results = sorted(results, key=lambda x: x["name"])
        return [r["name"] for r in results]

    def get_condition_terms(self, page=1, per_page=100):
        results = self.wcapi.get(f"products/attributes/3/terms", params={"per_page": per_page, "page": page}).json()
        results = sorted(results, key=lambda x: x["name"])
        return list(set([r["name"].split(" ")[-1].replace("(", "").replace(")", "") for r in results]))

    def get_card_type_terms(self, page=1, per_page=100):
        results = self.wcapi.get(f"products/attributes/8/terms", params={"per_page": per_page, "page": page}).json()
        results = sorted(results, key=lambda x: x["name"])
        return list(set([r["name"].split(" ")[-1].replace("(", "").replace(")", "") for r in results]))

    def get_categories_terms(self, page=1, per_page=100):
        results = self.wcapi.get(f"products/categories/", params={"per_page": per_page, "page": page}).json()
        results = sorted(results, key=lambda x: x["name"])
        return results

    def get_edit_tags_terms(self, page=1, per_page=100):
        results = self.wcapi.get(f"products/tags/", params={"per_page": per_page, "page": page}).json()
        results = sorted(results, key=lambda x: x["name"])
        return results

    def get_all_products(self):
        try:
            print("Getting all the products...")
            products = []
            i = 1
            while True:
                items = self.get_products(page=i, per_page=100)
                if items:
                    products.extend(items)
                    i += 1
                else:
                    break
            print(f"{len(products)} products were found")
            return products
        except Exception as e:
            print(e)
            pass

    def upload_image(self, file_name):
        end_point_url_img = f'{self.base_url}/wp-json/wp/v2/media'
        headers = {'Content-Type': "image/jpeg", 'Content-Disposition': 'attachment; filename=%s'
                                                                        % os.path.basename(file_name)}
        post = {'caption': '', 'description': ''}

        if "http" in file_name:
            data = requests.get(file_name).content
        else:
            data = open(file_name, 'rb').read()

        response = requests.post(url=end_point_url_img, data=data, headers=headers, json=post,
                                 auth=(self.wp_username, self.wp_password))
        response = response.json()
        return response["source_url"]

    def delete_image(self, id):
        end_point_url_img = f'{self.base_url}/wp-json/wp/v2/media/{id}'

        response = requests.delete(url=end_point_url_img, params={"force": True}, auth=(self.wp_username,
                                                                                        self.wp_password))
        response = response.json()
        return response

    def update_product(self, id, data):
        return self.wcapi.put(f"products/{id}", data).json()

    def delete_product(self, id):
        return self.wcapi.delete(f"products/{id}", params={"force": True}).json()

    def insert_product(self, data):
        response = self.wcapi.post(f"products", data).json()

        if hasattr(response, "data") and response["data"]["status"] != 201:
            raise Exception(response["message"])
        else:
            return response

    def get_products_by_id(self, id, page=1, per_page=100):
        return self.wcapi.get(f"products/{id}", params={"per_page": per_page, "page": page}).json()

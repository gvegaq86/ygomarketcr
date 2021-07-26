import os
from multiprocessing.pool import ThreadPool

import requests as requests
from woocommerce import API


class WCAPIUtils:
    def __init__(self, consumer_key="ck_b7254f31da371ea5c5c3641989e0591f0bb5ea0a",
                 consumer_secret="cs_f0634c862d71b393735fc4d440841edaa2132cd0"):
        self.wcapi = API(
            url="https://ygomarketcr.com",
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            version="wc/v3",
            timeout=60
        )
        self.codes = self.get_all_codes()
        self.base_url = "https://ygomarketcr.com"
        self.wp_username = "gvegaq86@gmail.com"
        self.wp_password = "yova69777"

    def get_products(self, page=1, per_page=100):
        return self.wcapi.get("products", params={"per_page": per_page, "page": page}).json()

    def get_codes(self, page=1, per_page=100):
        return self.wcapi.get("products/attributes/4/terms", params={"per_page": per_page, "page": page}).json()

    def get_all_codes(self):
        pool = ThreadPool(processes=20)
        results = []

        for x in range(1, 20):
            async_result = pool.apply_async(self.get_codes, (x, 100))
            results.append(async_result)

        codes = []
        for result in results:
            codes.extend(result.get())

        return codes

    def get_id_from_code(self, codigo):
        codigo = list(filter(lambda x: x['name'] == codigo, self.codes))

        if codigo:
            return codigo[0]['id']
        else:
            return None

    def get_product_by_filter(self, codigo, condition, edition, rarity):
        products = self.get_products_by_code_id(self.get_id_from_code(codigo))
        products = list(filter(lambda x: x['attributes'][1]['options'][0] == edition and
                                         condition in x['attributes'][4]['options'][0] and
                                         x['attributes'][3]['options'][0] == rarity, products))
        return products[0] if products else None

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

    def get_all_products(self):
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

    def update_product(self, id, data):
        return self.wcapi.put(f"products/{id}", data).json()

    def delete_product(self, id):
        return self.wcapi.delete(f"products/{id}").json()

    def insert_product(self, data):
        response = self.wcapi.post(f"products", data).json()
        if hasattr(response, "data") and response["data"]["status"] != 201:
            raise Exception(response["message"])
        else:
            return response

    def get_products_by_id(self, id, page=1, per_page=100):
        return self.wcapi.get(f"products/{id}", params={"per_page": per_page, "page": page}).json()

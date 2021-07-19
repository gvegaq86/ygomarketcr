from multiprocessing.pool import ThreadPool

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
                                         x['attributes'][4]['options'][0] == condition and
                                         x['attributes'][3]['options'][0] == rarity, products))
        return products[0] if products else None

    def get_products_by_code_id(self, id, page=1, per_page=100):
        return self.wcapi.get(f"products?attribute=pa_codigo&attribute_term={id}", params={"per_page": per_page,
                                                                                           "page": page}).json()

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

    def update_product(self, id, data):
        return self.wcapi.put(f"products/{id}", data).json()

    def get_products_by_id(self, id, page=1, per_page=100):
        return self.wcapi.get(f"products/{id}", params={"per_page": per_page, "page": page}).json()

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

    def get_products(self, page=1, per_page=100):
        return self.wcapi.get("products", params={"per_page": per_page, "page": page}).json()

    def get_products_by_id(self, id, page=1, per_page=100):
        return self.wcapi.get(f"products/{id}", params={"per_page": per_page, "page": page}).json()

    def get_all_products(self):
        print("Getting all the products...")
        products = []
        i = 1
        while True:
            items = self.get_products(page=i,  per_page=100)
            if items:
                products.extend(items)
                i += 1
            else:
                break
        print(f"{len(products)} products were found")
        return products

    def update_product(self, id, data):
        return self.wcapi.put(f"products/{id}", data).json()
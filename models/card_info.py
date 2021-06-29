

class CardInfo:
    def __init__(self, card_name, card_key, price=0, pricec="", condition="", edition="", rarity="", quantity=0,
                 expansion="", image="", web_site=""):
        self.card_name = card_name
        self.card_key = card_key
        self.price = price
        self.pricec = pricec
        self.condition = condition
        self.edition = edition
        self.rarity = rarity
        self.quantity = quantity
        self.expansion = expansion
        self.image = image
        self.web_site = web_site

    def get_dict_card_info(self):
        dict_card_info = {
                            "card_name": self.card_name,
                            "expansion": self.expansion,
                            "card_key": self.card_key,
                            "image": self.image,
                            "rarity": self.rarity,
                            "quantity": self.quantity,
                            "condition": self.condition,
                            "edition": self.edition,
                            "price": f'${self.price}',
                            "pricec": self.pricec,
                            "web_site": self.web_site,
                          }
        return dict_card_info



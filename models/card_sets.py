

class CardSets:
    def __init__(self, card_name, sets="", image=""):
        self.card_name = card_name
        self.image = image
        self.sets = sets

    def get_dict_card_sets(self):
        dict_card_sets = {
                            "card_name": self.card_name,
                            "image": self.image,
                            "sets": self.sets
                          }
        return dict_card_sets



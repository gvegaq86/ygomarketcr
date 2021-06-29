

class Set:
    def __init__(self, set_name, set_code):
        self.set_name = set_name
        self.set_code = set_code

    def get_dict_sets(self):
        dict_sets = {
            "set_name": self.set_name,
            "set_code": self.set_code
        }
        return dict_sets



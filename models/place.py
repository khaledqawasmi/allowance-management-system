class Place:
    def __init__(self, name, expected_cost):
        self.name = name
        self.expected_cost = expected_cost

    def validate_place(self):
        if not self.name:
            return False

        if self.expected_cost < 0:
            return False

        return True
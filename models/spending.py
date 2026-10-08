class Spending:
    def __init__(self, amount):
        self.amount = amount

    def validate_amount(self, remaining_balance):
        if self.amount < 0:
            return False

        if self.amount > remaining_balance:
            return False

        return True
class Allowance:

    def __init__(self, amount, period, number_days):
        self.amount = amount
        self.period = period
        self.number_days = number_days
        self.daily_budget = 0
        self.remaining_balance = amount
        self.remaining_daily_budget = 0

    def calculate_daily_budget(self):
        self.daily_budget = self.amount / self.number_days
        return self.daily_budget

    def update_remaining_balance(self, spending_amount):
        self.remaining_balance -= spending_amount

    def calculate_remaining_daily_budget(self, remaining_days):
        if remaining_days > 0:
            self.remaining_daily_budget = (
                self.remaining_balance / remaining_days
            )
        else:
            self.remaining_daily_budget = self.remaining_balance

        return self.remaining_daily_budget
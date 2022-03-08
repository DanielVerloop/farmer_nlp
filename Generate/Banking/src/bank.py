class BankAccount:

    balance = None

    def __init__(self, balance):
        self.balance = balance

    def get_balance(self):
        return self.balance

    def set_balance(self, balance):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        self.balance -= amount
        return self.balance
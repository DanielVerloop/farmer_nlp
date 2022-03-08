from behave import *
from Generate.Banking.src.bank import BankAccount

@given('a bank account with initial balance of 0')
def step_given_empty_account(context):
    context.bank_account = BankAccount(0)

@when('we deposit 100 pounds into the account')
def step_when_deposit(context):
    context.bank_account.deposit(100)

@then('the balance should be 100')
def step_then_balance(context):
    assert context.bank_account.balance == 100

@given('a bank account with initial balance of 1000')
def step_given_balance_1000(context):
    context.bank_account = BankAccount(1000)

@when('we withdraw 100 pounds from the account')
def step_when_withdraw_100(context):
    context.bank_account.withdraw(100)

@then('the balance should be 900')
def step_then_balance_is_900(context):
    assert context.bank_account.balance == 900

@given('a bank account with balance of 100')
def step_given_balance_100(context):
    context.bank_account = BankAccount(100)

@when('we deposit 20 pounds into the account')
def step_when_deposit_20(context):
    context.bank_account.deposit(20)

@then('the balance should be 120')
def step_then_balance_120(context):
    assert context.bank_account.balance == 120

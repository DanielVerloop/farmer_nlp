from behave import * 

from behave import * 

@given('Given a bank account with initial balance of 0') 
def step_impl(context): 
    context.bank_account = BankAccount(0)

@when('When we deposit 100 pounds into the account') 
def step_impl(context): 
    context.bank_account.deposit(100)

@then('Then the balance should be 100') 
def step_impl(context): 
    assert context.bank_account.balance == 100

@given('Given a bank account with initial balance of 1000') 
def step_impl(context): 
    context.bank_account = BankAccount(1000)

@when('When we withdraw 100 pounds from the account') 
def step_impl(context): 
    context.bank_account.withdraw(100)

@then('Then the balance should be 900') 
def step_impl(context): 
    assert context.bank_account.balance == 900

@given('Given a bank account with balance of 100') 
def step_impl(context): 
    context.bank_account = BankAccount(100)

@when('When we deposit 20 pounds into the account') 
def step_impl(context): 
    context.bank_account.deposit(20)

@then('Then the balance should be 120') 
def step_impl(context): 
    assert context.bank_account.balance == 120


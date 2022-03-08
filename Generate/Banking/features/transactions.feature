Feature: Transactions
  In order to manage my money,
  As an account owner
  I want to deposit and withdraw money from my account
  So that I can use it

  Scenario: deposit money to empty account
    Given a bank account with initial balance of 0
    When we deposit 100 pounds into the account
    Then the balance should be 100

  Scenario: withdraw money from a bank account
    Given a bank account with initial balance of 1000
    When we withdraw 100 pounds from the account
    Then the balance should be 900

  Scenario: deposit and withdraw money from a bank account
    Given a bank account with balance of 100
    When we deposit 20 pounds into the account
    Then the balance should be 120
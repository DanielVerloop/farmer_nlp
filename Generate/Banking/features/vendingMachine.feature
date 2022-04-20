#FOR TESTING ONLY!
@tag
Feature: Vending Machine

  @tag1
  Scenario Outline: Have Product and user have exact amount of money
    Given there exists a vending machine
    And it has 10 <product> in its inventory
    When inserts the <money> pounds
    And presses the button with the code for <product>
    Then the stock reduces in 1 unit
    And the <product> leaves the machine

    Examples:
      | product     | money |
      | "chips"     |  2.00 |
      | "chocolate" |  2.50 |
      | "cookie"    |  1.75 |
      | "candy"     |  1.50 |
      | "juice"     |  3.25 |
      | "water"     |  1.50 |
      | "coke"      |  2.25 |
      | "pepsi"     |  2.25 |

  @tag2
  Scenario Outline: Have Product and user to receive change
    Given there exists a vending machine
    And it has 10 <product> in its inventory
    When the user inserts the <money> dollars
    And selects the <product>
    And the <product> leaves the machine
    Then the inventory stock must be 9 units
    And the vending machine gives <change> back

    Examples:
      | product     | money | change |
      | "chips"     |  2.50 |   0.50 |
      | "chocolate" |  3.50 |   1.00 |
      | "cookie"    |  2.00 |   0.25 |
      | "candy"     |  2.00 |   0.50 |
      | "juice"     |  5.00 |   1.75 |
      | "water"     |  3.00 |   1.50 |
      | "coke"      |  3.00 |   0.75 |
      | "pepsi"     |  2.25 |   0.00 |

    Examples:
      | product     | money | change |
      | "chips"     |  2.50 |   0.50 |
      | "chocolate" |  3.50 |   1.00 |
      | "cookie"    |  2.00 |   0.25 |
      | "candy"     |  2.00 |   0.50 |
      | "juice"     |  5.00 |   1.75 |
      | "water"     |  3.00 |   1.50 |
      | "coke"      |  3.00 |   0.75 |
      | "pepsi"     |  2.25 |   0.00 |

  @tag3
  Scenario Outline: user give less money than the price of the product
    Given there exists a vending machine
    And it has 10 <product> in its inventory
    When the user insert the <money>
    And presses the button with the code for the product
    Then the vending machine asks for <missing> dollars

    Examples:
      | product     | money |                           missing |
      | "chips"     |  1.00 | "still missing this amount: 1.00" |
      | "chocolate" |  2.00 | "still missing this amount: 0.50" |
      | "cookie"    |  1.50 | "still missing this amount: 0.25" |
      | "candy"     |  0.50 | "still missing this amount: 1.00" |
      | "juice"     |  1.25 | "still missing this amount: 2.00" |
      | "water"     |  0.75 | "still missing this amount: 0.75" |
      | "coke"      |  2.00 | "still missing this amount: 0.25" |
      | "pepsi"     |  1.25 | "still missing this amount: 1.00" |
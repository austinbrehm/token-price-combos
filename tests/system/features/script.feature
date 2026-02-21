Feature: Token Price Combos

  Scenario: Run the Script with Valid Inputs
    When the user runs the command "python3 src/main.py" with valid inputs
    Then the output should include "Done!"
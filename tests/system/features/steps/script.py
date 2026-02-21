import subprocess

from behave import when, then


@when('the user runs the command "python3 src/main.py" with valid inputs')
def step_impl(context):
    result = subprocess.run(
        ["python3", "src/main.py"],
        input="eth\n1\nbtc\n0.1\n10000\n",
        text=True,
        capture_output=True,
    )
    context.stdout = result.stdout


@then('the output should include "Done!"')
def step_impl(context):
    assert "Done!" in context.stdout

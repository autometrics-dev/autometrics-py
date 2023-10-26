from autometrics import autometrics, init

init()


@autometrics
def hello():
    """A function that prints hello"""
    print("Hello")


# Use the built-in `help` function to print the docstring for `hello`
#
# In your console, you'll see links to prometheus metrics for the `hello` function,
# which were added by the `autometrics` decorator.
help(hello)

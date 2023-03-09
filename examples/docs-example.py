import time
from autometrics.autometrics import autometrics

@autometrics
def hello():
   '''A function that prints hello'''
   print("Hello")

help(hello)

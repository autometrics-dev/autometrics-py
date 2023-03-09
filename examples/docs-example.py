import time
import autometrics

@autometrics.autometrics
def hello():
   '''A function that prints hello'''
   print("Hello")

help(hello)

from prometheus_client import start_http_server
import time
import autometrics
import prometheus_url

@autometrics.autometrics
def hello():
   '''A function that prints hello'''
   print("Hello")

help(hello)


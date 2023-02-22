import urllib.parse

class Generator():
   def __init__(self, functionName):
       self.functionName = functionName
       self.baseUrl = 'http://localhost:9090/'


   def createURLs(self):

        requestRateQuery =f'sum by (function, module) (rate (function_calls_count_total{{function="{self.functionName}"}}[5m]))'
        latencyQuery= f'sum by (le, function, module) (rate(function_calls_duration_bucket{{function="{self.functionName}"}}[5m]))'
        errorRatioQuery = f'sum by (function, module) (rate (function_calls_count{{function="{self.functionName}", result="error"}}[5m])) / {requestRateQuery}'

        queries = [requestRateQuery,latencyQuery, errorRatioQuery]
        names =["requestRateURL", "latencyURL", "errorRatioURL"]
        urls = {}
        for n in names:
           for query in queries:
              generateUrl = self.createPrometheusUrl(query)
              urls[n] = generateUrl
              queries.remove(query)
              break
        return urls
           #return urls
        



   def createPrometheusUrl(self, query):
        urlEncode = urllib.parse.quote(query)
        url =f'{self.baseUrl}graph?g0.expr={urlEncode}&g0.tab=0'
        return url
    
g = Generator("test")
urls = g.createURLs()
print(urls)
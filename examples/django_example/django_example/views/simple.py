from autometrics import autometrics
from django.http import HttpResponse


@autometrics
def simple_handler(request):
    "This is the simplest possible handler.  It just returns a string."
    return HttpResponse("Hello World")

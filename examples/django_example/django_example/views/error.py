import random
from autometrics import autometrics
from django.http import HttpResponse, HttpResponseServerError
from django.views import View


class ErrorOrOkView(View):
    """View that returns an error or an ok response depending on the
    coin flip
    """

    @autometrics
    def get(self, request):
        result = random.choice(["error", "ok"])
        if result == "error":
            raise Exception(result)
        return HttpResponse(result)

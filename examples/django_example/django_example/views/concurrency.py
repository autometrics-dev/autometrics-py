import time
from autometrics import autometrics
from django.http import HttpResponse
from django.views import View


class ConcurrencyView(View):
    """Here you can see how concurrency tracking works in autometrics.
    Just add the `track_concurrency=True` argument, and autometrics
    will track the number of concurrent requests to this endpoint."""

    @autometrics(track_concurrency=True)
    def get(self, request):
        time.sleep(0.25)
        return HttpResponse("Many clients wait for a reply from this endpoint!")

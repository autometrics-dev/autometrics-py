import random
import time
from autometrics import autometrics
from django.http import HttpResponse
from django.views import View


class RandomLatencyView(View):
    """This view has a random latency between 1 and 500ms"""

    @autometrics
    def get(self, request):
        duration = random.randint(1, 10)

        time.sleep(duration / 10)

        return HttpResponse("i was waiting for {}ms!".format(duration))

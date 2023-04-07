from prometheus_client import generate_latest
from django.http import HttpResponse


def metrics(_request):
    return HttpResponse(generate_latest())

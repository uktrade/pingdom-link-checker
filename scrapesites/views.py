from django.shortcuts import render

from .models import Brokenlink, Responsetime


# Create your views here.
def url_search_results(request):
	broken_links = Brokenlink.objects.all()
	response_time = Responsetime.objects.get(id=1).response_time
	context = {'broken_links': broken_links, 'response_time': response_time}
	return render(request, 'check.xml', context)

def logs(request):
	broken_links = Brokenlink.objects.all()
	context = {'broken_links': broken_links}
	return render(request, 'logs.html', context)

def scan(request):
    return render(request, 'scan-base.html', {})

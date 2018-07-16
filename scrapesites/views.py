from django.shortcuts import render

from .models import Brokenlink, Responsetime, Urllist


# Create your views here.
def url_search_results(request):
	# broken_links = Brokenlink.objects.all()
	response_time = Responsetime.objects.get(id=1).response_time
	url_list = Urllist.objects.all()
	

	# context['status'] = not any(x.temp_url.enable for x in Brokenlink.objects.all())

	broken_links = [x for x in Brokenlink.objects.all() if x.temp_url.enable]
	is_ok = len(broken_links) == 0

	context = {'broken_links': broken_links, 'url_list': url_list, 'response_time': response_time, 'is_ok': is_ok}

	return render(request, 'check.xml', context)

def logs(request):
	broken_links = Brokenlink.objects.all()
	url_list = Urllist.objects.all()
	context = {'broken_links': broken_links, 'url_list': url_list}
	return render(request, 'logs.html', context)

def scan(request):
    return render(request, 'scan-base.html', {})

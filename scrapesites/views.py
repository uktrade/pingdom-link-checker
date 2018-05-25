from django.shortcuts import render

# Create your views here.

# Create your views here.
def url_search_results(request):
    return render(request, 'check.xml', {})

def logs(request):
    return render(request, 'index.html', {})
